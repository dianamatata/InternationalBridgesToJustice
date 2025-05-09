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
from langdetect import detect  # detect language
import json  # save in json files
from markdownify import (
    markdownify as md,
)  # markdownify: Handles more complex HTML structures, better at preserving formatting.
import pandas as pd
import glob
from src.file_manager import generate_hash
from src.scraping_functions import get_link_status, get_links, get_last_edited_date, extract_webpage_html_from_url, define_defensewiki_page_name


# Functions -------------------

def save_file(filename, content, file_type="json"):
    try:
        if file_type == "json":
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(content, file, indent=4)  # Save JSON content

        else:  # Handle other file types (e.g., plain text, Markdown, etc.)
            with open(filename, "w", encoding="utf-8") as file:
                file.write(content)

        print(f"File saved successfully: {filename}")

    except Exception as e:
        print(f"Error saving file {filename}: {e}")


def build_complex_link_tree(
    url,
    depth=1,
    visited=None,
    base_url="https://defensewiki.ibj.org",
    out_folder="IBJ_documents/legal_country_documents/docs_in_md_json",
):
    """Recursively builds a tree of links up to a certain depth."""

    if visited is None:
        visited = set()

    if depth == 0 or url in visited:
        return {}

    visited.add(url)
    links = get_links(url)
    tree = {url: {}}

    for link_i in links:
        link_type = "internal" if link_i.startswith(base_url) else "external"
        link_status = get_link_status(link_i)

        if link_status == "functional":
            response, soup = extract_webpage_html_from_url(link_i)
            md_text = md(response.text)
            page_name = define_defensewiki_page_name(link_i)  # Extract page name from URL
            filename = f"{out_folder}/{page_name}.md"
            viewcount_tag = soup.find("li", {"id": "viewcount"})
            viewcount = viewcount_tag.get_text(strip=True) if viewcount_tag else None

            tree[url][link_i] = {
                "type": link_type,
                "status": get_link_status(link_i),
                "link": link_i,
                "title": page_name,
                "extracted": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "hash": generate_hash(str(soup)),
                "last-edited": get_last_edited_date(soup),
                "language": detect(soup.get_text()),
                "viewcount": viewcount,
                "type": "defensewiki_doc",
                "full_path": filename,
                "nbr_of_words": len(md_text.split()),
                "nbr_of_lines": len(md_text.splitlines()),
                "content": md_text,
            }

        else:
            tree[url][link_i] = {"type": link_type, "status": get_link_status(link_i)}
        if depth > 1:
            subtree = build_complex_link_tree(link_i, depth - 1, visited)
            tree[url][link_i]["subtree"] = subtree

    return tree


def remove_content_field(tree):
    """Recursively removes the 'content' field from the tree structure."""
    if isinstance(tree, dict):
        tree.pop("content", None)  # Remove 'content' if it exists
        for key, value in tree.items():
            remove_content_field(value)  # Recurse into nested dictionaries
    elif isinstance(tree, list):
        for item in tree:
            remove_content_field(item)  # Recurse into lists


def build_link_tree_3(
    url,
    depth=1,
    visited=None,
    base_url="https://defensewiki.ibj.org",
    out_folder="IBJ_documents/legal_country_documents/docs_in_md_json",
):
    """Recursively builds a tree of links up to a certain depth."""

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
        tree[url][link_i] = {"type": link_type, "status": link_status}

        if depth > 1:
            subtree, visited = build_link_tree_3(
                link_i, depth - 1, visited, base_url, out_folder
            )
            tree[url][link_i]["subtree"] = subtree

    return tree, visited


def save_as_html(tree_links_validity, output_file):
    html_template = """<html>
    <head>
        <title>Tree Links Validity</title>
        <style>
            body {{ background-color: white; color: black; }}
            .functional {{ color: LimeGreen; }}
            .error {{ color: red; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h2>Tree Links Validity</h2>
        <pre>{}</pre>
    </body>
    </html>"""

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
os.getcwd()
folder_defense_wiki_raw = "data/raw/defensewiki.ibj.org"


# Get all the links from the defensewiki(refs,and all) as functional/not functional -----------------
# and save them as html and csv files

start_time = time.time()
url = "https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=2&offset=3"  # 2 pages
url = "https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=1500&offset=1000"  # 500 pages

# url = "https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=1300&offset=0" # all pages

tree_links_validity, visited_links = build_link_tree_3(url=url, visited=None, depth=2)
elapsed_time = time.time() - start_time
print(f"Elapsed Time: {elapsed_time} seconds")
# print(f"\033[92m{json.dumps(tree_links_validity, indent=4)}\033[0m")  # green color
with open("../data/processed/defensewiki.ibj.org/tree_links_validity.json", "w") as f:
    json.dump(tree_links_validity, f, indent=4)

save_as_html(
    tree_links_validity,
    output_file="../data/processed/defensewiki.ibj.org/tree_links_validity_1000_1500.html",
)
save_as_cvs(
    tree_links_validity,
    output_file="../data/processed/defensewiki.ibj.org/tree_links_validity_1000_1500.csv",
)
print("files saved")

# merge all the subdocuments:

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

# Concatenate all DataFrames into one big DataFrame
df_merged = pd.concat(df_list, ignore_index=True)

# Save merged file
output_file = "../data/processed/defensewiki.ibj.org/tree_links_validity_merged.csv"
df_merged.to_csv(output_file, sep="\t", index=False)

print(f"Merged file saved as {output_file}")

# Display first few rows to check
print(df_merged.head())

# Get all the links from the defensewiki(refs,and all) ----------------------------

# with open(f"{out_folder}/defensewiki1_functional_outdated_links.json", "r") as f:
#     tree = json.load(f)
# print(f"\033[93m{json.dumps(tree, indent=4)}\033[0m")  # yellow color

# first iteration
tree_links_validity, visited_links = build_link_tree_3(url, visited=None, depth=2)

# second iteration:
start_time = time.time()
tree_links_validity2, visited_links2 = build_link_tree_3(
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


# Example usage to map defense wiki -----------------------------

link_tree_defensewiki_test = build_complex_link_tree(
    "https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=2&offset=3",
    depth=1,
)
print(f"\033[92m{json.dumps(link_tree_defensewiki_test, indent=4)}\033[0m")
save_file(
    f"{folder_defense_wiki_raw}/link_tree_defensewiki.json",
    link_tree_defensewiki_test,
    file_type="json",
)
remove_content_field(link_tree_defensewiki_test)
print(f"\033[93m{json.dumps(link_tree_defensewiki_test, indent=4)}\033[0m")
save_file(
    f"{folder_defense_wiki_raw}/link_tree_defensewiki1.json",
    link_tree_defensewiki_test,
    file_type="json",
)


# MAP ALL defensewiki -----------------------------

link_tree_defensewiki = build_complex_link_tree(
    "https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=1300&offset=0",
    depth=1,
)
save_file(
    f"{folder_defense_wiki_raw}/defensewiki_all.json",
    link_tree_defensewiki,
    file_type="json",
)
remove_content_field(link_tree_defensewiki)
save_file(
    f"{folder_defense_wiki_raw}/defensewiki1_no_content.json",
    link_tree_defensewiki,
    file_type="json",
)
