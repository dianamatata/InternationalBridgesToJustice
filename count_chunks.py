import json


path = "/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/data/processed/defensewiki.ibj.org"

with open(f"{path}/chunks.jsonl", "r", encoding="utf-8") as jsonl_file:
    line_count = sum(1 for line in jsonl_file)
    print(f"Number of lines in the jsonl file: {line_count}")

path2 = "/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/data/processed/constituteproject.org"
with open(f"{path2}/constitution_chunks.jsonl", "r", encoding="utf-8") as jsonl_file:
    line_count2 = sum(1 for line in jsonl_file)
    print(f"Number of lines in the jsonl file: {line_count2}")

print(f"Total number of chunks: {line_count + line_count2}") # 50380 chunks in total of 500 words


# print first line of json file
with open(f"{path}/chunks.jsonl", "r", encoding="utf-8") as jsonl_file:
    first_line = jsonl_file.readline()
    print(json.loads(first_line))

