# This scripts build a tree of the links with depth =2 in the https://defensewiki.ibj.org/
# and checks the quality of the links

import requests
from bs4 import BeautifulSoup
import json
import time


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
    """Extracts all links from a webpage."""
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


def build_link_tree_basic(url, depth=2, visited=None, base_url="https://defensewiki.ibj.org"):
    """Recursively builds a tree of links up to a certain depth."""
    if visited is None:
        visited = set()

    if depth == 0 or url in visited:
        return {}, {}

    visited.add(url)
    links = get_links(url)

    labeled_links = {}

    for link_i in links:
        link_type = "internal" if link_i.startswith(base_url) else "external"
        labeled_links[link_i] = {"type": link_type}

    print(json.dumps(labeled_links, indent=4))

    # tree = {url: labeled_links}  # Store labeled links
    #
    # if depth > 0:
    #     for link_i in links:
    #         tree[url][link_i] = build_link_tree_basic(link_i, depth - 1, visited)


    tree = {url: {}}

    if depth > 0:
        for link_i in links:
            subtree, sub_labeled_links = build_link_tree_basic(link_i, depth - 1, visited)
            tree[url][link_i] = subtree  # Preserve the tree structure
            labeled_links.update(sub_labeled_links)  # Keep track of labeled links

    return tree, labeled_links


def build_link_tree(url, depth=2, visited=None, base_url="https://defensewiki.ibj.org"):
    """Recursively builds a tree of links up to a certain depth, ensuring last level is labeled."""

    if visited is None:
        visited = set()

    if url in visited:
        return {}

    visited.add(url)
    links = get_links(url)
    print(f"\033[92mLevel: {depth} for link: {url}\033[0m")
    print(json.dumps(links, indent=4))

    # print(json.dumps(links, indent=4))

    labeled_links = {}

    for link in links:
        link_type = "internal" if link.startswith(base_url) else "external"
        status = get_link_status(link)
        labeled_links[link] = {"type": link_type, "status": status}

    print(json.dumps(labeled_links, indent=4))

    tree = {url: labeled_links}  # Store labeled links

    # if depth > 0:  # Continue recursion if depth is not yet reached
    # TODO understand issue of running uselessly again the data
    #
    #     for link in links:
    #         if link.startswith("http"):  # Avoid relative links
    #             tree[url][link] = build_link_tree(link, depth - 1, visited)

    return tree



# try simple depth 0
link_tree1, labeled_links = build_link_tree_basic("https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=3&offset=3", depth=2)
print(f"\033[91m{json.dumps(link_tree1, indent=4)}\033[0m")  # Red color
print(f"\033[92m{json.dumps(labeled_links, indent=4)}\033[0m")  # Green color



# Example usage
root_url = "https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=5&offset=0"
root_url = "https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=1&offset=15"  # only one entry

start_time = time.time()
link_tree = build_link_tree(root_url, depth=2)
print(f"\033[92m ✅ Saved Tree \033[0m")  # Green color
elapsed_time = time.time() - start_time
print(f"Elapsed Time: {elapsed_time} seconds")



# try depth 0
link_tree = build_link_tree("https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=5&offset=0", depth=1)



print(f"\033[92m{json.dumps(link_tree, indent=4)}\033[0m")  # Green color

link_tree = build_link_tree("https://defensewiki.ibj.org/index.php?title=Singapore", depth=0)
print(f"\033[92m{json.dumps(link_tree, indent=4)}\033[0m")  # Green color

# TODO visit all the websites level0 get md direct,level1 get md if text, get pdf to markdown otherwise,  check if website exists, download files + metadata, check if file exists

link = 'https://defensewiki.ibj.org/index.php?title=Chile/es'
build_link_tree(link, 1, visited=None)
