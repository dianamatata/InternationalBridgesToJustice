import chromadb
from openai import OpenAI
import os
from scripts.create_embedding_database import load_legal_chunks
# The API key is stored in an environment file (.env), added to .gitignore for security reasons.
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
openai_api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI()

def openai_generate_embeddings(texts: list[str], model="text-embedding-3-large") -> list[list[float]]:
    """
    Generate embeddings for a list of texts using OpenAI's embedding API.
    """
    response = client.embeddings.create(model=model, input=texts)
    return [d.embedding for d in response.data]


def load_chroma_collection(chroma_collection_file_path: str, collection_name: str):
    """
    Load the database or create it
    chromadb.PersistentClient(): This initializes the ChromaDB client that manages access to your local vector DB.
    with Chroma in persistent mode,  data is auto-saved to disk in CHROMA_PATH.
    """
    client = chromadb.PersistentClient(path=chroma_collection_file_path)
    try:
        collection = client.get_collection(collection_name)  # Load collection
    except Exception as e:
        raise RuntimeError(f"Could not load collection '{collection_name}': {e}")
    return collection


def add_new_chunks_to_chroma_collection(chunks, collection, raw_embeddings_jsonl_file_path: str, chunk_ids_present_in_chromadb_collection_file_path: str):

    existing_ids = set(collection.get()["ids"])  # Get existing IDs
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    new_chunks = []
    seen_ids = set()

    for c in chunks:
        cid = c["title"]
        if cid not in existing_ids and cid not in seen_ids:
            new_chunks.append(c)
            seen_ids.add(cid)
    print(f"Adding new documents: {len(new_chunks)}")

    if new_chunks:
        texts = [c["content"] for c in new_chunks]
        ids = [c["title"] for c in new_chunks]
        metadata = [c.get("metadata", {}) for c in new_chunks]
        metadata = [{k: (v if v is not None else "") for k, v in m.items()} for m in metadata]

        embeddings = openai_generate_embeddings(texts)
        collection.add(
            documents=texts, ids=ids, embeddings=embeddings, metadatas=metadata
        )

        with open(raw_embeddings_jsonl_file_path, "w") as file:
            for i in range(len(texts)):
                file.write(
                    {
                        "id": ids[i],
                        "embedding": embeddings[i],
                        "text": texts[i],
                        "metadata": metadata[i],
                    }.__str__()
                    + "\n"
                )

        with open(chunk_ids_present_in_chromadb_collection_file_path, "a") as file:
            for cid in seen_ids:
                file.write(cid + "\n")

    else:
        print("No new documents to add")

    return collection
def perform_similarity_embeddings_search_from_collection(collection, query_text: str, number_of_results_to_retrieve: int = 5):
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
    )

    return results


def perform_similarity_search_with_country_filter(
    collection, query_text: str, country: str, number_of_results_to_retrieve: int = 5
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
        where={"country": country},
    )

    return results


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
    """
    Build the final prompt by inserting the claim and context into the template.
    """
    return prompt_template.format(claim=claim, context=context)


def format_prompt_for_completeness_check(
    prompt_template: str, keypoint: str, wiki_content: str, database_content: str
) -> str:
    """
    Build the final prompt by inserting the claim and context into the template.
    """
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

def get_openai_response(
    client,
    categorize_system_prompt: str,
    prompt: str,
    model="gpt-4o-mini",
    temperature=0.1,
) -> str:
    """
    Send the prompt to OpenAI's chat API and return the answer.
    """
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": categorize_system_prompt},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content


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

    results = perform_similarity_search_with_country_filter(
        collection=collection, query_text=claim, country="Burundi", number_of_results_to_retrieve=5
    )
    context_text = build_context_string_from_retrieve_documents(results)
    prompt = format_prompt_for_claim_verification(prompt_claim_verification, claim=claim, context=context_text)
    answer = get_openai_response(client, prompt)

    return results, answer