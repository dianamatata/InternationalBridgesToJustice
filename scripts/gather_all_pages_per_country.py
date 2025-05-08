# extract all pages linked to one country

import json
from tqdm import tqdm

# openAI
# The API key is stored in an environment file (.env), added to .gitignore for security reasons.
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
openai_api_key = os.environ.get("OPENAI_API_KEY")
from openai import OpenAI

client = OpenAI()

from src.translation import get_data, get_all_links_related_to_country, translate_to_english

# FUNCTIONS ------------------------------------------------------------


# MAIN ------------------------------------------------------------

input_path = "../data/processed/defensewiki.ibj.org"
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
        translated = translate_to_english(md_text)
        # take the spanish page 'https://defensewiki.ibj.org/index.php?title=Burundi/es', translate in english
        # take the french page 'https://defensewiki.ibj.org/index.php?title=Burundi/fr', translate in english

        # once we translated the 2 pages. we have 3 versions of burundi.
        # merge them? what if document super long? we actually have chunks.
        # loop over keypoints, gather from each chunk the info, unify and then complete?
# 3 save to new file


# 3 summarize per chapter
# 4 create new file country






"""
# TODO check the duplicates
# chunks is a list of dict chunks[0]['metadata']['link']
link = "https://defensewiki.ibj.org/index.php?title=Democratic_Republic_of_Congo/fr" # 33 chunks, 5 copied
link = "https://defensewiki.ibj.org/index.php?title=Russia/es" # 62 chunks, 61 copied
link = "https://defensewiki.ibj.org/index.php?title=Legal_Aid_Systems_and_Supporting_NGOs_around_the_world" # 49, 17 copied
link = "https://defensewiki.ibj.org/index.php?title=Constitution_du_Burundi" #50c, 48 copied
link = "https://defensewiki.ibj.org/index.php?title=African_Charter_on_Human_and_Peoples%27_Rights" # 17, 13 copied
link = "https://defensewiki.ibj.org/index.php?title=Uruguay" # 8, 6 copied
link = "https://defensewiki.ibj.org/index.php?title=Singapur" # 8, 7 copied
"""

len(filtered_chunks)
# TODO. create a rule in which if the hash is duplicated, which version do we keep. from which website?


# Load defense wiki pages --------------------------------

with open(
        "../data/interim/defensewiki_all.json",
    "r",
) as f:
    link_tree_defensewiki = json.load(f)

value_dict = list(link_tree_defensewiki.items())[0][1]


value_dict = list(chunks.items())[0][1]



# TODO  tester sur quelques pages pour voir un peu le format de la traduction etc et
#  TODO après tu peux batcher le tout

webpage = "https://defensewiki.ibj.org/index.php?title=Democratic_Republic_of_Congo/fr"

# TODO: before translation, some pages have duplicates. so we should remove the duplicated names first

pages_to_forget = [
    "https://defensewiki.ibj.org/index.php?title=Russia",

]

filtered_dict = {k: v for k, v in value_dict.items() if v.get('link') == "https://defensewiki.ibj.org/index.php?title=Democratic_Republic_of_Congo/fr"}
len(filtered_dict["https://defensewiki.ibj.org/index.php?title=Democratic_Republic_of_Congo/fr"]) # 13 but we have only 5 chunks repeated

link = "https://defensewiki.ibj.org/index.php?title=Russia/es"
filtered_dict = {k: v for k, v in value_dict.items() if v.get('link') == link}
len(filtered_dict[link])
# 13 but we have only 5 chunks repeated


# check combien de hashes avec le lien "https://defensewiki.ibj.org/index.php?title=Congo-brazzaville"
