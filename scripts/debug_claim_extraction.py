# from extract claims.py

# IMPORT ----------------------

# import spacy
# spacy_nlp = spacy.load("en_core_web_sm")
import re
import importlib
import sys
sys.path.append("VeriScore-main")  # NOT until 'veriscore', only up to the parent folder
import veriscore.claim_extractor as claim_extractor # Import the module
importlib.reload(claim_extractor) # Reload the module
ClaimExtractor = claim_extractor.ClaimExtractor # Now access your class

# FUNCTIONS ----------------------
def clean_markdown_text(text: str)-> str:

    text = text.strip()

    # 1. Remove all [[...]](#cite_note-...) patterns
    text = re.sub(r"\[\[.*?\]\]\(#.*?\)", "", text)

    # 2. Remove double newlines
    text = text.replace('\n\n', '\n')

    # 3. Remove bold markers **
    text = text.replace('**', '')

    # 4. (Optional) Remove redundant spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# MAIN ----------------------
# Get chunk to debug ---------------------
country_list = ["Burundi"]
chunk = chunks_to_extract[3]
# 'title': '8d307a0193139e5dd840b9e3972f91ef4b9468b478f5dd8e7c9c92ea9c1c8bdc'
content = chunk["content"]
sentences = content
sentences_cleaned = clean_markdown_text(content)
print(sentences_cleaned)
# sentences2 = get_sentence(content)
# now we want         sentences = response.split(".")
# sentences[2].strip()


model_name = "gpt-4o-mini"
cache_dir = "../data/cache"
claim_extractor = ClaimExtractor(
    model_name=model_name, cache_dir=cache_dir, use_external_model=False
)

response = chunk["content"]
prompt_source = chunk["title"]
print(prompt_source)
title = chunk["metadata"]["title"]
snippet_lst, claim_list, all_claims, prompt_tok_cnt, response_tok_cnt = (
    claim_extractor.custom_claim_extractor(sentences_cleaned)  # here
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

import json
output_dir = "../data/extracted_claims"
file_title = "test"
with open(f"{output_dir}/{file_title}.json", "w", encoding="utf-8") as file:
    json.dump(output_dict, file, indent=4)  # Save JSON content