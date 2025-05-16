# We want to add as metadata the country in all the defense wiki pages.
# Get country names, some are written in different languages, so creating title_to_country dictionary
# Update also chunks and collection of chromadb
# if title contains American_... > "United States", Chinese... > China
# some countries have duplicated pages, we have hashes that are not unique

import json
import pycountry
from collections import defaultdict, Counter
import json
import pandas as pd
import chromadb
import numpy as np
from src.config import path_chromadb, collection_name
from src.countries_dict import title_to_country, substring_to_country
from scrap_defensewiki_website import matching_country_name

# 1 - Get country names (and optional aliases) from pycountry
country_names1 = [country.name for country in pycountry.countries]

# 2 - Get country names from the Defense Wiki Country pages
file_country_names = "data/interim/country_names_1.txt"
with open(file_country_names, "r", encoding="utf-8") as f:
    country_names = f.read().splitlines()

missing_countries = [c for c in country_names1 if c not in country_names]

# 3. Update the defensewiki to add the country name
input_data = "data/interim/defensewiki_all.json"
with open(f"{input_data}l", "r", encoding="utf-8") as jsonl_file:
    defense_wiki_all = [
        json.loads(line) for line in jsonl_file
    ]  # Convert each line to a dictionary
    keys = defense_wiki_all[1].keys()

for d in defense_wiki_all:
    # Check if any country name is in the title, in this direction because 'Thailand-es' in 'Thailand'
    cleaned_title = d["title"].replace("_", " ").strip().lower()
    d["country"] = matching_country_name(country_names, cleaned_title)



# check all the missing countries labeled ""
check1 = [[e["title"], e["country"]] for e in defense_wiki_all if e["country"] is ""]
for c in check1:
    print(c)


# 4. check problems
# with Urugay
country_to_check = "Congo,_Democratic_Republic_of_the" 
def debug_country_naming(country_to_check: str):
    entry_to_check = [
        d for d in defense_wiki_all if country_to_check in d["title"]
    ]
    check1 = [[e["title"], e["country"]] for e in entry_to_check]
    for c in check1:
        print(c)
        
        
        
# save pages without countries
with open(f"data/interim/no_countries.txt", "w", encoding="utf-8") as file:
    for c in check1:
        file.write(f"{c}\n")

# save defense wiki with countries
with open("data/interim/defensewiki_all_1.json", "w", encoding="utf-8") as file:
    json.dump(defense_wiki_all, file, indent=4)  # Save JSON content

with open("data/interim/defensewiki_all_1.jsonl", "w", encoding="utf-8") as jsonl_file:
    for record in defense_wiki_all:
        jsonl_file.write(json.dumps(record) + "\n")

# 2 update the chunks with country names
# load defense wiki
with open("data/interim/defensewiki_all_1.json", "r", encoding="utf-8") as json_file:
    defense_wiki_all = json.load(json_file)


# load the chunks and add countries
path1 = "data/processed/defensewiki.ibj.org/chunks.jsonl"
chunks = []
for path in [path1]:
    with open(f"{path}", "r", encoding="utf-8") as jsonl_file:
        lines = jsonl_file.readlines()  # Read all lines once
        print(f"Number of lines in the jsonl file {path}: {len(lines)}")
        for line in lines:
            chunks.append(json.loads(line))
        for chunk in chunks:
            matches = [
                d["country"]
                for d in defense_wiki_all
                if d["title"] == chunk["metadata"]["title"]
            ]
            chunk["metadata"]["country"] = matches[0] if matches else ""
    print(f"Total number of chunks: {len(chunks)}")

# check we have countries
seen_countries = set([chunk['metadata']['country'] for chunk in chunks])


with open(
        "data/processed/defensewiki.ibj.org/chunks_1.json", "w", encoding="utf-8"
) as file:
    json.dump(chunks, file, indent=4)  # Save JSON content

with open(
        "data/processed/defensewiki.ibj.org/chunks_1.jsonl", "w", encoding="utf-8"
) as jsonl_file:
    for record in chunks:
        jsonl_file.write(json.dumps(record) + "\n")


# change embeddings and remove duplicates ----------------------------------------



input_data = "data/processed/defensewiki.ibj.org/chunks_1.json"
with open(input_data, "r", encoding="utf-8") as json_file:
    chunks = json.load(json_file)

# get duplicated hashes
titles = [chunk["title"] for chunk in chunks]
len(titles) == len(np.unique(titles))
# len(np.unique(titles)) 10605
# len(titles) 10941
duplicated_hash = [item for item, count in Counter(titles).items() if count > 1]
# get all duplicated chunks
duplicated_chunks = [d for d in chunks if d["title"] in duplicated_hash]
len(duplicated_chunks)
# extract pages names
duplicated_pages_data = [
    [
        d["title"],
        d["metadata"]["title"],
        d["metadata"]["link"],
        d["metadata"]["title_bis"],
    ]
    for d in duplicated_chunks
]
df_duplicates = pd.DataFrame(
    duplicated_pages_data, columns=["Hash Title", "Page Title", "Link", "Title Bis"]
)

output_file = "data/interim/duplicated_hashes_and_pages.csv"
df_duplicates.to_csv(output_file, sep="\t", index=False)

# if duplicate, only keep first hash ------------------------

seen = set() # unordered and unique
unique_chunks = []

for chunk in chunks:
    title = chunk["title"]
    if title not in seen:
        seen.add(title)
        unique_chunks.append(chunk)

# create a new file with unique_chunks ------------------------

path = "data/processed/defensewiki.ibj.org"

# JSON Lines (one dict per line)
with open(f"{path}/unique_chunks.jsonl", "w", encoding="utf-8") as jsonl_file:
    for chunk in unique_chunks:
        jsonl_file.write(json.dumps(chunk) + "\n")

# JSON (single array of dicts)
with open(f"{path}/unique_chunks.json", "w", encoding="utf-8") as json_file:
    json.dump(unique_chunks, json_file, ensure_ascii=False, indent=2)


# add country (and these changes) to the collection -----------------------------------
# In ChromaDB, embeddings and metadata are separate
# you don’t have to re-embed your text just to update or add metadata


client = chromadb.PersistentClient(path=path_chromadb)
collection = client.get_or_create_collection(name=collection_name)

# Group chunks by title
title_to_chunk = defaultdict(list)
for chunk in chunks:
    title_to_chunk[chunk["title"]].append(chunk)

unique_chunks = [chunks[0] for chunks in title_to_chunk.values()]

cleaned_chunks = []
for chunk in unique_chunks:
    country = chunk["metadata"].get("country", "Unknown")
    chunk["metadata"]["country"] = str(country) if country is not "" else "Unknown"
    cleaned_chunks.append(chunk)

collection.upsert(
    ids=[chunk["title"] for chunk in unique_chunks],
    documents=[chunk["content"] for chunk in cleaned_chunks],
    metadatas=[{"country": chunk["metadata"]["country"]} for chunk in cleaned_chunks],
)

valid_chunks = [
    chunk
    for chunk in cleaned_chunks
    if isinstance(chunk["content"], str) and chunk["content"].strip() != ""
]
len(valid_chunks)
len(cleaned_chunks)


# # Get all the IDs from the collection
# documents = collection.get()
# existing_ids = [doc["id"] for doc in documents["documents"]]
# len(np.unique(documents['ids'])) == len(documents['ids'])
