# We want to get all the country names and links from url which is the "country pages" section
# The links we want are in this structure:

# <h2><span class="mw-headline" id="Country_Pages">Country Pages</span></h2>
# <div style="float: left; width: 33%">

import requests  # get url info
from bs4 import BeautifulSoup
import json
import numpy as np

# 1 - Get country names (and optional aliases) from pycountry
import pycountry
country_names1 = [country.name for country in pycountry.countries]
len(country_names1) # 249

# 2 - Get country names from the Defense Wiki Country pages
file_country_names = "/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/data/interim/country_names_1.txt"
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
    "Malasia": "Malaysia"
}

substring_to_country = {
    "American_": "United States",
    "American ": "United States",
    "Chinese": "China",
    "Canadian": "Canada",
    "Cairo": "Egypt",
}

# if title contains American_... > "United States", Chinese... > China

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
entry_to_check = [d for d in defense_wiki_all if "Urugay" in d['title']]
check1 = [[e['title'], e['country']] for e in entry_to_check]
for c in check1:
    print(c)

d['country'] = next((country for key, country in substring_to_country.items() if key in d['title']), None)







with open(f"data/interim/no_countries.txt", "w", encoding="utf-8") as file:
    for c in check1:
        file.write(f"{c}\n")


country = 'Congo, Democratic Republic of the'
a = 'Congo,_Democratic_Republic_of_the'
cleaned_title = a.replace('_', ' ').strip()
country.lower() in cleaned_title.lower()

but  'Congo, Republic of the' in country_names





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
    print(f"Total number of chunks: {len(chunks)}")

# chunk = chunks[21]

for chunk in chunks:
    if chunk['metadata']['title'].replace('_', ' ') in country_names:
        chunk['metadata']['country'] = chunk['metadata']['title'].replace('_', ' ')
    else:
        chunk['metadata']['country'] = None

with open("data/processed/defensewiki.ibj.org/chunks_1.json", "w", encoding="utf-8") as file:
    json.dump(chunks,file, indent=4)  # Save JSON content

with open("data/processed/defensewiki.ibj.org/chunks_1.jsonl", "w", encoding="utf-8") as jsonl_file:
    for record in chunks:
        jsonl_file.write(json.dumps(record) + "\n")

# In ChromaDB, embeddings and metadata are separate
# you don’t have to re-embed your text just to update or add metadata
import chromadb
CHROMA_PATH = "data/chroma_db"
client = chromadb.PersistentClient(
        path=CHROMA_PATH)
collection = client.get_or_create_collection(name="legal_collection")

collection.upsert(
    ids=[chunk["title"] for chunk in chunks],
    documents=None,
    metadatas=[{"country": chunk["metadata"]["country"]} for chunk in chunks]
)

# Get all the IDs from the collection
documents = collection.get()
existing_ids = [doc["id"] for doc in documents["documents"]]
len(np.unique(documents['ids'])) == len(documents['ids'])


titles = [chunk["title"] for chunk in chunks]
len(titles)  == len(np.unique(titles))

from collections import Counter

duplicates = [item for item, count in Counter(titles).items() if count > 1]
target_title = "7d6aaa2ea99efdc4a1e112e4ec25c5df4200472f73796f09f24592fc58e030f3"
target_title = 'd8a727cf0fd04fe135157f5471f144954d633653037a153c41161a22ce9d21cc'
matching_chunks = [chunk for chunk in chunks if chunk["title"] == target_title]
print(matching_chunks)
# TODO: solve problem page 'Thailand-es' and Tailandia, which are the same.
#


#
# for d in defense_wiki_all:
#     if d['title'].replace('_', ' ') in country_names:
#         d['country'] = d['title'].replace('_', ' ')
#     else:
#         d['country'] = None


print("Duplicate titles:", duplicates)
# Check for duplicates, why do we have duplicates?

len(existing_ids)  # Total number of existing IDs
len(np.unique(existing_ids))  # Number of unique IDs

import numpy as np
a = [chunk["title"] for chunk in chunks]
len(a)
len(np.unique(a)) # 111
# filter on country first



# check what is the country for Antigua and Barbuda, check missing countries



# chunks = load_legal_chunks()    # Get chunks

# update metadata with the country name
# resave the chunks

# 6 - Run RAG with selecting the chunks with the country name first

# 7- Run over 1 full country


