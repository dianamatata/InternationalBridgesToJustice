# file outdated, now we are running keypoint_evaluation.py directly

# LIBRARIES ---------------------------------------------------
import os
os.chdir('/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice')
import json
from tqdm import tqdm
from src.config import Paths
from src.openai_utils import openai_client
from src.chromadb_utils import load_collection
from src.get_completeness import KeypointEvaluation
from src.file_manager import get_country_names

# MAIN ---------------------------------------------------

with open(Paths.PATH_FILE_PROMPT_COMPLETENESS, "r") as file:
    prompt_completeness = file.read()

with open(Paths.PATH_FILE_SYSTEM_PROMPT_COMPLETENESS, "r") as file:
    system_prompt = file.read()

with open(Paths.PATH_JSON_FILE_DESCRIPTIVE_COMPLETENESS_KEYPOINTS, "r") as file:
    completeness_keypoints = json.load(file)

collection = load_collection(Paths.PATH_CHROMADB, Paths.COLLECTION_NAME)

# For sequencial analysis :

country_names = get_country_names(country_names_filepath="data/interim/country_names_1.txt")
country_names = ["Burundi"]  # then test ["China", "India", "Singapore"]
for country in country_names:
    print(f"Country: {country}")
    for keypoint in tqdm(completeness_keypoints):
        evaluation = KeypointEvaluation(country=country, keypoint=keypoint, system_prompt=system_prompt, model="gpt-4o-mini", collection=collection, lazy=True)
        evaluation.run_similarity_searches(collection=collection)
        evaluation.define_prompt(prompt_template=prompt_completeness)
        evaluation.check_completeness(client=openai_client, temperature=0.1)
        evaluation.save_answer_as_json()
        evaluation.save_log_as_json()

# For batch analysis:

