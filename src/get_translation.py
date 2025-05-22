import json
import os
from src.openai_utils import build_batch_request
import openai
from dotenv import load_dotenv
from src.get_response import GetResponse
load_dotenv()  # Load environment variables from .env file
openai_api_key = os.environ.get("OPENAI_API_KEY")
client = openai.OpenAI()

def get_chunks_not_in_english(json_file_path: str):
    with open(json_file_path, "r", encoding="utf-8") as json_file:
        chunks = json.load(json_file)
    filtered_chunks = [c for c in chunks if c['metadata']['language'] != 'en']
    return filtered_chunks

# def translate_to_english(md_text: str, client):
#     system_message = "You are a translator that preserves markdown formatting and the references/citations/sources."
#     prompt_text = f"Translate the following Markdown file to English, keeping the formatting:\n\n{md_text} and not translating the text in the sources and references (articles, links,...)"
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": system_message},
#             {"role": "user", "content": prompt_text}
#         ],
#         temperature=0.2,
#         seed=1130,
#     )
#     translated_text = response.choices[0].message.content
#     return translated_text

# def create_batch_file_for_translation(jsonl_output_file_path: str, chunks: list):
#     system_prompt = "You are a translator that preserves markdown formatting and the references/citations/sources."
#     with open(jsonl_output_file_path, "a", encoding="utf-8") as outfile:
#         for i, chunk in enumerate(chunks):
#             prompt_text = f"Translate the following Markdown file to English, keeping the formatting:\n\n{chunk['content']} and not translating the text in the sources and references (articles, links,...)"
#             request = build_batch_request(custom_id=f"translation {chunk['title']}", system_prompt=system_prompt,
#                                           user_prompt=prompt_text)
#             outfile.write(json.dumps(request) + "\n")

class Translator():

    def __init__(self, model_name: str = "gpt-4o-mini", cache_dir: str = "./data/cache/"):
        self.model_name = model_name
        cache_dir = os.path.join(cache_dir, self.model_name)
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_file = os.path.join(cache_dir, f"translation_cache.json")
        self.get_model_response = GetResponse(cache_file=self.cache_file,
                                              model_name=self.model_name,
                                              max_tokens=1000,
                                              temperature=0.2)
        self.system_message = "You are a translator that preserves markdown formatting and the references/citations/sources."

    def translate_to_english(self, md_text: str, cost_estimate_only=False):
        self.prompt_text = f"Translate the following Markdown file to English, keeping the formatting:\n\n{md_text} and not translating the text in the sources and references (articles, links,...)"
        response, prompt_tok_cnt, response_tok_cnt = self.get_model_response.get_response(self.system_message,
                                                                                          self.prompt_text,
                                                                                          cost_estimate_only)
        return response.choices[0].message.content, prompt_tok_cnt, response_tok_cnt

    def create_batch_file_for_translation(self, jsonl_output_file_path: str, chunks: list):
        with open(jsonl_output_file_path, "a", encoding="utf-8") as outfile:
            for i, chunk in enumerate(chunks):
                prompt_text = f"Translate the following Markdown file to English, keeping the formatting:\n\n{chunk['content']} and not translating the text in the sources and references (articles, links,...)"
                request = build_batch_request(custom_id=f"translation {chunk['title']}",
                                              system_prompt=self.system_message,
                                              user_prompt=prompt_text,
                                              temperature=0.2,
                                              model=self.model_name)

                outfile.write(json.dumps(request) + "\n")

