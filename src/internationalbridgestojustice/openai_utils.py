from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # Only runs once even if imported multiple times
openai_client = OpenAI()


def openai_generate_embeddings(
    texts: list[str], model="text-embedding-3-large"
) -> list[list[float]]:
    response = openai_client.embeddings.create(model=model, input=texts)
    return [d.embedding for d in response.data]


def get_openai_response(
    client,
    categorize_system_prompt: str,
    prompt: str,
    response_format,
    model="gpt-4o-mini",
    temperature=0.1,
) -> str:
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": categorize_system_prompt},
            {"role": "user", "content": prompt},
        ],
        response_format=response_format,
    )

    return response.choices[0].message.content


def build_batch_request(
    custom_id: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.1,
    model: str = "gpt-4o-mini",
):
    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",  #  this is what tells OpenAI to use client.chat.completions.create
        "body": {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": 1000,
        },
    }


def upload_batch_file_to_openAI(client, batch_file_name: str):
    file = client.files.create(file=open(batch_file_name, "rb"), purpose="batch")
    return file


def submit_batch_job(client, file_id: str):
    batch = client.batches.create(
        input_file_id=file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",  # Or "1h" depending on plan
    )
    print("Batch job submitted:", batch.id)
    return batch


def check_progress_batch_id(batch_id: str):
    batch = openai_client.batches.retrieve(batch_id=batch_id)
    print(f"Batch {batch_id} status: {batch.status}")
    if batch.status == "succeeded":
        print("Batch completed successfully.")
    elif batch.status == "failed":
        print("Batch failed.")
    else:
        print("Batch is still in progress.")


def retrieve_and_save_batch_results(
    batch_id: str, output_file_path_jsonl: str, return_parsed_results: bool = True
):
    result = openai_client.batches.retrieve(batch_id=batch_id)
    output_stream = openai_client.files.content(result.output_file_id)
    parsed_results = []
    with open(output_file_path_jsonl, "a", encoding="utf-8") as f:
        lines = output_stream.iter_lines()
        for line in lines:
            if line.strip():  # skip empty lines
                try:
                    json_obj = json.loads(line)
                    f.write(json.dumps(json_obj, ensure_ascii=False) + "\n")
                    if return_parsed_results:
                        parsed_results.append(json_obj)
                except json.JSONDecodeError as e:
                    print(f"Skipping invalid line: {e}")

    if return_parsed_results:
        return parsed_results
