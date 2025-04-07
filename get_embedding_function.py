# https://python.langchain.com/docs/integrations/text_embedding/openai/
# %pip install -qU langchain-openai
import getpass
import os
os.environ["OPENAI_API_KEY"] = (
    "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"
)


# Import with langchain framework
from langchain_openai import OpenAIEmbeddings

def get_embedding_function():

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large", dimension=1024
        # With the `text-embedding-3` class
        # of models, you can specify the size
        # of the embeddings you want returned.
        # dimensions=1024
        # il vaut mieux un grand embedding car dans tous les cas il calcule tout. sauf si on a trop de chunk et que ca pese lourd
    )
    return embeddings


# Import withOUT langchain framework

import openai

def get_embedding(text, model="text-embedding-3-large", dimension=1024):
    # Request the embedding from OpenAI API
    response = openai.Embedding.create(
        model=model,
        input=text
    )



# Function to get embedding, Chatgpt ---------------------

def get_embedding_function():
    # Define your OpenAI API key
    openai.api_key = "your-openai-api-key"  # Replace with your OpenAI API key

    def get_embedding(text, model="text-embedding-3-large", dimension=1024):
        # Request the embedding from OpenAI API
        response = openai.Embedding.create(
            model=model,
            input=text
        )

        # Extract the embedding vector from the response
        embedding = response['data'][0]['embedding']
        return embedding

    return get_embedding

# Example usage:
embedding_function = get_embedding_function()

# Getting the embedding of some text
text = "Your text to embed here"
embedding = embedding_function(text)
print(embedding)
