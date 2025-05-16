from src.query_functions import perform_similarity_search_metadata_filter, format_prompt_for_completeness_check, build_context_string_from_retrieve_documents, get_openai_response
import json
from src.config import path_folder_completeness

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
        self.out_jsonfile = f"{path_folder_completeness}/{self.country}.json"
        self.out_md_file = f"{path_folder_completeness}/{self.country}_answer.md"
        self.out_summary_file = f"{path_folder_completeness}/{self.country}_summary.md"
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
        self.prompt = format_prompt_for_completeness_check(
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
            f.write(f"Keypoint '{self.point}' covered?  {assessment} \n\n")

