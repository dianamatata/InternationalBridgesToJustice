import json
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
openai_api_key = os.environ.get("OPENAI_API_KEY")
from openai import OpenAI

from scripts.create_embedding_database import load_legal_chunks
from claim_verification import (
    perform_similarity_search_with_country_filter,
    build_context_string_from_retrieve_documents,
    load_chroma_collection,
    format_prompt,
    retrieve_source_titles_from_chunks,
    get_openai_response,
    prompt_claim_verification,
)

CHROMA_PATH = "../data/chroma_db"
COLLECTION_NAME = "legal_collection"


def verify_claim(claim, collection, client, PROMPT_TEMPLATE):

    # Perform similarity search with the query text
    # results = perform_similarity_search(collection=collection, query_text=claim, n_results=5)
    results = perform_similarity_search_with_country_filter(
        collection=collection, query_text=claim, country="Burundi", number_of_results_to_retrieve=5
    )
    print("results")
    # Build the context from the similarity search results
    context_text = build_context_string_from_retrieve_documents(results)

    # Format the final prompt to send to OpenAI
    prompt = format_prompt(PROMPT_TEMPLATE, claim=claim, context=context_text)
    print("prompt")

    answer = get_openai_response(client, prompt)
    print("answer")

    return results, answer


client = OpenAI()  # Global client instance

collection = load_chroma_collection(CHROMA_PATH, COLLECTION_NAME)
print(f"Collection contains {collection.count()} documents.")
chunks = load_legal_chunks()  # Get chunks

# check number of chunks for the country
chunks_selected = [
    chunk for chunk in chunks if chunk["metadata"]["country"] == "Burundi"
]
print(f"There are {len(chunks_selected)} chunks linked to this country.")


country = "Burundi"
with open(f"data/extracted_claims/{country}.json", "r", encoding="utf-8") as json_file:
    country_extracted_claims = json.load(json_file)

chunk = 1
i = 0
claim = claims[0]
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
                    claim, collection, client, prompt_claim_verification
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

"The Organization of African Unity (OUA) is later known as The African Union (AU)."
#     chunk_claims['response'].split(".")[i]
# IndexError: list index out of range
# "Burundi's Constitution recalls its commitment and respect for the Universal Declaration of Human Rights..." # TODO solve problem


a = [c["metadata"]["title_bis"] for c in chunks]
