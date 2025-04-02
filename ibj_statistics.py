##  Things we want to extract per page
# view_count: popularity of the page - in metadata
# word or line count: how much info we got on the page  - in metadata
# number of links, functional or not: how well documented is the page #TODO
# count how represented are languages across pages  - in metadata

import json
import re
import os
from collections import defaultdict
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

print(matplotlib.get_backend())  # module://backend_interagg


language_counts = defaultdict(int)


def extract_info(link_tree_defensewiki):
    data_list = []
    global language_counts
    if isinstance(link_tree_defensewiki, dict):
        for key, value_dict in link_tree_defensewiki.items():
            if isinstance(value_dict, dict):
                for key, value in value_dict.items():
                    if isinstance(value, dict):
                        if type(value["viewcount"]) is not str:
                            viewcount = float("nan")
                        else:
                            match = re.search(r"(\d[\d,]*)", value["viewcount"])
                            viewcount = (
                                int(match.group(1).replace(",", "")) if match else 0
                            )
                        data_list.append(
                            [
                                value["title"],
                                value["language"],
                                value["nbr_of_lines"],
                                value["nbr_of_words"],
                                viewcount,
                            ]
                        )  # to know it has been swapped nbr of lines and nbr of words

        # Create DataFrame
        df = pd.DataFrame(
            data_list,
            columns=["Title", "Language", "nbr_of_words", "nbr_of_lines", "Viewcount"],
        )
        df.set_index("Title", inplace=True)  # Set Title as index
        return df


# TODO it hasn't been annotated well, rerun the scraping_file? or replace strings ...


dir_plots = "/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/Plots"
# Load JSON file
with open(
    "/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/IBJ_documents/legal_country_documents/docs_in_md_json/defensewiki1_no_content.json",
    "r",
) as f:
    link_tree_defensewiki = json.load(f)

summary_defensewiki = extract_info(link_tree_defensewiki)
summary_defensewiki = summary_defensewiki.reset_index()  # [1252 rows x 5 columns]
summary_defensewiki.to_csv(
    "/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/Data/summary_defensewiki.csv",
    index=False,
)


# load and stats
summary_defensewiki = pd.read_csv(
    "/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/Data/summary_defensewiki.csv"
)

# Sort languages by decreasing count
summary_defensewiki["Language"].value_counts()
language_counts = summary_defensewiki["Language"].value_counts().reset_index()
language_counts.columns = ["Language", "Count"]

lang_map = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "ru": "Russian",
    "ar": "Arabic",
    "zh-cn": "Chinese (Simplified)",
    "pt": "Portuguese",
    "ko": "Korean",
    "it": "Italian",
    "fa": "Persian (Farsi)",
    "vi": "Vietnamese",
}

# Plot languages ----------------------
plt.figure(figsize=(10, 6))
palette = sns.color_palette("husl", n_colors=12)  # len(language_counts['Language'])
ax = sns.barplot(
    x="Language",
    y="Count",
    data=language_counts,
    palette=palette,
    order=language_counts["Language"],
    hue="Language",
)

for i, count in enumerate(language_counts["Count"]):
    ax.annotate(
        format(count, ","),  # Format count with commas
        (i, count),  # Use index position for x-axis
        ha="center",
        va="bottom",
        fontsize=10,
    )

plt.title("Language Distribution")
plt.xlabel("Language")
plt.ylabel("Count")
ax.set_xticklabels(
    [lang_map.get(lang, lang) for lang in summary_defensewiki["Language"].unique()],
    rotation=45,
)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.subplots_adjust(bottom=0.3)
plt.yscale("log")
plt.savefig(os.path.join(dir_plots, "plot_defensewiki_Languages.png"), dpi=300)
plt.show()


# Plot Viewcount ----------------------
summary_defensewiki_sorted = summary_defensewiki.sort_values(
    by="Viewcount", ascending=False
).head(50)
plt.figure(figsize=(20, 18))
palette = sns.color_palette("husl", n_colors=30)
sns.barplot(
    y="Viewcount",
    x="Title",
    data=summary_defensewiki_sorted,
    label="Viewcount",
    color="b",
)
plt.subplots_adjust(bottom=0.4)
plt.xticks(rotation=90)
plt.yscale("log")
plt.title("Pages sorted by Viewcount")
plt.savefig(os.path.join(dir_plots, "plot_defensewiki_Viewcounts.png"), dpi=300)
plt.show()


# Plot nbr_of_lines ----------------------
summary_defensewiki_sorted_lines = summary_defensewiki.sort_values(
    by="nbr_of_lines", ascending=False
).head(50)
plt.figure(figsize=(20, 18))
palette = sns.color_palette("husl", n_colors=30)
sns.barplot(
    y="nbr_of_lines",
    x="Title",
    data=summary_defensewiki_sorted_lines,
    label="nbr_of_lines",
    color="b",
)
plt.subplots_adjust(bottom=0.4)
plt.xticks(rotation=90)
plt.title("Pages sorted by Number of Lines")
plt.savefig(os.path.join(dir_plots, "plot_defensewiki_nbr_of_lines.png"), dpi=300)
plt.show()


# https://defensewiki.ibj.org/index.php?title=Code_de_Proc%C3%A9dure_P%C3%A9nale_du_B%C3%A9nin_(B%C3%A9nin_Criminal_Procedure_Code)

# TODO: check why nbr of words do not work and we have NaNs


# # print 10 first items
# print(json.dumps(dict(list(link_tree_defensewiki.items())[:1]), indent=4))
#
# print(f"\033[93m{json.dumps(link_tree_defensewiki, indent=4)}\033[0m")  # green color
#
# # Run the function
# extract_info(link_tree_defensewiki)


# key = "https://defensewiki.ibj.org/index.php?title=Core_Value_8:_Uses_proportionality_and_reflects_the_goals_of_reformation_and_rehabilitation/es"
# value_dict = link_tree_defensewiki[url][key]
#
# # Keep summary_defensewiki and clear all other variables
# for name in list(globals().keys()):
#     if name != 'summary_defensewiki':
#         del globals()[name]
