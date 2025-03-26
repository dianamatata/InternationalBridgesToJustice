# tutorial: https://github.com/pixegami/rag-tutorial-v2/blob/main/populate_database.py

import os
import json
from langchain_community.document_loaders import PyPDFDirectoryLoader # TODO: uninstall
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document

# ¨!!!!!!! recommendation: better than PyPDFDirectoryLoader
from langchain_pymupdf4llm import PyMuPDF4LLMLoader, PyMuPDF4LLMParser


loader = PyMuPDF4LLMLoader("example.pdf")
docs = loader.load()
print(docs[0].page_content)  # Extracted text


def load_documents(DATA_PATH):
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()


# 1. Load the PDF
# legal_pdf_path = "/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/IBJ_documents/legal_country_documents/raw_pdfs"
legal_pdf_path = "/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/IBJ_documents/legal_country_documents/raw_pdfs_2pages"
output_doc_path = "/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/IBJ_documents/legal_country_documents/docs_in_md_json"


# Print the list of PDFs
pdf_files = [f for f in os.listdir(legal_pdf_path) if f.endswith(".pdf")]
print("PDF Files:", pdf_files)

# To load all the documents at once
documents = load_documents(legal_pdf_path)

full_content = ""
metadata = []

for doc in documents:
    # each page of the pdf is a doc, meaning

    # 2 get Metadata and content for each page
    meta = doc.metadata
    print(f"\033[91m{json.dumps(doc.metadata, indent=4)}\033[0m")  # Red color

    content = doc.page_content
    # print(f"\033[92m{doc.page_content}\033[0m")  # Red color

    # 3 Add content to metadata
    metadata.append(doc.metadata)

    # doc.metadata["content"] = doc.page_content
    del doc.metadata["producer"]
    del doc.metadata["creator"]

    # 4. Save content to a Markdown file
    name = os.path.basename(meta["source"]).replace('.pdf', '') +  "_"  + str(meta["page"]) + "_" + str(meta["total_pages"])
    markdown_name = os.path.join(output_doc_path, name + ".md")
    with open(markdown_name, "w", encoding="utf-8") as md_file:
        md_file.write(f"# Full Document\n\n{doc.page_content}")  # Adds a title header for the whole document

    # # 5. Save metadata of single page to a JSON file
    # metafile = os.path.join(output_doc_path, "metadata.json")
    # with open(metafile, "w", encoding="utf-8") as json_file:
    #     json.dump(doc.metadata, json_file, indent=4)


# 5. Save ALL metadata to a JSON file
metafile = os.path.join(output_doc_path, "metadata.json")
with open(metafile, "w", encoding="utf-8") as json_file:
    json.dump(metadata, json_file, indent=4)

    print(f"\033[91m{json.dumps(metadata, indent=4)}\033[0m")  # Red color



print("Full PDF saved as Markdown and metadata saved as JSON.")

# # 2. Get the full content of the document
# full_content = ""
# for doc in documents:
#     full_content += doc.page_content + "\n\n"  # Concatenate all pages' content
#


# NEXT STEPS

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI  # Replace with your preferred LLM

# 2. Split text by paragraphs (double newlines)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # Adjust based on your needs
    chunk_overlap=50,  # Optional: Overlap for better context
    separators=["\n\n"]  # Splits by paragraphs
)

docs = text_splitter.split_documents(documents)

# 3. Send Chunks to LLM
llm = ChatOpenAI(model_name="gpt-4")  # Replace with your LLM
for doc in docs:
    response = llm.invoke(doc.page_content)
    print(response)

# 3. Save to Markdown
with open("output.md", "w", encoding="utf-8") as f:
    for doc in documents:
        f.write(f"## Paragraph\n\n{doc.page_content}\n\n")

