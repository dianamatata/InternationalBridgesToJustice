from src.internationalbridgestojustice.openai_utils import (
    get_openai_response,
)
from src.internationalbridgestojustice.chromadb_utils import (
    perform_similarity_search_in_collection,
)
from src.internationalbridgestojustice.file_manager import (
    build_context_string_from_retrieve_documents,
)
import json
from src.internationalbridgestojustice.config import Paths

# __init__ method: Initializes a chunk object with the title, content, mime_type, and metadata.
# __repr__ method: Provides a formal string representation of the chunk for debugging.
# __str__ method: Provides a human-readable summary of the chunk, showing the title and a preview of the content.


class KeypointEvaluation:
    def __init__(
        self,
        country: str,
        keypoint: str,
        system_prompt: str,
        model: str = "gpt-4o-mini",
        collection=None,
        lazy=True,
    ):
        self.country = country
        self.keypoint_description = keypoint["Description"]
        self.keypoint = keypoint["Keypoint"]
        self.custom_id = f"{country}-{self.keypoint}"
        self.out_answer_file = (
            f"{Paths.PATH_FOLDER_COMPLETENESS}/{self.country}_completeness.json"
        )
        self.out_log_file = (
            f"{Paths.PATH_FOLDER_COMPLETENESS}/{self.country}_completeness_log.json"
        )
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
        return f"Country: {self.country}\nKeypoint: {self.keypoint}\nAnswer: {self.answer[:200]}..."

    def to_dict(self):
        return {
            "country": self.country,
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
            query_text=self.keypoint_description,
            metadata_param="link",
            metadata_value=f"https://defensewiki.ibj.org/index.php?title={self.country}",
            number_of_results_to_retrieve=5,
        )

        self.database_content = perform_similarity_search_in_collection(
            collection,
            query_text=self.keypoint_description,
            metadata_param="country",
            metadata_value=self.country,
            number_of_results_to_retrieve=5,
        )

    def define_prompt(self, prompt_template: str):
        self.prompt = prompt_template.format(
            keypoint=self.keypoint,
            keypoint_description=self.keypoint_description,
            wiki_content=build_context_string_from_retrieve_documents(
                self.wiki_content
            ),
            database_content=build_context_string_from_retrieve_documents(
                self.database_content
            ),
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
        self.answer = json.loads(self.answer)

    def batch_check_completeness(
        self, client, keypoints: list[str], temperature: float = 0.1
    ):
        # TODO: issue should it be sequencial in 2 steps, first design prompt, then call to get answer?
        # TODO get_openai_batch_response does not exist

        # Prepare all user prompts (for example, formatted keypoints)
        prompts = [f"Keypoint: {kp}" for kp in keypoints]

        # Call batch API
        answers = get_openai_batch_response(
            client=client,
            categorize_system_prompt=self.system_prompt,
            prompts=prompts,
            response_format=self.response_format,
            model=self.model,
            temperature=temperature,
        )

        # Parse all JSON answers
        parsed_answers = [json.loads(ans) for ans in answers]

        return parsed_answers

    def save_log_as_json(self):
        log_data = {
            "country": self.country,
            "keypoint": self.keypoint,
            "answer": self.answer,
            "wiki_content": {
                "ids": self.wiki_content.get("ids", [[]])[0]
                if self.wiki_content.get("ids")
                else None,
                "distances": self.wiki_content.get("distances", [[]])[0]
                if self.wiki_content.get("distances")
                else None,
                "documents": self.wiki_content.get("documents", [[]])[0]
                if self.wiki_content.get("documents")
                else None,
            },
            "database_content": {
                "ids": self.database_content.get("ids", [[]])[0]
                if self.database_content.get("ids")
                else None,
                "distances": self.database_content.get("distances", [[]])[0]
                if self.database_content.get("distances")
                else None,
            },
        }

        with open(self.out_log_file, "a", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

    def save_answer_as_json(self):
        with open(self.out_answer_file, "a", encoding="utf-8") as json_file:
            json.dump(self.answer, json_file, indent=2)


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
            "description": "The original keypoint.",
        },
        "Keypoint_Description": {
            "type": "string",
            "description": "The original keypoint description.",
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
                "items": {"type": "string"},
            },
            "description": " For each sentence of the chapter, provide a list of extracted claims",
        },
        "All_Claims ": {
            "type": "array",
            "items": {"type": "string"},
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
                        "description": "The sentence from which claims are extracted.",
                    },
                    "claims": {
                        "type": "array",
                        "description": "List of claim dictionaries extracted from the sentence.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "claim": {
                                    "type": "string",
                                    "description": "The claim extracted from the sentence.",
                                },
                                "decision": {
                                    "type": "string",
                                    "enum": [
                                        "Supported",
                                        "Contradicted",
                                        "Inconclusive",
                                    ],
                                    "description": "The claim extracted from the sentence.",
                                },
                                "full_answer": {
                                    "type": "string",
                                    "description": "Specific laws or legal chapters to justify your decision if applicable (not necessary for Inconclusive).",
                                },
                                "sources": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Chunk titles that support the claim.",
                                },
                                "document_ids": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Chunk hashes that support the claim.",
                                },
                                "distances": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Distances of the chunks that support the claim.",
                                },
                            },
                            "required": [
                                "claim",
                                "decision",
                                "sources",
                                "document_ids",
                                "distances",
                            ],
                        },
                    },
                },
            },
        },
    },
}
