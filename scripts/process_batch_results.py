import json
from keypoint_evaluation import KeypointEvaluation
from src.config import path_json_file_completeness_keypoints

file_batch_results = "data/interim/batch_results.jsonl"
# Load the list
with open(path_json_file_completeness_keypoints, "r") as f:
    data = json.load(f)
    list_of_instances = [KeypointEvaluation.from_dict(d) for d in data]

    # Build a dictionary for fast lookup (best if you do this often) O(1) more efficient
    lookup = {obj.custom_id: obj for obj in list_of_instances}

# Process the batch results
with open(file_batch_results, "r", encoding="utf-8") as results_file:
    for line in results_file:
        result = json.loads(line)
        custom_id = result["custom_id"]
        answer = result["response"]["choices"][0]["message"]["content"]

        # extract the right instance:
        found_evaluation = lookup.get(custom_id)
        if found_evaluation:
            print("Found:", found_evaluation)
            found_evaluation.save_evaluation(answer)
        else:
            print(f"problem with id: {custom_id}")
