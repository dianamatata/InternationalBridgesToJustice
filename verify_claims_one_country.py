import json
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
openai_api_key = os.environ.get("OPENAI_API_KEY")
from openai import OpenAI

from create_embedding_database import load_legal_chunks
from query_database import (perform_similarity_search,
                            build_context_text,
                            load_chroma_collection,
                            format_prompt,
                            retrieve_source_titles,
                            get_openai_response,
                            PROMPT_TEMPLATE)

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "legal_collection"

def verify_claim(claim, collection, client, PROMPT_TEMPLATE):

    # Perform similarity search with the query text
    results = perform_similarity_search(collection, claim, n_results=5)

    # Build the context from the similarity search results
    context_text = build_context_text(results)

    # Format the final prompt to send to OpenAI
    prompt = format_prompt(PROMPT_TEMPLATE, claim=claim, context=context_text)

    answer = get_openai_response(client, prompt)

    return results, answer



client = OpenAI()  # Global client instance

collection = load_chroma_collection(CHROMA_PATH, COLLECTION_NAME)
print(f"Collection contains {collection.count()} documents.")
chunks = load_legal_chunks()  # Get chunks

country = "Burundi-fr"
with (open(f"data/extracted_claims/{country}.json", "r", encoding="utf-8") as json_file):
    country_extracted_claims = json.load(json_file)

chunk = 1
i = 0
for chunk in range(0,len(country_extracted_claims)):
    chunk_claims = country_extracted_claims[chunk]
    for i in range(0, len(chunk_claims['claim_list'])):
        sentence = chunk_claims['response'].split(".")[i]
        claims = chunk_claims['claim_list'][i]
        for claim in claims:
            results, answer  = verify_claim(claim, collection, client, PROMPT_TEMPLATE)
            source_titles = retrieve_source_titles(results, chunks)  # TODO load chunks

            # append to claim_data
            claim_data = {
                "sentence" : chunk_claims['response'].split(".")[i]
                "claim": claim,
                "decision": answer.split("###")[1].strip(),  # Strip to remove whitespace
                "full_answer": answer,
                "sources": source_titles,
                "document_ids": results.get("ids", [[]])[0],
                "distances": results.get("distances", [[]])[0],
            }

            with open(f"data/verified_claims/{country}_claims.jsonl", "a", encoding="utf-8") as jsonl_file:
                jsonl_file.write(json.dumps(claim_data) + "\n")

            with open(f"data/verified_claims/{country}_claims.json", "a", encoding="utf-8") as json_file:
                json.dump(claim_data, json_file, ensure_ascii=False, indent=4)


a = [c['metadata']['title_bis'] for c in chunks]
