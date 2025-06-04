# LIBRARIES ---------------------------------------------------
from src.openai_utils import openai_client
from tqdm import tqdm
import src
import importlib
importlib.reload(src.query_functions)
from src.chromadb_utils import load_collection, perform_similarity_search_in_collection
from src.query_functions import (
    get_openai_response,
    format_prompt_for_completeness_check,
    get_completeness_keypoints
)
from src.file_manager import get_country_names, save_completeness_result, build_context_string_from_retrieve_documents
from src.config import Paths

# MAIN ---------------------------------------------------

with open(Paths.PATH_FILE_PROMPT_COMPLETENESS, "r") as file:
    prompt_completeness = file.read()

with open(Paths.PATH_FILE_SYSTEM_PROMPT_COMPLETENESS, "r") as file:
    system_prompt = file.read()

completeness_keypoints = get_completeness_keypoints(completeness_checklist_filepath = Paths.PATH_MD_FILE_COMPLETENESS_KEYPOINTS)
collection = load_collection(Paths.PATH_CHROMADB, Paths.COLLECTION_NAME)

country_names = get_country_names(country_names_filepath="data/interim/country_names_1.txt")
country_names = ["Burundi"]  # TODO remove this line to run for all countries

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

            wiki_content = perform_similarity_search_in_collection(
                collection,
                query_text=keypoint_to_check,
                metadata_param="link",
                metadata_value=f"https://defensewiki.ibj.org/index.php?title={country}",
                number_of_results_to_retrieve=5,
            )

            database_content = perform_similarity_search_in_collection(
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
                client=openai_client,
                categorize_system_prompt=system_prompt,
                prompt=prompt,
                model="gpt-4o-mini",
                temperature=0.1,
            )

            completeness_assessment = answer.split("**")[2].replace("\n", "")
            out_jsonfile = f"{Paths.PATH_FOLDER_COMPLETENESS}/{country}.json"
            out_md_file = f"{Paths.PATH_FOLDER_COMPLETENESS}/{country}_answer.md"
            out_summary_file = f"{Paths.PATH_FOLDER_COMPLETENESS}/{country}_summary.md"
            save_completeness_result(
                country,
                keypoint_to_check,
                wiki_content,
                database_content,
                answer,
                out_jsonfile=out_jsonfile,
                out_md_file=out_md_file,
            )

            with open(out_summary_file, "a", encoding="utf-8") as file:  # save summary
                file.write(f"Keypoint '{point}' covered?  {completeness_assessment} \n\n")
