from scripts.verify_one_claim import (
    build_context_string_from_retrieve_documents,
    load_chroma_collection,
    perform_similarity_search_metadata_filter,
    get_openai_response,
)
from src.keypoint_evaluation import KeypointEvaluation
from src.config import path_folder_completeness, path_file_prompt_completeness, path_chromadb, collection_name
jsonl_file_completeness_batch = f"{path_folder_completeness}/batch_input.jsonl"
from ensure_completeness_country_pages import (format_prompt_for_completeness_check,
                                               get_completeness_keypoints)

# modules for OpenAI
import os
import json
from tqdm import tqdm  # make your loops show a smart progress meter
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
openai_api_key = os.environ.get("OPENAI_API_KEY")
from openai import OpenAI


# DEFINE CLASS KeypointEvaluation ---------------------------------------------------


# FUNCTIONS ---------------------------------------------------

# TODO: make prompt_completeness a global variable is it a good idea?
prompt_completeness = None

def load_prompt_completeness():
    global prompt_completeness  # TODO: is it a good idea to have it global?
    with open(path_file_prompt_completeness, "r") as f:
        prompt_completeness = f.read()


# MAIN ---------------------------------------------------
# general loading
client = OpenAI()
legal_collection = load_chroma_collection(path_chromadb, collection_name)
system_prompt = "You are a critical legal analyst tasked with evaluating whether a legal wiki chapter adequately addresses a specific legal keypoint. Your response must be precise, structured, and based on legal reasoning. When relevant, cite and summarize laws from the provided legal database. Avoid vague language and clearly distinguish between complete, partial, or missing legal coverage."
load_prompt_completeness()
keypoints = get_completeness_keypoints()


# batch submission  ----------------------------------------
outfile_name = (jsonl_file_completeness_batch)
with open(outfile_name, "w") as outfile:
    countries = ["India"]  # TODO remove this line to run for all countries
    chapter = ""
    for country in countries:
        for point in tqdm(keypoints[10:13]): # TODO change this line to run for all keypoints
            indent = len(point) - len(
                point.lstrip()
            )
            if indent == 0:
                chapter = point
                print(chapter)
            if indent > 0:
                print(f"\033[92m{country}: \033[0m\033[93m{chapter}: \033[0m\033[94m{point}\033[0m")
                keypoint_to_check = f"{chapter}: {point}"
                evaluation = KeypointEvaluation(country, chapter, point, collection=legal_collection, lazy=True)
                evaluation.ensure_loaded(legal_collection)
                evaluation.define_prompt(path_file_prompt_completeness)

                request = evaluation.build_batch_request(
                    custom_id=f"{country}-{chapter}-{point}",
                    system_prompt=system_prompt,
                    user_prompt=evaluation.prompt,
                )

                outfile.write(json.dumps(request) + "\n")

                # Save
                with open("data/completeness/keypoints.json", "a") as f:
                    json.dump(evaluation.to_dict(), f)




# DEBUGGING ---------------------------------------------------
# evaluation.custom_id=f"{country}-{chapter}-{point}"
# evaluation.wiki_content = wiki_content
# evaluation.database_content = database_content
# create class item
# country = "Burundi"
# chapter = "7. Rights in prison"
# point = "      4. Juveniles\n"
evaluation = KeypointEvaluation(
    country, chapter, point, collection=legal_collection, lazy=True
)
evaluation.ensure_loaded(legal_collection)  # Ensure the content is loaded
evaluation.define_prompt(path_file_prompt_completeness)
evaluation.check_completeness(
    client, system_prompt, model="gpt-4o-mini", temperature=0.1
)
evaluation.save_evaluation()


hash_to_search = "39b44e8d658b6a112d380b2dbe02397c050ac5c759c23c15847d9dd46b2c64d8"
selected_chunk = next(
    (chunk for chunk in chunks if chunk["title"] == hash_to_search), None
)


# Load if one element
# with open("data/completeness/keypoints.json", "r") as f:
#     data = json.load(f)
#     loaded_instance = KeypointEvaluation.from_dict(data)


