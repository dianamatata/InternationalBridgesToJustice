from src.query_functions import format_prompt_for_completeness_check
from src.openai_utils import get_openai_response
from src.chromadb_utils import perform_similarity_search_in_collection
from src.file_manager import build_context_string_from_retrieve_documents
import json
from src.config import Paths

# __init__ method: Initializes a chunk object with the title, content, mime_type, and metadata.
# __repr__ method: Provides a formal string representation of the chunk for debugging.
# __str__ method: Provides a human-readable summary of the chunk, showing the title and a preview of the content.

class KeypointEvaluation:
    def __init__(self, country: str, chapter: str, point: str, system_prompt: str, model: str = "gpt-4o-mini", collection=None, lazy=True):
        self.country = country
        self.chapter = chapter
        self.point = point
        self.custom_id = f"{country}-{chapter}-{point}"
        self.keypoint = f"{chapter}: {point}"
        self.out_jsonfile = f"{Paths.PATH_FOLDER_COMPLETENESS}/{self.country}.json"
        self.out_md_file = f"{Paths.PATH_FOLDER_COMPLETENESS}/{self.country}_answer.md"
        self.out_summary_file = f"{Paths.PATH_FOLDER_COMPLETENESS}/{self.country}_summary.md"
        self.wiki_content = None
        self.database_content = None
        self.answer = None
        self.model = model
        self.system_prompt = system_prompt
        self.response_format = {
            "type": "json_schema",
            "json_schema": {"name": "CompletenessCheck", "schema": schema_completeness},
        }
        if not lazy:
            if collection is None:
                raise ValueError("collection must be provided if lazy=False")
            self.run_similarity_searches(collection)

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

    def run_similarity_searches(self, collection):
        self.wiki_content = perform_similarity_search_in_collection(
            collection,
            query_text=self.keypoint,
            metadata_param="link",
            metadata_value=f"https://defensewiki.ibj.org/index.php?title={self.country}",
            number_of_results_to_retrieve=5,
        )

        self.database_content = perform_similarity_search_in_collection(
            collection,
            query_text=self.keypoint,
            metadata_param="country",
            metadata_value=self.country,
            number_of_results_to_retrieve=5,
        )

    def define_prompt(self, prompt_completeness: str):
        self.prompt = format_prompt_for_completeness_check(
            prompt_template=prompt_completeness,
            keypoint=self.keypoint,
            wiki_content=build_context_string_from_retrieve_documents(self.wiki_content),
            database_content=build_context_string_from_retrieve_documents(self.database_content),
        )

    def check_completeness(self, client, temperature: float = 0.1):

        self.answer = get_openai_response(
            client=client,
            categorize_system_prompt=self.system_prompt,
            prompt=self.prompt,
            model=self.model,
            temperature=temperature,
            response_format=self.response_format,
        )

    def add_similarity_metadata_to_answer(self):
        self.answer["custom_id"] = self.custom_id
        self.answer["wiki_ids"] = self.wiki_content["ids"][0]
        self.answer["wiki_distances"] = self.wiki_content["distances"][0]
        self.answer["database_ids"] = self.database_content["ids"][0]
        self.answer["database_distances"] = self.database_content["distances"][0]

    # the underscore in front of _run_similarity_searches is a Python naming convention to indicate that the method is
    # intended for internal use only (a "private" or "protected" method by convention), whereas ensure_loaded is likely
    # intended to be used externally, as part of the class's public interface.

    def build_batch_request(self, custom_id: str, user_prompt: str, temperature: float = 0.1):
        return {
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature
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


schema_completeness = {
    "type": "object",
    "name": "CountryPageCompleteness",
    "description": "Country Page Rewritten after the completeness check",
    "properties": {
        "Country": {
            "type": "string",
            "description": "The country page.",
            "default": "Unknown",
        },
        "Keypoint": {
            "type": "string",
            "description": "The keypoint we check it is complete in the country page.",
        },
        "Classification": {
            "type": "string",
            "enum": ["Complete", "Needs refinement", "Missing"],
            "description": "A brief summary of the article's content and findings.",
        },
        "Missing_or_Unclear": {
            "type": "string",
            "description": "Briefly explain any gaps, ambiguities, or lack of legal grounding",
        },
        "Legal_Provisions_Check": {
            "type": "string",
            "enum": ["Present", "Missing"],
            "description": "Are relevant legal provisions available in the database? Answer with Present or Missing.",
        },
        "Summary_of_Relevant_Laws": {
            "type": "string",
            "description": "Clearly list the article numbers, titles, and explain their relevance.",
        },
        "Rewritten_Wiki_Chapter": {
            "type": "string",
            "description": " Rewrite the chapter to incorporate relevant legal content.",
        },
    },
}

schema_keypoints = {
    "type": "object",
    "name": "CountryPageCompleteness",
    "description": "Country Page Rewritten after the completeness check",
    "properties": {
        "Keypoint": {
            "type": "string",
            "description": "The original keypoint.",
        },
        "Description": {
            "type": "string",
            "description": "Description of the keypoint that help disambiguate and capture the intent",
        },
    },
}

schema_final = {
    "type": "object",
    "name": "CountryPage",
    "description": "Country Page Rewritten after the completeness check",
    "properties": {
        "Country": {
            "type": "string",
            "description": "The country page.",
            "default": "Unknown",
        },
        "Keypoint": {
            "type": "string",
            "description": "The keypoint we check it is complete in the country page.",
        },
        "Classification": {
            "type": "string",
            "description": "A brief summary of the article's content and findings.",
        },
        "Missing_or_Unclear": {
            "type": "string",
            "description": "Briefly explain any gaps, ambiguities, or lack of legal grounding",
        },
        "Legal_Provisions_Check:": {
            "type": "string",
            "description": "Are relevant legal provisions available in the database? Answer with Present or Missing.",
        },
        "Summary_of_Relevant_Laws": {
            "type": "string",
            "description": "Clearly list the article numbers, titles, and explain their relevance.",
        },
        "Rewritten_Wiki_Chapter ": {
            "type": "string",
            "description": " Rewrite the chapter to incorporate relevant legal content.",
        },
        "Claim_List": {
            "type": "array",
            "items": {
                "type": "array",
                "items": {
                    "type": "string"
                },
            },
            "description": " For each sentence of the chapter, provide a list of extracted claims",
        },
        "All_Claims ": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": " All the extracted claims of the chapter, with duplicates removed.",
        },
        "All_claims_per_sentence": {
            "type": "array",
            "description": "For each sentence of the chapter, provide a list of dictionaries (one dict per sentence) of extracted claims and their verification status",
            "items": {
                "type": "object",
                "properties": {
                    "sentence": {
                        "type": "string",
                        "description": "The sentence from which claims are extracted."
                    },
                    "claims": {
                        "type": "array",
                        "description": "List of claim dictionaries extracted from the sentence.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "claim": {
                                    "type": "string",
                                    "description": "The claim extracted from the sentence."
                                },
                                "decision": {
                                    "type": "string",
                                    "enum": ["Supported", "Contradicted", "Inconclusive"],
                                    "description": "The claim extracted from the sentence."
                                },
                                "full_answer": {
                                    "type": "string",
                                    "description": "Specific laws or legal chapters to justify your decision if applicable (not necessary for Inconclusive)."
                                },
                                "sources": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Chunk titles that support the claim."
                                },
                                "document_ids": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Chunk hashes that support the claim."
                                },
                                "distances": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Distances of the chunks that support the claim."
                                }
                            },
                            "required": ["claim", "decision", "sources", "document_ids", "distances"],
                        },
                    },
                },
            },
        },
    },
}
