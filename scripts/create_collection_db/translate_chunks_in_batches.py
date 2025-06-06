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

check_progress_batch_id(batch_id="batch_6842f6bc28848190a58223b8d7c5c36b")

parsed_results = retrieve_and_save_batch_results(
    batch_id="batch_6842d4c7d33c819084f1a30f683c5c4b",
    output_file_path_jsonl="data/interim/test_retrieve_and_save_batch_results.jsonl",
    return_parsed_results=True,
)

# create chunks_translated
translated_chunks_Burundi = create_new_chunks_from_translated_results(
    chunks_not_in_english=Burundi_chunks_not_in_english, parsed_results=parsed_results
)


result = parsed_results[19]
# TODO Create new collection with the translated chunks
# Burundi: Batch job submitted: batch_6842f6bc28848190a58223b8d7c5c36b in progress
# Batch job submitted: batch_6842d4c7d33c819084f1a30f683c5c4b finished successfully
