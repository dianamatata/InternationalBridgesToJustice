import json
from tqdm import tqdm
from src import extract_chapters, split_text_into_chunks
from src.internationalbridgestojustice.config import MAX_CHUNK_SIZE, Paths

headers_to_exclude_from_chunks = {
    "REFERENCES",
    "Referencias",
    "References",
    "Navigation menu",
    "Page actions",
    "Personal tools",
    "Navigation",
    "Search",
    "Glossary",
    "Tools",
    "Contents",
}

# MAIN --------------------

with open(Paths.PATH_JSONL_FILE_DEFENSEWIKI, "r", encoding="utf-8") as jsonl_file:
    defense_wiki_all = [
        json.loads(line) for line in jsonl_file
    ]  # Convert each line to a dictionary
    keys = defense_wiki_all[1].keys()
    chunks = []

    for page in tqdm(range(0, len(defense_wiki_all))):
        document = defense_wiki_all[page]["content"]
        document_sections = extract_chapters(
            document, headers_to_exclude_from_chunks=headers_to_exclude_from_chunks
        )
        parent_dict = defense_wiki_all[page]
        print(f"{parent_dict['title']}")

        for section in document_sections:
            # print(f"s: {section}")
            # print(f"\033[92mr: {' '.join(section.split()[0:7])}\033[0m")
            new_chunks = split_text_into_chunks(
                document_sections[section],
                section,
                parent_dict,
                max_chunk_size=MAX_CHUNK_SIZE,
                separator="\n\n",
            )
            chunks.extend(new_chunks)

with open(
    f"{Paths.PATH_FOLDER_DEFENSE_WIKI}/chunks.jsonl", "w", encoding="utf-8"
) as jsonl_file:
    for chunk in chunks:
        jsonl_file.write(json.dumps(chunk.__dict__) + "\n")

with open(
    f"{Paths.PATH_FOLDER_DEFENSE_WIKI}/chunks.json", "w", encoding="utf-8"
) as json_file:
    json.dump(
        [chunk.__dict__ for chunk in chunks], json_file, ensure_ascii=False, indent=2
    )
