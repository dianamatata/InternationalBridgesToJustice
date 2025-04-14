import chromadb
from openai import OpenAI
client = OpenAI()
import os
import json
from create_embedding_database import load_legal_chunks
# The API key is stored in an environment file (.env), added to .gitignore for security reasons.
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
openai_api_key = os.environ.get("OPENAI_API_KEY")


# --- CONFIGURATION ---

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "legal_collection"

PROMPT_TEMPLATE = (
    "You need to determine whether the database contains enough information to fact-check the claim, "
    "and then decide whether the claim is **Supported**, **Contradicted**, or **Inconclusive** based on that information. "
    "You can cite specific laws or legal chapters to justify your decision.\n\n"

    "Very important: Make sure that the information used for verification comes from the correct country. "
    "You can find the country name in the 'metadata':'title' or 'metadata':'country' fields of the context.\n\n"

    "Does the database provide enough information to fact-check the claim? \n"
    "If no, label claim as ###Inconclusive###\n"
    "If yes, state the judgment as one of the following categories, marked with ###:\n\n"

    "###Supported###\n"
    "A claim is supported by the database if everything in the claim is supported and nothing is contradicted by the information in the database. "
    "There can be some results that are not fully related to the claim.\n\n"

    "###Contradicted###\n"
    "A claim is contradicted if some part of it directly conflicts with information in the database, and no supporting evidence is provided for that part.\n\n"

    "###Inconclusive###\n"
    "A claim is inconclusive if:\n"
    "- A part of the claim cannot be verified with the available information,\n"
    "- A part of the claim is both supported and contradicted by different sources,\n"
    "- The claim contains unclear references (e.g., 'the person', 'the law', 'they').\n\n"

    "Claim: {claim}\n\n"
    "Context: {context}"
)

# --- HELPER FUNCTIONS ---

def openai_embed(texts: list[str], model="text-embedding-3-large") -> list[list[float]]:
    """
    Generate embeddings for a list of texts using OpenAI's embedding API.
    """
    response = client.embeddings.create(
        model=model,
        input=texts
    )
    return [d.embedding for d in response.data]

def load_chroma_collection(path: str, collection_name: str):
    """
    Load an existing Chroma collection from disk.
    """
    client = chromadb.PersistentClient(path=path)
    try:
        collection = client.get_collection(collection_name) # Load collection
    except Exception as e:
        raise RuntimeError(f"Could not load collection '{collection_name}': {e}")
    return collection

def perform_similarity_search(collection, query_text: str, n_results: int = 5):
    """
    Get the query embedding using OpenAI, then query the collection for similar documents.
    """
    # Generate query embedding (note: openai_embed returns a list, so take the first element)
    query_embedding = openai_embed([query_text])[0]

    # Query Chroma and include documents and distances (also include ids if you need to retrieve source info later)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"] #collection.query() always returns the ids
    )

    return results

def perform_similarity_search_with_country_filter(collection, query_text: str,  country: str, n_results: int = 5):
    """
    Get the query embedding using OpenAI, then query the collection for similar documents.
    """
    # Generate query embedding (note: openai_embed returns a list, so take the first element)
    query_embedding = openai_embed([query_text])[0]

    # Query Chroma and include documents and distances (also include ids if you need to retrieve source info later)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"], #collection.query() always returns the ids
        where={"country": country}
    )

    return results


def build_context_text(results: dict) -> str:
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

def get_openai_response(client, prompt: str, model="gpt-4") -> str:
    """
    Send the prompt to OpenAI's chat API and return the answer.
    """

    # Create the chat completion
    response = client.chat.completions.create(model=model,
    messages=[
        {"role": "system", "content": "You are a legal assistant."},
        {"role": "user", "content": prompt}
    ])

    # Accessing the response
    print(response.choices[0].message.content)
    return response.choices[0].message.content

def retrieve_source_titles(results: dict, all_chunks: list[dict]) -> list[str]:
    """
    Retrieves human-friendly source titles for each returned chunk ID.
    Looks up each id from the results in the provided chunks.
    """
    sources = results.get("ids", [[]])[0]
    chunks_for_answer = []
    for source in sources:
        # Assume each chunk in all_chunks has a 'title' or a corresponding field to match the source id.
        matching_chunks = [chunk for chunk in all_chunks if chunk.get('title') == source]
        if matching_chunks:
            title_bis = matching_chunks[0]['metadata'].get('title_bis', source)
            chunks_for_answer.append(title_bis)
        else:
            chunks_for_answer.append(f"No matching chunk found for ID: {source}")
    return chunks_for_answer


# --- MAIN SCRIPT ---



def main():

    chunks = load_legal_chunks()    # Get chunks
    #     chunks = chunks1[0:100]     # for testing
    #     add_to_chroma(chunks)

    # Initialize the client
    client = OpenAI()

    QUERY_TEXT = "Until proven innocent, the accused has to remain in prison."
    QUERY_TEXT = "In India, Until proven innocent, the accused has to remain in prison."


    # Load the Chroma collection
    collection = load_chroma_collection(CHROMA_PATH, COLLECTION_NAME)
    print(f"Collection contains {collection.count()} documents.")

    # Perform similarity search with the query text
    # results = perform_similarity_search(collection=collection, query_text=QUERY_TEXT, n_results=5)

    # Perform similarity search with the query text
    results = perform_similarity_search_with_country_filter(collection=collection, query_text=QUERY_TEXT, country="India", n_results=5)
    res_summary = [r['title_bis'] for r in results['metadatas'][0]]
    print(f"Results summary: {res_summary}")

    # Build the context from the similarity search results
    context_text = build_context_text(results)

    # Format the final prompt to send to OpenAI
    prompt = format_prompt(PROMPT_TEMPLATE, claim=QUERY_TEXT, context=context_text)
    # print("Formatted prompt:\n", prompt)

    # Get the answer from OpenAI
    answer = get_openai_response(client, prompt)
    print("\nOpenAI response:\n", answer)

    source_titles = retrieve_source_titles(results, chunks) # TODO load chunks
    formatted_response = f"Response: {answer}\n\nSources: {source_titles}"

    claim_data = {
        "claim": QUERY_TEXT,
        "decision": answer.split("###")[1].strip(),  # Strip to remove whitespace
        "full_answer": answer,
        "sources": source_titles,
        "document_ids": results.get("ids", [[]])[0],
        "distances": results.get("distances", [[]])[0],
    }

    print(f"\033[93m{json.dumps(claim_data, indent=4)}\033[0m")

    with open(f"data/verified_claims/claims_1.jsonl", "a", encoding="utf-8") as jsonl_file:
        jsonl_file.write(json.dumps(claim_data) + "\n")

    with open(f"data/verified_claims/claims_1.json", "a", encoding="utf-8") as json_file:
        json.dump(claim_data, json_file, ensure_ascii=False, indent=4)


# TODO integrate https://github.com/Yixiao-Song/VeriScore/blob/main/veriscore/claim_verifier.py


if __name__ == "__main__":
    # If the file is run directly, it will call the main() function.
    # i.e. not imported as a module in another script.
    main()
