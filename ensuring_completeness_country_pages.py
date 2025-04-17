# LIBRARIES ---------------------------------------------------
import os
# The API key is stored in an environment file (.env), added to .gitignore for security reasons.
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
openai_api_key = os.environ.get("OPENAI_API_KEY")

from openai import OpenAI
import chromadb
import json
from pprint import pprint

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


def check_keypoint_covered(country, chapter, point):
    # Query database for the 5 most relevant chunks looking for that country and this specific point
    # check if the point is covered in the database, if yes extract relevant lawys and legal chapters
    # check if the input data on document covers the point
    # with all this info "re"formulate an answer and assess whether we answered well the question

PROMPT_KEYPOINT_COUNTRY = (
    "Your task is to critically assess whether the following wiki chapter contains sufficient information to address the point: **{keypoint}**.\n\n"
    "Based on your analysis, classify the wiki chapter as one of the following:\n"
    "- **Complete**: The wiki chapter directly and sufficiently addresses the point.\n"
    "- **Needs refinement**: The point is mentioned but lacks clarity, depth, or specificity.\n"
    "- **Missing**: The point is not addressed at all.\n\n"
    "To support your reasoning, consult the database content. It may contain legal references or authoritative information related to the point, but this is not guaranteed.\n"
    "Cite specific laws or legal chapters from the database when relevant to justify your decision.\n\n"
    "Wiki_content (to be evaluated):\n{wiki_content}\n\n"
    "Database_content (for reference and legal support):\n{database_content}\n"
)

# V2: we want: Emphasis on legal grounding, Guidance on how to use the database: not just citation, but summarization + relevance
PROMPT_KEYPOINT_COUNTRY = (
    "You are tasked with evaluating whether the following wiki chapter provides sufficient, focused, and legally grounded information to address the key point: **{keypoint}**.\n\n"
    "Classify the wiki chapter as one of the following:\n"
    "- **Complete**: The chapter directly addresses the point with adequate legal detail (e.g., cites laws, explains protections or procedures).\n"
    "- **Needs refinement**: The chapter touches on the topic but lacks clear definitions, specific legal references, or concrete details. In this case, specify **what is missing**, and use the database to **suggest how the wiki could be improved**, e.g., by summarizing or citing relevant laws.\n"
    "- **Missing**: The chapter does not address the point at all.\n\n"
    "Your analysis should be critical. Avoid generic affirmations. Focus on whether the wiki clearly defines the legal concepts involved, cites relevant protections, and aligns with the key point.\n\n"
    "If available, use the database content to extract **specific legal articles or provisions** that clarify or strengthen the wiki's coverage. Explain **what these laws say**, and how they relate to the key point. Don't just mention a law — summarize its relevance.\n\n"
    "Wiki_content (chapter to be evaluated):\n{wiki_content}\n\n"
    "Database_content (legal text for potential support):\n{database_content}\n"
)

# MAIN ---------------------------------------------------
client = OpenAI()

countries = get_countries()
keypoints = get_completeness_checklist()

chapter = ""
for country in countries:
    for point in keypoints:
        # if point is not a new chapter
        indent = len(point) - len(point.lstrip())  # Capture the indentation (number of leading spaces)
        if indent == 0:
            chapter = point
        if indent > 0:
            result = check_keypoint_covered(country, chapter, point)
            if result:
                print(f"Keypoint '{point}' is covered in {country}.")
            else:
                print(f"Keypoint '{point}' is NOT covered in {country}.")
                # check in database
                # check on internet

# debug
chapter = keypoints[10]
point = keypoints[11]
keypoint_to_check = f"{chapter}: {point}" # '2. Rights of the Accused:    1. Right Against Unlawful Arrests, Searches and Seizures'
country = "Burundi"
COLLECTION_NAME = "legal_collection"
CHROMA_PATH = "data/chroma_db"
collection = load_chroma_collection(CHROMA_PATH, COLLECTION_NAME)
print(f"keypoint: {keypoint_to_check}, country: {country}")

wiki_content = perform_similarity_search_metadata_filter(collection,
                                                             query_text=keypoint_to_check,
                                                             metadata_param="link",
                                                             metadata_value="https://defensewiki.ibj.org/index.php?title=Burundi",
                                                             n_results=5)

database_content = perform_similarity_search_metadata_filter(collection,
                                                         query_text=keypoint_to_check,
                                                         metadata_param="country",
                                                         metadata_value="Burundi",
                                                         n_results=5)

context_database = build_context_text(database_content)
context_wiki = build_context_text(wiki_content)

prompt = format_prompt(PROMPT_KEYPOINT_COUNTRY, keypoint=f"{chapter}: {point}", wiki_content=context_wiki, database_content=context_database)

answer = get_openai_response(client, prompt)
pprint(answer)

# SAVE ---------------------------------------------------

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
    "answer": answer
}

# TODO save the answer in a json file
with open(f"data/completeness/{country}.json", "a", encoding="utf-8") as json_file:
    json.dump(country_keypoint, json_file, indent=4)

# v2
"""
('**Complete**: The chapter directly addresses the key point - Right Against '
 'Unlawful Arrests, Searches, and Seizures - with adequate legal detail.\n'
 '\n'
 'The wiki chapter provides a comprehensive breakdown of the procedural '
 'safeguards against unlawful arrests, searches, and seizures, with references '
 'to relevant sections in the Constitution and the Code of Criminal Procedure. '
 'It includes a detailed discussion of the right to be informed of the motives '
 'for arrest, the right to be presumed innocent, and the right to be assisted '
 'by a lawyer. Police procedures are also covered, with specific emphasis on '
 'the rights of the accused during the pre-jurisdictional phase and police '
 'custody.\n'
 '\n'
 "The wiki chapter could be enhanced by referencing the database's legal "
 'provisions. For instance, it could cite Article 39 about ensuring freedom in '
 'accordance with provisions of law, Article 43 about protection against '
 'arbitrary interference in private life, and Article 40 about presumption of '
 'innocence for a person accused of a criminal act. These articles could '
 "provide additional backing to the wiki's coverage of the right against "
 'unlawful arrests, and searches, and seizures.\n'
 '\n'
 'Overall, however, the wiki chapter is in line with the key point and '
 'provides detailed explanations, legal references, and specifics on the legal '
 'protections of the accused. It offers a clear view of the legal framework '
 'surrounding arrests, searches, seizures, and the rights of the accused in '
 'the process.')


# v1
('**Needs refinement**: The wiki chapter does provide an overview and address '
 'the right against unlawful arrests, searches, and seizures but it lacks '
 'specific detail and depth on this point. There is no direct mention of what '
 'constitutes an "unlawful" arrest, search, or seizure, or the guarantees '
 'under the code of criminal procedure, constitution, or any other relevant '
 'laws that specifically protect individuals against them. \n'
 '\n'
 'What is available in the wiki is valuable information about overall rights '
 'of the accused, such as the right to be informed of reasons for arrest, to '
 'be presumed innocent, to be assisted by a lawyer, not to be subjected to '
 'torture, to be judged within a reasonable time, to a public trial, to an '
 'interpreter, to silence, and to know the content of the case-file. However, '
 'the specific topic of rights against unlawful arrests, searches, and '
 'seizures needs a more focused definition and elaboration.\n'
 '\n'
 'In justifying this, even from the database content, *Article 39* is a direct '
 'legal reference for the protection against deprivation of freedom, and '
 '*Article 43* also mentions protection against arbitrary interference and '
 'infringement, which can provide key details for the right against unlawful '
 'arrests, searches, and seizures. This valuable information can be used to '
 'refine the given point in the wiki chapter.')
 """
