from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()  # Only runs once even if imported multiple times
openai_client = OpenAI()

def openai_generate_embeddings(texts: list[str], model="text-embedding-3-large") -> list[list[float]]:
    response = openai_client.embeddings.create(model=model, input=texts)
    return [d.embedding for d in response.data]

def get_openai_response(
    client,
    categorize_system_prompt: str,
    prompt: str,
    model="gpt-4o-mini",
    temperature=0.1,
) -> str:
    """
    Send the prompt to OpenAI's chat API and return the answer.
    """
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": categorize_system_prompt},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content

def build_batch_request(custom_id: str, system_prompt: str, user_prompt: str, temperature: float = 0.1, model: str = "gpt-4o-mini"):
    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions", #  this is what tells OpenAI to use client.chat.completions.create
        "body": {
            "model": model,
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
