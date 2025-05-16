import requests
from bs4 import BeautifulSoup
from markdownify import (
    markdownify as md,
)  # markdownify: Handles more complex HTML structures, better at preserving formatting.
import json
import re
import os

from src.config import path_folder_constitutions_with_md_files, start_url_constitutions, base_url_constitutions, path_jsonl_file_with_constitutions_all_countries



response_base = requests.get(start_url_constitutions)
soup_base = BeautifulSoup(response_base.text, "html.parser")
internal_links_for_constitutions = soup_base.select("div.constitution-links a")
dictionary_countryname_countrylink = {
    a["href"].replace("/constitution/", "").split("?")[0]: a["href"]
    for a in soup_base.select("div.constitution-links a")
}

for country_year, link in list(dictionary_countryname_countrylink.items())[10:]:

    if not os.path.exists(f"{path_folder_constitutions_with_md_files}/{country_year}.md"):
        print(f"Constitution not extracted yet: {country_year}: Link: {link}")

        response = requests.get(base_url_constitutions + link)
        soup = BeautifulSoup(response.text, "html.parser")

        for span in soup.find_all(
            "span", class_="topic"
        ):  # Find and remove all spans with class_="topic"
            span.decompose()  # .decompose(): Completely removes the matched elements from the soup.

        md_text = md(
            str(soup)
        )  # Convert modified HTML to Markdown # if no decompose: md_text = md(response.text)

        cleaned_md_text = re.sub(
            r"^\s*,+\s*$|,\s*,\s*", "", md_text, flags=re.MULTILINE
        )
        # ^\s*,+\s*$ → Matches lines that contain only commas (possibly with spaces around them).
        # ,\s*,\s* → Matches sequences of commas surrounded by spaces.
        # re.MULTILINE → Ensures the regex applies to each line separately.

        file_info = {
            "link": link,
            "country": "_".join(country_year.split("_")[:-1]),
            "year": country_year.split("_")[1],
            "path": f"{path_folder_constitutions_with_md_files}/{country_year}.md",
            "filename": f"{country_year}.md",
            "language": link.split("=")[1],
            "type": "constitution",
            "content": cleaned_md_text,
        }

        # save constitution
        with open(f"{path_folder_constitutions_with_md_files}/{country_year}.md", "w") as file:
            file.write(cleaned_md_text)
        # save with metadata in jsonl
        with open(
            path_jsonl_file_with_constitutions_all_countries, "a", encoding="utf-8"
        ) as jsonl_file:
            jsonl_file.write(json.dumps(file_info) + "\n")
    else:
        print(f"Constitution already extracted: {country_year}")
