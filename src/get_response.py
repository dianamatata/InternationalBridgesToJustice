import os
import json
import tiktoken
from openai import OpenAI

class GetResponse():
    # OpenAI model list: https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo
    def __init__(self, cache_file, model_name: str = "gpt-4o-mini", max_tokens=1000, temperature=0):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.cache_file = cache_file

        # invariant variables
        self.tokenizer = tiktoken.encoding_for_model("gpt-4")

        # model keys
        self.key = os.getenv("OPENAI_API_KEY_PERSONAL")
        self.client = OpenAI(api_key=self.key)
        self.seed = 1130

        # cache related
        self.cache_dict = self.load_cache()
        self.add_n = 0
        self.save_interval = 1
        self.print_interval = 20

    # Returns the response from the model given a system message and a prompt text.
    def get_response(self, system_message, prompt_text, response_format, cost_estimate_only=False):

        if cost_estimate_only:
            return None, self.tok_count(prompt_text)

        if "gpt" in self.model_name:
            message = [{"role": "system", "content": system_message},
                       {"role": "user", "content": prompt_text}]
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=message,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                seed=self.seed,
                response_format=response_format
            )
            response_content = response.choices[0].message.content.strip()
            total_cost = compute_chatgpt_4o_cost(response, self.model_name, verbose=True)
            return response_content, total_cost

    # Returns the number of tokens in a text string.
    def tok_count(self, text: str) -> int:
        num_tokens = len(self.tokenizer.encode(text))
        return num_tokens

    def save_cache(self):
        # load the latest cache first, since if there were other processes running in parallel, cache might have been updated
        for k, v in self.load_cache().items():
            self.cache_dict[k] = v
        with open(self.cache_file, "w") as f:
            json.dump(self.cache_dict, f, indent=4)

    def load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as f:
                # load a json file
                cache = json.load(f)
                print(f"Loading cache from {self.cache_file}...")
        else:
            cache = {}
        return cache

def compute_chatgpt_4o_cost(response, model, verbose: bool = False) -> float:
    # costs="https://openai.com/api/pricing/"
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens

    if model == "gpt-4o-mini":
        cost_per_1M_input_tokens = 0.15
        cost_per_1M_output_tokens = 0.60
    elif model == "gpt-4o":
        cost_per_1M_input_tokens = 2.5
        cost_per_1M_output_tokens = 10
    elif model == "gpt-4.1-mini":
        cost_per_1M_input_tokens = 0.4
        cost_per_1M_output_tokens = 1.60

    total_cost = (input_tokens / 1e6) * cost_per_1M_input_tokens
    total_cost += (output_tokens / 1e6) * cost_per_1M_output_tokens

    if verbose:
        print(f"Total input tokens: {input_tokens}")
        print(f"Total output tokens: {output_tokens}")
        print(f"Total tokens: {input_tokens + output_tokens}")
        print(f"Estimated cost: ${total_cost:.4f}")

    return total_cost