import json
import pandas as pd
import tiktoken
tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")

summary_defensewiki = pd.read_csv("../data/interim/summary_defensewiki.csv")
nbr_of_words = summary_defensewiki[summary_defensewiki["Language"] != "en"]["nbr_of_words"].sum()
print(f"Number of words not in English: {nbr_of_words}") # 1 008 229

with open(
        "../data/interim/defensewiki_all.json",
    "r",
) as f:
    link_tree_defensewiki = json.load(f)

tokens_for_not_english_pages_IBJ = open("../data/interim/dimension_files_not_english.txt", "a")
input_tokens = {}
value_dict = list(link_tree_defensewiki.items())[0][1]
for key, value in list(value_dict.items())[0:]:
    if isinstance(value, dict):
        if value['language'] != 'en':
            print(key)
            text = value['content']
            input_token = tokenizer.encode(text)
            input_tokens[key] = len(input_token)
            a = f"page: {key} \nlength in words: {len(text.split())} and in tokens: {len(input_token)}, language: {value['language']}\n\n"
            tokens_for_not_english_pages_IBJ.write(a)


values = input_tokens.values()
total_input_tokens = sum(values)
print(f"total_input_tokens: {total_input_tokens}")
tokens_for_not_english_pages_IBJ.write(f"total_input_tokens: {total_input_tokens}")
tokens_for_not_english_pages_IBJ.close()
