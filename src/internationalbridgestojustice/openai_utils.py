import json
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
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": 2000,
    }

    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",  #  this is what tells OpenAI to use client.chat.completions.create
        "body": body,
    }


def build_batch_request_with_schema(
    custom_id: str,
    system_prompt: str,
    user_prompt: str,
    schema: dict,  # your json schema here
    schema_name: str,
    temperature: float = 0.1,
    model: str = "gpt-4o-mini",
    max_tokens: int = 2000,
):
    # define the tool format for batch API
    tools = [
        {"type": "function", "function": {"name": schema_name, "parameters": schema}}
    ]

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "tools": tools,
        "tool_choice": {"type": "function", "function": {"name": schema_name}},
    }

    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": body,
    }


def upload_batch_file_to_openAI(client, batch_file_name: str):
    file = client.files.create(file=open(batch_file_name, "rb"), purpose="batch")
    return file


def submit_batch_job(client, file_id: str, completion_window: str = "24h"):
    batch = client.batches.create(
        input_file_id=file_id,
        endpoint="/v1/chat/completions",
        completion_window=completion_window,
    )
    print("Batch job submitted:", batch.id)
    return batch


def save_batch_id(batch, country, path_file: str):
    with open(
        path_file,
        "a",
        encoding="utf-8",
    ) as f:
        f.write(f"{country}: {batch.id}\n")


def check_progress_batch_id(batch_id: str):
    batch = openai_client.batches.retrieve(batch_id=batch_id)
    print(f"Batch {batch_id} status: {batch.status}")


def retrieve_and_save_batch_results(
    batch_id: str, output_file_path_jsonl: str, return_parsed_results: bool = True
):
    result = openai_client.batches.retrieve(batch_id=batch_id)
    output_stream = openai_client.files.content(result.output_file_id)
    parsed_results = []
    with open(output_file_path_jsonl, "w", encoding="utf-8") as f:
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


def retrieve_tool_calls(parsed_results):
    results_list = []
    for i in range(len(parsed_results)):
        tool_calls = parsed_results[i]["response"]["body"]["choices"][0]["message"][
            "tool_calls"
        ]
        arguments_str = tool_calls[0]["function"]["arguments"]
        try:
            result = json.loads(arguments_str)
        except json.JSONDecodeError:
            try:
                arguments_str += '"}'
                result = json.loads(arguments_str)
            except json.JSONDecodeError:
                arguments_str += '"}'
                result = json.loads(arguments_str)
        result = {"custom_id": parsed_results[i]["custom_id"], **result}
        results_list.append(result)

    return results_list


