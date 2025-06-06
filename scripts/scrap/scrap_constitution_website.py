import requests
from bs4 import BeautifulSoup
from markdownify import (
    markdownify as md,
)
import json
import re
import os
from src.internationalbridgestojustice.config import Paths


response_base = requests.get(Paths.START_URL_CONSTITUTIONS)
soup_base = BeautifulSoup(response_base.text, "html.parser")
internal_links_for_constitutions = soup_base.select("div.constitution-links a")
dictionary_countryname_countrylink = {
    a["href"].replace("/constitution/", "").split("?")[0]: a["href"]
    for a in soup_base.select("div.constitution-links a")
}

for country_year, link in list(dictionary_countryname_countrylink.items()):
    if not os.path.exists(
        f"{Paths.PATH_FOLDER_CONSTITUTIONS_WITH_MD_FILES}/{country_year}.md"
    ):
        print(f"Constitution not extracted yet: {country_year}: Link: {link}")

        response = requests.get(Paths.BASE_URL_CONSTITUTIONS + link)
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
            "path": f"{Paths.PATH_FOLDER_CONSTITUTIONS_WITH_MD_FILES}/{country_year}.md",
            "filename": f"{country_year}.md",
            "language": link.split("=")[1],
            "type": "constitution",
            "content": cleaned_md_text,
        }

        # save constitution
        with open(
            f"{Paths.PATH_FOLDER_CONSTITUTIONS_WITH_MD_FILES}/{country_year}.md", "w"
        ) as file:
            file.write(cleaned_md_text)
        # save with metadata in jsonl
        with open(
            Paths.PATH_JSONL_FILE_WITH_CONSTITUTIONS_ALL_COUNTRIES,
            "a",
            encoding="utf-8",
        ) as jsonl_file:
            jsonl_file.write(json.dumps(file_info) + "\n")
    else:
        print(f"Constitution already extracted: {country_year}")
