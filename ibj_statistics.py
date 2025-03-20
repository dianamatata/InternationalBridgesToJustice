##  Things we want to extract per page
# view_count: popularity of the page - in metadata
# word or line count: how much info we got on the page  - in metadata
# number of links, functional or not: how well documented is the page #TODO
# count how represented are languages across pages  - in metadata

# TODOLIST

# 1: scrape all IBJ:
     # 0: check if link working or not?
# 2: plot statistics

import json
import re
from collections import defaultdict
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


# Load JSON file
with open("/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/IBJ_documents/legal_country_documents/docs_in_md_json/defensewiki1_no_content.json", "r") as f:
    link_tree_defensewiki = json.load(f)

# Initialize counters
language_counts = defaultdict(int)
total_views = 0
page_counts = 0
viewcounts = []

# Recursive function to extract data

def extract_info(link_tree_defensewiki):
    data_list = []
    global total_views, page_counts, language_counts,viewcounts
    if isinstance(link_tree_defensewiki, dict):
        for key, value_dict in link_tree_defensewiki.items():
            print(key)
            if isinstance(value_dict, dict):
                for key, value in value_dict.items():
                    print(key)
                    if isinstance(value, dict):
                        print(value["viewcount"])
                        if type(value["viewcount"]) is not str:
                            viewcount = float('nan')
                        else:
                            match = re.search(r"(\d[\d,]*)", value["viewcount"])
                            viewcount = int(match.group(1).replace(",", "")) if match else 0
                        data_list.append([value['title'], value['language'], value['nbr_of_lines'],value['nbr_of_words'],viewcount])

        # Create DataFrame
        df = pd.DataFrame(data_list, columns=["Title", "Language", "Viewcount", "nbr_of_lines", "nbr_of_words"])
        df.set_index("Title", inplace=True)  # Set Title as index
        return df


summary_defensewiki = extract_info(link_tree_defensewiki)

summary_defensewiki['Language'].value_counts()

summary_defensewiki.to_csv('/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/summary_defensewiki.csv', index=False)

# Language
# en       925
# es       163
# fr       115
# ru        24
# ar        10
# zh-cn      7
# pt         4
# ko         1
# it         1
# fa         1
# vi         1

# es – Spanish
# fr – French
# ru – Russian
# ar – Arabic
# zh-cn – Chinese (Simplified)
# pt – Portuguese
# ko – Korean
# it – Italian
# fa – Persian (Farsi)
# vi – Vietnamese
import matplotlib
matplotlib.use('Qt5Agg')  # Switch to Qt5Agg backend after installing PyQt5 or PySide2
import matplotlib.pyplot as plt
import seaborn as sns

plt.show()

# Set up the plot with a clear size
plt.figure(figsize=(10, 6))
sns.countplot(x='Language', data=summary_defensewiki, palette="Set2", hue='Viewcount')
plt.title('Language Distribution')
plt.xlabel('Language')
plt.ylabel('Count')
# Rotate the x-axis labels for better readability if needed
plt.xticks(rotation=45)
# Display the plot
plt.show()



sns.set_color_codes("pastel")
plt = sns.barplot(x="Viewcount", y="Title", data=summary_defensewiki,
            label="Title", color="b")            # Recurse into nested structures
plt.show()

# print 10 first items
print(json.dumps(dict(list(link_tree_defensewiki.items())[:1]), indent=4))



print(f"\033[93m{json.dumps(link_tree_defensewiki_test, indent=4)}\033[0m")  # green color

# Run the function
extract_info(link_tree_defensewiki_test)


# Compute statistics
avg_views = total_views / page_counts if page_counts > 0 else 0

# Print results
print(f"Total Pages: {page_counts}")
print(f"Total Views: {total_views}")
print(f"Average Views per Page: {avg_views:.2f}")
print("Language Distribution:", dict(language_counts))

url="https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=1300&offset=0"
# key = "https://defensewiki.ibj.org/index.php?title=Core_Value_8:_Uses_proportionality_and_reflects_the_goals_of_reformation_and_rehabilitation/es"
# value_dict = link_tree_defensewiki[url][key]

# Keep summary_defensewiki and clear all other variables
for name in list(globals().keys()):
    if name != 'summary_defensewiki':
        del globals()[name]