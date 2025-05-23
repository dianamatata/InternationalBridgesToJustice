import json
from src.openai_utils import upload_batch_file_to_openAI, submit_batch_job
from src.get_translation import Translator, get_chunks_not_in_english
from src.openai_utils import openai_client

# Load the chunks --------------------------------
filtered_chunks = get_chunks_not_in_english(json_file_path= "../data/processed/defensewiki.ibj.org/unique_chunks.json")

# Create batches to translate and submit requests --------------------------------
translator = Translator(model_name="gpt-4o-mini")
translator.create_batch_file_for_translation(jsonl_output_file_path="../data/interim/batch_input_translation.jsonl", chunks=filtered_chunks)
file = upload_batch_file_to_openAI(batch_file_name="../data/interim/batch_input_translation.jsonl")
# TODO check how many requests in the batch first
batch = submit_batch_job(file_id=file.id)
print("Batch job submitted:", batch.id)

# Retrieve and save results --------------------------------

result = openai_client.batches.retrieve(batch_id="batch_6818c363af4c8190892dac4d68abbd84")
response = openai_client.files.content(result.output_file_id)
with open("../data/interim/batch_results_translation.jsonl", "wb") as f:
    f.write(response.read())
# TODO: save the results
