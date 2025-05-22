from src.file_manager import save_file
from src.scraping_functions import scrap_defensewiki_website, remove_content_field_from_tree_dict
from src.config import Paths
from src.countries_dict import title_to_country, substring_to_country

with open(Paths.FILE_COUNTRY_NAMES, "r", encoding="utf-8") as f:
    list_country_names = f.read().splitlines()

dict_defensewiki = scrap_defensewiki_website(
    url="https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=1300&offset=0",
    base_url=Paths.BASE_URL_DEFENSE_WIKI,
    list_country_names=list_country_names,
    out_folder=Paths.PATH_FOLDER_DEFENSE_WIKI,
    title_to_country=title_to_country,
    substring_to_country=substring_to_country,
    visited=None
)

save_file(filename=f"{Paths.PATH_FOLDER_DEFENSE_WIKI}/defensewiki_all.jsonl", content=dict_defensewiki, file_type="jsonl")
remove_content_field_from_tree_dict(dict_defensewiki)
save_file(filename=f"{Paths.PATH_FOLDER_DEFENSE_WIKI}/defensewiki_no_content.json", content=dict_defensewiki, file_type="json")