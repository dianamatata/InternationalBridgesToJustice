import os
import json
import numpy as np
from tqdm import tqdm
from src.internationalbridgestojustice.get_claims import ClaimExtractor
from src.internationalbridgestojustice.config import Paths
from src.internationalbridgestojustice.file_manager import (
    load_jsonl_and_convert_to_list_of_dict,
)

model_name = "gpt-4o-mini"
cache_dir = "./data/cache"

data = load_jsonl_and_convert_to_list_of_dict(Paths.PATH_JSONL_FILE_DEFENSEWIKI_CHUNKS)
country_list = ["Burundi"]
data_country = [d for d in data if "Burundi" == d["metadata"]["country"]]

links_list_to_extract = []
for item in data:
    title = item["metadata"]["country"]
    if any(country in title for country in country_list):
        links_list_to_extract.append(item["metadata"]["link"])

links_list_to_extract = np.unique(links_list_to_extract)
print(links_list_to_extract)

claim_extractor = ClaimExtractor(
    model_name=model_name,
    prompt_file=Paths.PATH_FILE_PROMPT_CLAIM_EXTRACTION,
    cache_dir=cache_dir,
)

# extract a page -------------------------------------
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
                claim_extractor.scan_text_for_claims(response)
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
            jsonl_file_extracted_claims = os.path.join(
                Paths.PATH_FOLDER_CLAIM_EXTRACTION, filename
            )  # Specify your output directory
            with open(
                jsonl_file_extracted_claims, "a"
            ) as jsonl_file:  # a appends, w overwrites
                jsonl_file.write(json.dumps(output_dict) + "\n")
        print(f"extracted claims are saved at {Paths.PATH_JSONL_FILE_EXTRACTED_CLAIMS}")


# extract a country ----------------------------------
country_list = ["India"]
for dict_item in tqdm(data):
    title = dict_item["metadata"]["title"]
    if any(country in title for country in country_list):
        print(title)
        response = dict_item["content"]
        prompt_source = dict_item["title"]
        print(prompt_source)
        snippet_lst, claim_list, all_claims, prompt_tok_cnt, response_tok_cnt = (
            claim_extractor.scan_text_for_claims(response)
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
        jsonl_file_extracted_claims = os.path.join(
            Paths.PATH_FOLDER_CLAIM_EXTRACTION, filename
        )  # Specify your output directory
        with open(
            jsonl_file_extracted_claims, "a"
        ) as jsonl_file:  # a appends, w overwrites
            jsonl_file.write(json.dumps(output_dict) + "\n")
print(f"extracted claims are saved at {Paths.PATH_JSONL_FILE_EXTRACTED_CLAIMS}")
