import json
from keypoint_evaluation import KeypointEvaluation

# Load the list
with open("data/completeness/keypoints.json", "r") as f:
    data = json.load(f)
    list_of_instances = [KeypointEvaluation.from_dict(d) for d in data]

    # Build a dictionary for fast lookup (best if you do this often) O(1) more efficient
    lookup = {obj.custom_id: obj for obj in list_of_instances}

# Process the batch results
with open("batch_results.jsonl", "r", encoding="utf-8") as results_file:
    for line in results_file:
        result = json.loads(line)
        custom_id = result["custom_id"]
        answer = result["response"]["choices"][0]["message"]["content"]

        # extract the right instance:
        found_evalutation = lookup.get(custom_id)
        if found_evalutation:
            print("Found:", found_evalutation)
            found_evalutation.save_evaluation(answer)
        else:
            print(f"problem with id: {custom_id}")
