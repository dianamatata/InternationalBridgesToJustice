# https://github.com/pixegami/rag-tutorial-v2/blob/main/query_data.py
import chromadb
import openai
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
openai_api_key = os.environ.get("OPENAI_API_KEY")

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "legal_collection"
PROMPT_TEMPLATE = """Use the context below to verify a claim:

You need to judge whether a claim is supported or contradicted by the information in the database, or whether there is not enough information to make the judgement. You can cite a specific law or legal chapter to explain your decision.
Mark your answer with ### signs.

Below are the definitions of the three categories:

Supported: A claim is supported by the database if everything in the claim is supported and nothing is contradicted by the information in the database. There can be some results that are not fully related to the claim.
Contradicted: A claim is contradicted by the results if something in the claim is contradicted by some results. There should be no result that supports the same part.
Inconclusive: A claim is inconclusive based on the results if:
- a part of a claim cannot be verified by the results,
- a part of a claim is supported and contradicted by different pieces of evidence,
- the entity/person mentioned in the claim has no clear referent (e.g., "the approach", "Emily", "a book").

Claim: {claim}

Context: {context}

Answer:"""


# functions ------------
def openai_embed(texts: list[str], model="text-embedding-3-large") -> list[list[float]]:
    # It’s a helper function to generate embeddings using OpenAI’s API.
    response = openai.embeddings.create(
        model=model,
        input=texts
    )
    return [d.embedding for d in response.data]

# main ---------------------

CHROMA_PATH = "data/chroma_db"

# Load the client from disk
client = chromadb.PersistentClient(path=CHROMA_PATH)

# Load your previously saved collection
collection = client.get_collection("legal_collection")

query_text = "Until proven innocent, the accused has to remain in prison."

# 1 - Embed the query text python Copier Modifier
query_embedding = openai_embed([query_text])[0]

# 2. Query Chroma

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5,
    include=["documents", "distances"]
)

# 3. Build the context string
documents = results["documents"][0]
scores = results["distances"][0]

# Combine documents and scores if needed
context_text = "\n\n---\n\n".join(doc for doc in documents)




#format prompt
prompt = PROMPT_TEMPLATE.format(context=context_text, claim=query_text)
print(prompt)

# send it to opanAI
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a legal assistant."},
        {"role": "user", "content": prompt}
    ]
)

answer = response.choices[0].message.content
print(answer)

# get sources
sources = results['ids'][0]
chunks_for_answer = []
for source in sources:
    print(source)
    matching_chunks = [chunk for chunk in chunks1 if chunk.get('title') == source]
    chunks_for_answer.append(matching_chunks[0]['metadata']['title_bis'])
    if matching_chunks:
        chunk = matching_chunks[0]
        if chunk['metadata']['title_bis']:
            print(chunk['metadata']['title_bis'])
        else:
            print(chunk['metadata'])
    else:
        print(f"No matching chunk found for ID: {source}")

# print response

sources = results['ids'][0]
formatted_response = f"Response: {answer}\n\n\nSources: {chunks_for_answer}"
print(formatted_response)
