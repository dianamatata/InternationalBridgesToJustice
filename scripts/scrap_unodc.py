import requests # get url info
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time


# La page charge certains éléments dynamiquement via JavaScript.
# requests ne charge que le HTML statique, donc si le lien est généré après coup, il ne sera pas présent dans soup_base.

# TODO use the json file
# TODO scrap all the attachements
#  https://sherloc.unodc.org/cld/en/v3/sherloc/legdb/data.json?lng=en&criteria=%7B%22filters%22:%5B%5D,%22match%22:%22%22,%22startAt%22:0,%22sortings%22:%22%22%7D
# TODO search for all pdf links


# extract all the legal docs
out_folder = "Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/data/raw/unodc.org"
out_folder_2 = "Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/data/processed/unodc.org"

start_url = "https://sherloc.unodc.org/cld/en/v3/sherloc/legdb/index.html"


# Configuration du driver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Exécute en arrière-plan (facultatif)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Charger la page
start_url = "https://sherloc.unodc.org/cld/en/v3/sherloc/legdb/index.html"
driver.get(start_url)
time.sleep(5)  # Attendre que le JavaScript charge les éléments

# Récupérer le HTML après chargement
soup_base = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()



# Extraire tous les liens des pays
country_names = []
for link in soup_base.find_all("a", class_="cover-parent"):
    href = link.get("href", "")
    country = href.split('"')[9]
    country_names.append(country)
    print(country)


country = "Argentina"
country = "United Kingdom of Great Britain and Northern Ireland"
country.replace(' ','%20')

for country in country_names:
    link = ''.join([
        "https://sherloc.unodc.org/cld/v3/sherloc/legdb/search.html?lng=en#?c={%22filters%22:[{%22fieldName%22:%22en%23legislation@country_label_s%22,%22value%22:%22",
        country.replace(' ','%20'),
        "%22}],%22sortings%22:%22%22}"
    ])

# Charger la page
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(link)
time.sleep(5)  # Attendre que le JavaScript charge les éléments
# Récupérer le HTML après chargement
soup_base_2 = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

links_countrypage = soup_base_2.find_all("a", class_="cover-parent")
links_dict = []
for link in links_countrypage:
    title = link.get("title", "")  # Récupère le titre, s'il existe
    href = link.get("href", "")  # Récupère l'URL dans href

    # Ajouter le titre et l'URL au dictionnaire
    links_dict.append({"title": title, "href": href})

# Afficher le résultat
print(links_dict)
for link in links_dict:
    full_link = ''.join(["https://sherloc.unodc.org", link.get("href","").replace(' ','%20')]).replace('"','%22')
    driver.get(full_link)
    soup_base_3 = BeautifulSoup(driver.page_source, "html.parser")
    links_level_3 = soup_base_3.find_all("a", class_="cover-parent")


# TODO: add timer
# TODO: demander a IBJ de les contacter

# link = links_dict[1]
# real
https://sherloc.unodc.org/cld/en/v3/sherloc/legdb/legislationCollection.html?lng=en&tmpl=%22sherloc%22&country=%22GBR%22&title=%22Anti-Corruption%20Law%20(Revision%202019)%20(Cayman%20Islands)%22
# we get
https://sherloc.unodc.org/cld/en/v3/sherloc/legdb/legislationCollection.html?lng=en&tmpl=%22sherloc%22&country=%22GBR%22&title=%22Anti-Corruption%20Law%20(Revision%202019)%20(Cayman%20Islands)%22