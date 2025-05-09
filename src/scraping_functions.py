import requests
import re
from bs4 import BeautifulSoup
import unicodedata  # text formating
from urllib.parse import unquote  # text formating


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
    # Normalize the string to remove accents and special characters. This normalizes the string, breaking down accented characters into their base characters (e.g., ô becomes o).
    page_name = (
        unicodedata.normalize("NFKD", page_name).encode("ASCII", "ignore").decode()
    )
    return page_name