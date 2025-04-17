# We want to add as metadata the country in all the defense wiki pages.
# Get country names, some are written in different languages, so creating title_to_country dictionary
# Update also chunks and collection of chromadb
# if title contains American_... > "United States", Chinese... > China
# some countries have duplicated pages, we have hashes that are not unique


import json
import numpy as np

# 1 - Get country names (and optional aliases) from pycountry
import pycountry
country_names1 = [country.name for country in pycountry.countries]
len(country_names1) # 249

# 2 - Get country names from the Defense Wiki Country pages
file_country_names = "data/interim/country_names_1.txt"
with open(f"{file_country_names}", "r", encoding="utf-8") as f:
    country_names = f.read().splitlines()
    len(country_names) # 204

# 3. Update the defensewiki to add the country name
input_data = "data/interim/defensewiki_all.json"
with open(f"{input_data}l", "r", encoding="utf-8") as jsonl_file:
    defense_wiki_all = [
        json.loads(line) for line in jsonl_file
    ]  # Convert each line to a dictionary
    keys = defense_wiki_all[1].keys()


title_to_country = {
    "Tunez": "Tunisia",
    "Suiza": "Switzerland",
    "Singapur": "Singapore",
    "Egipto": "Egypt",
    "Ruanda": "Rwanda",
    "Brasil": "Brazil",
    "Camboya": "Cambodia",
    "Inglaterra_y_Gales": "England and Wales",
    "South_Korea-es": "South Korea",
    "Canadian_Charter_of_Rights_and_Freedoms": "Canada",
    "Azerbaiyan": "Azerbaijan",
    "Alemania": "Germany",
    "Camerun": "Cameroon",
    "Suazilandia": "Swaziland",
    "Filipinas": "Philippines",
    "Francia": "France",
    "Japon": "Japan",
    "Zimbabue": "Zimbabwe",
    "Tailandia": "Thailand",
    "Urugay": "Uruguay",
    "Sudafrica": "South Africa",
    "Libia": "Libya",
    "Maurice-fr": "Mauritius",
    "South_Korea": "South Korea",
    "United_State_Supreme_Court": "United States",
    "Cote_dIvoire": "Ivory Coast",
    "Lao's_People_Democratic_Republic": "Laos",
    "Chinese-English_Legal_Lexicon": "China",
    "Chinese_Law_Primer": "China",
    "Cairo_Declaration_on_Human_Rights_in_Islam": "Egypt",
    "American_Bar_Association_Model_Rules_of_Professional_Conduct_-_Rule_3.1._Meritorious_Claims_and_Contentions": "United States",
    "Republique_du_Congo_(Congo-Brazzaville)": "Congo, Republic of the",
    "Democratic_Republic_of_Congo-fr": "Congo, Democratic Republic of the",
    "Democratic_Republic_of_Congo-es": "Congo, Democratic Republic of the",
    "Congo-brazzaville": "Congo, Republic of the",
    "Congo": "Congo, Democratic Republic of the", # not sure for this one
    "Inglaterra": "England and Wales",
    "Japon": "Japan",
    "Malasia": "Malaysia",
    "Kenia": "Kenya",
    "Francais": "France",
}

substring_to_country = {
    "American_": "United States",
    "American ": "United States",
    "Chinese": "China",
    "Canadian": "Canada",
    "Cairo": "Egypt",
}


for d in defense_wiki_all:
    # Check if any country name is in the title, in this direction because 'Thailand-es' in 'Thailand'
    cleaned_title = d['title'].replace('_', ' ').strip().lower()

    matching_country = next((country for country in country_names if country.lower().strip() in cleaned_title), None)
    if matching_country:
        d['country'] = matching_country
    else:
        # 2. Try exact title correction dictionary
        corrected = title_to_country.get(d['title'], None)
        if corrected:
            d['country'] = corrected
        else:
            # 3. Try substring-based matching
            d['country'] = next(
                (country for key, country in substring_to_country.items() if key in d['title']),
                None
            )

# check all the country None
check1 = [[e['title'], e['country']] for e in defense_wiki_all if e['country'] is None]
for c in check1:
    print(c)


# 4. check problems
# with Urugay
entry_to_check = [d for d in defense_wiki_all if 'Congo,_Democratic_Republic_of_the' in d['title']]
check1 = [[e['title'], e['country']] for e in entry_to_check]
for c in check1:
    print(c)

# save pages without countries
with open(f"data/interim/no_countries.txt", "w", encoding="utf-8") as file:
    for c in check1:
        file.write(f"{c}\n")

