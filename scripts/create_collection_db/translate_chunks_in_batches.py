from src.internationalbridgestojustice.openai_utils import (
    upload_batch_file_to_openAI,
    submit_batch_job,
    openai_client,
    retrieve_and_save_batch_results,
    check_progress_batch_id,
)
from src.internationalbridgestojustice.get_translation import (
    Translator,
    get_chunks_in_english,
    get_chunks_for_one_country,
    create_new_chunks_from_translated_results,
)
from src.internationalbridgestojustice.config import Paths
from src.internationalbridgestojustice.file_manager import save_file

from src.internationalbridgestojustice.chromadb_utils import (
    load_collection,
    batch_embed_and_add,
)

# Load the chunks --------------------------------

defense_chunks_not_in_english = get_chunks_in_english(
    jsonl_file_path="data/processed/defensewiki.ibj.org/unique_chunks.jsonl",
    in_english=False,
)
defense_chunks_in_english = get_chunks_in_english(
    jsonl_file_path="data/processed/defensewiki.ibj.org/unique_chunks.jsonl",
    in_english=True,
)

constitution_chunks_not_in_english = get_chunks_in_english(
    jsonl_file_path=Paths.PATH_JSONL_FILE_CONSTITUTION_CHUNKS, in_english=False
)
constitution_chunks_in_english = get_chunks_in_english(
    jsonl_file_path=Paths.PATH_JSONL_FILE_CONSTITUTION_CHUNKS, in_english=True
)

other_legal_docs_chunks_not_in_english = get_chunks_in_english(
    jsonl_file_path=Paths.PATH_JSONL_FILE_LEGAL_OTHERS, in_english=False
)
other_legal_docs_chunks_in_english = get_chunks_in_english(
    jsonl_file_path=Paths.PATH_JSONL_FILE_LEGAL_OTHERS, in_english=True
)


print("DefenseWiki chunks not in English:", len(defense_chunks_not_in_english))
print("DefenseWiki chunks in English:", len(defense_chunks_in_english))
print("Constitution chunks not in English:", len(constitution_chunks_not_in_english))
print("Constitution chunks in English:", len(constitution_chunks_in_english))
print(
    "Other legal chunks not in English:",
    len(other_legal_docs_chunks_not_in_english),
)
print("Other legal chunks in English:", len(other_legal_docs_chunks_in_english))

total_chunks_not_in_english = (
    defense_chunks_not_in_english
    + constitution_chunks_not_in_english
    + other_legal_docs_chunks_not_in_english
)
total_chunks_in_english = (
    defense_chunks_in_english
    + constitution_chunks_in_english
    + other_legal_docs_chunks_in_english
)

# Filter the chunks on Burundi to create a Burundi collection and run just for that country ----------

Burundi_chunks_not_in_english = get_chunks_for_one_country(
    total_chunks_not_in_english, country="Burundi"
)
Burundi_chunks_in_english = get_chunks_for_one_country(
    total_chunks_in_english, country="Burundi"
)
print("Burundi_chunks_not_in_english: ", len(Burundi_chunks_not_in_english))
print("Burundi_chunks_in_english: ", len(Burundi_chunks_in_english))

# Create batches to translate and submit requests --------------------------------
# Key limits and considerations when using GPT-4o Mini via OpenAI's Batch API
# Maximum Enqueued Tokens per Batch: Up to 2,000,000 tokens can be enqueued at one time.
# Context Window: Up to 128,000 tokens per request.
# Maximum Output Tokens: Up to 16,384 tokens per request.
# estimate one request = 1500 tokens

# filtered_chunks = total_chunks_not_in_english[0:1000]
filtered_chunks = Burundi_chunks_not_in_english

translator = Translator(model_name="gpt-4o-mini")

translator.create_batch_file_for_translation(
    jsonl_output_file_path="data/interim/batch_input_translation_Burundi.jsonl",
    chunks=filtered_chunks,
)

file = upload_batch_file_to_openAI(
    client=openai_client,
    batch_file_name="data/interim/batch_input_translation_Burundi.jsonl",
)

batch = submit_batch_job(client=openai_client, file_id=file.id)

batch_id = "batch_6842f6bc28848190a58223b8d7c5c36b"
check_progress_batch_id(batch_id=batch_id)

parsed_results = retrieve_and_save_batch_results(
    batch_id=batch_id,
    output_file_path_jsonl="data/interim/translation_Burundi_results.jsonl",
    return_parsed_results=True,
)

# create chunks_translated
translated_chunks_Burundi = create_new_chunks_from_translated_results(
    chunks_not_in_english=filtered_chunks, parsed_results=parsed_results
)

# save new chunks
save_file(
    filename=Paths.PATH_TRANSLATED_CHUNKS,
    content=translated_chunks_Burundi,
    file_type="jsonl1",
)

# create a new collection with the translated chunks of Burundi + original in enlish

Burundi_chunks = Burundi_chunks_in_english + translated_chunks_Burundi

# V2 will only have chunks in english
chroma_collection_file_path = "data/chroma_db_v2"
collection_name = "legal_collection_v2"
chunk_ids_present_in_chromadb_collection_file_path = "data/chroma_db_v2/seen_ids.txt"
raw_embeddings = "data/chroma_db_v2/raw_embeddings.jsonl"

collection = load_collection(
    chroma_collection_file_path=chroma_collection_file_path,
    collection_name=collection_name,
    new_collection=True,  # Set to True to create a new collection
)

for Burundi_chunks in [Burundi_chunks_in_english, translated_chunks_Burundi]:
    collection = batch_embed_and_add(
        Burundi_chunks,
        collection,
        raw_embeddings,
        chunk_ids_present_in_chromadb_collection_file_path,
        batch_size=1000,
    )
print(f"Collection contains {collection.count()} documents.")
