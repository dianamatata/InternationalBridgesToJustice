# script to add description to keypoints before calling completeness
import openai
import json
from src.internationalbridgestojustice.config import Paths
from src.internationalbridgestojustice.query_functions import get_completeness_keypoints
from src.internationalbridgestojustice.openai_utils import get_openai_response
import re
from pprint import pprint

client = openai.Client()


def extract_keypoint_from_file(completeness_checklist_filepath: str):
    completeness_keypoints = get_completeness_keypoints(
        completeness_checklist_filepath=completeness_checklist_filepath
    )

    keypoints_to_check = []
    levels = [""] * 5  # Allow up to 5 levels of nesting

    for point in completeness_keypoints:
        indent = len(point) - len(point.lstrip())
        level = indent // 3  # 3 spaces per indentation level
        levels[level] = point.strip()
        # Clear deeper levels
        for i in range(level + 1, len(levels)):
            levels[i] = ""

        # Only keep points that are not pure chapter headings (i.e., non-topmost)
        if level > 0:
            full_keypoint = ": ".join(filter(None, levels[: level + 1]))
            full_keypoint = re.sub(
                r":{2,}", ":", full_keypoint
            )  # removing all repeated colons (e.g., ::: or more) with a regex
            keypoints_to_check.append(full_keypoint)

    return keypoints_to_check


response_format_keypoints = {
    "type": "object",
    "name": "KeypointDescription",
    "description": "",
    "properties": {
        "Keypoint": {
            "type": "string",
            "description": "The original keypoint.",
        },
        "Description": {
            "type": "string",
            "description": "Sentence describing the keypoint clearly and precisely",
        },
    },
}


def generate_description(keypoint):
    system_prompt = (
        "You are an assistant helping to disambiguate and clarify keypoints used for legal document search."
        "Your job is to rewrite each keypoint as a more descriptive sentence that captures its intent clearly."
    )
    user_prompt = f"Keypoint: {keypoint}"

    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "KeypointDescription",
            "schema": response_format_keypoints,
        },
    }

    answer = get_openai_response(
        client=client,
        categorize_system_prompt=system_prompt,
        prompt=user_prompt,
        response_format=response_format,
        model="gpt-4o-mini",
        temperature=0.3,
    )
    return answer


# script to generate descriptive keypoints from a list of keypoints
keypoints_to_check = extract_keypoint_from_file(
    completeness_checklist_filepath=Paths.PATH_MD_FILE_COMPLETENESS_KEYPOINTS
)
results_keypoints_json_strs = [generate_description(kp) for kp in keypoints_to_check]
results_keypoints = [
    json.loads(s) for s in results_keypoints_json_strs
]  # Convert each JSON string into a Python dict
pprint(results_keypoints[1:3])

with open(
    Paths.PATH_JSON_FILE_DESCRIPTIVE_COMPLETENESS_KEYPOINTS, "w", encoding="utf-8"
) as f:
    json.dump(results_keypoints, f, indent=2, ensure_ascii=False)


# check result
with open(
    Paths.PATH_JSON_FILE_DESCRIPTIVE_COMPLETENESS_KEYPOINTS, "r", encoding="utf-8"
) as f:
    data_keypoints = json.load(f)
