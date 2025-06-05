from tqdm import tqdm
from src.chromadb_utils import add_new_chunks_to_collection, load_collection
from src.file_manager import load_legal_chunks
from src.config import Paths

def batch_embed_and_add(chunks, collection, raw_embeddings_jsonl_file_path: str, chunk_ids_present_in_chromadb_collection_file_path: str, batch_size: int =2000):
    for i in tqdm(range(0, len(chunks), batch_size)):
        batch = chunks[i : i + batch_size]
        collection = add_new_chunks_to_collection(batch, collection, raw_embeddings_jsonl_file_path, chunk_ids_present_in_chromadb_collection_file_path)
    return collection


def main():

    chunk_ids_present_in_chromadb_collection_file_path = "data/chroma_db/seen_ids.txt"
    collection = load_collection(chroma_collection_file_path=Paths.PATH_CHROMADB,  collection_name=Paths.COLLECTION_NAME)
    chunks = load_legal_chunks([Paths.PATH_JSONL_FILE_DEFENSEWIKI_CHUNKS, Paths.PATH_JSONL_FILE_CONSTITUTION_CHUNKS])  # Get chunks
    print(f"Total number of chunks: {len(chunks)}")

    print(f"Total of {len(chunks)}")
    # batches because max 600000 tokens per request, we could do 2000 chunks per batch?

    collection = batch_embed_and_add(chunks, collection, Paths.PATH_JSONL_FILE_RAW_EMBEDDINGS, chunk_ids_present_in_chromadb_collection_file_path, batch_size=1000)
    print(f"Collection contains {collection.count()} documents.")


# TODO understand which size of embedding we want. input max de l'embedding model 8000 tokens
# TODO: save embeddings as jsonl
# TODO: make modular code to add to embeddings but not recreate embeddings
# TODO: batch tokens before running embedding
