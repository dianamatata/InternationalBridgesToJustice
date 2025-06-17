import json
from collections import Counter
from src.internationalbridgestojustice.openai_utils import (
    upload_batch_file_to_openAI,
    submit_batch_job,
    openai_client,
    retrieve_and_save_batch_results,
    check_progress_batch_id,
    save_batch_id,
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

defense_chunks_in_english, defense_chunks_not_in_english = get_chunks_in_english(
    jsonl_file_path="data/processed/defensewiki.ibj.org/unique_chunks.jsonl"
)

constitution_chunks_in_english, constitution_chunks_not_in_english = (
    get_chunks_in_english(jsonl_file_path=Paths.PATH_JSONL_FILE_CONSTITUTION_CHUNKS)
)

other_legal_docs_chunks_in_english, other_legal_docs_chunks_not_in_english = (
    get_chunks_in_english(jsonl_file_path=Paths.PATH_JSONL_FILE_LEGAL_OTHERS)
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
COUNTRY = "Burundi"

Country_chunks_not_in_english = get_chunks_for_one_country(
    total_chunks_not_in_english, country=COUNTRY
)
Country_chunks_in_english = get_chunks_for_one_country(
    total_chunks_in_english, country=COUNTRY
)
print(COUNTRY, "chunks not in English: ", len(Country_chunks_not_in_english))
print(COUNTRY, "chunks  in English: , ", len(Country_chunks_in_english))

filtered_chunks = Country_chunks_not_in_english

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

save_batch_id(
    batch=batch,
    path_file="data/interim/batch_id_input_translation.txt",
)

batch_id = "batch_6842f6bc28848190a58223b8d7c5c36b"
check_progress_batch_id(batch_id=batch_id)

parsed_results = retrieve_and_save_batch_results(
    batch_id=batch_id,
    output_file_path_jsonl="data/interim/translation_Burundi_results.jsonl",
    return_parsed_results=True,
)

# create chunks_translated
translated_chunks = create_new_chunks_from_translated_results(
    chunks_not_in_english=filtered_chunks, parsed_results=parsed_results
)

# save new chunks
save_file(
    filename=Paths.PATH_TRANSLATED_CHUNKS,
    content=translated_chunks,
    file_type="jsonl1",
)


# create a new collection with the translated chunks of Burundi + original in english
Country_chunks = Country_chunks_in_english + translated_chunks

# TODO change chunks metadata before creating the collection # check chunk_structure.py
# TODO # perform_similarity_search_in_collection only filters on one param, country or legal type to pick!!! so create a fusion metadata entry
with open(Paths.PATH_TRANSLATED_CHUNKS, "r", encoding="utf-8") as file:
    translated_chunks = [json.loads(line) for line in file]

for chunk in Country_chunks_in_english + translated_chunks:
    metadata = chunk["metadata"]
    if metadata.get("type") == "constitution":
        metadata["type"] = "ground_truth"
    elif "type" not in metadata and "legal_type" in metadata:
        metadata["type"] = "ground_truth"
    metadata["type_country"] = (
        f"{metadata.get('type', 'unknown')}_{metadata.get('country', 'unknown')}"
    )

# v5 will only have chunks in english
chroma_collection_file_path = "data/chroma_db_v5"
collection_name = "legal_collection_v5"
chunk_ids_present_in_chromadb_collection_file_path = "data/chroma_db_v5/seen_ids.txt"
raw_embeddings = "data/chroma_db_v5/raw_embeddings.jsonl"

collection = load_collection(
    chroma_collection_file_path=chroma_collection_file_path,
    collection_name=collection_name,
    new_collection=True,  # Set to True to create a new collection
)

# check how many of each type
type_counter = Counter()
for country_chunks in [Country_chunks_in_english, translated_chunks]:
    for chunk in country_chunks:
        metadata_type = chunk["metadata"].get("type", "missing")
        type_counter[metadata_type] += 1
print(type_counter)

# in 2 steps otherwise error: 'Requested 310340 tokens, max 300000 tokens per request'
for Country_chunks in [Country_chunks_in_english, translated_chunks]:
    collection = batch_embed_and_add(
        Country_chunks,
        collection,
        raw_embeddings,
        chunk_ids_present_in_chromadb_collection_file_path,
        batch_size=1000,
    )
print(f"Collection contains {collection.count()} documents.")
