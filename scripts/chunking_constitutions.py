import json  # save in json files
from chunking_functions import extract_chapters, split_text_into_chunks_with_metadata
from tqdm import tqdm
MAX_CHUNK_SIZE = 500

from src.file_manager import load_jsonl_and_convert_to_list_of_dict


# FUNCTIONS --------------------

folder_with_constitutions_all_countries = "data/processed/constituteproject.org"
file_with_constitutions_all_countries = f"{folder_with_constitutions_all_countries}/constituteproject.jsonl"
constitutions_all = load_jsonl_and_convert_to_list_of_dict(input_data=file_with_constitutions_all_countries)
keys = constitutions_all[1].keys()

chunks = []
for page in tqdm(range(0, len(constitutions_all))):
    print(constitutions_all[page]["filename"])
    document = constitutions_all[page]["content"]
    constitutions_all[page]["country"] = "_".join(
        constitutions_all[page]["filename"].split("_")[:-1]
    )
    document_sections = extract_chapters(
        document, headers_to_exclude_from_chunks=None
    )
    parent_dict = constitutions_all[page]
    for section in document_sections:
        # print(section)
        new_chunks = split_text_into_chunks_with_metadata(
            document_sections[section],
            section,
            parent_dict,
            title="country",
            max_chunk_size=MAX_CHUNK_SIZE,
            separator="\n\n",
        )
        chunks.extend(new_chunks)

print(f"Len chunks: {len(chunks)}")


with open(
    f"{folder_with_constitutions_all_countries}/constitution_chunks.jsonl", "w", encoding="utf-8"
) as jsonl_file:
    for chunk in chunks:
        jsonl_file.write(json.dumps(chunk.__dict__) + "\n")
jsonl_file.close()


with open(
    f"{folder_with_constitutions_all_countries}/constituteproject.jsonl", "w", encoding="utf-8"
) as jsonl_file:
    jsonl_file.write(json.dumps(constitutions_all) + "\n")

with open(f"{folder_with_constitutions_all_countries}/constituteproject.json", "w", encoding="utf-8") as json_file:
    for entry in constitutions_all:
        json_file.write(json.dumps(entry) + "\n")

# check it is writen
with open(f"{folder_with_constitutions_all_countries}/constitution_chunks.jsonl", "r", encoding="utf-8") as f:
    print(f.readlines()[:2])  # Affiche les 5 premières lignes

# debug

# file_path = "data/raw/constituteproject.org/Singapore_2016.md"
# with open(file_path, "r", encoding="utf-8") as file:
#     document = file.read()

# i = 3
# match = matches[i]
# section = document_sections['2. Interpretation']
# page=162
# parent_dict = [constitution for constitution in constitutions_all if constitution['country'] == 'Singapore']
# section = '2. Interpretation'
# text = document_sections[section]
# metadata = parent_dict
# max_chunk_size = MAX_CHUNK_SIZE
# title = 'country'
# # Filter the metadata to only include the selected keys
# selected_keys = ['link', 'country', 'year', 'path', 'filename', 'language', 'type']
# filtered_metadata = {key: metadata.get(key) for key in metadata if key != 'content'}
#
# metadata1 = {key: parent_dict[key] for key in selected_keys}
# constitutions_all[1].keys()
# constitutions_all[1]['country']
# constitutions_all[1]['content']
constitutions_all[page]["country"]
"_".join(constitutions_all[page]["filename"].split("_")[:-1])
