import json
from src.internationalbridgestojustice.get_claims import (
    ClaimVerificator,
    json_to_markdown_verified_claim,
)
from src.internationalbridgestojustice.config import Paths
from src.internationalbridgestojustice.chromadb_utils import load_collection
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
from tqdm import tqdm


country = "Burundi"
jsonl_file_claim_extraction_batch_output = (
    f"{Paths.PATH_FOLDER_CLAIM_EXTRACTION}/batch_output_extraction_Burundi_all.jsonl"
)
jsonl_file_claim_verification_batch_input = (
    f"{Paths.PATH_FOLDER_CLAIM_VERIFICATION}/batch_input_verification_Burundi_all.jsonl"
)
jsonl_file_claim_verification_batch_output = f"{Paths.PATH_FOLDER_CLAIM_VERIFICATION}/batch_output_verification_Burundi_all.jsonl"

legal_collection = load_collection(Paths.PATH_CHROMADB_v5, Paths.COLLECTION_NAME_v5)

batch_submission = True
if batch_submission == False:
    claim = "The detention of minors is subject to strict judicial oversight."
    claim = "Burundi is located in the Great Lakes region of Africa."
    claim_verificator = ClaimVerificator(claim=claim)
    results, answer = claim_verificator.verify_claim(
        collection=legal_collection,
        client=openai_client,
        country=country,
    )
    response_obj = json.loads(answer)
    print(json.dumps(response_obj, indent=2, ensure_ascii=False))

if batch_submission == True:
    claim_verificator = ClaimVerificator(claim=claim)
    # TODO missing the script removing duplicated claims in claim_extraction
    with open(jsonl_file_claim_extraction_batch_output, "r") as file:
        claims_extracted = [json.loads(line) for line in file]

    claim_set = set()
    simil_search_all = []
    for element in tqdm(claims_extracted):
        if len(element["All_Claims"]) != 0:
            for i, claim in enumerate(element["All_Claims"]):
                if claim not in claim_set:
                    # print(f"Claim {i}: {claim}")
                    claim_set.add(claim)
                    custom_id = f"{element['custom_id'].replace('claimextraction', 'claimverification', 1)}:{i}"
                    request, simil_search = (
                        claim_verificator.create_batch_file_for_verification(
                            custom_id=custom_id,
                            claim=claim,
                            collection=legal_collection,
                            client=openai_client,
                            country=country,
                            jsonl_output_file_path=jsonl_file_claim_verification_batch_input,
                        )
                    )
                    simil_search = {"custom_id": custom_id, **simil_search}
                    simil_search_all.append(simil_search)

    with open(
        f"{Paths.PATH_FOLDER_CLAIM_VERIFICATION}/simil_search.jsonl",
        "w",
        encoding="utf-8",
    ) as jsonl_file:
        for record in simil_search_all:
            jsonl_file.write(json.dumps(record) + "\n")

    file = upload_batch_file_to_openAI(
        client=openai_client,
        batch_file_name=jsonl_file_claim_verification_batch_input,
    )
    batch = submit_batch_job(client=openai_client, file_id=file.id)
    save_batch_id(
        batch=batch,
        country=country,
        path_file=f"{Paths.PATH_FOLDER_CLAIM_VERIFICATION}/batch_id_verification.txt",
    )

    # RETRIEVE RESULTS ---------------------------------------------------
    batch_id = "batch_685152df88a48190bf179557d34fa2e7"  # all burundi new
    print(f"Batch job submitted: {batch_id}")

    check_progress_batch_id(batch_id=batch_id)
    # result = openai_client.batches.retrieve(batch_id=batch_id) # if failed:

    parsed_results = retrieve_and_save_batch_results(
        batch_id=batch_id,
        output_file_path_jsonl="data/verified_claims/test.jsonl",
        return_parsed_results=True,
    )
    results_list = retrieve_tool_calls(parsed_results)

    save_file(
        filename=jsonl_file_claim_verification_batch_output,
        content=results_list,
        file_type="jsonl1",
    )

# save in markdown
with open(
    "data/verified_claims/verified_claims_Burundi.md", "w", encoding="utf-8"
) as f:
    for data in results_list:
        f.write(f"{json_to_markdown_verified_claim(data)}\n\n")
# TODO Burundi is described as landlocked in section 3.3.4 of the context, not acceptable
# old
# from src.internationalbridgestojustice.query_functions import (
#     retrieve_source_titles_from_chunks,
# )


# # append to claim_data
# claim_data = {
#     "sentence": chunk_claims["response"].split(".")[i],
#     "claim": claim,
#     "decision": answer.split("###")[
#         1
#     ].strip(),  # Strip to remove whitespace
#     "full_answer": answer,
#     "sources": source_titles,
#     "document_ids": results.get("ids", [[]])[0],
#     "distances": results.get("distances", [[]])[0],
# }
