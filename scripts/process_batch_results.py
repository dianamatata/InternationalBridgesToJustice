import json
from scripts.country_page_review.keypoint_evaluation import KeypointEvaluation

file_batch_input = "data/interim/batch_input_translation.jsonl"
file_batch_results = "data/interim/batch_results_translation.jsonl"
# Load the list
with open(file_batch_input, "r") as input_file:
    file_batch_input_data = [json.loads(line) for line in input_file]

    for line in input_file:
        input_data = json.loads(line)
        # TODO load all not just last instance

    list_of_instances = [KeypointEvaluation.from_dict(d) for d in data]
    # Build a dictionary for fast lookup (best if you do this often) O(1) more efficient
    lookup = {obj.custom_id: obj for obj in list_of_instances}

# Process the batch results
with open(file_batch_results, "r", encoding="utf-8") as results_file:
    for line in results_file:
        result = json.loads(line)
        custom_id = result["custom_id"]
        print(custom_id)
        answer = result["response"]["body"]["choices"][0]["message"]["content"]
        print(answer)
        # extract the right instance:
        found_evaluation = lookup.get(custom_id)
        if found_evaluation:
            print("Found:", found_evaluation)
            found_evaluation.save_evaluation(answer)
        else:
            print(f"problem with id: {custom_id}")

result["response"]["body"]["choices"][0]["message"]["content"]
