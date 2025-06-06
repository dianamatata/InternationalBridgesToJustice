import json
from veriscore.search_API import SearchAPI  # Use the full package name

fetch_search = SearchAPI()
first_line["all_claim_lst"]
claim_snippets = fetch_search.get_snippets(first_line["all_claim_lst"])

claim1 = first_line["all_claim_lst"][0]
snippets1 = first_line["claim_verification_result"][0]
claim_search_results = first_line["claim_search_results"]


test_input_file = "../../test_veriscore/data_sample.jsonl"

with open(test_input_file, "r") as f:
    first_line = json.loads(f.readline())
    print(first_line.keys())
