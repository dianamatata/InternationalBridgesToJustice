import os
import json
from tqdm import tqdm  # make your loops show a smart progress meter
import sys
from veriscore.claim_extractor import ClaimExtractor
import numpy as np
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
openai_api_key = os.environ.get("OPENAI_API_KEY")

sys.path.append("VeriScore-main/veriscore")

# initialize objects
input_path = "../data/processed/defensewiki.ibj.org"
input_file_name = "chunks_1"
input_file = f"{input_path}/{input_file_name}.jsonl"
output_dir = "../data/extracted_claims"
output_file = f"{output_dir}/claims_{input_file_name}.jsonl"
model_name = "gpt-4o-mini"
use_external_model = "store_true"
cache_dir = "../data/cache"

# Read JSONL file line by line
with open(input_file, "r", encoding="utf-8") as jsonl_file:
    data = [
        json.loads(line) for line in jsonl_file
    ]  # Convert each line to a dictionary

# # Extract all "content" values into a list, now these are hashes
# title_list=[]
# for item in data:
#     title_list.append(item['metadata']['title'])
# np.unique(title_list[6:54])

# extract 1 or many countries and all the links
links_list_to_extract = []
country_list = ["Burundi"]  # 'Singapore', 'Burundi', 'India'

for item in data:
    title = item["metadata"]["country"]
    if any(country in title for country in country_list):
        links_list_to_extract.append(item["metadata"]["link"])

links_list_to_extract = np.unique(links_list_to_extract)
print(links_list_to_extract)

claim_extractor = ClaimExtractor(
    model_name=model_name, cache_dir=cache_dir, use_external_model=False
)

# extract a page -------------------------------------
# debug
# chunk = chunks_to_extract[3]
page = links_list_to_extract[0]
chunks_to_extract = []
for dict_item in tqdm(data):
    if dict_item["metadata"]["link"] == page:
        chunks_to_extract.append(dict_item)
        for chunk in chunks_to_extract:
            response = chunk["content"]
            prompt_source = chunk["title"]
            print(prompt_source)
            title = chunk["metadata"]["title"]
            snippet_lst, claim_list, all_claims, prompt_tok_cnt, response_tok_cnt = (
                claim_extractor.non_qa_scanner_extractor(response)
            )
            output_dict = {
                "prompt_source": prompt_source,
                "response": response.strip(),
                "prompt_tok_cnt": prompt_tok_cnt,
                "response_tok_cnt": response_tok_cnt,
                "model": model_name,
                "abstained": False,  # "abstained": False, "abstained": True
                "claim_list": claim_list,
                "all_claims": all_claims,
            }
            filename = (
                f"{title.replace(' ', '_').replace('/', '_').replace(':', '_')}.jsonl"
            )
            output_file = os.path.join(
                output_dir, filename
            )  # Specify your output directory
            with open(output_file, "a") as jsonl_file:  # a appends, w overwrites
                jsonl_file.write(json.dumps(output_dict) + "\n")
        print(f"extracted claims are saved at {output_file}")


# extract a country ----------------------------------
country_list = ["India"]
for dict_item in tqdm(data):  # data from 6 to 54 for Singapore
    title = dict_item["metadata"]["title"]
    if any(country in title for country in country_list):
        print(title)
        response = dict_item["content"]
        prompt_source = dict_item["title"]
        print(prompt_source)
        snippet_lst, claim_list, all_claims, prompt_tok_cnt, response_tok_cnt = (
            claim_extractor.non_qa_scanner_extractor(response)
        )
        output_dict = {
            "prompt_source": prompt_source,
            "response": response.strip(),
            "prompt_tok_cnt": prompt_tok_cnt,
            "response_tok_cnt": response_tok_cnt,
            "model": model_name,
            "abstained": False,  # "abstained": False, "abstained": True
            "claim_list": claim_list,
            "all_claims": all_claims,
        }

        filename = (
            f"{title.replace(' ', '_').replace('/', '_').replace(':', '_')}.jsonl"
        )
        output_file = os.path.join(
            output_dir, filename
        )  # Specify your output directory
        with open(output_file, "a") as jsonl_file:  # a appends, w overwrites
            jsonl_file.write(json.dumps(output_dict) + "\n")
print(f"extracted claims are saved at {output_file}")


# STOP HERE
# TODO: change paths and check
# TODO
filename = "Burundi-fr.jsonl"

filename = "Burundi.jsonl"
file_title = filename.replace(".jsonl", "")
output_file = os.path.join(output_dir, filename)  # Specify your output directory

# read claims in jsonl  # Convert each line to a dictionary
with open(f"{output_file}", "r", encoding="utf-8") as jsonl_file:
    data_out = [json.loads(line) for line in jsonl_file]

# save in json for easy reading
with open(f"{output_dir}/{file_title}.json", "w", encoding="utf-8") as file:
    json.dump(data_out, file, indent=4)  # Save JSON content


# Open the output file where you want to save the text
with open(
    f"{output_dir}/{file_title}_chunk_text.txt", "w", encoding="utf-8"
) as response_file, open(
    f"{output_dir}/{file_title}_all_claims.txt", "w", encoding="utf-8"
) as claims_file:
    for i in range(len(data_out)):  # Iterate over the first 15 entries
        if i < len(data_out):  # Ensure the index is within the available range

            # Get and write the response
            response_file.write(f"Entry {i + 1}:\n")
            response = data_out[i]["response"].strip()
            response_file.write(
                response + "\n\n"
            )  # Write the response followed by two newlines

            # Get and write all_claims
            all_claims = data_out[i]["all_claims"]
            claims_file.write(f"Entry {i + 1}:\n")
            claims_file.write(
                "\n".join(all_claims) + "\n\n"
            )  # Write each claim on a new line, separate entries with double newlines

print(
    f"Responses saved to {output_dir}/{file_title}_chunk_text.txt and claims saved to {output_dir}/{file_title}_all_claims.txt."
)

# dict_keys(['prompt_source', 'response', 'prompt_tok_cnt', 'response_tok_cnt', 'model', 'abstained', 'claim_list', 'all_claim_lst', 'claim_search_results', 'claim_verification_result'])
# len(data_out)
# data_out[0]['claim_list'] # data_out[0].keys()
