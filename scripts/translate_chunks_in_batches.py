from src.internationalbridgestojustice.openai_utils import (
    upload_batch_file_to_openAI,
    submit_batch_job,
)
from src.internationalbridgestojustice.get_translation import (
    Translator,
    get_chunks_in_english,
)
from src.internationalbridgestojustice.config import Paths
from src.internationalbridgestojustice.openai_utils import openai_client

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
    "Other legal docs chunks not in English:",
    len(other_legal_docs_chunks_not_in_english),
)
print("Other legal docs chunks in English:", len(other_legal_docs_chunks_in_english))

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


filtered_chunks = total_chunks_not_in_english[2:3]
# Create batches to translate and submit requests --------------------------------
translator = Translator(model_name="gpt-4o-mini")
translator.create_batch_file_for_translation(
    jsonl_output_file_path="data/interim/batch_input_translation.jsonl",
    chunks=filtered_chunks,
)
file = upload_batch_file_to_openAI(
    client=openai_client, batch_file_name="data/interim/batch_input_translation.jsonl"
)
# TODO check how many requests in the batch first
batch = submit_batch_job(client=openai_client, file_id=file.id)

print("Batch job submitted:", batch.id)
# Batch job submitted: batch_6842d4c7d33c819084f1a30f683c5c4b

# check progress
batch = openai_client.batches.retrieve(
    batch_id="batch_6842d4c7d33c819084f1a30f683c5c4b"
)
print("Batch status:", batch.status)

# Retrieve and save results --------------------------------

result = openai_client.batches.retrieve(
    batch_id="batch_6842d4c7d33c819084f1a30f683c5c4b"
)
output_stream = openai_client.files.content(result.output_file_id)

# Save the contents to disk (e.g., results.jsonl)
with open("data/interim/batch_results_translation.jsonl", "a", encoding="utf-8") as f:
    for line in output_stream:
        decoded_line = line.decode("utf-8")  # convert bytes to string
        f.write(decoded_line)
