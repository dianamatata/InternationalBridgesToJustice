import json
from tqdm import tqdm
from src.openai_client import openai_client
from src.query_functions import load_chroma_collection
from src.get_completeness import KeypointEvaluation
from src.config import path_folder_completeness, path_file_prompt_completeness, path_chromadb, collection_name, path_file_system_prompt_completeness, path_md_file_completeness_keypoints
from ensure_completeness_country_pages import get_completeness_keypoints


# MAIN ---------------------------------------------------
legal_collection = load_chroma_collection(path_chromadb, collection_name)

with open(path_file_prompt_completeness, "r") as file:
    prompt_completeness = file.read()

with open(path_file_system_prompt_completeness, "r") as file:
    system_prompt = file.read()

keypoints = get_completeness_keypoints(completeness_checklist_filepath=path_md_file_completeness_keypoints)
jsonl_file_completeness_batch = f"{path_folder_completeness}/batch_input.jsonl"

batch_submission = True

if batch_submission == True:

    with open(jsonl_file_completeness_batch, "w") as outfile:
        countries = ["India"]  # TODO remove this line to run for all countries
        chapter = ""
        for country in countries:
            for point in tqdm(keypoints):
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

elif batch_submission == False:

    country = "Burundi"
    chapter = "7. Rights in prison"
    point = "2. Immigrant’s Rights in Detention"

    evaluation = KeypointEvaluation(
        country, chapter, point, collection=legal_collection, lazy=True
    )
    evaluation.ensure_loaded(legal_collection)  # Ensure the content is loaded
    evaluation.define_prompt(path_file_prompt_completeness)
    evaluation.check_completeness(
        openai_client, system_prompt, model="gpt-4o-mini", temperature=0.1
    )
    evaluation.save_evaluation()

