# 1️⃣ Fetch HTML + Extract Metadata at the Same Time using BeautifulSoup
# Downloads the HTML
# Extracts metadata (last edited date, view count, language)
# Computes a hash for versioning
# Saves everything into the HTML file

import os
import re # handles text
import requests # get url info
from bs4 import BeautifulSoup
import hashlib # get hash
from datetime import datetime
from langdetect import detect # detect language
from urllib.parse import unquote # text formating
import unicodedata # text formating
import json # save in json files
import html2text # html2text: Faster, more configurable, widely used.
from markdownify import markdownify as md # markdownify: Handles more complex HTML structures, better at preserving formatting.


# FUNCTIONS -------------------------

def extract_webpage_html_from_url(url):
    response = requests.get(url) # Fetch the html of page in soup
    response.raise_for_status()  # Raise an error for failed requests
    soup = BeautifulSoup(response.text, "html.parser") # Parse the HTML
    return response, soup

def get_all_links_from_url(url):

    response, soup = extract_webpage_html_from_url(url)
    links = []
    for a_tag in soup.select("ol.special li a"):
        if '&action=history' not in a_tag.get('href', ''):
            link = a_tag.get("href")
            links.append(link)

    # Convert relative URLs to absolute URLs
    full_links = [requests.compat.urljoin(url, link) for link in links]

    # print(full_links)
    print(f"\033[93mTotal of valid links found: {len(full_links)}\033[0m")  # Red color
    return full_links

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

def metadata_in_dict(metadata_dict, response,soup, link, filename):
    md_text = md(response.text)

    metadata_dict[link] = {
        'link': link,
        'title': define_page_name(link),
        'hash': generate_hash(str(soup)),
        'extracted': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'last-edited': get_last_edited_date(soup),
        'language': detect(soup.get_text()),
        'viewcount': soup.find('li', {'id': 'viewcount'}),
        'type': "defensewiki_doc",
        'full_path': filename,
        'nbr_of_lines': len(md_text.split()),
        'nbr_of_words': len(md_text.splitlines()),
        'content': md_text
        # Add country for legal separation # TODO
    }
    return metadata_dict

# metadata_dict['https://defensewiki.ibj.org/index.php?title=Chile/es']['hash']

def html_to_markdown(html_content):
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = False  # Keep links
    markdown_text = text_maker.handle(html_content)
    print(markdown_text)
    return markdown_text

def fetch_page_and_metadata(start_url, out_folder):

    full_links = get_all_links_from_url(start_url)
    metadata_dict = {}

    for link in full_links[:3]:
        print(link)
        response, soup = extract_webpage_html_from_url(link)
        new_hash = generate_hash(str(soup))

        if link in metadata_dict:
            if metadata_dict.get(link) and metadata_dict[link].get('hash') == new_hash:
                print("already downloaded")
            else:
                metadata_dict = get_file_and_metadata(response, soup, link, out_folder, metadata_dict)
        else:
            metadata_dict = get_file_and_metadata(response, soup, link, out_folder, metadata_dict)


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


def get_file_and_metadata(response, soup, link, out_folder, metadata_dict):

            page_name = define_page_name(link)  # Extract page name from URL
            filename = f"{out_folder}/{page_name}.md"
            metadata_dict = metadata_in_dict(metadata_dict, response, soup, link, filename)  # Save metadata
            save_file(filename, md(response.text), file_type="json")
            print(f"\033[92m ✅ Saved page with metadata: {filename} \033[0m")  # Green color
            return metadata_dict


def get_internal_links(soup, page_name):
    # Extract links
    base_url = "https://defensewiki.ibj.org"
    links = [base_url + a["href"] for a in soup.find_all("a", class_="internal")]

    # Download PDFs
    for link in links:
        filename_2 = link.split("/")[-1]  # Extract file name
        filepath_2 = f"{out_folder}/{page_name}__{filename_2}"
        print(filepath_2)
        response = requests.get(link)
        # TODO: add metadata for files


        if response.status_code == 200: # exists
            with open(filepath_2, "wb") as pdf_file:
                pdf_file.write(response.content)
            print(f"Downloaded: {filepath_2}")
        else:
            print(f"Failed to download: {link}")



# MAIN -------------------------

# Example: Fetch and process a Wikipedia-style page
start_url = "https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=20&offset=0"
start_urls = 'https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=2000&offset=0'  # Showing below up to 1,251 results in range #1 to #1,251.
pop_pages_url = "https://defensewiki.ibj.org/index.php?title=Special:PopularPages
"out_folder = "html_pages/defensewiki.ibj.org"
os.makedirs(out_folder, exist_ok=True)
fetch_page_and_metadata(start_url, out_folder)
chile_url = "https://defensewiki.ibj.org/index.php?title=Chile/es"
url = chile_url

print(json.dumps(metadata_dict, indent=2))