def check_failed_batch(batch_id: str, openai_client):
    try:
        batch = openai_client.batches.retrieve(batch_id=batch_id)

        print(f"=== BATCH STATUS: {batch.status.upper()} ===")
        print(f"Batch ID: {batch.id}")
        print(f"Status: {batch.status}")
        print(f"Created at: {batch.created_at}")
        print(f"Failed at: {batch.failed_at}")
        print(f"Endpoint: {batch.endpoint}")
        print(f"Completion window: {batch.completion_window}")

        # Check request counts
        if batch.request_counts:
            print("\n=== REQUEST COUNTS ===")
            print(f"Total: {batch.request_counts.total}")
            print(f"Completed: {batch.request_counts.completed}")
            print(f"Failed: {batch.request_counts.failed}")

        # Check for errors
        if batch.errors:
            print("\n=== BATCH ERRORS ===")
            for i, error in enumerate(batch.errors):
                print(f"Error {i + 1}:")
                print(f"  Code: {error.get('code', 'Unknown')}")
                print(f"  Message: {error.get('message', 'Unknown')}")
                if "line" in error:
                    print(f"  Line: {error['line']}")

        # Check error file if available
        if batch.error_file_id:
            print("\n=== ERROR FILE CONTENT ===")
            print(f"Error file ID: {batch.error_file_id}")

            try:
                error_stream = openai_client.files.content(batch.error_file_id)
                error_content = error_stream.text

                print("Error file content:")
                print("-" * 50)
                print(error_content)
                print("-" * 50)

                # Try to parse error file as JSONL
                if error_content.strip():
                    print("\n=== PARSED ERROR DETAILS ===")
                    for i, line in enumerate(error_content.strip().split("\n")):
                        if line.strip():
                            try:
                                error_obj = json.loads(line)
                                print(f"Error {i + 1}:")
                                print(
                                    f"  Custom ID: {error_obj.get('custom_id', 'Unknown')}"
                                )
                                if "error" in error_obj:
                                    err = error_obj["error"]
                                    print(f"  Error type: {err.get('type', 'Unknown')}")
                                    print(f"  Error code: {err.get('code', 'Unknown')}")
                                    print(
                                        f"  Error message: {err.get('message', 'Unknown')}"
                                    )
                                print()
                            except json.JSONDecodeError:
                                print(f"Error {i + 1}: Could not parse JSON: {line}")

            except Exception as e:
                print(f"Could not retrieve error file: {e}")

        # Check input file for validation
        if batch.input_file_id:
            print("\n=== INPUT FILE VALIDATION ===")
            print(f"Input file ID: {batch.input_file_id}")

            try:
                input_stream = openai_client.files.content(batch.input_file_id)
                input_content = input_stream.text

                print(f"Input file size: {len(input_content)} characters")
                lines = input_content.strip().split("\n")
                print(f"Number of lines: {len(lines)}")

                # Validate first few lines
                print("\n=== FIRST FEW LINES VALIDATION ===")
                for i, line in enumerate(lines[:3]):  # Check first 3 lines
                    print(f"Line {i + 1}:")
                    if line.strip():
                        try:
                            parsed = json.loads(line)
                            print("  ✅ Valid JSON")

                            # Check required fields
                            required = ["custom_id", "method", "url", "body"]
                            missing = [f for f in required if f not in parsed]
                            if missing:
                                print(f"  ❌ Missing fields: {missing}")
                            else:
                                print("  ✅ All required fields present")

                                # Check response_format if present
                                body = parsed.get("body", {})
                                if "response_format" in body:
                                    rf = body["response_format"]
                                    print(
                                        f"  Response format: {rf.get('type', 'Unknown')}"
                                    )

                                    if rf.get("type") == "json_schema":
                                        js = rf.get("json_schema", {})
                                        if "strict" not in js:
                                            print(
                                                "  ⚠️  json_schema missing 'strict' field"
                                            )
                                        else:
                                            print(
                                                f"  ✅ json_schema has strict: {js['strict']}"
                                            )

                        except json.JSONDecodeError as e:
                            print(f"  ❌ Invalid JSON: {e}")
                    else:
                        print("  Empty line")
                    print()

            except Exception as e:
                print(f"Could not retrieve input file: {e}")

        return {
            "batch": batch,
            "status": batch.status,
            "errors": batch.errors,
            "error_file_id": batch.error_file_id,
            "input_file_id": batch.input_file_id,
        }

    except Exception as e:
        print(f"Error checking batch: {e}")
        return None


def get_common_batch_failure_causes():
    """Return common causes of batch failures and how to fix them."""

    return {
        "Invalid JSON": {
            "cause": "Malformed JSON in input file",
            "fix": "Validate each line with json.loads()",
        },
        "Missing required fields": {
            "cause": "Missing custom_id, method, url, or body",
            "fix": "Ensure all required fields are present",
        },
        "Invalid response_format": {
            "cause": "Malformed json_schema or missing strict mode",
            "fix": "Add 'strict': true and fix schema structure",
        },
        "File encoding issues": {
            "cause": "Non-UTF8 encoding",
            "fix": "Save file with UTF-8 encoding",
        },
        "Empty or corrupted file": {
            "cause": "File upload failed or corrupted",
            "fix": "Re-upload the file",
        },
        "Model not supported": {
            "cause": "Using unsupported model in batch API",
            "fix": "Use supported models like gpt-4o-mini",
        },
        "Rate limits": {
            "cause": "Too many requests or tokens",
            "fix": "Reduce batch size or wait",
        },
    }
