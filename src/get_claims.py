import re
import os
import regex
from src.get_response import GetResponse

class ClaimExtractor():

    def __init__(self, model_name: str = "gpt-4o-mini", prompt_file: str = "data/prompts/prompt_claim_extraction.md", cache_dir: str = "./data/cache/"):
        self.model = None
        self.prompt_file = prompt_file
        cache_dir = os.path.join(cache_dir, model_name)
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_file = os.path.join(cache_dir, f"claim_extraction_cache.json")
        self.get_model_response = GetResponse(cache_file=self.cache_file,
                                              model_name=model_name,
                                              max_tokens=1000,
                                              temperature=0)
        self.system_message = "You are a helpful assistant who can extract verifiable atomic claims from a piece of text. Each atomic fact should be verifiable against reliable external world knowledge (e.g., via Wikipedia)"

    def scan_text_for_claims(self, response, cost_estimate_only=False):

        """
        Given a model output
        - split the response into sentences using spaCy > no, points now
        - snippet = (context1 = 0-3 sentence) <SOS>Sent<EOS> (context2 = 0-1 sentence)
        - call fact_extractor on each snippet
        """
        sentences = self.clean_text(response)
        sentences = sentences.split(".")

        all_facts_lst = []
        prompt_tok_cnt, response_tok_cnt = 0, 0         # keep track of token counts

        snippet_lst = []
        fact_lst_lst = []

        for i, sentence in enumerate(sentences):
            lead_sent = sentences[0]  # 1st sentence of the para
            context1 = " ".join(sentences[max(0, i - 3):i])
            sentence = f"<SOS>{sentences[i].strip()}<EOS>"
            context2 = " ".join(sentences[i + 1:i + 2])

            if len(sentences) <= 5:
                snippet = f"{context1.strip()} {sentence.strip()} {context2.strip()}".strip()
            else:
                snippet = f"{lead_sent.strip()} {context1.strip()} {sentence.strip()} {context2.strip()}".strip()

            snippet_lst.append(snippet)

            facts, prompt_tok_num, response_tok_num = self.fact_extractor_for_snippet(snippet, sentences[i].strip(),
                                                                                      cost_estimate_only=cost_estimate_only)
            prompt_tok_cnt += prompt_tok_num
            response_tok_cnt += response_tok_num

            if facts == None:
                fact_lst_lst.append([None])
                continue

        # deduplication
        fact_lst = []
        for fact in facts:
            if fact.strip() == "":
                continue
            # cases where GPT returns its justification
            elif fact.startswith("Note:"):
                continue
            elif fact not in all_facts_lst:
                all_facts_lst.append(fact.strip())
            fact_lst.append(fact.strip())
        fact_lst_lst.append(fact_lst)

        print(f"Returning facts and token counts for the whole response ...")
        return snippet_lst, fact_lst_lst, all_facts_lst, prompt_tok_cnt, response_tok_cnt

    def fact_extractor_for_snippet(self, snippet, sentence, cost_estimate_only=False):
        """
        snippet = (context1) <SOS>sentence<EOS> (context2)
        sentence = the sentence to be focused on
        """

        prompt_template = open(self.prompt_file, "r").read()
        prompt_text = prompt_template.format(snippet=snippet, sentence=sentence)
        response, prompt_tok_cnt, response_tok_cnt = self.get_model_response.get_response(self.system_message,
                                                                                          prompt_text,
                                                                                          cost_estimate_only)
        if not response or "No verifiable claim." in response:
            return None, prompt_tok_cnt, response_tok_cnt
        else:
            # remove itemized list
            claims = [x.strip().replace("- ", "") for x in response.split("\n")]
            # remove numbers in the beginning
            claims = [regex.sub(r"^\d+\.?\s", "", x) for x in claims]
            return claims, prompt_tok_cnt, response_tok_cnt

    def clean_text(text: str) -> str:
        text = text.strip()
        text = re.sub(r"\[\[.*?\]\]\(#.*?\)", "", text) # 1. Remove all [[...]](#cite_note-...) patterns
        text = text.replace('\n\n', '\n') # 2. Remove double newlines
        text = text.replace('**', '') # 3. Remove bold markers **
        text = re.sub(r'\s+', ' ', text).strip() # 4. Remove redundant spaces
        return text
