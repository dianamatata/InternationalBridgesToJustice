import json
from tqdm import tqdm
from src.openai_utils import openai_client
from src.query_functions import load_chroma_collection
from src.get_completeness import KeypointEvaluation
from src.config import Paths
from ensure_completeness_country_pages import get_completeness_keypoints


# MAIN ---------------------------------------------------
legal_collection = load_chroma_collection(Paths.PATH_CHROMADB, Paths.COLLECTION_NAME)

with open(Paths.PATH_FILE_SYSTEM_PROMPT_COMPLETENESS, "r") as file:
    system_prompt = file.read()

keypoints = get_completeness_keypoints(completeness_checklist_filepath=Paths.PATH_MD_FILE_COMPLETENESS_KEYPOINTS)
jsonl_file_completeness_batch = f"{Paths.PATH_FOLDER_COMPLETENESS}/batch_input.jsonl"

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
                    evaluation.define_prompt(Paths.PATH_FILE_PROMPT_COMPLETENESS)

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
    evaluation.define_prompt(Paths.PATH_FILE_PROMPT_COMPLETENESS)
    evaluation.check_completeness(
        openai_client, system_prompt, model="gpt-4o-mini", temperature=0.1
    )
    evaluation.save_evaluation()

