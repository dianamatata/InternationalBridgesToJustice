import chromadb
import openai
import os

# The API key is stored in an environment file (.env), added to .gitignore for security reasons.
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
openai_api_key = os.environ.get("OPENAI_API_KEY")


# --- CONFIGURATION ---

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "legal_collection"
PROMPT_TEMPLATE2 = (
    "You need to judge whether a claim is supported or contradicted by the information in the database, "
    "or whether there is not enough information to make the judgement. You can cite a specific law or legal chapter to explain your decision."
    "Mark your answer with ### signs.\n\n"
    "Below are the definitions of the three categories:\n\n"
    "Supported: A claim is supported by the database if everything in the claim is supported and nothing is "
    "contradicted by the information in the database. There can be some results that are not fully related to the claim.\n\n"
    "Contradicted: A claim is contradicted by the results if something in the claim is contradicted by some results. "
    "There should be no result that supports the same part.\n\n"
    "Inconclusive: A claim is inconclusive based on the results if:\n"
    "- a part of a claim cannot be verified by the results,\n"
    "- a part of a claim is supported and contradicted by different pieces of evidence,\n"
    "- the entity/person mentioned in the claim has no clear referent (e.g., 'the approach', 'Emily', 'a book').\n\n"
    "Claim: {claim}\n\n"
    "Context: {context}"
)

PROMPT_TEMPLATE = """Use the context below to verify a claim:

You need to judge whether a claim is supported or contradicted by the information in the database, or whether there is not enough information to make the judgement. 
Mark your answer with ### signs.

Below are the definitions of the three categories:

Supported: A claim is supported by the database if everything in the claim is supported and nothing is contradicted by the information in the database. There can be some results that are not fully related to the claim.
Contradicted: A claim is contradicted by the results if something in the claim is contradicted by some results. There should be no result that supports the same part.
Inconclusive: A claim is inconclusive based on the results if:
- a part of a claim cannot be verified by the results,
- a part of a claim is supported and contradicted by different pieces of evidence,
- the entity/person mentioned in the claim has no clear referent (e.g., "the approach", "Emily", "a book").

    "Claim: {claim}\n\n"
    "Context: {context}"

"""

# --- HELPER FUNCTIONS ---

def openai_embed(texts: list[str], model="text-embedding-3-large") -> list[list[float]]:
    """
    Generate embeddings for a list of texts using OpenAI's embedding API.
    """
    response = openai.embeddings.create(
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
        include=["documents", "distances", "ids"]
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

def get_openai_response(prompt: str, model="gpt-4") -> str:
    """
    Send the prompt to OpenAI's chat API and return the answer.
    """
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a legal assistant."},
            {"role": "user", "content": prompt}
        ]
    )
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
    QUERY_TEXT = "Until proven innocent, the accused has to remain in prison."

    # Load the Chroma collection
    collection = load_chroma_collection(CHROMA_PATH, COLLECTION_NAME)

    # Perform similarity search with the query text
    results = perform_similarity_search(collection, QUERY_TEXT, n_results=5)

    # Build the context from the similarity search results
    context_text = build_context_text(results)

    # Format the final prompt to send to OpenAI
    prompt = format_prompt(PROMPT_TEMPLATE, claim=QUERY_TEXT, context=context_text)
    print("Formatted prompt:\n", prompt)

    # Get the answer from OpenAI
    answer = get_openai_response(prompt)
    print("\nOpenAI response:\n", answer)

    source_titles = retrieve_source_titles(results, chunks1) # TODO load chunks
    formatted_response = f"Response: {answer}\n\nSources: {source_titles}"

    print("\nFinal formatted response:\n", formatted_response)

# results.get("ids", [[]])[0]
# sources = results['ids'][0]


if __name__ == "__main__":
    # If the file is run directly, it will call the main() function.
    # i.e. not imported as a module in another script.
    main()