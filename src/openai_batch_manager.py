import json
import openai
client = openai.OpenAI()

def build_batch_request(custom_id: str, system_prompt: str, user_prompt: str, temperature: float = 0.1):
    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions", #  this is what tells OpenAI to use client.chat.completions.create
        "body": {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": 1000
        }
    }

def upload_batch_file_to_openAI(batch_file_name: str):
    file = client.files.create(
        file=open(batch_file_name, "rb"),
        purpose="batch"
    )
    return file

def submit_batch_job(file_id: str):
    batch = client.batches.create(
        input_file_id=file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h"  # Or "1h" depending on plan
    )
    return batch
