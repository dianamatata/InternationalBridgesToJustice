import json
def get_data_from_jsonl_file(jsonl_input_file: str):
    with open(jsonl_input_file, "r", encoding="utf-8") as jsonl_file:
        data = [
            json.loads(line) for line in jsonl_file
        ]
    return data
