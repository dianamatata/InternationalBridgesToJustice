import json
from src.internationalbridgestojustice.get_claims import ClaimExtractor
from src.internationalbridgestojustice.config import Paths
from src.internationalbridgestojustice.file_manager import save_file
from src.internationalbridgestojustice.openai_utils import (
    openai_client,
    upload_batch_file_to_openAI,
    submit_batch_job,
    check_progress_batch_id,
    save_batch_id,
    retrieve_and_save_batch_results,
    retrieve_tool_calls,
)

# extract from output of completeness script
country = "Burundi"
input_file_from_completeness_jsonl = (
    "data/completeness/batch_output_completeness_Burundi_all.jsonl"
)
output_file_path_jsonl = (
    f"{Paths.PATH_FOLDER_CLAIM_EXTRACTION}/claims_extraction_Burundi_test.jsonl"
)

jsonl_file_claim_extraction_batch = (
    f"{Paths.PATH_FOLDER_CLAIM_EXTRACTION}/batch_input_extraction_Burundi_all.jsonl"
)
jsonl_file_claim_extraction_batch_output = (
    f"{Paths.PATH_FOLDER_CLAIM_EXTRACTION}/batch_output_extraction_Burundi_all.jsonl"
)

completeness_keypoints = []
with open(input_file_from_completeness_jsonl, "r", encoding="utf-8") as file:
    for line in file:
        completeness_keypoints.append(json.loads(line))

batch_submission = False

if batch_submission == False:
    claim_extractor = ClaimExtractor()
    for keypoint in completeness_keypoints:
        keypoint = completeness_keypoints[1]
        print(keypoint["Rewritten_Wiki_Chapter"])
        response = keypoint["Rewritten_Wiki_Chapter"]

        snippet_lst, claim_list, all_claims, total_cost = (
            claim_extractor.scan_text_for_claims(response)
        )
        output_dict = {
            "country": keypoint["Country"],
            "keypoint": keypoint["Keypoint"],
            "response": response.strip(),
            "total_cost": total_cost,
            "claim_list": claim_list,
            "all_claims": all_claims,
        }

        with open(output_file_path_jsonl, "a") as jsonl_file:  # a appends, w overwrites
            jsonl_file.write(json.dumps(output_dict) + "\n")

    print(f"extracted claims are saved at {Paths.PATH_JSONL_FILE_EXTRACTED_CLAIMS}")

elif batch_submission == True:
    claim_extractor = ClaimExtractor()
    for keypoint in completeness_keypoints:
        claim_extractor.create_batch_file_for_extraction(
            custom_id=keypoint["custom_id"].replace(
                "completeness", "claimextraction", 1
            ),
            response=keypoint["Rewritten_Wiki_Chapter"],
            country=country,
            keypoint=keypoint["Keypoint"],
            jsonl_output_file_path=jsonl_file_claim_extraction_batch,
        )

    file = upload_batch_file_to_openAI(
        client=openai_client,
        batch_file_name=jsonl_file_claim_extraction_batch,
    )
    batch = submit_batch_job(client=openai_client, file_id=file.id)
    save_batch_id(
        batch=batch,
        country=country,
        path_file=f"{Paths.PATH_FOLDER_CLAIM_EXTRACTION}/batch_id_extraction.txt",
    )

    # RETRIEVE RESULTS ---------------------------------------------------

    # TODO retrieve results in other script
    # TODO do we really need to run openAI per sentence. can we just write a prompt that also does the sentence separation?
    batch_id = "batch_685009985fa48190961415687c207498"  # test burundi
    batch_id = "batch_6851200fb0248190b5e8917a5e8a22c7"  # all burundi new

    print(f"Batch job submitted: {batch_id}")

    check_progress_batch_id(batch_id=batch_id)
    # result = openai_client.batches.retrieve(batch_id=batch_id) # if failed:

    parsed_results = retrieve_and_save_batch_results(
        batch_id=batch_id,
        output_file_path_jsonl="data/extracted_claims/claimExtraction_Burundi_results_all.jsonl",
        return_parsed_results=True,
    )
    results_list = retrieve_tool_calls(parsed_results)

    save_file(
        filename=jsonl_file_claim_extraction_batch_output,
        content=results_list,
        file_type="jsonl1",
    )
