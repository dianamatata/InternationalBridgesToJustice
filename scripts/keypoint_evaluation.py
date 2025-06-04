import json
from tqdm import tqdm
from src.openai_utils import openai_client
from src.chromadb_utils import load_collection
from src.get_completeness import KeypointEvaluation
from src.config import Paths
from src.query_functions import get_completeness_keypoints


# MAIN ---------------------------------------------------
legal_collection = load_collection(Paths.PATH_CHROMADB, Paths.COLLECTION_NAME)

with open(Paths.PATH_FILE_PROMPT_COMPLETENESS, "r") as file:
    prompt_completeness = file.read()

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
                    evaluation = KeypointEvaluation(country, chapter=chapter, point=point, system_prompt=system_prompt,
                                                    model="gpt-4o-mini", collection=legal_collection, lazy=True)
                    evaluation.run_similarity_searches(collection=legal_collection)
                    evaluation.define_prompt(prompt_completeness=Paths.PATH_FILE_PROMPT_COMPLETENESS)

                    request = evaluation.build_batch_request(
                        custom_id=f"{country}-{keypoint_to_check}",
                        user_prompt=evaluation.prompt,
                        temperature=0.1
                    )

                    outfile.write(json.dumps(request) + "\n")

                    # Save
                    with open("data/completeness/keypoints.json", "a") as f:
                        json.dump(evaluation.to_dict(), f)

elif batch_submission == False:

    country = "Burundi"
    chapter = "7. Rights in prison"
    point = "2. Immigrant’s Rights in Detention"

    evaluation = KeypointEvaluation(country, chapter=chapter, point=point, system_prompt=system_prompt,
                                    model="gpt-4o-mini", collection=legal_collection, lazy=True)
    evaluation.run_similarity_searches(collection=legal_collection)
    evaluation.define_prompt(prompt_completeness=Paths.PATH_FILE_PROMPT_COMPLETENESS)
    evaluation.check_completeness(client=openai_client, temperature=0.1)

    evaluation.save_evaluation()

