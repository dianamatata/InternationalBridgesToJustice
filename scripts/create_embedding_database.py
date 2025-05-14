import os
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
openai_api_key = os.environ.get("OPENAI_API_KEY")
from src.query_functions import add_new_chunks_to_chroma_collection, load_chroma_collection
from src.file_manager import load_legal_chunks


def batch_embed_and_add(chunks, collection, raw_embeddings_jsonl_file_path: str, chunk_ids_present_in_chromadb_collection_file_path: str, batch_size: int =2000):
    for i in tqdm(range(0, len(chunks), batch_size)):
        batch = chunks[i : i + batch_size]
        collection = add_new_chunks_to_chroma_collection(batch, collection, raw_embeddings_jsonl_file_path, chunk_ids_present_in_chromadb_collection_file_path)
    return collection


def main():

    CHROMA_PATH = "data/chroma_db"
    path_defensewiki_chunks = "data/processed/defensewiki.ibj.org/chunks_1.jsonl"
    path_constitution_chunks = "data/processed/constituteproject.org/constitution_chunks.jsonl"
    raw_embeddings_jsonl_file_path = "data/chroma_db/raw_embeddings.jsonl"
    chunk_ids_present_in_chromadb_collection_file_path = "data/chroma_db/seen_ids.txt"

    collection = load_chroma_collection(path=CHROMA_PATH, name="legal_collection")
    chunks = load_legal_chunks([path_defensewiki_chunks, path_constitution_chunks])  # Get chunks
    print(f"Total number of chunks: {len(chunks)}")

    print(f"Total of {len(chunks)}")
    # batches because max 600000 tokens per request, we could do 2000 chunks per batch?

    collection = batch_embed_and_add(chunks, collection, raw_embeddings_jsonl_file_path, chunk_ids_present_in_chromadb_collection_file_path, batch_size=1000)
    print(f"Collection contains {collection.count()} documents.")


# TODO understand which size of embedding we want. input max de l'embedding model 8000 tokens
# TODO: save embeddings as jsonl
# TODO: make modular code to add to embeddings but not recreate embeddings
# TODO: batch tokens before running embedding
