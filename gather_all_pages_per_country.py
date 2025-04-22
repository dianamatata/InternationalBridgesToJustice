# extract all pages linked to one country

import json
import numpy as np
from tqdm import tqdm


# FUNCTIONS ------------------------------------------------------------

def get_data(input_file):
    with open(input_file, "r", encoding="utf-8") as jsonl_file:
        data = [
            json.loads(line) for line in jsonl_file
        ]
    return data


def get_all_links_related_to_country(data, country_list)
    links_list_to_extract = []
    for item in data:
        title = item['metadata']['country']
        if any(country in title for country in country_list):
            links_list_to_extract.append(item['metadata']["link"])

    links_list_to_extract = np.unique(links_list_to_extract)
    print(links_list_to_extract)
    return links_list_to_extract


# MAIN ------------------------------------------------------------

input_path = "data/processed/defensewiki.ibj.org"
input_file = f"{input_path}/chunks_1.jsonl"
country_list = ["Burundi"] # 'Singapore', 'Burundi', 'India'

# 1 get all links for one country

data = get_data(input_file)
links_list_to_extract = get_all_links_related_to_country(data, country_list)

# for now need manual refinement of links that we accept
links_list_to_extract = ['https://defensewiki.ibj.org/index.php?title=Burundi',
                         'https://defensewiki.ibj.org/index.php?title=Burundi/es',
                         'https://defensewiki.ibj.org/index.php?title=Burundi/fr']

# 2 translate all pages in English

# page = links_list_to_extract[0]

chunks_to_extract = []
for dict_item in tqdm(data):
    if dict_item['metadata']["link"] in links_list_to_extract:
        chunks_to_extract.append(dict_item)
        # take the spanish page 'https://defensewiki.ibj.org/index.php?title=Burundi/es', translate in english
        # take the french page 'https://defensewiki.ibj.org/index.php?title=Burundi/fr', translate in english


# 3 summarize per chapter
# 4 create new file country
