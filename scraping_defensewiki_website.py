# This scripts build a tree of the links with depth =2 in the https://defensewiki.ibj.org/
# and checks the quality of the links


import time
import re # handles text
import requests # get url info
from bs4 import BeautifulSoup
import hashlib # get hash
from datetime import datetime
from langdetect import detect # detect language
from urllib.parse import unquote # text formating
import unicodedata # text formating
import json # save in json files
from markdownify import markdownify as md # markdownify: Handles more complex HTML structures, better at preserving formatting.



def get_link_status(url):
    """Checks the status of a link (functional or error)."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return "functional"
        else:
            return "error"
    except requests.exceptions.RequestException:
        return "error"

def get_links(url):
    """Extracts all links from a webpage. level1: we want the reference of the specific pages and internal links"""

    level = "level_1"
    if url.startswith("https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit"):
        level = "level_0"

    base_url = "https://defensewiki.ibj.org"

    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        if level == "level_0":
            # Add the base_url to the relative links
            links = [base_url + str(a_tag.get("href"))
                     for a_tag in soup.select("ol.special li a") if '&action=history' not in a_tag.get("href")]
            return links

        if level == "level_1":
            links1 = [base_url + a["href"] for a in soup.find_all("a", class_="internal")]
            links2 = [a["href"] for a in soup.select("a.external")]
            links = links1 + links2

            return links

        else:
            return []

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def generate_hash(content):
    """Generate SHA-256 hash of the given content."""
    return hashlib.sha256(content.encode()).hexdigest()

def get_last_edited_date(soup):
    # Find the <li> element with id="lastmod" containing the last modified date
    lastmod_li = soup.find('li', {'id': 'lastmod'})
    if lastmod_li:
        text = lastmod_li.get_text()
        # Use regular expression to extract the date and time
        date_match = re.search(r'(\d{1,2} \w+ \d{4}), at (\d{2}:\d{2})', text)
        if date_match:
            date = date_match.group(1)  # Extracted date (e.g., "2 October 2019")
            time = date_match.group(2)  # Extracted time (e.g., "08:54")

            return f"{date}, {time}"

    return lastmod_li

def define_page_name(link):
    # Decode the URL and get the page name
    page_name = unquote(link.split("title=")[1].split("&")[0].replace("/", "-"))
    # Normalize the string to remove accents and special characters. This normalizes the string, breaking down accented characters into their base characters (e.g., ô becomes o).
    page_name = unicodedata.normalize('NFKD', page_name).encode('ASCII', 'ignore').decode()
    return page_name

def extract_webpage_html_from_url(url):
    response = requests.get(url) # Fetch the html of page in soup
    response.raise_for_status()  # Raise an error for failed requests
    soup = BeautifulSoup(response.text, "html.parser") # Parse the HTML
    return response, soup

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


def build_complex_link_tree(url, depth=1, visited=None, base_url="https://defensewiki.ibj.org",
                            out_folder="/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/IBJ_documents/legal_country_documents/docs_in_md_json"):
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
            page_name = define_page_name(link_i)  # Extract page name from URL
            filename = f"{out_folder}/{page_name}.md"
            viewcount_tag = soup.find('li', {'id': 'viewcount'})
            viewcount = viewcount_tag.get_text(strip=True) if viewcount_tag else None

            tree[url][link_i] = {"type": link_type,
                                 "status": get_link_status(link_i),
                                 'link': link_i,
                                 'title': page_name,
                                 'extracted': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                 'hash': generate_hash(str(soup)),
                                 'last-edited': get_last_edited_date(soup),
                                 'language': detect(soup.get_text()),
                                 'viewcount': viewcount,
                                 'type': "defensewiki_doc",
                                 'full_path': filename,
                                 'nbr_of_words': len(md_text.split()),
                                 'nbr_of_lines': len(md_text.splitlines()),
                                 'content': md_text
                                 }

        else:
            tree[url][link_i] = {"type": link_type,
                                 "status": get_link_status(link_i)}
        if depth > 1:
            subtree = build_link_tree(link_i, depth - 1, visited)
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


def link_exists_in_tree(link_tree, target_link):
    tree_str = json.dumps(link_tree, ensure_ascii=False) # Convert the tree to a string
    return target_link in tree_str # Check if the target link exists in the string representation of the tree


def build_link_tree_3(url, depth=1, visited=None, base_url="https://defensewiki.ibj.org",
                      out_folder="/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/IBJ_documents/legal_country_documents/docs_in_md_json"):
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
            subtree, visited = build_link_tree_3(link_i, depth - 1, visited, base_url, out_folder)
            tree[url][link_i]["subtree"] = subtree

    return tree, visited




# MAIN --------------------------------------
out_folder = "/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/IBJ_documents/legal_country_documents/docs_in_md_json"

# Example usage get all the links from the defensewiki(refs,and all)
# tree_links_validity define already
start_time = time.time()
tree_links_validity = build_link_tree_3("https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=2&offset=3", depth=2, tree=tree_links_validity)
elapsed_time = time.time() - start_time
print(f"Elapsed Time: {elapsed_time} seconds")
print(f"\033[92m{json.dumps(tree_links_validity, indent=4)}\033[0m")  # green color



# Get all the links from the defensewiki(refs,and all) ----------------------------

# with open(f"{out_folder}/defensewiki1_functional_outdated_links.json", "r") as f:
#     tree = json.load(f)
# print(f"\033[93m{json.dumps(tree, indent=4)}\033[0m")  # yellow color

# first iteration
url = "https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=5&offset=0"
tree_links_validity, visited_links = build_link_tree_3(url, visited=None, depth=2)

# second iteration:
url = "https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=20&offset=0"
start_time = time.time()
tree_links_validity2, visited_links2 = build_link_tree_3(url, visited=visited_links, depth=2)
elapsed_time = time.time() - start_time
print(f"Elapsed Time: {elapsed_time} seconds")

# save tree
print(f"\033[92m{json.dumps(tree_links_validity2, indent=4)}\033[0m")  # green color
save_file(f"{out_folder}/defensewiki1_functional_outdated_links_2.json", tree_links_validity2, file_type="json")

# save visited links
with open(f"{out_folder}/defensewiki1_visited_links.txt", "w") as file:
    file.write("\n".join(visited_links))



# Example usage to map defense wiki -----------------------------

link_tree_defensewiki_test = build_complex_link_tree("https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=2&offset=3", depth=1)
print(f"\033[92m{json.dumps(link_tree_defensewiki_test, indent=4)}\033[0m")
out_folder = "/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/IBJ_documents/legal_country_documents/docs_in_md_json"
save_file(f"{out_folder}/link_tree_defensewiki.json", link_tree_defensewiki_test, file_type="json")
remove_content_field(link_tree_defensewiki_test)
print(f"\033[93m{json.dumps(link_tree_defensewiki_test, indent=4)}\033[0m")
save_file(f"{out_folder}/link_tree_defensewiki1.json", link_tree_defensewiki_test, file_type="json")



# MAP ALL defensewiki -----------------------------

link_tree_defensewiki = build_complex_link_tree("https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=1300&offset=0", depth=1)
save_file(f"{out_folder}/defensewiki_all.json", link_tree_defensewiki, file_type="json")
remove_content_field(link_tree_defensewiki)
save_file(f"{out_folder}/defensewiki1_no_content.json", link_tree_defensewiki, file_type="json")



