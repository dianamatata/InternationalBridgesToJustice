import json
import os
from src.internationalbridgestojustice.openai_utils import build_batch_request
import openai
from dotenv import load_dotenv
from src.internationalbridgestojustice.get_response import GetResponse

load_dotenv()  # Load environment variables from .env file
openai_api_key = os.environ.get("OPENAI_API_KEY")
client = openai.OpenAI()


def get_chunks_in_english(jsonl_file_path: str, in_english: bool = True):
    if jsonl_file_path.endswith(".json"):
        with open(jsonl_file_path, "r", encoding="utf-8") as json_file:
            chunks = json.load(json_file)

    elif jsonl_file_path.endswith(".jsonl"):
        chunks = []
        with open(jsonl_file_path, "r", encoding="utf-8") as jsonl_file:
            for line in jsonl_file:
                chunks.append(json.loads(line))
    else:
        raise ValueError("File must be in JSON or JSONL format.")

    filtered_chunks_in_english = [
        c for c in chunks if c["metadata"]["language"] == "en"
    ]
    filtered_chunks_not_in_english = [
        c for c in chunks if c["metadata"]["language"] != "en"
    ]
    return filtered_chunks_in_english, filtered_chunks_not_in_english


def get_chunks_for_one_country(chunks: list[dict], country: str):
    filtered_chunks = [c for c in chunks if c["metadata"]["country"] == country]
    return filtered_chunks


def create_new_chunks_from_translated_results(
    chunks_not_in_english: list[dict], parsed_results: list[dict]
) -> list[dict]:
    new_chunks = []
    for result in parsed_results:
        print(f"Processing result with custom_id: {result['custom_id']}")
        custom_id = result["custom_id"]
        chunk_id = custom_id.split(" ")[1]
        translated_content = result["response"]["body"]["choices"][0]["message"][
            "content"
        ]

        # Find the original chunk based on custom_id
        original_chunk = next(
            (chunk for chunk in chunks_not_in_english if chunk["title"] == chunk_id),
            None,
        )

        if original_chunk:
            print(f"Original Chunk found: {original_chunk}")

            translated_chunk = {
                "title": original_chunk["title"],
                "content": translated_content,
                "metadata": original_chunk["metadata"].copy(),
            }
            translated_chunk["metadata"]["language"] = "en"
            new_chunks.append(translated_chunk)

    return new_chunks


class Translator:
    def __init__(
        self, model_name: str = "gpt-4o-mini", cache_dir: str = "./data/cache/"
    ):
        self.model_name = model_name
        cache_dir = os.path.join(cache_dir, self.model_name)
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_file = os.path.join(cache_dir, "translation_cache.json")
        self.get_model_response = GetResponse(
            cache_file=self.cache_file,
            model_name=self.model_name,
            max_tokens=1000,
            temperature=0.2,
        )
        self.system_message = "You are a translator that preserves markdown formatting and the references/citations/sources."

    def create_batch_file_for_translation(
        self, jsonl_output_file_path: str, chunks: list
    ):
        with open(jsonl_output_file_path, "w", encoding="utf-8") as outfile:
            for i, chunk in enumerate(chunks):
                prompt_text = f"Translate the following Markdown file to English, keeping the formatting:\n\n{chunk['content']} and not translating the text in the sources and references (articles, links,...)"
                request = build_batch_request(
                    custom_id=f"translation {chunk['title']}",
                    system_prompt=self.system_message,
                    user_prompt=prompt_text,
                    temperature=0.2,
                    model=self.model_name,
                )

                outfile.write(json.dumps(request) + "\n")


def translate_to_english(self, md_text: str, cost_estimate_only=False):
    self.prompt_text = f"Translate the following Markdown file to English, keeping the formatting:\n\n{md_text} and not translating the text in the sources and references (articles, links,...)"
    response, prompt_tok_cnt, response_tok_cnt = self.get_model_response.get_response(
        self.system_message, self.prompt_text, cost_estimate_only
    )
    return response.choices[0].message.content, prompt_tok_cnt, response_tok_cnt
