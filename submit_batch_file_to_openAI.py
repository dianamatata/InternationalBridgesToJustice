import openai

client = openai.OpenAI()

# Upload file
file = client.files.create(
    file=open("batch_input.jsonl", "rb"),
    purpose="batch"
)

# Create batch job
batch = client.batches.create(
    input_file_id=file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h"  # Or "1h" depending on plan
)

print("Batch job submitted:", batch.id)
