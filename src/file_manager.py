import json
import pandas as pd
from typing import Dict
import re

def get_data_from_jsonl_file(jsonl_input_file: str):
    with open(jsonl_input_file, "r", encoding="utf-8") as jsonl_file:
        data = [
            json.loads(line) for line in jsonl_file
        ]
    return data

def extract_info_from_defensewiki_and_create_dataframe(defensewiki_json_nocontent: Dict):
    """
    Load the data and extract info from the json file: language, view_count, and line + word count.

    :param defensewiki_json_nocontent:
    :return: defensewiki_summary_dataframe
    """

    data_list = []
    global language_counts
    if isinstance(defensewiki_json_nocontent, dict):
        for key, value_dict in defensewiki_json_nocontent.items():
            if isinstance(value_dict, dict):
                for key, value in value_dict.items():
                    if isinstance(value, dict):
                        if type(value["viewcount"]) is not str:
                            viewcount = float("nan")
                        else:
                            match = re.search(r"(\d[\d,]*)", value["viewcount"])
                            viewcount = (
                                int(match.group(1).replace(",", "")) if match else 0
                            )
                        data_list.append(
                            [
                                value["title"],
                                value["language"],
                                value["nbr_of_lines"],
                                value["nbr_of_words"],
                                viewcount,
                            ]
                        )  # to know it has been swapped nbr of lines and nbr of words

        # Create DataFrame
        defensewiki_summary_dataframe = pd.DataFrame(
            data_list,
            columns=["Title", "Language", "nbr_of_words", "nbr_of_lines", "Viewcount"],
        )
        defensewiki_summary_dataframe.set_index("Title", inplace=True)  # Set Title as index
        return defensewiki_summary_dataframe
