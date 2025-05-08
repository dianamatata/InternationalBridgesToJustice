import json

path1 = "data/processed/defensewiki.ibj.org/chunks.jsonl"
path2 = "data/processed/constituteproject.org/constitution_chunks.jsonl"
chunks = []
for path in [path1, path2]:
    with open(f"{path}", "r", encoding="utf-8") as jsonl_file:
        lines = jsonl_file.readlines()  # Read all lines once
        print(f"Number of lines in the jsonl file {path}: {len(lines)}")
        for line in lines:
            chunks.append(json.loads(line))
    print(f"Total number of chunks: {len(chunks)}")  # Should be 50380

chunks[0]
