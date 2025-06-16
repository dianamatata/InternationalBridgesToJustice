import json
import os
from tqdm import tqdm
from src.internationalbridgestojustice.openai_utils import (
    openai_client,
    upload_batch_file_to_openAI,
    submit_batch_job,
    check_progress_batch_id,
    save_batch_id,
    retrieve_and_save_batch_results,
    retrieve_tool_calls,
)
from src.internationalbridgestojustice.chromadb_utils import load_collection
from src.internationalbridgestojustice.get_completeness import (
    KeypointEvaluation,
    json_to_markdown,
    completeness_statistics,
)
from src.internationalbridgestojustice.config import Paths
from src.internationalbridgestojustice.file_manager import save_file

# MAIN ---------------------------------------------------

with open(Paths.PATH_FILE_PROMPT_COMPLETENESS, "r") as file:
    prompt_completeness = file.read()

with open(Paths.PATH_FILE_SYSTEM_PROMPT_COMPLETENESS, "r") as file:
    system_prompt = file.read()

with open(Paths.PATH_JSON_FILE_DESCRIPTIVE_COMPLETENESS_KEYPOINTS, "r") as file:
    completeness_keypoints = json.load(file)

legal_collection = load_collection(Paths.PATH_CHROMADB_v2, Paths.COLLECTION_NAME_v2)

batch_submission = True

if batch_submission == True:
    countries = ["Burundi"]  # TODO remove this line to run for all countries
    for country in countries:
        jsonl_file_completeness_batch = f"{Paths.PATH_FOLDER_COMPLETENESS}/batch_input_completeness_Burundi_all.jsonl"
        os.remove(jsonl_file_completeness_batch)
        jsonl_file_completeness_batch_output = f"{Paths.PATH_FOLDER_COMPLETENESS}/batch_output_completeness_Burundi_all.jsonl"

        for keypoint in tqdm(completeness_keypoints):
            print(f"\033[92m{country}: \033[0m\033[93m{keypoint}: \033[0m")

            evaluation = KeypointEvaluation(
                country=country,
                keypoint=keypoint,
                system_prompt=system_prompt,
                model="gpt-4o-mini",
                collection=legal_collection,
                lazy=True,
            )
            evaluation.run_similarity_searches(collection=legal_collection)
            evaluation.define_prompt(prompt_completeness)
            evaluation.create_batch_file_for_completeness(
                jsonl_output_file_path=jsonl_file_completeness_batch,
                prompt=evaluation.prompt,
            )

        file = upload_batch_file_to_openAI(
            client=openai_client,
            batch_file_name=jsonl_file_completeness_batch,
        )
        batch = submit_batch_job(client=openai_client, file_id=file.id)
        save_batch_id(
            batch=batch,
            country=country,
            path_file=f"{Paths.PATH_FOLDER_COMPLETENESS}/batch_id_completeness.txt",
        )
    # RETRIEVE RESULTS ---------------------------------------------------

    # batch_684d683daacc8190acdd08591eabd9fa all burundi
    # TODO retrieve results in other script
    batch_id = "batch_684d683daacc8190acdd08591eabd9fa"
    print(f"Batch job submitted: {batch_id}")
    check_progress_batch_id(batch_id=batch_id)
    result = openai_client.batches.retrieve(batch_id=batch_id)
    parsed_results = retrieve_and_save_batch_results(
        batch_id=batch_id,
        output_file_path_jsonl="data/interim/completeness_Burundi_results.jsonl",
        return_parsed_results=True,
    )
    results_list = retrieve_tool_calls(parsed_results)

    save_file(
        filename=jsonl_file_completeness_batch_output,
        content=results_list,
        file_type="jsonl1",
    )

    with open(
        "data/completeness/completeness_Burundi_results.md", "a", encoding="utf-8"
    ) as f:
        for result in results_list:
            f.write(f"{json_to_markdown(result)}\n\n")

    counter_LPC, counter_Classification = completeness_statistics(results_list)
    with open(
        "data/completeness/completeness_Burundi_statistics.txt", "a", encoding="utf-8"
    ) as f:
        f.write(f"{counter_LPC}\n{counter_Classification}\n")


elif batch_submission == False:
    country = "Burundi"
    chapter = "7. Rights in prison"
    point = "2. Immigrant’s Rights in Detention"

    evaluation = KeypointEvaluation(
        country,
        chapter=chapter,
        point=point,
        system_prompt=system_prompt,
        model="gpt-4o-mini",
        collection=legal_collection,
        lazy=True,
    )
    evaluation.run_similarity_searches(collection=legal_collection)
    evaluation.define_prompt(prompt_completeness=Paths.PATH_FILE_PROMPT_COMPLETENESS)
    evaluation.check_completeness(client=openai_client, temperature=0.1)
    evaluation.save_evaluation()
