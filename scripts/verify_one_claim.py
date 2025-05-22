# --- IMPORTS ---
import json
from src.openai_utils import openai_client
from scripts.create_embedding_database import load_legal_chunks
from src.query_functions import (load_chroma_collection,
                                 perform_similarity_search_with_country_filter,
                                 build_context_string_from_retrieve_documents,
                                 format_prompt_for_claim_verification,
                                 get_openai_response,
                                 retrieve_source_titles_from_chunks)

from src.config import Paths

with open("data/prompts/prompt_claim_verification.md", "r") as f:
    prompt_claim_verification = f.read()


# --- MAIN SCRIPT ---

chunks = load_legal_chunks([Paths.PATH_JSONL_FILE_DEFENSEWIKI_CHUNKS, Paths.PATH_JSONL_FILE_CONSTITUTION_CHUNKS])  # Get chunks
claim_to_verify = "In India, Until proven innocent, the accused has to remain in prison."

collection = load_chroma_collection(chroma_collection_file_path=Paths.PATH_CHROMADB,  collection_name=Paths.COLLECTION_NAME)
print(f"Collection contains {collection.count()} documents.")

results = perform_similarity_search_with_country_filter(
    collection=collection, query_text=claim_to_verify, country="India", number_of_results_to_retrieve=5
)

res_summary = [r["title_bis"] for r in results["metadatas"][0]]
print(f"Results summary: {res_summary}")

context_text = build_context_string_from_retrieve_documents(results)

prompt = format_prompt_for_claim_verification(prompt_claim_verification, claim=claim_to_verify, context=context_text)

answer = get_openai_response(openai_client, prompt)
print("\nOpenAI response:\n", answer)

source_titles = retrieve_source_titles_from_chunks(results, chunks)

claim_data = {
    "claim": claim_to_verify,
    "decision": answer.split("###")[1].strip(),  # Strip to remove whitespace
    "full_answer": answer,
    "sources": source_titles,
    "document_ids": results.get("ids", [[]])[0],
    "distances": results.get("distances", [[]])[0],
}

print(f"\033[93m{json.dumps(claim_data, indent=4)}\033[0m")

with open(
        f"../data/verified_claims/claims_1.jsonl", "a", encoding="utf-8"
) as jsonl_file:
    jsonl_file.write(json.dumps(claim_data) + "\n")

with open(
        f"../data/verified_claims/claims_1.json", "a", encoding="utf-8"
) as json_file:
    json.dump(claim_data, json_file, ensure_ascii=False, indent=4)


# TODO integrate https://github.com/Yixiao-Song/VeriScore/blob/main/veriscore/claim_verifier.py
