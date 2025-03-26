# >>> - Transform the json file in jsonl file

import json # save in json files
input_data = "/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/data/interim/defensewiki_all.json"

# 1 - Load JSON
with open(input_data, "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

records = data["https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=1300&offset=0"]

# 2 - Write each dictionary as a new line in JSONL format
with open(f"{input_data}l", "w", encoding="utf-8") as jsonl_file:
    for record in records:
        jsonl_file.write(json.dumps(records[record]) + "\n")

# 3 - Read JSONL file line by line
with open(f"{input_data}l", "r", encoding="utf-8") as jsonl_file:
    defense_wiki_all = [json.loads(line) for line in jsonl_file]  # Convert each line to a dictionary

# 4 - Now `data1` is a list of dictionaries
print(len(defense_wiki_all))  # Should print 1252 if correctly processed
print(f"{json.dumps(defense_wiki_all[0], indent=4)}")

# 5 - Loop over Defensewiki to extract all the pages as markdown
path = "/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/data/raw/defensewiki.ibj.org"

with open(f"{input_data}l", "r", encoding="utf-8") as jsonl_file:
    defense_wiki_all = [json.loads(line) for line in jsonl_file]  # Convert each line to a dictionary

for page in range(1, len(defense_wiki_all)):
    title_value = defense_wiki_all[page]["title"]
    filename = f"{path}/{title_value}.md"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(defense_wiki_all[page]["content"])