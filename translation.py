# in ibj_statistics.py we computed the number of words and tokens for the pages not in english
# that we need to translate
# total_input_tokens: 1857676
import json
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
openai_api_key = os.environ.get("OPENAI_API_KEY")
from openai import OpenAI

client = OpenAI()

# Functions ---------------------------------------------

def get_data(input_file):
    with open(input_file, "r", encoding="utf-8") as jsonl_file:
        data = [
            json.loads(line) for line in jsonl_file
        ]
    return data


def get_all_links_related_to_country(data, country_list):
    links_list_to_extract = []
    for item in data:
        title = item['metadata']['country']
        if any(country in title for country in country_list):
            links_list_to_extract.append(item['metadata']["link"])

    links_list_to_extract = np.unique(links_list_to_extract)
    print(links_list_to_extract)
    return links_list_to_extract

def translate_to_english(md_text):
    system_message = "You are a translator that preserves markdown formatting and the references/citations/sources."
    prompt_text = f"Translate the following Markdown file to English, keeping the formatting:\n\n{md_text} and not translating the text in the sources and references (articles, links,...)"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt_text}
        ],
        temperature=0.2,
        seed=1130,
    )
    translated = response.choices[0].message.content
    return translated


# Load the chunks --------------------------------

# with open("data/processed/defensewiki.ibj.org/unique_chunks.jsonl", "r", encoding="utf-8") as jsonl_file:
#     for line in jsonl_file:
#         chunks.append(json.loads(line))

with open("data/processed/defensewiki.ibj.org/unique_chunks.json", "r", encoding="utf-8") as json_file:
    chunks = json.load(json_file)

filtered_chunks = [c for c in chunks if c['metadata']['language'] != 'en']
len(filtered_chunks) # 3553

links_list_to_extract = ['https://defensewiki.ibj.org/index.php?title=Burundi',
                         'https://defensewiki.ibj.org/index.php?title=Burundi/es',
                         'https://defensewiki.ibj.org/index.php?title=Burundi/fr']

filtered_chunks_2 = [c for c in filtered_chunks if c['metadata']['link'] in links_list_to_extract]
seen_countries = set([chunk['metadata']['country'] for chunk in filtered_chunks_2])

[print(c['metadata']) for c in filtered_chunks_2]

#  filtered_chunks_2[0]['content'] we have 19 entries for Burundi fr and es

chunk = filtered_chunks_2[1]
md_text = chunk['content']
translated = translate_to_english(md_text)
print(translated)
print(md_text)


translation_file = open("data/interim/translation_file.txt", "a")
translation_file.write(f"Title: {chunk['title']}\n\n{chunk['metadata']}\n\nOriginal text:\n{md_text}\n\nTranslated text:\n{translated}\n\n")
translation_file.close()
# this works for a small subset

# TODO: create pipeline to do this for all our chunks
# Do we want the original content to be saved in the chunk? SHould we replace chunk['content']
# and create a category chunk['untranslated_content']
# Then create batches

