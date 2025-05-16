from src.file_manager import save_file
from src.scraping_functions import scrap_defensewiki_website, remove_content_field_from_tree_dict
from src.config import base_url_defense_wiki, path_folder_defense_wiki, file_country_names
from src.countries_dict import title_to_country, substring_to_country

with open(file_country_names, "r", encoding="utf-8") as f:
    list_country_names = f.read().splitlines()

dict_defensewiki = scrap_defensewiki_website(
    url="https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=1300&offset=0",
    base_url=base_url_defense_wiki,
    list_country_names=list_country_names,
    out_folder=path_folder_defense_wiki,
    title_to_country=title_to_country,
    substring_to_country=substring_to_country,
    visited=None
)

save_file(filename=f"{path_folder_defense_wiki}/defensewiki_all.jsonl", content=dict_defensewiki, file_type="jsonl")
remove_content_field_from_tree_dict(dict_defensewiki)
save_file(filename=f"{path_folder_defense_wiki}/defensewiki_no_content.json", content=dict_defensewiki, file_type="json")


