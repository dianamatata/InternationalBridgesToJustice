import json
from src.openai_batch_manager import upload_batch_file_to_openAI, submit_batch_job
from src.translation_src import create_batch_file_for_translation, get_chunks_not_in_english
import openai
client = openai.OpenAI()

# Load the chunks --------------------------------
filtered_chunks = get_chunks_not_in_english(json_file_path= "../data/processed/defensewiki.ibj.org/unique_chunks.json")

# Create batches to translate and submit requests --------------------------------

create_batch_file_for_translation(jsonl_output_file_path="../data/interim/batch_input_translation.jsonl", chunks=filtered_chunks)
file = upload_batch_file_to_openAI(batch_file_name="../data/interim/batch_input_translation.jsonl")
# TODO check how many requests in the batch first
batch = submit_batch_job(file_id=file.id)
print("Batch job submitted:", batch.id)

# Retrieve and save results --------------------------------

result = client.batches.retrieve(batch_id="batch_6818c363af4c8190892dac4d68abbd84")
# TODO: save the results

