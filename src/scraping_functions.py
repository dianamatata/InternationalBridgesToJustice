import requests
import re
from bs4 import BeautifulSoup
import unicodedata  # text formating
from urllib.parse import unquote  # text formating
import time
from datetime import datetime
from langdetect import detect
from markdownify import markdownify as md
from typing import Optional, Set, Dict
from src.file_manager import generate_hash

def get_link_status(url: str):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return "functional"
        else:
            return "error"
    except requests.exceptions.RequestException:
        return "error"

def get_links(url: str):
    """Extracts all links from a webpage. level1: we want the reference of the specific pages and internal links"""
    level = "level_1"
    if url.startswith(
        "https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit"
    ):
        level = "level_0"

    base_url = "https://defensewiki.ibj.org"

    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        if level == "level_0":
            # Add the base_url to the relative links
            links = [
                base_url + str(a_tag.get("href"))
                for a_tag in soup.select("ol.special li a")
                if "&action=history" not in a_tag.get("href")
            ]
            return links

        if level == "level_1":
            links1 = [
                base_url + a["href"] for a in soup.find_all("a", class_="internal")
            ]
            links2 = [a["href"] for a in soup.select("a.external")]
            links = links1 + links2

            return links

        else:
            return []

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []


def matching_country_name(country_names: str, title: str, title_to_country: dict, substring_to_country: dict) -> str:

    matching_country = next(
        (
            country
            for country in country_names
            if country.lower().strip() == title
        ),
        None,
    )
    if matching_country:
        return matching_country

    else:
        matching_country_1 = next(
            (
                country
                for country in country_names
                if country.lower().strip() in title
            ),
            None,
        )
        if matching_country_1:
            return matching_country_1

        else:
            matching_country_2 = next(
                (
                    value
                    for key, value in title_to_country.items()
                    if key.lower().strip() in title
                ),
                None,
            )
            if matching_country_2:
                return matching_country_2

            else:
                matching_country_3 = next(
                    (
                        value
                        for key, value in substring_to_country.items()
                        if key.lower().strip() in title
                    ),
                    None,
                )

                if matching_country_3:
                    return matching_country_3
                else:
                    return ""


def scrap_defensewiki_website(
        url: str,
        base_url: str,
        list_country_names: list[str],
        out_folder: str,
        title_to_country: str,
        substring_to_country: str,
        visited: Optional[Set[str]] = None
) -> Dict:

    if visited is None:
        visited = set()
    if url in visited:
        return {}

    visited.add(url)
    links = get_links(url)
    defense_wiki_dict = {url: {}}

    for link_i in links:
        link_type = "internal" if link_i.startswith(base_url) else "external"
        link_status = get_link_status(link_i)

        link_info = {
            "type": link_type,
            "status": link_status
        }

        if link_status == "functional":
            response, soup = extract_webpage_html_from_url(link_i)
            md_text = md(response.text)
            page_name = define_defensewiki_page_name(link_i)  # Extract page name from URL
            filename = f"{out_folder}/{page_name}.md"
            viewcount_tag = soup.find("li", {"id": "viewcount"})
            viewcount = viewcount_tag.get_text(strip=True) if viewcount_tag else None
            country = matching_country_name(list_country_names, page_name, title_to_country, substring_to_country)

            link_info= {
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
                "country": country
            }

        print({k: link_info[k] for k in ["country", "title", "link"] if k in link_info})

        defense_wiki_dict[link_i] = link_info

    return defense_wiki_dict


def get_last_edited_date(soup):
    # Find the <li> element with id="lastmod" containing the last modified date
    lastmod_li = soup.find("li", {"id": "lastmod"})
    if lastmod_li:
        text = lastmod_li.get_text()
        # Use regular expression to extract the date and time
        date_match = re.search(r"(\d{1,2} \w+ \d{4}), at (\d{2}:\d{2})", text)
        if date_match:
            date = date_match.group(1)  # Extracted date (e.g., "2 October 2019")
            time = date_match.group(2)  # Extracted time (e.g., "08:54")
            return f"{date}, {time}"
    return lastmod_li

def extract_webpage_html_from_url(url: str):
    response = requests.get(url)  # Fetch the html of page in soup
    response.raise_for_status()  # Raise an error for failed requests
    soup = BeautifulSoup(response.text, "html.parser")  # Parse the HTML
    return response, soup

def define_defensewiki_page_name(defensewiki_link: str):
    page_name = unquote(defensewiki_link.split("title=")[1].split("&")[0].replace("/", "-"))
    page_name = page_name.replace("_", " ").strip().lower()
    # Normalize the string to remove accents and special characters. This normalizes the string, breaking down accented characters into their base characters (e.g., ô becomes o).
    page_name = (
        unicodedata.normalize("NFKD", page_name).encode("ASCII", "ignore").decode()
    )
    return page_name

def remove_content_field_from_tree_dict(tree):
    """Recursively removes the 'content' field from the tree structure."""
    if isinstance(tree, dict):
        tree.pop("content", None)  # Remove 'content' if it exists
        for key, value in tree.items():
            remove_content_field_from_tree_dict(value)  # Recurse into nested dictionaries
    elif isinstance(tree, list):
        for item in tree:
            remove_content_field_from_tree_dict(item)  # Recurse into lists

def save_status_link_dictionary_as_html(tree_links_validity, output_file):
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