# LIBRARIES ---------------------------------------------------
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
openai_api_key = os.environ.get("OPENAI_API_KEY")

from openai import OpenAI
from tqdm import tqdm
import importlib  # Use importlib.reload() to re-import your module after editing it
import src
importlib.reload(src.query_functions)
from src.query_functions import (
    load_chroma_collection,
    build_context_string_from_retrieve_documents,
    perform_similarity_search_metadata_filter,
    get_openai_response,
    format_prompt_for_completeness_check,
    get_completeness_keypoints
)
from src.file_manager import get_country_names, save_completeness_result


# MAIN ---------------------------------------------------
client = OpenAI()

CHROMA_PATH = "../data/chroma_db"
COLLECTION_NAME = "legal_collection"
collection = load_chroma_collection(CHROMA_PATH, COLLECTION_NAME)

country_names = get_country_names(country_names_filepath="data/interim/country_names_1.txt")
country_names = ["Burundi"]  # TODO remove this line to run for all countries

completeness_keypoints = get_completeness_keypoints(completeness_checklist_filepath ="data/raw/IBJ_docs/Completeness_checklist.md")

with open("data/prompts/prompt_completeness.md", "r") as f:
    prompt_completeness = f.read()

system_prompt = "You are a critical legal analyst tasked with evaluating whether a legal wiki chapter adequately addresses a specific legal keypoint. Your response must be precise, structured, and based on legal reasoning. When relevant, cite and summarize laws from the provided legal database. Avoid vague language and clearly distinguish between complete, partial, or missing legal coverage."
chapter = ""
for country in country_names:
    for point in tqdm(completeness_keypoints):
        # if point is not a new chapter (look at the indentation to know)
        indent = len(point) - len(
            point.lstrip()
        )
        if indent == 0:
            chapter = point
        if indent > 0:
            print(f"\033[93m{chapter}:\033[0m\033[94m{point}\033[0m")
            keypoint_to_check = f"{chapter}: {point}"

            wiki_content = perform_similarity_search_metadata_filter(
                collection,
                query_text=keypoint_to_check,
                metadata_param="link",
                metadata_value=f"https://defensewiki.ibj.org/index.php?title={country}",
                number_of_results_to_retrieve=5,
            )

            database_content = perform_similarity_search_metadata_filter(
                collection,
                query_text=keypoint_to_check,
                metadata_param="country",
                metadata_value=country,
                number_of_results_to_retrieve=5,
            )

            context_database = build_context_string_from_retrieve_documents(database_content)
            context_wiki = build_context_string_from_retrieve_documents(wiki_content)

            prompt = format_prompt_for_completeness_check(
                prompt=prompt_completeness,
                keypoint=keypoint_to_check,
                wiki_content=context_wiki,
                database_content=context_database,
            )

            answer = get_openai_response(
                client=client,
                categorize_system_prompt=system_prompt,
                prompt=prompt,
                model="gpt-4o-mini",
                temperature=0.1,
            )

            completeness_assessment = answer.split("**")[2].replace("\n", "")
            out_jsonfile = f"data/completeness/{country}.json"
            out_md_file = f"data/completeness/{country}_answer.md"
            out_summary_file = f"data/completeness/{country}_summary.md"
            save_completeness_result(
                country,
                keypoint_to_check,
                wiki_content,
                database_content,
                answer,
                out_jsonfile=out_jsonfile,
                out_md_file=out_md_file,
            )  # save as json file and md file

            with open(out_summary_file, "a", encoding="utf-8") as f:  # save summary
                f.write(f"Keypoint '{point}' covered?  {completeness_assessment} \n\n")
