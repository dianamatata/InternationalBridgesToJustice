import pymupdf4llm
from tqdm import tqdm
import json
import os
from src.internationalbridgestojustice.config import (
    legal_files_info_list,
    Paths,
    MAX_CHUNK_SIZE,
)
from src.internationalbridgestojustice.chunking_functions import (
    extract_chapters,
    split_text_into_chunks_with_metadata,
)
from src.internationalbridgestojustice.file_manager import (
    load_jsonl_and_convert_to_list_of_dict,
)

# pdfs to json file and content in markdown --------------------

EXTRACTED_DOCS_LIST_PATH = (
    f"{Paths.PATH_FOLDER_LEGAL_FILES_JSONL}/extracted_files_list.json"
)

# Step 1: Load already extracted file names
if os.path.exists(EXTRACTED_DOCS_LIST_PATH):
    with open(EXTRACTED_DOCS_LIST_PATH, "r", encoding="utf-8") as f:
        extracted_filenames = set(json.load(f))
else:
    extracted_filenames = set()

# Step 2: Open JSONL file in append mode and append files
with open(Paths.PATH_JSONL_FILE_WITH_LEGAL_FILES, "a", encoding="utf-8") as f_out:
    for file in tqdm(legal_files_info_list):
        if file["filename"] in extracted_filenames:
            print(f"Skipping {file['filename']} as it is already processed.")
            continue
        else:
            print(f"Processing: {file['filename']}")
            try:
                file["content"] = pymupdf4llm.to_markdown(file["path"])
            except Exception as e:
                print(f"Failed to extract content from {file['filename']}: {e}")
                file["content"] = ""
            f_out.write(json.dumps(file, ensure_ascii=False) + "\n")
            extracted_filenames.add(file["filename"])

# Step 3: Save updated extracted list
with open(EXTRACTED_DOCS_LIST_PATH, "w", encoding="utf-8") as f:
    json.dump(sorted(list(extracted_filenames)), f, ensure_ascii=False, indent=2)


# chunking ---------------
other_legal_files_all = load_jsonl_and_convert_to_list_of_dict(
    input_data=Paths.PATH_JSONL_FILE_WITH_LEGAL_FILES
)

chunks = []
for page in tqdm(range(0, len(other_legal_files_all))):
    print(other_legal_files_all[page]["filename"])
    document = other_legal_files_all[page]["content"]
    document_sections = extract_chapters(document, headers_to_exclude_from_chunks=None)
    parent_dict = other_legal_files_all[page]
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

with open(Paths.PATH_JSONL_FILE_LEGAL_OTHERS, "w", encoding="utf-8") as jsonl_file:
    for chunk in chunks:
        jsonl_file.write(json.dumps(chunk.__dict__) + "\n")
jsonl_file.close()


with open(Paths.PATH_JSONL_FILE_LEGAL_OTHERS, "r", encoding="utf-8") as f:
    print(f.readlines()[:2])  # Affiche les premières lignes
