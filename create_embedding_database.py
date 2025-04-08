import chromadb
import openai
import os
import json

# Set  API key (ideally use env variable)
os.environ["OPENAI_API_KEY"] = (
    "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"
)

CHROMA_PATH = "data/chroma_db"

# Load the database or create it
# chromadb.PersistentClient(): This initializes the ChromaDB client that manages access to your local vector DB.
client = chromadb.PersistentClient(path=CHROMA_PATH) # you're already using Chroma in persistent mode, where data is auto-saved to disk in CHROMA_PATH.

# Create or get collection
# A collection in Chroma is like a table of documents with: ids, documents (text chunks), embeddings, metadata
collection = client.get_or_create_collection(name="legal_collection")

def openai_embed(texts: list[str], model="text-embedding-3-large") -> list[list[float]]:
    response = openai.embeddings.create(
        model=model,
        input=texts
    )
    return [d.embedding for d in response.data]


def load_legal_chunks():
    # get all paths where chunks are stored
    path1 = "data/processed/defensewiki.ibj.org/chunks.jsonl"
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
    return {k: (v if v is not None else "") for k, v in meta.items()} #  remove or replace None values

def add_to_chroma(chunks):

    # Load the existing database.
    existing_ids = set(collection.get()["ids"])     # Get existing IDs
    print(f"Number of existing documents in DB: {len(existing_ids)}")
    new_chunks = [c for c in chunks if c["title"] not in existing_ids]     # Filter new chunks

    if new_chunks:
        print(f"👉 Adding new documents: {len(new_chunks)}")
        texts = [c["content"] for c in new_chunks]
        ids = [c["title"] for c in new_chunks]
        metadata = [c.get("metadata", {}) for c in new_chunks]
        metadata = [clean_metadata(m) for m in metadata]

        # Compute embeddings
        embeddings = openai_embed(texts)
        # Add to collection
        collection.add(documents=texts, ids=ids, embeddings=embeddings, metadatas=metadata)

        # Export to JSONL
        with open("data/chroma_db/raw_embeddings.jsonl", "w") as f:
            for i in range(len(texts)):
                f.write(
                    {
                        "id": ids[i],
                        "embedding": embeddings[i],
                        "text": texts[i],
                        "metadata": metadata[i],
                    }.__str__() + "\n"
                )
    else:
        print("✅ No new documents to add")


def main():
    chunks1 = load_legal_chunks()    # Get chunks
    chunks = chunks1[0:100]     # for testing
    add_to_chroma(chunks)








# TODO understand which size of embedding we want. input max de l'embedding model 8000 tokens
# TODO: save embeddings as jsonl
# TODO: make modular code to add to embeddings but not recreate embeddings
# TODO: batch tokens before running embedding



