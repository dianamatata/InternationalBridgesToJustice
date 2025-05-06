import json

# Functions --------------------------------
def build_batch_request(custom_id: str, system_prompt: str, user_prompt: str, temperature: float = 0.1):
    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions", #  this is what tells OpenAI to use client.chat.completions.create
        "body": {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": 1000
        }
    }


# Main --------------------------------
##  GET CHUNKS TO TRANSLATE --------------------------------

system_prompt = "You are a translator that preserves markdown formatting and the references/citations/sources."

with open("data/processed/defensewiki.ibj.org/unique_chunks.json", "r", encoding="utf-8") as json_file:
    chunks = json.load(json_file)

filtered_chunks = [c for c in chunks if c['metadata']['language'] != 'en']

links_list_to_extract = ['https://defensewiki.ibj.org/index.php?title=Burundi',
                         'https://defensewiki.ibj.org/index.php?title=Burundi/es',
                         'https://defensewiki.ibj.org/index.php?title=Burundi/fr']

filtered_chunks_2 = [c for c in filtered_chunks if c['metadata']['link'] in links_list_to_extract]

len(filtered_chunks_2)  # 19 entries for Burundi fr and es

##  Create batch file --------------------------------

with open("data/interim/batch_input_translation.jsonl", "a", encoding="utf-8") as outfile:
    for i, chunk in enumerate(filtered_chunks_2):  # chunks is your list of markdown dicts
        print(chunk['title'])
        prompt_text = f"Translate the following Markdown file to English, keeping the formatting:\n\n{chunk['content']} and not translating the text in the sources and references (articles, links,...)"
        request = build_batch_request(
            custom_id=f"translation {chunk['title']}",
            system_prompt=system_prompt,
            user_prompt=prompt_text,
        )
        outfile.write(json.dumps(request) + "\n")

##  submit to openAI --------------------------------
import openai

client = openai.OpenAI()

# Upload file
file = client.files.create(
    file=open("data/interim/batch_input_translation.jsonl", "rb"),
    purpose="batch"
)

# Create batch job
batch = client.batches.create(
    input_file_id=file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h"  # Or "1h" depending on plan
)

print("Batch job submitted:", batch.id)
# Batch job submitted: batch_6818c363af4c8190892dac4d68abbd84

##  retrieve results --------------------------------


batch = client.batches.retrieve("batch_6818c363af4c8190892dac4d68abbd84")
print("Status:", batch.status)
result = client.batches.retrieve(batch_id="batch_6818c363af4c8190892dac4d68abbd84")
with open("data/interim/batch_results_translation.jsonl", "w", encoding="utf-8") as f:
    f.write(result)


# TODO: create pipeline to do this for all our BURUNDI chunks
# Do we want the original content to be saved in the chunk?
# chunk['untranslated_content'] = chunk['content']
# chunk['content'] = translate_to_english(chunk['content'])
# TODO check this works and do this for all chunks

