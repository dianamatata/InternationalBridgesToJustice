import chromadb
import openai
import os
import json
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
openai_api_key = os.environ.get("OPENAI_API_KEY")

CHROMA_PATH = "data/chroma_db"


def openai_embed(texts: list[str], model="text-embedding-3-large") -> list[list[float]]:
    response = openai.embeddings.create(model=model, input=texts)
    return [d.embedding for d in response.data]


def load_legal_chunks():
    # get all paths where chunks are stored
    path1 = "data/processed/defensewiki.ibj.org/chunks_1.jsonl"
    path2 = "data/processed/constituteproject.org/constitution_chunks.jsonl"

    chunks = []
    for path in [path1, path2]:
        with open(f"{path}", "r", encoding="utf-8") as jsonl_file:
            lines = jsonl_file.readlines()  # Read all lines once
            print(f"Number of lines in the jsonl file {path}: {len(lines)}")
            for line in lines:
                chunks.append(json.loads(line))
        print(f"Total number of chunks: {len(chunks)}")  # Should be 50380

    return chunks


def clean_metadata(meta: dict) -> dict:
    return {
        k: (v if v is not None else "") for k, v in meta.items()
    }  #  remove or replace None values


def add_to_chroma(chunks, collection):

    # Load the existing database.
    existing_ids = set(collection.get()["ids"])  # Get existing IDs
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Prepare new chunks and ensure uniqueness of IDs
    new_chunks = []
    seen_ids = set()

    for c in chunks:
        cid = c["title"]
        if cid not in existing_ids and cid not in seen_ids:
            new_chunks.append(c)
            seen_ids.add(cid)
    print(f"👉 Adding new documents: {len(new_chunks)}")

    if new_chunks:
        texts = [c["content"] for c in new_chunks]
        ids = [c["title"] for c in new_chunks]
        metadata = [c.get("metadata", {}) for c in new_chunks]
        metadata = [clean_metadata(m) for m in metadata]

        # Compute embeddings
        embeddings = openai_embed(texts)
        # Add to collection
        collection.add(
            documents=texts, ids=ids, embeddings=embeddings, metadatas=metadata
        )

        # Export to JSONL
        with open("data/chroma_db/raw_embeddings.jsonl", "w") as f:
            for i in range(len(texts)):
                f.write(
                    {
                        "id": ids[i],
                        "embedding": embeddings[i],
                        "text": texts[i],
                        "metadata": metadata[i],
                    }.__str__()
                    + "\n"
                )

        # Add seen IDs to text file
        with open("data/chroma_db/seen_ids.txt", "a") as f:
            for cid in seen_ids:
                f.write(cid + "\n")

    else:
        print("✅ No new documents to add")

    return collection


def batch_embed_and_add(chunks, collection, batch_size=2000):
    for i in tqdm(range(0, len(chunks), batch_size)):
        batch = chunks[i : i + batch_size]
        collection = add_to_chroma(batch, collection)

    return collection


def main():

    # Load the database or create it
    # chromadb.PersistentClient(): This initializes the ChromaDB client that manages access to your local vector DB.
    client = chromadb.PersistentClient(
        path=CHROMA_PATH
    )  # you're already using Chroma in persistent mode, where data is auto-saved to disk in CHROMA_PATH.

    # Create or get collection in Chroma is like a table of documents with: ids, documents (text chunks), embeddings, metadata
    collection = client.get_or_create_collection(name="legal_collection")

    chunks = load_legal_chunks()  # Get chunks
    print(f"Total of {len(chunks)}")
    # batches because max 600000 tokens per request, we could do 2000 chunks per batch?
    collection = batch_embed_and_add(chunks, collection, batch_size=1000)
    print(f"Collection contains {collection.count()} documents.")


# TODO understand which size of embedding we want. input max de l'embedding model 8000 tokens
# TODO: save embeddings as jsonl
# TODO: make modular code to add to embeddings but not recreate embeddings
# TODO: batch tokens before running embedding
