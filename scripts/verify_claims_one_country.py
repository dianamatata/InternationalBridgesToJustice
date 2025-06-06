import json
from scripts.create_embedding_database import load_legal_chunks
from src.internationalbridgestojustice.query_functions import (
    verify_claim,
    load_chroma_collection,
    retrieve_source_titles_from_chunks,
)
from src.internationalbridgestojustice.config import Paths
from src.internationalbridgestojustice.openai_utils import openai_client

collection = load_chroma_collection(Paths.PATH_CHROMADB, Paths.COLLECTION_NAME)
print(f"Collection contains {collection.count()} documents.")
chunks = load_legal_chunks(
    [
        Paths.PATH_JSONL_FILE_DEFENSEWIKI_CHUNKS,
        Paths.PATH_JSONL_FILE_CONSTITUTION_CHUNKS,
    ]
)  # Get chunks

chunks_selected = [
    chunk for chunk in chunks if chunk["metadata"]["country"] == "Burundi"
]
print(f"There are {len(chunks_selected)} chunks linked to this country.")

with open(Paths.PATH_FILE_PROMPT_CLAIM_VERIFICATION, "r") as f:
    prompt_claim_verification = f.read()

country = "Burundi"
with open(f"data/extracted_claims/{country}.json", "r", encoding="utf-8") as json_file:
    country_extracted_claims = json.load(json_file)

# TODO repeats i think because country_extracted_claims for all chunks?
for chunk in range(
    2, len(country_extracted_claims)
):  # loop on chunks, here 10. analysis chunk 3
    chunk_claims = country_extracted_claims[chunk]
    for i in range(0, len(chunk_claims["claim_list"])):  # loop on claims. 18
        sentence = chunk_claims["response"].split(".")[i]
        claims = chunk_claims["claim_list"][i]
        for claim in claims:
            print(f"Claim: {claim}")
            if claim != None:
                results, answer = verify_claim(
                    claim, collection, openai_client, prompt_claim_verification
                )
                source_titles = retrieve_source_titles_from_chunks(results, chunks)

                # append to claim_data
                claim_data = {
                    "sentence": chunk_claims["response"].split(".")[i],
                    "claim": claim,
                    "decision": answer.split("###")[
                        1
                    ].strip(),  # Strip to remove whitespace
                    "full_answer": answer,
                    "sources": source_titles,
                    "document_ids": results.get("ids", [[]])[0],
                    "distances": results.get("distances", [[]])[0],
                }
                print("Saving claim data...")

                with open(
                    f"data/verified_claims/{country}_claims.jsonl",
                    "a",
                    encoding="utf-8",
                ) as jsonl_file:
                    jsonl_file.write(json.dumps(claim_data) + "\n")

                with open(
                    f"data/verified_claims/{country}_claims.json", "a", encoding="utf-8"
                ) as json_file:
                    json.dump(claim_data, json_file, ensure_ascii=False, indent=4)

# TODO batches of requests
