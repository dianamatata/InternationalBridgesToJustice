import re
import os
import regex
import json
from src.internationalbridgestojustice.get_response import GetResponse
from src.internationalbridgestojustice.chromadb_utils import (
    perform_similarity_search_in_collection,
)

from src.internationalbridgestojustice.openai_utils import (
    get_openai_response,
    build_batch_request_with_schema,
)
from src.internationalbridgestojustice.file_manager import (
    build_context_string_from_retrieve_documents,
)


class ClaimExtractor:
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        prompt_file: str = "data/prompts/prompt_claim_extraction.md",
        cache_dir: str = "./data/cache/",
    ):
        self.model = model
        self.prompt_file = prompt_file
        cache_dir = os.path.join(cache_dir, model)
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_file = os.path.join(cache_dir, "claim_extraction_cache.json")
        self.get_model_response = GetResponse(
            cache_file=self.cache_file,
            model_name=self.model,
            max_tokens=1000,
            temperature=0,
        )
        self.system_prompt = "You are a helpful assistant who can extract verifiable atomic claims from a piece of text. Each atomic fact should be verifiable against reliable external world knowledge (e.g., via Wikipedia)"

    def scan_text_for_claims(self, response, cost_estimate_only=False):
        """
        Given a model output
        - split the response into sentences using spaCy > no, points now
        - snippet = (context1 = 0-3 sentence) <SOS>Sent<EOS> (context2 = 0-1 sentence)
        - call fact_extractor on each snippet
        """
        sentences = clean_text(response)
        sentences = [
            s.strip() for s in sentences.split(".") if s.strip() != ""
        ]  # remove empty sentences

        all_facts_lst = []
        total_cost = 0

        snippet_lst = []
        fact_lst_lst = []

        for i, sentence in enumerate(sentences):
            lead_sent = sentences[0]  # 1st sentence of the para
            context1 = " ".join(sentences[max(0, i - 3) : i])
            sentence = f"<SOS>{sentences[i].strip()}<EOS>"
            context2 = " ".join(sentences[i + 1 : i + 2])

            if len(sentences) <= 5:
                snippet = (
                    f"{context1.strip()} {sentence.strip()} {context2.strip()}".strip()
                )
            else:
                snippet = f"{lead_sent.strip()} {context1.strip()} {sentence.strip()} {context2.strip()}".strip()

            snippet_lst.append(snippet)

            facts, total_cost = self.fact_extractor_for_snippet(
                snippet, sentences[i].strip(), cost_estimate_only=cost_estimate_only
            )
            total_cost += total_cost

            if facts == None:
                fact_lst_lst.append([])
                continue

            # deduplication
            fact_lst = []
            for fact in facts:
                fact = fact.strip()
                if fact == "":
                    continue
                elif fact.startswith("Note:"):
                    continue
                elif fact not in all_facts_lst:
                    all_facts_lst.append(fact)
                fact_lst.append(fact)
            fact_lst_lst.append(fact_lst)

        print("Returning facts and token counts for the whole response ...")
        return (
            snippet_lst,
            fact_lst_lst,
            all_facts_lst,
            total_cost,
        )

    def fact_extractor_for_snippet(self, snippet, sentence, cost_estimate_only=False):
        """
        snippet = (context1) <SOS>sentence<EOS> (context2)
        sentence = the sentence to be focused on
        """

        prompt_template = open(self.prompt_file, "r").read()
        prompt_text = prompt_template.format(snippet=snippet, sentence=sentence)
        response, total_cost = self.get_model_response.get_response(
            self.system_prompt,
            prompt_text,
            response_format=None,
            cost_estimate_only=cost_estimate_only,
            verbose=False,
        )
        if not response or "No verifiable claim." in response:
            return None, total_cost
        else:
            # remove itemized list
            claims = [x.strip().replace("- ", "") for x in response.split("\n")]
            # remove numbers in the beginning
            claims = [regex.sub(r"^\d+\.?\s", "", x) for x in claims]
            return claims, total_cost

    def create_batch_file_for_extraction(
        self,
        custom_id: str,
        response: str,
        country: str,
        keypoint: str,
        jsonl_output_file_path: str,
        temperature: float = 0.2,
    ):
        """
        scan_text_for_claims is for direct processing, here we create a batch file for extraction
        """
        sentences = clean_text(response)
        sentences = [
            s.strip() for s in sentences.split(".") if s.strip() != ""
        ]  # remove empty sentences

        snippet_lst = []

        for i, sentence in enumerate(sentences):
            lead_sent = sentences[0]  # 1st sentence of the para
            context1 = " ".join(sentences[max(0, i - 3) : i])
            sentence = f"<SOS>{sentences[i].strip()}<EOS>"
            context2 = " ".join(sentences[i + 1 : i + 2])

            if len(sentences) <= 5:
                snippet = (
                    f"{context1.strip()} {sentence.strip()} {context2.strip()}".strip()
                )
            else:
                snippet = f"{lead_sent.strip()} {context1.strip()} {sentence.strip()} {context2.strip()}".strip()

            snippet_lst.append(snippet)

            prompt_template = open(self.prompt_file, "r").read()

            self.prompt = prompt_template.format(
                snippet=snippet, sentence=sentences[i].strip()
            )

            with open(jsonl_output_file_path, "a", encoding="utf-8") as outfile:
                request = build_batch_request_with_schema(
                    custom_id=f"{custom_id}--{i}",
                    system_prompt=self.system_prompt,
                    user_prompt=self.prompt,
                    schema=schema_extraction_for_batches,
                    schema_name="Extraction",
                    temperature=temperature,
                    model=self.model,
                )
                self.request = request
                outfile.write(json.dumps(request) + "\n")
        return request


def clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(
        r"\[\[.*?\]\]\(#.*?\)", "", text
    )  # 1. Remove all [[...]](#cite_note-...) patterns
    text = text.replace("\n\n", "\n")  # 2. Remove double newlines
    text = text.replace("**", "")  # 3. Remove bold markers **
    text = re.sub(r"\s+", " ", text).strip()  # 4. Remove redundant spaces
    return text


schema_extraction_for_batches = {
    "type": "object",
    "description": "Sentences Extracted",
    "properties": {
        "Country": {"type": "string", "description": "The country page."},
        "Keypoint": {"type": "string", "description": "The original keypoint."},
        "All_Claims ": {
            "type": "array",
            "items": {"type": "string"},
            "description": " All the extracted claims, with duplicates removed.",
        },
    },
    "required": [
        "Country",
        "Keypoint",
        "All_Claims",
    ],
    "additionalProperties": False,
}


# schema_extraction_for_batches = {
#     "type": "object",
#     "description": "Sentences Extracted",
#     "properties": {
#         "Country": {"type": "string", "description": "The country page."},
#         "Keypoint": {"type": "string", "description": "The original keypoint."},
#         "Claim_List": {
#             "type": "array",
#             "items": {
#                 "type": "array",
#                 "items": {"type": "string"},
#             },
#             "description": " For each sentence, provide a list of extracted claims",
#         },
#         "All_Claims ": {
#             "type": "array",
#             "items": {"type": "string"},
#             "description": " All the extracted claims, with duplicates removed.",
#         },
#     },
#     "required": [
#         "Country",
#         "Keypoint",
#         "Claim_List",
#         "All_Claims",
#     ],
#     "additionalProperties": False,
# }


class ClaimVerificator:
    def __init__(
        self,
        claim: str,
        model: str = "gpt-4o-mini",
        prompt_file: str = "data/prompts/prompt_claim_verification.md",
        cache_dir: str = "./data/cache/",
    ):
        self.claim = claim
        self.prompt_file = prompt_file
        self.prompt_template = open(self.prompt_file, "r").read()
        cache_dir = os.path.join(cache_dir, model)
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_file = os.path.join(cache_dir, "claim_extraction_cache.json")
        self.get_model_response = GetResponse(
            cache_file=self.cache_file,
            model_name=model,
            max_tokens=1000,
            temperature=0,
        )
        self.system_prompt = "You are a helpful assistant who can extract verifiable atomic claims from a piece of text. Each atomic fact should be verifiable against reliable external world knowledge (e.g., via Wikipedia)"

    def verify_claim(
        self,
        claim: str,
        collection,
        client,
        country: str,
    ):
        # TODO need to check that new collection is organized like that
        results = perform_similarity_search_in_collection(
            collection=collection,
            query_text=claim,
            metadata_param="country",
            metadata_value=country,
            number_of_results_to_retrieve=5,
        )
        context_text = build_context_string_from_retrieve_documents(results)
        prompt = self.format_prompt_for_claim_verification(
            prompt_template=self.prompt_template, claim=claim, context=context_text
        )
        answer = get_openai_response(client, prompt)

        return results, answer

    def create_batch_file_for_verification(
        self,
        claim: str,
        collection,
        client,
        prompt_claim_verification: str,
        metadata_param: str,
        metadata_value: str,
    ):
        results = perform_similarity_search_in_collection(
            collection=collection,
            query_text=claim,
            metadata_param=metadata_param,
            metadata_value=metadata_value,
            number_of_results_to_retrieve=5,
        )
        context_text = build_context_string_from_retrieve_documents(results)
        prompt = self.format_prompt_for_claim_verification(
            prompt_template=prompt_claim_verification, claim=claim, context=context_text
        )
        # answer = get_openai_response(client, prompt)

        return results, answer

    def format_prompt_for_claim_verification(
        prompt_template: str, claim: str, context: str
    ) -> str:
        return prompt_template.format(claim=claim, context=context)
