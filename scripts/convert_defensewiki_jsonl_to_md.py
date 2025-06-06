import json

# Loop over Defensewiki to extract all the pages as markdown

input_data = "data/interim/defensewiki_all.jsonl"
path = "data/raw/defensewiki.ibj.org"

with open(f"{input_data}", "r", encoding="utf-8") as jsonl_file:
    defense_wiki_all = [
        json.loads(line) for line in jsonl_file
    ]  # Convert each line to a dictionary

for page in range(1, len(defense_wiki_all)):
    title_value = defense_wiki_all[page]["title"]
    filename = f"{path}/{title_value}.md"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(defense_wiki_all[page]["content"])

# open jsonl
data = []
with open(f"{path}/chunks.jsonl", "r", encoding="utf-8") as json_file:
    for line in jsonl_file:
        data.append(json.loads(line))

# write jsonl
with open(f"{path}/chunks.jsonl", "w", encoding="utf-8") as jsonl_file:
    for record in data:
        jsonl_file.write(json.dumps(record) + "\n")
