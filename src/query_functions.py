import chromadb
from openai import OpenAI
import os
import json
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

    client = chromadb.PersistentClient(path=chroma_collection_file_path)
    try:
        collection = client.get_collection(collection_name)  # Load collection
    except Exception as e:
        raise RuntimeError(f"Could not load collection '{collection_name}': {e}")
    return collection


def perform_similarity_embeddings_search_from_collection(collection, query_text: str, number_of_results_to_retrieve: int = 5):
    """
    Get the query embedding using OpenAI, then query the collection for similar documents.
    """
    # Generate query embedding (note: openai_embed returns a list, so take the first element)
    query_embedding = openai_generate_embeddings([query_text])[0]

    # Query Chroma and include documents and distances (also include ids if you need to retrieve source info later)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=number_of_results_to_retrieve,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],  # collection.query() always returns the ids
    )

    return results


def perform_similarity_search_with_country_filter(
    collection, query_text: str, country: str, number_of_results_to_retrieve: int = 5
):
    """
    Get the query embedding using OpenAI, then query the collection for similar documents.
    """
    # Generate query embedding (note: openai_embed returns a list, so take the first element)
    query_embedding = openai_generate_embeddings([query_text])[0]

    # Query Chroma and include documents and distances (also include ids if you need to retrieve source info later)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=number_of_results_to_retrieve,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],  # collection.query() always returns the ids
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
    # Generate query embedding (note: openai_embed returns a list, so take the first element)
    query_embedding = openai_generate_embeddings([query_text])[0]

    # Query Chroma and include documents and distances (also include ids if you need to retrieve source info later)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=number_of_results_to_retrieve,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],  # collection.query() always returns the ids
        where={metadata_param: metadata_value},
    )

    return results


def build_context_string_from_retrieve_documents(results: dict) -> str:
    """
    Build a context string from the retrieved documents.
    """
    # Extract the first result list (there's one list per query embedding)
    documents = results["documents"][0]
    # Optionally, also extract distances if you want to incorporate or log them.
    # scores = results["distances"][0]

    # Combine documents using a separator for clarity
    context_text = "\n\n---\n\n".join(doc for doc in documents)
    return context_text


def format_prompt(prompt_template: str, claim: str, context: str) -> str:
    """
    Build the final prompt by inserting the claim and context into the template.
    """
    return prompt_template.format(claim=claim, context=context)


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
    # Create the chat completion
    # default temp is 1. Burundi has been run with 1. Values can be from 0 through 2.
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": categorize_system_prompt},
            {"role": "user", "content": prompt},
        ],
    )

    # Accessing the response # print(response.choices[0].message.content)
    return response.choices[0].message.content


def retrieve_source_titles_from_chunks(results: dict, all_chunks: list[dict]) -> list[str]:
    """
    Retrieves human-friendly source titles for each returned chunk ID.
    Looks up each id from the results in the provided chunks.
    """
    sources = results.get("ids", [[]])[0]
    chunks_for_answer = []
    for source in sources:
        # Assume each chunk in all_chunks has a 'title' or a corresponding field to match the source id.
        matching_chunks = [
            chunk for chunk in all_chunks if chunk.get("title") == source
        ]
        if matching_chunks:
            title_bis = matching_chunks[0]["metadata"].get("title_bis", source)
            chunks_for_answer.append(title_bis)
        else:
            chunks_for_answer.append(f"No matching chunk found for ID: {source}")
    return chunks_for_answer
