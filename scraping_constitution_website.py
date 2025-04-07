import requests  # get url info
from bs4 import BeautifulSoup
from markdownify import (
    markdownify as md,
)  # markdownify: Handles more complex HTML structures, better at preserving formatting.
import json
import re
import os


# extract all the constitutions
out_folder = "data/raw/constituteproject.org"
out_folder_2 = "data/processed/constituteproject.org"

start_url = "https://www.constituteproject.org/constitutions?lang=en&status=in_force&status=is_draft"
base_url = "https://www.constituteproject.org"

response_base = requests.get(start_url)  # Fetch the html of page in soup
soup_base = BeautifulSoup(response_base.text, "html.parser")  # Parse the HTML
link1 = soup_base.select("div.constitution-links a")
# country_links = {a.text.strip(): a["href"] for a in soup2.select("div.constitution-links a")}
country_links = {
    a["href"].replace("/constitution/", "").split("?")[0]: a["href"]
    for a in soup_base.select("div.constitution-links a")
}

print(f"{json.dumps(country_links, indent=4)}")

for country_year, link in list(country_links.items())[10:]:

    if not os.path.exists(f"{out_folder}/{country_year}.md"):
        print(f"Constitution not extracted yet: {country_year}: Link: {link}")

        response = requests.get(base_url + link)  # Fetch the html of page in soup
        soup = BeautifulSoup(response.text, "html.parser")  # Parse the HTML

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
            "path": f"{out_folder}/{country_year}.md",
            "filename": f"{country_year}.md",
            "language": link.split("=")[1],
            "type": "constitution",
            "content": cleaned_md_text,
        }

        # save constitution
        with open(f"{out_folder}/{country_year}.md", "w") as file:
            file.write(cleaned_md_text)
        # save with metadata in jsonl
        with open(
            f"{out_folder_2}/constituteproject.jsonl", "a", encoding="utf-8"
        ) as jsonl_file:
            jsonl_file.write(json.dumps(file_info) + "\n")
    else:
        print(f"Constitution already extracted: {country_year}")
