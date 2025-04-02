import os
import json
from tqdm import tqdm  # make your loops show a smart progress meter
import sys

sys.path.append(
    "/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/VeriScore-main/veriscore"
)
from veriscore.claim_extractor import ClaimExtractor

os.environ["OPENAI_API_KEY_PERSONAL"] = (
    "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"
)


# initialize objects

input_path = "/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/data/processed/defensewiki.ibj.org"
input_file_name = "chunks"
input_file = f"{input_path}/{input_file_name}.jsonl"
output_dir = "./test_veriscore/output"
output_file = f"{output_dir}/claims_{input_file_name}.jsonl"

data_dir = "./test_veriscore"
model_name = "gpt-4o-mini"
use_external_model = "store_true"
cache_dir = "./data/cache"

# Read JSONL file line by line
with open(input_file, "r", encoding="utf-8") as jsonl_file:
    data = [
        json.loads(line) for line in jsonl_file
    ]  # Convert each line to a dictionary

# Extract all "content" values into a list
data_title_list = [entry["title"] for entry in data]
for title in data_title_list[5:15]:
    print(title)

claim_extractor = ClaimExtractor(
    model_name=model_name, cache_dir=cache_dir, use_external_model=False
)

with open(output_file, "a") as f:  # a appends, w overwrites
    for dict_item in tqdm(data[15:52]):  # 5:52
        print(dict_item["title"])
        response = dict_item["content"]
        prompt_source = dict_item["title"]
        print(prompt_source)
        question = ""
        snippet_lst, claim_list, all_claims, prompt_tok_cnt, response_tok_cnt = (
            claim_extractor.non_qa_scanner_extractor(response)
        )

        output_dict = {
            "question": question.strip(),
            "prompt_source": prompt_source,
            "response": response.strip(),
            "prompt_tok_cnt": prompt_tok_cnt,
            "response_tok_cnt": response_tok_cnt,
            "model": model_name,
            "abstained": False,  # "abstained": False, "abstained": True
            "claim_list": claim_list,
            "all_claims": all_claims,
        }
        f.write(json.dumps(output_dict) + "\n")
print(f"extracted claims are saved at {output_file}")


# read claims
with open(f"{output_file}", "r", encoding="utf-8") as jsonl_file:
    data_out = [
        json.loads(line) for line in jsonl_file
    ]  # Convert each line to a dictionary
# len(data_out) 47: from 5 to 52
# data_out[0]['claim_list']
# data_out[0]['all_claims']

# save in json for easy reading
with open("./test_veriscore/output/claims_chunks.json", "w", encoding="utf-8") as file:
    json.dump(data_out, file, indent=4)  # Save JSON content


# Open the output file where you want to save the text
with open(
    "./test_veriscore/output/output_responses.txt", "w", encoding="utf-8"
) as response_file, open(
    "./test_veriscore/output/output_all_claims.txt", "w", encoding="utf-8"
) as claims_file:
    for i in range(15):  # Iterate over the first 15 entries
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
    "Responses saved to 'output_responses.txt' and claims saved to 'output_all_claims.txt'."
)

# dict_keys(['prompt_source', 'response', 'prompt_tok_cnt', 'response_tok_cnt', 'model', 'abstained', 'claim_list', 'all_claim_lst', 'claim_search_results', 'claim_verification_result'])
