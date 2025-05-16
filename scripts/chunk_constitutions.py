import json  # save in json files
from src.chunking_functions import extract_chapters, split_text_into_chunks_with_metadata
from tqdm import tqdm
from src.file_manager import load_jsonl_and_convert_to_list_of_dict
from src.config import MAX_CHUNK_SIZE, path_jsonl_file_with_constitutions_all_countries, path_jsonl_file_constitution_chunks


constitutions_all = load_jsonl_and_convert_to_list_of_dict(input_data=path_jsonl_file_with_constitutions_all_countries)

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
        new_chunks = split_text_into_chunks_with_metadata(
            document_sections[section],
            section,
            parent_dict,
            title="country",
            max_chunk_size=MAX_CHUNK_SIZE,
            separator="\n\n",
        )
        chunks.extend(new_chunks)


with open(
    path_jsonl_file_constitution_chunks, "w", encoding="utf-8"
) as jsonl_file:
    for chunk in chunks:
        jsonl_file.write(json.dumps(chunk.__dict__) + "\n")
jsonl_file.close()


with open(
    path_jsonl_file_with_constitutions_all_countries, "w", encoding="utf-8"
) as jsonl_file:
    jsonl_file.write(json.dumps(constitutions_all) + "\n")


# check it is writen
with open(path_jsonl_file_constitution_chunks, "r", encoding="utf-8") as f:
    print(f.readlines()[:2])  # Affiche les 5 premières lignes

