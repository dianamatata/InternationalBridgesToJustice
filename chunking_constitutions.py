import json  # save in json files

MAX_CHUNK_SIZE = 500
from chunking_and_formatting_defensewiki import extract_chapters, split_text_into_chunks
from chunking_and_formatting_defensewiki import split_text_into_chunks_with_metadata
from tqdm import tqdm

# FUNCTIONS --------------------

# adapt this code
out_folder_2 = "/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/data/processed/constituteproject.org"
with open(
    f"{out_folder_2}/constituteproject.jsonl", "r", encoding="utf-8"
) as jsonl_file:
    constitutions_all = [
        json.loads(line) for line in jsonl_file
    ]  # Convert each line to a dictionary
    keys = constitutions_all[1].keys()
    chunks = []

    for page in tqdm(range(0, len(constitutions_all))):
        print(constitutions_all[page]["filename"])
        document = constitutions_all[page]["content"]
        # change country title
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
    f"{out_folder_2}/constitution_chunks.jsonl", "w", encoding="utf-8"
) as jsonl_file:
    for chunk in chunks:
        jsonl_file.write(json.dumps(chunk.__dict__) + "\n")
jsonl_file.close()


with open(
    f"{out_folder_2}/constitution_chunks.json", "a", encoding="utf-8"
) as json_file:
    for chunk in chunks:
        json_file.write(json.dumps(chunk.__dict__) + "\n")
json_file.close()

#
# with open(f"{out_folder_2}/constitution_chunks.jsonl", "w", encoding="utf-8") as jsonl_file:
#     for chunk in chunks:
#         print(json.dumps(chunk.__dict__))


# # Vérification et correction du format
# if isinstance(constitutions_all, list) and isinstance(constitutions_all[0], list):
#     constitutions_all = constitutions_all[0]  # Enlever la liste imbriquée
#
# # Sauvegarde en JSONL
# with open(f"{out_folder_2}/constituteproject.jsonl", "w", encoding="utf-8") as jsonl_file:
#     for entry in constitutions_all:
#         jsonl_file.write(json.dumps(entry, ensure_ascii=False) + "\n")


# resave constitutions_all with corrected country names

with open(
    f"{out_folder_2}/constituteproject.jsonl", "w", encoding="utf-8"
) as jsonl_file:
    jsonl_file.write(json.dumps(constitutions_all) + "\n")

with open(f"{out_folder_2}/constituteproject.json", "w", encoding="utf-8") as json_file:
    for entry in constitutions_all:
        json_file.write(json.dumps(entry) + "\n")

# check it is writen
with open(f"{out_folder_2}/constitution_chunks.jsonl", "r", encoding="utf-8") as f:
    print(f.readlines()[:2])  # Affiche les 5 premières lignes

# debug

# file_path = "/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/data/raw/constituteproject.org/Singapore_2016.md"
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
