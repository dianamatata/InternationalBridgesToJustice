# LIBRARIES ---------------------------------------------------
import os
# The API key is stored in an environment file (.env), added to .gitignore for security reasons.
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
openai_api_key = os.environ.get("OPENAI_API_KEY")

from openai import OpenAI
import chromadb
import json
from tqdm import tqdm  # make your loops show a smart progress meter
from pprint import pprint
import re
import importlib # Use importlib.reload() to re-import your module after editing it
import query_database
importlib.reload(query_database)

from query_database import (load_chroma_collection,
                            build_context_text,
                            perform_similarity_search_metadata_filter,
                            get_openai_response) # TODO format_prompt, move it to query_database?


# FUNCTIONS ---------------------------------------------------

# 1 extract checklist to ensure completeness of country pages
def get_completeness_checklist():
    completeness_checklist_filepath = "data/raw/IBJ_docs/Completeness_checklist.md"
    with open(completeness_checklist_filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    keypoints = []
    for line in lines[2:]:
        stripped = line.strip()
        if line.strip() == "":
            continue  # skip empty lines
        keypoints.append(line.replace("  \n", ""))
    return keypoints


# 2 - Get country names from the Defense Wiki Country pages
def get_countries():
    country_names_filepath = "data/interim/country_names_1.txt"
    with open(f"{country_names_filepath}", "r", encoding="utf-8") as f:
        country_names = f.read().splitlines()
        len(country_names) # 204
        return country_names

def format_prompt(prompt_template: str, keypoint: str, wiki_content: str, database_content: str) -> str:
    """
    Build the final prompt by inserting the claim and context into the template.
    """
    return prompt_template.format(keypoint=keypoint, wiki_content=wiki_content, database_content=database_content)


def check_keypoint_covered(collection, client, country, chapter, point, PROMPT_KEYPOINT_COUNTRY_v2):

    keypoint_to_check = f"{chapter}: {point}"

    # Query wiki_content for the 5 most relevant chunks looking for that country and this specific point
    wiki_content = perform_similarity_search_metadata_filter(collection,
                                                             query_text=keypoint_to_check,
                                                             metadata_param="link",
                                                             metadata_value=f"https://defensewiki.ibj.org/index.php?title={country}",
                                                             n_results=5)

    # Query database for the 5 most relevant chunks looking for that country and this specific point
    database_content = perform_similarity_search_metadata_filter(collection,
                                                                 query_text=keypoint_to_check,
                                                                 metadata_param="country",
                                                                 metadata_value=country,
                                                                 n_results=5)

    context_database = build_context_text(database_content)
    context_wiki = build_context_text(wiki_content)

    prompt = format_prompt(PROMPT_KEYPOINT_COUNTRY_v2, keypoint=f"{chapter}: {point}", wiki_content=context_wiki,
                           database_content=context_database)

    answer = get_openai_response(client, prompt)
    # pprint(prompt)
    # pprint(answer)
    return answer


def save_answer(country, keypoint_to_check, wiki_content, database_content, answer):
    """
    Save the answer to a JSON file.
    """
    country_keypoint = {
        "country": country,
        "keypoint": keypoint_to_check,
        "wiki_content": {
            "ids": wiki_content.get("ids", [[]])[0],
            "title_bis": wiki_content.get("metadatas", [[]])[0],
            "distances": wiki_content.get("distances", [[]])[0],
        },
        "database_content": {
            "ids": database_content.get("ids", [[]])[0],
            "title_bis": database_content.get("metadatas", [[]])[0],
            "distances": database_content.get("distances", [[]])[0],
        },
        "answer": answer,
        "completeness_assessment" : answer.split("**")[1]
    }

    # save the answer in a json file
    with open(f"data/completeness/{country}.json", "a", encoding="utf-8") as json_file:
        json.dump(country_keypoint, json_file, indent=4)

    """
        Save the answer to a MD file.
    """

    with open(f"data/completeness/{country}_answer.md", "a", encoding="utf-8") as f:
        f.write(f"# {country}\n\n")
        f.write(f"## {keypoint_to_check}\n\n")
        f.write(answer)
        f.write("\n\n\n\n")


# MAIN ---------------------------------------------------
client = OpenAI()

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "legal_collection"
collection = load_chroma_collection(CHROMA_PATH, COLLECTION_NAME)

countries = get_countries()
keypoints = get_completeness_checklist()

with open("prompt_completeness.md", "r") as f:
    PROMPT_KEYPOINT_COUNTRY_v2 = f.read()

countries = ["Burundi"] # TODO remove this line to run for all countries
chapter = ""
for country in countries:
    for point in tqdm(keypoints):
    # for point in tqdm(keypoints[10:15]): # TODO remove this line to run for all keypoints
        # if point is not a new chapter
        indent = len(point) - len(point.lstrip())  # Capture the indentation (number of leading spaces)
        if indent == 0:
            chapter = point
        if indent > 0:
            print(f"\033[93m{chapter}:\033[0m\033[94m{point}\033[0m")
            keypoint_to_check = f"{chapter}: {point}"

            wiki_content = perform_similarity_search_metadata_filter(collection,
                                                                     query_text=keypoint_to_check,
                                                                     metadata_param="link",
                                                                     metadata_value=f"https://defensewiki.ibj.org/index.php?title={country}",
                                                                     n_results=5)

            database_content = perform_similarity_search_metadata_filter(collection,
                                                                         query_text=keypoint_to_check,
                                                                         metadata_param="country",
                                                                         metadata_value=country,
                                                                         n_results=5)

            context_database = build_context_text(database_content)
            context_wiki = build_context_text(wiki_content)

            prompt = format_prompt(PROMPT_KEYPOINT_COUNTRY_v2, keypoint=f"{chapter}: {point}", wiki_content=context_wiki,
                                   database_content=context_database)

            answer = get_openai_response(client, prompt)
            completeness_assessment = re.split(r':|\n', answer.split("**")[2])[1]
            save_answer(country, keypoint_to_check, wiki_content, database_content, answer) # save as json file and md file
            with open(f"data/completeness/{country}_summary.md", "a", encoding="utf-8") as f: # save summary
                f.write(f"Keypoint '{point}' covered?  {completeness_assessment} \n\n")


# debug
# chapter = keypoints[10]
# point = keypoints[11]
# all in one function? need to return database_content and more things, no for the moment
# answer = check_keypoint_covered(collection, client, country, chapter, point, PROMPT_KEYPOINT_COUNTRY_v2)
