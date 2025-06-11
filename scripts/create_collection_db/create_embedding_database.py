from src.internationalbridgestojustice.chromadb_utils import (
    load_collection,
    batch_embed_and_add,
)


def main():
    # # with 1st database ------------------------
    # chroma_collection_file_path = "data/chroma_db"
    # collection_name = "legal_collection"
    # chunk_ids_present_in_chromadb_collection_file_path = "data/chroma_db/seen_ids.txt"
    # raw_embeddings = "data/chroma_db/raw_embeddings.jsonl"
    #
    # chunks = load_legal_chunks(
    #     [
    #         Paths.PATH_JSONL_FILE_DEFENSEWIKI_CHUNKS,
    #         Paths.PATH_JSONL_FILE_CONSTITUTION_CHUNKS,
    #     ]
    # )  # Get chunks
    # print(f"Total number of chunks: {len(chunks)}")
    #
    # print(f"Total of {len(chunks)}")
    # # batches because max 600000 tokens per request, we could do 2000 chunks per batch?

    # with 2nd database with translated content --------------------------
    chroma_collection_file_path = "data/chroma_db_v2"
    collection_name = "legal_collection_v2"
    chunk_ids_present_in_chromadb_collection_file_path = (
        "data/chroma_db_v2/seen_ids.txt"
    )
    raw_embeddings = "data/chroma_db_v2/raw_embeddings.jsonl"

    # TODO: get chunks - see translate_chunks_in_batches.py

    collection = load_collection(
        chroma_collection_file_path=chroma_collection_file_path,
        collection_name=collection_name,
        new_collection=True,  # Set to True to create a new collection
    )

    collection = batch_embed_and_add(
        chunks,
        collection,
        raw_embeddings,
        chunk_ids_present_in_chromadb_collection_file_path,
        batch_size=1000,
    )
    print(f"Collection contains {collection.count()} documents.")


# TODO understand which size of embedding we want. input max de l'embedding model 8000 tokens
# TODO: batch tokens before running embedding