# <ul><li><a class="internal" href="/images/8/86/Constitution_Chile_1980.pdf" title="Constitution Chile 1980.pdf"> Constitución de Chile</a></li> # https://defensewiki.ibj.org/images/8/86/Constitution_Chile_1980.pdf
# <li><a class="internal" href="/images/6/6c/Criminal_Procedure_Chile.pdf" title="Criminal Procedure Chile.pdf"> Código Procesal Penal de Chile</a></li></ul>

filename="html_pages/defensewiki.ibj.org/test.md"
with open(filename, "w", encoding="utf-8") as f:
    f.write(html_to_markdown(response.text)) # simpler but better?

# TODO: keep this one, save as content, we need to keep response
filename="html_pages/defensewiki.ibj.org/test1.md"
with open(filename, "w", encoding="utf-8") as f:
    f.write(md(response.text))

filename="html_pages/defensewiki.ibj.org/test2.md"
with open(filename, "w", encoding="utf-8") as f:
    f.write(response.text) # too much


url_caselaw ="https://caselaw.ihrda.org/fr/library/table/?q=(allAggregations:!f,filters:(),from:0,includeUnpublished:!t,limit:5,order:asc,sort:metadata.case_headnotes,treatAs:number,unpublished:!f)"
url_caselaw ="https://caselaw.ihrda.org/fr/library/table/?q=(allAggregations:!f,filters:(),from:30,includeUnpublished:!t,limit:3000,order:asc,sort:metadata.case_headnotes,treatAs:number,unpublished:!f)"


# 🎨 ANSI Color Codes:
# 🔴 Red: \033[91m
# 🟢 Green: \033[92m
# 🔵 Blue: \033[94m
# 🟡 Yellow: \033[93m
# ⚪ Reset (default color): \033[0m

#TODO
# both languages are save: Chile/es and Chile
# extract all the documents and links referenced there!
# add a check if document has already been downloaded, have a lib with hashes?

def get_data_from_caselaw():

    url_caselaw1 = "https://caselaw.ihrda.org/api/search?allAggregations=false&filters=%7B%7D&from=0&includeUnpublished=true&limit=5&order=asc&sort=metadata.case_headnotes&treatAs=number&unpublished=false&include=%5B%22permissions%22%5D"
    response = requests.get(url_caselaw1)
    soup2 = BeautifulSoup(response.text, "html.parser")
    print(response.json())

    # Assuming the response is a JSON object (for example, from an API response)
    data = response.json()

    # Initialize an empty dictionary to store the extracted data
    pdf_data = {}

    # Function to safely extract metadata fields
    # Avoid IndexError:
    # Used a helper function get_metadata_value(metadata, key) that checks if a field exists before accessing [0].
    # If the key does not exist or is empty, it returns 'N/A' instead of crashing.
    # Added Safe Checks:
    #
    # "creationDate": Now checks if the key exists before trying to convert it to a date.
    # "outcome" and "keywords": Used .get() to avoid missing key errors.
    def get_metadata_value(metadata, key):
        """Returns the first value in metadata[key] if it exists, else returns 'N/A'."""
        if key in metadata and metadata[key]:  # Ensure key exists and is not empty
            return metadata[key][0].get("value", "N/A")  # Safely get "value"
        return "N/A"

    # Loop through the 'rows' structure in the data
    if 'rows' in data:
        for item in data['rows']:
            # Check if 'documents' exist
            if 'documents' in item:
                for document in item['documents']:
                    filename = document.get('filename', 'N/A')
                    if filename != 'N/A':  # Check if filename exists
                        metadata = item.get('metadata', {})

                        # Add extracted data
                        pdf_data[filename] = {
                            'title': item.get('title', 'N/A'),
                            'language': document.get('language', 'N/A'),
                            'creationDate': datetime.utcfromtimestamp(document['creationDate'] / 1000).strftime(
                                '%Y-%m-%d %H:%M:%S') if 'creationDate' in document else 'N/A',
                            'size': document.get('size', 'N/A'),
                            'totalPages': document.get('totalPages', 'N/A'),
                            # 'mimetype': document.get('mimetype', 'N/A'),
                            'status': document.get('status', 'N/A'),
                            'eccj_app_no': get_metadata_value(metadata, 'eccj_app_no_'),
                            'eccj_jud_no': get_metadata_value(metadata, 'eccj_jud_no_'),
                            'case_headnotes': get_metadata_value(metadata, 'case_headnotes'),
                            'outcome': metadata.get('outcome', [{}])[0].get('label', 'N/A') if metadata.get(
                                'outcome') else 'N/A',
                            'keywords': [kw['label'] for kw in metadata.get('keywords', [])] if metadata.get(
                                'keywords') else [],
                        }
    print(pdf_data)
    # TODO: rename file but get original_filename, or link?

    # Print the extracted data
    print(json.dumps(pdf_data, indent=2))




# TODO pdf to text: at the end? iterate
# TODO check all the links from wiki
# TODO: how do I build a tree
# TODO: integrate glossary https://defensewiki.ibj.org/images/b/b4/Glossary_EN_FR_ES.pdf in LLM
