from src.openai_utils import openai_generate_embeddings, get_openai_response

def perform_similarity_search_metadata_filter(
    collection,
    query_text: str,
    metadata_param: str,
    metadata_value: str,
    number_of_results_to_retrieve: int = 5,
):
    """
    Get the query embedding using OpenAI, then query the collection for similar documents.
    """
    query_embedding = openai_generate_embeddings([query_text])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=number_of_results_to_retrieve,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
        where={metadata_param: metadata_value},
    )

    return results


def build_context_string_from_retrieve_documents(results: dict) -> str:
    """
    Build a context string from the retrieved documents.
    """
    # Extract the first result list (there's one list per query embedding)
    documents = results["documents"][0]
    # scores = results["distances"][0]
    context_text = "\n\n---\n\n".join(doc for doc in documents)
    return context_text


def format_prompt_for_claim_verification(prompt_template: str, claim: str, context: str) -> str:

    return prompt_template.format(claim=claim, context=context)


def format_prompt_for_completeness_check(
    prompt_template: str, keypoint: str, wiki_content: str, database_content: str
) -> str:

    return prompt_template.format(
        keypoint=keypoint, wiki_content=wiki_content, database_content=database_content
    )

def get_completeness_keypoints(completeness_checklist_filepath: str):
    with open(completeness_checklist_filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    completeness_keypoints = []
    for line in lines[2:]:
        stripped = line.strip()
        if line.strip() == "":
            continue
        completeness_keypoints.append(line.replace("  \n", ""))
    return completeness_keypoints


def retrieve_source_titles_from_chunks(results: dict, all_chunks: list[dict]) -> list[str]:
    """
    Retrieves human-friendly source titles for each returned chunk ID.
    Looks up each id from the results in the provided chunks.
    """
    sources = results.get("ids", [[]])[0]
    chunks_for_answer = []
    for source in sources:
        matching_chunks = [
            chunk for chunk in all_chunks if chunk.get("title") == source
        ]
        if matching_chunks:
            title_bis = matching_chunks[0]["metadata"].get("title_bis", source)
            chunks_for_answer.append(title_bis)
        else:
            chunks_for_answer.append(f"No matching chunk found for ID: {source}")
    return chunks_for_answer


def verify_claim(claim: str, collection, client, prompt_claim_verification: str):

    results = perform_similarity_search_metadata_filter(
        collection=collection, query_text=claim, metadata_param="country", metadata_value="Burundi", number_of_results_to_retrieve=5
    )
    context_text = build_context_string_from_retrieve_documents(results)
    prompt = format_prompt_for_claim_verification(prompt_claim_verification, claim=claim, context=context_text)
    answer = get_openai_response(client, prompt)

    return results, answer