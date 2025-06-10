import json
import pandas as pd
from typing import Dict
import re
import hashlib  # get hash


def generate_hash(content: str):
    """Generate SHA-256 hash of the given content."""
    return hashlib.sha256(content.encode()).hexdigest()


def save_file(filename: str, content, file_type="json"):
    try:
        if file_type == "json":
            with open(filename, "w", encoding="utf-8") as json_file:
                json.dump(content, json_file, indent=4)
        elif file_type == "jsonl1":
            with open(filename, "w", encoding="utf-8") as jsonl_file:
                for record in content:
                    jsonl_file.write(json.dumps(record) + "\n")
        elif file_type == "jsonl":
            with open(filename, "w", encoding="utf-8") as jsonl_file:
                for record in content:
                    jsonl_file.write(json.dumps(content[record]) + "\n")
        else:
            with open(filename, "w", encoding="utf-8") as file:
                file.write(str(content))  # Convert to string to be safe

        print(f"File saved successfully: {filename}")

    except Exception as e:
        print(f"Error saving file {filename}: {e}")


def load_jsonl_and_convert_to_list_of_dict(
    input_data: str, encoding: str = "utf-8"
) -> list:
    with open(input_data, "r", encoding=encoding) as jsonl_file:
        data = [
            json.loads(line) for line in jsonl_file
        ]  # Convert each line to a dictionary
    return data


def load_json_file(file_path: str):
    with open(file_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data


def extract_info_from_defensewiki_and_create_dataframe(
    defensewiki_json_nocontent: Dict,
):
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
        defensewiki_summary_dataframe.set_index(
            "Title", inplace=True
        )  # Set Title as index
        return defensewiki_summary_dataframe


def get_country_names(country_names_filepath: str = "data/interim/country_names_1.txt"):
    with open(f"{country_names_filepath}", "r", encoding="utf-8") as f:
        country_names = f.read().splitlines()
        return country_names


def save_completeness_result(
    country: str,
    keypoint_to_check: str,
    wiki_content: Dict,
    database_content: Dict,
    answer: str,
    out_jsonfile: str,
    out_md_file: str,
):
    country_keypoint = {
        "country": country,
        "keypoint": keypoint_to_check,
        "wiki_content": {
            "ids": wiki_content.get("ids", [[]])[0],
            "title_bis": wiki_content.get("metadatas", [[]])[0],
            "distances": wiki_content.get("distances", [[]])[0],
        },
        "database_content": {
            "ids": database_content.get("ids", [[]])[0],
            "title_bis": database_content.get("metadatas", [[]])[0],
            "distances": database_content.get("distances", [[]])[0],
        },
        "answer": answer,
        "completeness_assessment": answer.split("**")[1],
    }

    # save the answer in a json file
    with open(out_jsonfile, "a", encoding="utf-8") as json_file:
        json.dump(country_keypoint, json_file, indent=4)

    # save the answer in an md file
    with open(out_md_file, "a", encoding="utf-8") as f:
        f.write(f"# {country}\n\n")
        f.write(f"## {keypoint_to_check}\n\n")
        f.write(answer)
        f.write("\n\n\n\n")


def load_legal_chunks(list_of_paths: list[str]):
    chunks = []
    for path in list_of_paths:
        with open(f"{path}", "r", encoding="utf-8") as jsonl_file:
            lines = jsonl_file.readlines()  # Read all lines once
            for line in lines:
                chunks.append(json.loads(line))
    return chunks


def extract_chunk_from_hash(hash_to_search: str, chunks):
    selected_chunk = next(
        (chunk for chunk in chunks if chunk["title"] == hash_to_search), None
    )
    return selected_chunk


def build_context_string_from_retrieve_documents(results: dict) -> str:
    """
    Build a context string from the retrieved documents.
    """
    # Extract the first result list (there's one list per query embedding)
    documents = results["documents"][0]
    # scores = results["distances"][0]
    context_text = "\n\n---\n\n".join(doc for doc in documents)
    return context_text