# save defense wiki with countries
with open("data/interim/defensewiki_all_1.json", "w", encoding="utf-8") as file:
    json.dump(defense_wiki_all,file, indent=4)  # Save JSON content

with open("data/interim/defensewiki_all_1.jsonl", "w", encoding="utf-8") as jsonl_file:
    for record in defense_wiki_all:
        jsonl_file.write(json.dumps(record) + "\n")

# 2 update the chunks with country names
# load defense wiki
with (open("data/interim/defensewiki_all_1.json", "r", encoding="utf-8") as json_file):
    defense_wiki_all = json.load(json_file)


# load the chunks
path1 = "data/processed/defensewiki.ibj.org/chunks.jsonl"
chunks = []
for path in [path1]:
    with open(f"{path}", "r", encoding="utf-8") as jsonl_file:
        lines = jsonl_file.readlines()  # Read all lines once
        print(f"Number of lines in the jsonl file {path}: {len(lines)}")
        for line in lines:
            chunks.append(json.loads(line))
        for chunk in chunks:
            # get original page, get title and country and update!
            chunk['metadata']['country'] = [d['country'] for d in defense_wiki_all if d['title'] == chunk['metadata']['title']]
    print(f"Total number of chunks: {len(chunks)}")

with open("data/processed/defensewiki.ibj.org/chunks_1.json", "w", encoding="utf-8") as file:
    json.dump(chunks, file, indent=4)  # Save JSON content

with open("data/processed/defensewiki.ibj.org/chunks_1.jsonl", "w", encoding="utf-8") as jsonl_file:
    for record in chunks:
        jsonl_file.write(json.dumps(record) + "\n")


# change embeddings and remove duplicates ----------------------------------------
import json
from collections import Counter
import pandas as pd
import chromadb
import numpy as np


input_data = "data/processed/defensewiki.ibj.org/chunks_1.json"
with open(input_data, "r", encoding="utf-8") as json_file:
    chunks = json.load(json_file)

# get duplicated hashes
titles = [chunk["title"] for chunk in chunks]
len(titles)  == len(np.unique(titles))
# len(np.unique(titles)) 10605
# len(titles) 10941
duplicated_hash = [item for item, count in Counter(titles).items() if count > 1]
# get all duplicated chunks
duplicated_chunks = [d for d in chunks if d['title'] in duplicated_hash]
len(duplicated_chunks)
# extract pages names
duplicated_pages_data = [[d['title'], d['metadata']['title'], d['metadata']['link'],d['metadata']['title_bis']] for d in duplicated_chunks]
df_duplicates = pd.DataFrame(duplicated_pages_data, columns=['Hash Title', 'Page Title', 'Link', 'Title Bis'])

output_file = "data/interim/duplicated_hashes_and_pages.csv"
df_duplicates.to_csv(output_file, sep="\t", index=False)

# TODO: if duplicate, only keep first hash

# In ChromaDB, embeddings and metadata are separate
# you don’t have to re-embed your text just to update or add metadata


from collections import defaultdict
CHROMA_PATH = "data/chroma_db"
client = chromadb.PersistentClient(
        path=CHROMA_PATH)
collection = client.get_or_create_collection(name="legal_collection")

# Group chunks by title
title_to_chunk = defaultdict(list)
for chunk in chunks:
    title_to_chunk[chunk["title"]].append(chunk)

# Take only the first chunk per unique title
unique_chunks = [chunks[0] for chunks in title_to_chunk.values()]

# country None not accepted
cleaned_chunks = []
for chunk in unique_chunks:
    country = chunk["metadata"].get("country", "Unknown")
    # Ensure it's a string, not list or None
    chunk["metadata"]["country"] = str(country) if country is not None else "Unknown"
    cleaned_chunks.append(chunk)

len(cleaned_chunks)

collection.upsert(
    ids=[chunk["title"] for chunk in unique_chunks],
    documents=[chunk["content"] for chunk in cleaned_chunks],
    metadatas=[{"country": chunk["metadata"]["country"]} for chunk in cleaned_chunks]
)


# Error executing model: Unable to compute the prediction using a neural network model.
# It can be an invalid input data or broken/unsupported model (error code: -1).

# ✅ Option 1: Switch to CPU-based inference
# ✅ Option 2: Check for invalid content
valid_chunks = [chunk for chunk in cleaned_chunks if isinstance(chunk["content"], str) and chunk["content"].strip() != ""]
len(valid_chunks)
len(cleaned_chunks)


# # Get all the IDs from the collection
# documents = collection.get()
# existing_ids = [doc["id"] for doc in documents["documents"]]
# len(np.unique(documents['ids'])) == len(documents['ids'])