import json
from tqdm import tqdm
from src.config import Paths, MAX_CHUNK_SIZE
from src.chunking_functions import extract_chapters, split_text_into_chunks_with_metadata
from src.file_manager import load_jsonl_and_convert_to_list_of_dict, save_file


constitutions_all = load_jsonl_and_convert_to_list_of_dict(input_data=Paths.PATH_JSONL_FILE_WITH_CONSTITUTIONS_ALL_COUNTRIES)

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
    Paths.PATH_JSONL_FILE_CONSTITUTION_CHUNKS, "w", encoding="utf-8") as jsonl_file:
    for chunk in chunks:
        jsonl_file.write(json.dumps(chunk.__dict__) + "\n")
jsonl_file.close()

save_file(filename=Paths.PATH_JSONL_FILE_WITH_CONSTITUTIONS_ALL_COUNTRIES, content=constitutions_all, file_type="jsonl")

with open(Paths.PATH_JSONL_FILE_CONSTITUTION_CHUNKS, "r", encoding="utf-8") as f:
    print(f.readlines()[:2])  # Affiche les premières lignes

