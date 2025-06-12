import json
from tqdm import tqdm
from src.internationalbridgestojustice.openai_utils import (
    openai_client,
    upload_batch_file_to_openAI,
    submit_batch_job,
    check_progress_batch_id,
    save_batch_id,
    retrieve_and_save_batch_results,
)
from src.internationalbridgestojustice.chromadb_utils import load_collection
from src.internationalbridgestojustice.get_completeness import KeypointEvaluation
from src.internationalbridgestojustice.config import Paths


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
        jsonl_file_completeness_batch = (
            f"{Paths.PATH_FOLDER_COMPLETENESS}/batch_input_completeness_Burundi.jsonl"
        )

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
            prompt = evaluation.prompt
            evaluation.create_batch_file_for_completeness(
                jsonl_output_file_path=jsonl_file_completeness_batch,
                prompt=evaluation.prompt,
            )

        file = upload_batch_file_to_openAI(
            client=openai_client,
            batch_file_name=f"{Paths.PATH_FOLDER_COMPLETENESS}/batch_input_completeness_Burundi.jsonl",
        )
        batch = submit_batch_job(client=openai_client, file_id=file.id)
        save_batch_id(
            batch=batch,
            path_file=f"{Paths.PATH_FOLDER_COMPLETENESS}/batch_id_completeness.txt",
        )

    batch_id = "batch_684acce8ed588190a9f6f4bc006cf883"
    print(f"Batch job submitted: {batch_id}")
    check_progress_batch_id(batch_id=batch_id)

    # test
    # Get batch info and output file
    result = openai_client.batches.retrieve(batch_id=batch_id)
    output_stream = openai_client.files.content(result.output_file_id)

    # Convert stream to text
    output_text = output_stream.text

    # Parse JSONL (each line is a separate JSON object)
    results = []
    for line in output_text.strip().split("\n"):
        if line.strip():  # Skip empty lines
            parsed_result = json.loads(line)
            results.append(parsed_result)

    parsed_results = retrieve_and_save_batch_results(
        batch_id=batch_id,
        output_file_path_jsonl="data/interim/completeness_Burundi_results.jsonl",
        return_parsed_results=True,
    )


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
