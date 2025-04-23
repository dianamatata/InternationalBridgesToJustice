from query_database import (build_context_text,
                            load_chroma_collection,
                            perform_similarity_search_metadata_filter,
                            get_openai_response)
from ensuring_completeness_country_pages import format_prompt

# modules for OpenAI
import os
import json
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
openai_api_key = os.environ.get("OPENAI_API_KEY")
from openai import OpenAI


# DEFINE CLASS KeypointEvaluation ---------------------------------------------------


# __init__ method: Initializes a chunk object with the title, content, mime_type, and metadata.
# __repr__ method: Provides a formal string representation of the chunk for debugging.
# __str__ method: Provides a human-readable summary of the chunk, showing the title and a preview of the content.

class KeypointEvaluation:
    def __init__(self, country, chapter, point):
        self.country = country
        self.chapter = chapter
        self.point = point
        self.keypoint = f"{chapter}: {point}"
        self.out_jsonfile = f"data/completeness/{self.country}.json"
        self.out_md_file = f"data/completeness/{self.country}_answer.md"
        self.out_summary_file = f"data/completeness/{self.country}_summary.md"

    def __repr__(self):
        return f"<KeypointEvaluation({self.country}, {self.keypoint}...)>"

    def __str__(self):
        return f"Country: {self.country}\nChapter: {self.chapter}\nPoint: {self.point}\nAnswer: {self.answer[:200]}..."


    def _save_evaluation(self):
        """
        Save the answer to a JSON file.
        """
        country_keypoint = {
            "country": self.country,
            "keypoint": self.keypoint,
            "wiki_content": {
                "ids": self.wiki_content.get("ids", [[]])[0],
                "distances": self.wiki_content.get("distances", [[]])[0],
            },
            "database_content": {
                "ids": self.database_content.get("ids", [[]])[0],
                "distances": self.database_content.get("distances", [[]])[0],
            },
            "answer": self.answer,
            "completeness_assessment": self.answer.split("**")[2].replace("\n", "")
        }

        # save the answer in a json file
        with open(self.out_jsonfile, "a", encoding="utf-8") as json_file:
            json.dump(country_keypoint, json_file, indent=4)

        """
            Save the answer to a MD file.
        """

        with open(self.out_md_file, "a", encoding="utf-8") as f:
            f.write(f"# {self.country}\n\n")
            f.write(f"## {self.keypoint}\n\n")
            f.write(self.answer)
            f.write("\n\n\n\n")

        """
            Save the summary to a MD file.
        """

        with open(self.out_summary_file, "a", encoding="utf-8") as f:  # save summary
            f.write(f"Keypoint '{point}' covered?  {self.answer.split("**")[2].replace("\n", "")} \n\n")


# FUNCTIONS ---------------------------------------------------

# TODO: make prompt_completeness a global variable is it a good idea?
prompt_completeness = None

def load_prompt_completeness():
    global prompt_completeness # TODO: is it a good idea to have it global?
    with open("prompt_completeness.md", "r") as f:
        prompt_completeness = f.read()

load_prompt_completeness()




# general loading
client = OpenAI()

collection = load_chroma_collection("data/chroma_db", "legal_collection")
system_prompt = "You are a critical legal analyst tasked with evaluating whether a legal wiki chapter adequately addresses a specific legal keypoint. Your response must be precise, structured, and based on legal reasoning. When relevant, cite and summarize laws from the provided legal database. Avoid vague language and clearly distinguish between complete, partial, or missing legal coverage."

# create class item

country = "Burundi"
chapter = "7. Rights in prison"
point = '      4. Juveniles\n'
evaluation = KeypointEvaluation(country, chapter, point)

# TODO: save this pipeline as a self function!

evaluation.wiki_content = perform_similarity_search_metadata_filter(collection,
                                                         query_text=evaluation.keypoint,
                                                         metadata_param="link",
                                                         metadata_value=f"https://defensewiki.ibj.org/index.php?title={evaluation.country}",
                                                         n_results=5)

evaluation.database_content = perform_similarity_search_metadata_filter(collection,
                                                             query_text=evaluation.keypoint,
                                                             metadata_param="country",
                                                             metadata_value=evaluation.country,
                                                             n_results=5)

evaluation.prompt = format_prompt(
    prompt=prompt_completeness,
    keypoint=evaluation.keypoint,
    wiki_content=build_context_text(evaluation.wiki_content),
    database_content=build_context_text(evaluation.database_content)
)

evaluation.answer = get_openai_response(
    client=client,
    categorize_system_prompt=system_prompt,
    prompt=evaluation.prompt,
    model="gpt-4o-mini",
    temperature=0.1
)

evaluation.save_evaluation()  # save as json file and md file





hash_to_search='39b44e8d658b6a112d380b2dbe02397c050ac5c759c23c15847d9dd46b2c64d8'
selected_chunk = next((chunk for chunk in chunks if chunk['title'] == hash_to_search), None)

