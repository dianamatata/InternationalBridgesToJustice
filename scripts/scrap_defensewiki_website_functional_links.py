"""
This script aims at building a tree of the links with depth =2 from the url https://defensewiki.ibj.org/
and checks the quality of the links

Different functions are performed here:
- extracting all the page contents from the DefenseWiki in a recursive way (we save defensewiki1 with everything and defensewiki1_no_content with the metadata but not the content of the pages)
- for each DefenseWiki page, extract the links and check if they are functional or not
"""

import os
import time
from datetime import datetime
from langdetect import detect
import json
from markdownify import (
    markdownify as md,
)
import pandas as pd
import glob
from src.file_manager import generate_hash, save_file
from src.scraping_functions import get_link_status, get_links, get_last_edited_date, extract_webpage_html_from_url, define_defensewiki_page_name, remove_content_field_from_tree_dict, save_status_link_dictionary_as_html
from typing import Optional, Set, Dict
from src.config import base_url_defense_wiki, path_folder_defense_wiki

# Functions -------------------

def iterative_check_of_functional_and_outdated_links_from_the_DefenseWiki(
    url,
    depth=1,
    visited=None,
    base_url=base_url_defense_wiki,
    out_folder=path_folder_defense_wiki,
):

    if visited is None:
        visited = set()

    if depth == 0 or url in visited:
        return {}, visited

    visited.add(url)
    links = get_links(url)
    tree = {url: {}}

    for link_i in links:
        if link_i in visited:  # Skip if already visited
            print(f"Skipping already present link: {link_i}")
            continue
        print(f"Processing: {link_i}")

        link_type = "internal" if link_i.startswith(base_url) else "external"
        link_status = get_link_status(link_i)
        link_info = {
            "type": link_type,
            "status": link_status
        }

        if depth > 1:
            subtree, visited = iterative_check_of_functional_and_outdated_links_from_the_DefenseWiki(
                link_i, depth - 1, visited, base_url, out_folder
            )
            link_info["subtree"] = subtree

        tree[url][link_i] = link_info

    return tree, visited

def format_json_with_colors(data):
    json_str = json.dumps(data, indent=4)
    json_str = json_str.replace(
        '"status": "functional"',
        '"status": "<span class=\'functional\'>functional link</span>"',
    )
    json_str = json_str.replace(
        '"status": "error"',
        '"status": "<span class=\'error\'>error - link broken</span>"',
    )
    return json_str

    formatted_json = format_json_with_colors(tree_links_validity)

    # Write to an HTML file
    with open(output_file, "w") as f:
        f.write(html_template.format(formatted_json))

    print(f"HTML file created: {output_file}")


def save_as_cvs(
    tree_links_validity,
    output_file="data/processed/defensewiki.ibj.org/tree_links_validity.csv",
):
    # Extract the root key (first level)
    root_key = list(tree_links_validity.keys())[0]
    # Extract principal pages
    principal_pages = tree_links_validity[root_key]

    data = []
    # Loop through each principal page and extract its links
    for principal_page, links in principal_pages.items():
        print(principal_page)
        if "subtree" in links and principal_page in links["subtree"]:
            links_2 = links["subtree"][principal_page]
            for link, details in links_2.items():
                data.append(
                    {
                        "Principal Page": principal_page,
                        "Link": link,
                        "Status": details["status"],
                    }
                )

    df = pd.DataFrame(data)

    df.to_csv(output_file, index=False)


# MAIN --------------------------------------
# Get all the links from the defensewiki(refs,and all) as functional/not functional -----------------
# and save them as html and csv files

os.getcwd()
folder_defense_wiki_raw = "data/raw/defensewiki.ibj.org"
start_time = time.time()
url = "https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=2&offset=3"  # 2 pages
# url = "https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=1500&offset=1000"  # 500 pages
# url = "https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=1300&offset=0" # all pages

tree_links_validity, visited_links = iterative_check_of_functional_and_outdated_links_from_the_DefenseWiki(url=url, visited=None, depth=2)
elapsed_time = time.time() - start_time
print(f"Elapsed Time: {elapsed_time} seconds")
# print(f"\033[92m{json.dumps(tree_links_validity, indent=4)}\033[0m")  # green color
with open("../data/processed/defensewiki.ibj.org/tree_links_validity.json", "w") as f:
    json.dump(tree_links_validity, f, indent=4)

save_status_link_dictionary_as_html(
    tree_links_validity,
    output_file="../data/processed/defensewiki.ibj.org/tree_links_validity_1000_1500.html",
)
save_as_cvs(
    tree_links_validity,
    output_file="../data/processed/defensewiki.ibj.org/tree_links_validity_1000_1500.csv",
)
print("files saved")

# merge all the subdocuments ---------------------------------

# Define the path pattern for your CSV files
csv_files = glob.glob("data/processed/defensewiki.ibj.org/tree_links_validity_*.csv")

df_list = []
for file in csv_files:
    print(file)
    try:
        df = pd.read_csv(file, sep=";", engine="python")  # Tab-separated
        df_list.append(df)
    except Exception as e:
        print(f"Error reading {file}: {e}")

df_merged = pd.concat(df_list, ignore_index=True)
output_file = "data/processed/defensewiki.ibj.org/tree_links_validity_merged.csv"
df_merged.to_csv(output_file, sep="\t", index=False)


# Get all the links from the defensewiki(refs,and all) ----------------------------

# with open(f"{out_folder}/defensewiki1_functional_outdated_links.json", "r") as f:
#     tree = json.load(f)
# print(f"\033[93m{json.dumps(tree, indent=4)}\033[0m")  # yellow color

# first iteration
tree_links_validity, visited_links = iterative_check_of_functional_and_outdated_links_from_the_DefenseWiki(url, visited=None, depth=2)

# second iteration:
start_time = time.time()
tree_links_validity2, visited_links2 = iterative_check_of_functional_and_outdated_links_from_the_DefenseWiki(
    url, visited=visited_links, depth=2
)
elapsed_time = time.time() - start_time
print(f"Elapsed Time: {elapsed_time} seconds")

# save tree
print(f"\033[92m{json.dumps(tree_links_validity, indent=4)}\033[0m")  # green color
save_file(
    f"{folder_defense_wiki_raw}/defensewiki1_functional_outdated_links_2.json",
    tree_links_validity2,
    file_type="json",
)

# save visited links
with open(f"{folder_defense_wiki_raw}/defensewiki1_visited_links.txt", "w") as file:
    file.write("\n".join(visited_links))


