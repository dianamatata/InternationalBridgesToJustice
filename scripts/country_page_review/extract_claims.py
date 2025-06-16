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
claim_extractor = ClaimExtractor()
country = "Burundi"
input_file_path_jsonl = (
    f"{Paths.PATH_FOLDER_COMPLETENESS}/batch_output_completeness_Burundi_all.jsonl"
)
output_file_path_jsonl = f"{Paths.PATH_FOLDER_CLAIM_EXTRACTION}/claims_Burundi.jsonl"

jsonl_file_claim_extraction_batch = (
    f"{Paths.PATH_FOLDER_CLAIM_EXTRACTION}/batch_input_extraction_Burundi_all.jsonl"
)
jsonl_file_claim_extraction_batch_output = (
    f"{Paths.PATH_FOLDER_COMPLETENESS}/batch_output_extraction_Burundi_all.jsonl"
)

completeness_keypoints = []
with open(input_file_path_jsonl, "r", encoding="utf-8") as file:
    for line in file:
        completeness_keypoints.append(json.loads(line))

batch_submission = False

if batch_submission == False:
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
    for keypoint in completeness_keypoints:
        print(keypoint["Rewritten_Wiki_Chapter"])
        response = keypoint["Rewritten_Wiki_Chapter"]

        claim_extractor.create_batch_file_for_extraction(
            response=response,
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
        batch_id = "batch_685009985fa48190961415687c207498"  # test burundi
        print(f"Batch job submitted: {batch_id}")

        check_progress_batch_id(batch_id=batch_id)
        # if failed:
        # result = openai_client.batches.retrieve(batch_id=batch_id)

        parsed_results = retrieve_and_save_batch_results(
            batch_id=batch_id,
            output_file_path_jsonl="data/interim/claimExtraction_Burundi_results.jsonl",
            return_parsed_results=True,
        )
        results_list = retrieve_tool_calls(parsed_results)

        save_file(
            filename=jsonl_file_claim_extraction_batch_output,
            content=results_list,
            file_type="jsonl1",
        )
