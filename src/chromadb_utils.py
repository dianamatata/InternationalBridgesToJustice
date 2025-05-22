import chromadb
from src.openai_utils import openai_generate_embeddings


def load_chroma_collection(chroma_collection_file_path: str, collection_name: str):
    """
    Load the database or create it
    chromadb.PersistentClient(): This initializes the ChromaDB client that manages access to your local vector DB.
    with Chroma in persistent mode,  data is auto-saved to disk in CHROMA_PATH.
    """
    chroma_client = chromadb.PersistentClient(path=chroma_collection_file_path)
    try:
        collection = chroma_client.get_collection(collection_name)  # Load collection
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
