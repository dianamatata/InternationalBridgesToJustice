from scripts.claim_verification import (
    build_context_string_from_retrieve_documents,
    load_chroma_collection,
    perform_similarity_search_metadata_filter,
    get_openai_response,
)
from ensuring_completeness_country_pages import (format_prompt,
                                                 get_completeness_checklist)

# modules for OpenAI
import os
import json
from tqdm import tqdm  # make your loops show a smart progress meter
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
openai_api_key = os.environ.get("OPENAI_API_KEY")
from openai import OpenAI


# DEFINE CLASS KeypointEvaluation ---------------------------------------------------


# __init__ method: Initializes a chunk object with the title, content, mime_type, and metadata.
# __repr__ method: Provides a formal string representation of the chunk for debugging.
# __str__ method: Provides a human-readable summary of the chunk, showing the title and a preview of the content.


class KeypointEvaluation:
    def __init__(self, country, chapter, point, collection=None, lazy=True):
        self.country = country
        self.chapter = chapter
        self.point = point
        self.custom_id = f"{country}-{chapter}-{point}"
        self.keypoint = f"{chapter}: {point}"
        self.out_jsonfile = f"data/completeness/{self.country}.json"
        self.out_md_file = f"data/completeness/{self.country}_answer.md"
        self.out_summary_file = f"data/completeness/{self.country}_summary.md"
        self.wiki_content = None
        self.database_content = None
        self.answer = None
        if not lazy:
            if collection is None:
                raise ValueError("collection must be provided if lazy=False")
            self._run_similarity_searches(collection)

    def __repr__(self):
        return f"<KeypointEvaluation({self.country}, {self.keypoint}...)>"

    def __str__(self):
        return f"Country: {self.country}\nChapter: {self.chapter}\nPoint: {self.point}\nAnswer: {self.answer[:200]}..."


    def to_dict(self):
        return {
            "country": self.country,
            "chapter": self.chapter,
            "point": self.point,
            "custom_id": self.custom_id,
            "keypoint": self.keypoint,
            "out_jsonfile": self.out_jsonfile,
            "out_md_file": self.out_md_file,
            "out_summary_file": self.out_summary_file,
            "wiki_content": self.wiki_content,
            "database_content": self.database_content,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def _run_similarity_searches(self, collection):
        self.wiki_content = perform_similarity_search_metadata_filter(
            collection,
            query_text=self.keypoint,
            metadata_param="link",
            metadata_value=f"https://defensewiki.ibj.org/index.php?title={self.country}",
            number_of_results_to_retrieve=5,
        )

        self.database_content = perform_similarity_search_metadata_filter(
            collection,
            query_text=self.keypoint,
            metadata_param="country",
            metadata_value=self.country,
            number_of_results_to_retrieve=5,
        )

    def ensure_loaded(self, collection):
        if self.wiki_content is None or self.database_content is None:
            self._run_similarity_searches(collection)

    def define_prompt(self, prompt_completeness):
        self.prompt = format_prompt(
            prompt_template=prompt_completeness,
            keypoint=self.keypoint,
            wiki_content=build_context_string_from_retrieve_documents(self.wiki_content),
            database_content=build_context_string_from_retrieve_documents(self.database_content),
        )

    def check_completeness(
        self, client, system_prompt, model="gpt-4o-mini", temperature=0.1
    ):

        self.answer = get_openai_response(
            client=client,
            categorize_system_prompt=system_prompt,
            prompt=self.prompt,
            model=model,
            temperature=temperature,
        )

    # the underscore in front of _run_similarity_searches is a Python naming convention to indicate that the method is
    # intended for internal use only (a "private" or "protected" method by convention), whereas ensure_loaded is likely
    # intended to be used externally, as part of the class's public interface.

    def build_batch_request(self, custom_id: str, system_prompt: str, user_prompt: str, temperature: float = 0.1):
        return {
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature,
                "max_tokens": 1000
            }
        }

    def save_evaluation(self):
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
            "completeness_assessment": self.answer.split("**")[2].replace("\n", ""),
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
            assessment = self.answer.split("**")[2].replace("\n", "")
            f.write(f"Keypoint '{point}' covered?  {assessment} \n\n")


# FUNCTIONS ---------------------------------------------------

# TODO: make prompt_completeness a global variable is it a good idea?
prompt_completeness = None

def load_prompt_completeness():
    global prompt_completeness  # TODO: is it a good idea to have it global?
    with open("../data/prompts/prompt_completeness.md", "r") as f:
        prompt_completeness = f.read()


# MAIN ---------------------------------------------------
# general loading
client = OpenAI()
legal_collection = load_chroma_collection("../data/chroma_db", "legal_collection")
system_prompt = "You are a critical legal analyst tasked with evaluating whether a legal wiki chapter adequately addresses a specific legal keypoint. Your response must be precise, structured, and based on legal reasoning. When relevant, cite and summarize laws from the provided legal database. Avoid vague language and clearly distinguish between complete, partial, or missing legal coverage."
load_prompt_completeness()
keypoints = get_completeness_checklist()


# batch submission  ----------------------------------------
outfile_name = ("data/completeness/batch_input.jsonl")
with open(outfile_name, "w") as outfile:
    countries = ["India"]  # TODO remove this line to run for all countries
    chapter = ""
    for country in countries:
        for point in tqdm(keypoints[10:13]): # TODO change this line to run for all keypoints
            indent = len(point) - len(
                point.lstrip()
            )
            if indent == 0:
                chapter = point
                print(chapter)
            if indent > 0:
                print(f"\033[92m{country}: \033[0m\033[93m{chapter}: \033[0m\033[94m{point}\033[0m")
                keypoint_to_check = f"{chapter}: {point}"
                evaluation = KeypointEvaluation(country, chapter, point, collection=legal_collection, lazy=True)
                evaluation.ensure_loaded(legal_collection)
                evaluation.define_prompt(prompt_completeness)

                request = evaluation.build_batch_request(
                    custom_id=f"{country}-{chapter}-{point}",
                    system_prompt=system_prompt,
                    user_prompt=evaluation.prompt,
                )

                outfile.write(json.dumps(request) + "\n")

                # Save
                with open("data/completeness/keypoints.json", "a") as f:
                    json.dump(evaluation.to_dict(), f)




# DEBUGGING ---------------------------------------------------
# evaluation.custom_id=f"{country}-{chapter}-{point}"
# evaluation.wiki_content = wiki_content
# evaluation.database_content = database_content
# create class item
# country = "Burundi"
# chapter = "7. Rights in prison"
# point = "      4. Juveniles\n"
evaluation = KeypointEvaluation(
    country, chapter, point, collection=legal_collection, lazy=True
)
evaluation.ensure_loaded(legal_collection)  # Ensure the content is loaded
evaluation.define_prompt(prompt_completeness)
evaluation.check_completeness(
    client, system_prompt, model="gpt-4o-mini", temperature=0.1
)
evaluation.save_evaluation()


hash_to_search = "39b44e8d658b6a112d380b2dbe02397c050ac5c759c23c15847d9dd46b2c64d8"
selected_chunk = next(
    (chunk for chunk in chunks if chunk["title"] == hash_to_search), None
)


# Load if one element
# with open("data/completeness/keypoints.json", "r") as f:
#     data = json.load(f)
#     loaded_instance = KeypointEvaluation.from_dict(data)


