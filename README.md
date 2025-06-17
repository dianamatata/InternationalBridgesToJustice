# Artificial intelligence for legal assistance in developing countries

## Objectives

This project seeks to enhance access to legal resources for defenders and citizens in developing countries, where such resources are often fragmented or outdated. By integrating cutting-edge artificial intelligence (AI) technologies, including large language models (LLMs), into the public DefenseWiki platform, the project aims to automate and optimize the curation of legal knowledge.
 
The primary objective is to enhance DefenseWiki’s capabilities by incorporating AI to systematically improve the quality and relevance of its content. This will be achieved through web scraping of documents from DefenseWiki and external sources, combined with the implementation of an LLM-based agentic framework to verify and update legal claims.
 
Additionally, this project will lay the foundation for the future development of a virtual assistant that delivers tailored legal information to users. The end goal is to provide accurate and up-to-date legal knowledge across more than 130 countries, significantly reducing the time defenders spend on legal research. This will empower legal professionals, improve legal literacy, and promote a more equitable justice system globally.


## Repository overview

### Jupyter Notebooks to understand the different steps of the project 

* [plot_ibj_statistics.ipynb](notebooks%2Fplot_ibj_statistics.ipynb)
Run statistics on the data extracted on the DefenseWiki website

* [translate_chunk.ipynb](notebooks%2Ftranslate_chunk.ipynb)
Translate a chunk of text to English using OpenAI API

* [translate_Burundi_chunks.ipynb](notebooks%2Ftranslate_Burundi_chunks.ipynb)
Translate all a country page using batch processing with OpenAI API

* [test_completeness.ipynb](notebooks%2Ftest_completeness.ipynb)
Notebook to test the completeness check functionality of the IBJ project.

* [verify_one_claim.ipynb](notebooks%2Fverify_one_claim.ipynb)
Verify one claim from the Defense Wiki using OpenAI API and the legal database

### Utility scripts to run the different steps of the project

* [chromadb_utils.py](src%2Finternationalbridgestojustice%2Fchromadb_utils.py)
Utility functions to interact with the ChromaDB database, including creating collections, adding documents, and performing similarity searches.
* [chunking_functions.py](src%2Finternationalbridgestojustice%2Fchunking_functions.py)
Utility functions for chunking text, including creating hashes for chunks, splitting text into smaller pieces, and managing metadata.
* [config.py](src%2Finternationalbridgestojustice%2Fconfig.py)
Configuration file for the project, including API keys, paths for different files and directories, and other settings.
* [countries_dict.py](src%2Finternationalbridgestojustice%2Fcountries_dict.py)
As countries are not always named the same way in the Defense Wiki and in the IBJ database, this file contains a dictionary to map the country names from the Defense Wiki to the IBJ database.
* [file_manager.py](src%2Finternationalbridgestojustice%2Ffile_manager.py)
Utility functions for managing files, including reading and writing JSON files, handling file paths, and managing directories.
* [get_claims.py](src%2Finternationalbridgestojustice%2Fget_claims.py)
Utility functions for extracting claims from the Defense Wiki content, including identifying claims, extracting relevant information, and formatting the output.
* [get_completeness.py](src%2Finternationalbridgestojustice%2Fget_completeness.py)
Utility functions for checking the completeness of the Defense Wiki content, including identifying missing sections, verifying the presence of key information, and formatting the output.
* [get_responses.py](src%2Finternationalbridgestojustice%2Fget_responses.py)
Utility functions for interacting with the OpenAI API, including sending requests, handling responses, and managing API keys.
* [get_translation.py](src%2Finternationalbridgestojustice%2Fget_translation.py)
Utility functions for translating text using the OpenAI API, including handling different languages, managing translation requests, and formatting the output.
* [openai_utils.py](src%2Finternationalbridgestojustice%2Fopenai_utils.py)
Utility functions for interacting with the OpenAI API, including sending requests, handling responses, and managing API keys.
* [query_functions.py](src%2Finternationalbridgestojustice%2Fquery_functions.py)
Functions to sort in other scripts...
* [scraping_functions.py](src%2Finternationalbridgestojustice%2Fscraping_functions.py)
Utility functions for scraping content from the Defense Wiki and other legal sources, including handling HTML content, extracting relevant information, and managing metadata.

### 1 - Data Collection and Preparation

To ensure the reliability of the Defense Wiki, it is essential to create a structured legal database to verify and cross-check its content. Since the platform is open and collaborative, and legal frameworks evolve over time, some entries may be incomplete, outdated, or inaccurate. Therefore, it is essential that all legal information in the Defense Wiki remains precise, verifiable, and current, supported by trustworthy sources and rigorous fact-checking.

#### 1 - Establish a comprehensive list of sources from which legal information can be retrieved. 

With IBJ, we are defining a list of trustworthy sources that can be used to verify the content of the Defense Wiki. 
This includes official government websites, legal databases, and other reputable sources of legal information (see shared spreadsheet).


#### 2 - Scrape the content of these sources
Important Metadata: When integrating a document, add its publication date, its country of application/ legal type/ source type, its legal status (in force, amended, draft, its legal relevance (national vs. regional laws, soft law vs. hard law), its original language, the website from where the document has been retrieved.
Save output in a structured format (JSON, JSONL) for easy access and analysis.

* [scrap_defensewiki_website.py](scripts%2Fscrap_defensewiki_website.py)
Scrap the Defense Wiki and save content and metadata in a jsonl file.

* [scrap_defensewiki_website_functional_links.py](scripts%2Fscrap%2Fscrap_defensewiki_website_functional_links.py)
Check reference links that are working and outdated

* [scrap_constitution_website.py](scripts%2Fscrap_constitution_website.py)
Scrap the Constitution website and save content and metadata in a jsonl file

* [scraping_unodc.py](scripts/scrap/scrap_unodc.py) <font color="yellow">*TODO*</font>

#### 3 - Chunk the content of the scraped documents

* [chunking_defensewiki.py](scripts/chunk/chunk_defensewiki.py)
Chunk the Defense Wiki content into smaller pieces and save them in a json file

* [chunking_constitutions.py](scripts/chunk/chunk_constitutions.py)
Chunk the Constitution content into smaller pieces and save them in a json file

* [extract_and_chunk_other_legal_docs.py](scripts%2Fextract_and_chunk_other_legal_docs.py)
Extract and scrap and chunk other pdf legal documents

#### 4 - Translate the content to English

* [translate_Burundi_chunks.ipynb](notebooks%2Ftranslate_Burundi_chunks.ipynb)
Translate all the Burundi chunks to English. Code needs to be adapted to all.

* [translation_batches.py](scripts/create_collection_db/translate_chunks_in_batches.py)
Template to adapt and run translation for all chunks.

#### 5 - Create the embedding database and the collection 

* [create_embedding_database.py](scripts/create_collection_db/create_embedding_database.py) 
Create the embedding database for the Defense Wiki and legal database content. 

<font color="yellow">*TODO: create script to check if hashes have been modified> version-control*</font>

#### 6 - Preprocessing

A further challenge lies in content redundancy and divergence. The Defense Wiki contains duplicated pages or sections that could be edited independently, leading to inconsistencies or even contradictory claims.

Detection of duplicates
* Not unique hashes
hashes defined in [chunking_functions.py](src/internationalbridgestojustice/chunking_functions.py) 
  - <font color="yellow">*TODO manage hashes*</font>
  - [country_pages.py](scripts/clean_defensewiki_country_pages.py) were we discovered that some hashes are repeated
* Compute similarity looking at the distance between embeddings
* Duplicates: Paragraphs or whole pages? Some countries have duplicated pages, but also some chunks (often the Contents one, which can be ignored)
* Apply many pages for one country protocol (below)


### 3 - Country Page Review

#### A - Completeness

* [improve_keypoints.py](scripts%2Fimprove_keypoints.py)
This script is used to improve the key points for each country page in the Defense Wiki. 
From a simple bullet point list, it creates a more detailed key point list, to increase the match with the embeddings. Our embedding model performs better with longer texts.
* [prompt_completeness.md](data/prompts/prompt_completeness.md) the prompt to check the completeness of the page
* [system_prompt_claim_verification.md](data%2Fprompts%2Fsystem_prompt_claim_verification.md) the associated system prompt
* [get_completeness.py](src%2Finternationalbridgestojustice%2Fget_completeness.py) 
All the functions to check the completeness of a country page
* [test_completeness.ipynb](notebooks%2Ftest_completeness.ipynb)
Notebook to test the completeness for one country page and one keypoint
* [keypoint_evaluation.py](scripts%2Fcountry_page_review%2Fkeypoint_evaluation.py) 
This script is used to evaluate the key points for each country page in the Defense Wiki.
* [process_batch_results.py](scripts/process_batch_results.py) to process the results once the batch requests are done
  - <font color="orange">*TODO: need to loop over all the outputs from one country and build the new page from it. maybe somehow keep the labels "missing", "complete", "need refinement" and the titles
and create a new md page*</font>

#### B - Accuracy
* [query_database.py](scripts/country_page_review/verify_one_claim.py) has the perform_similarity_search_with_country_filter function, to retrieve the 5 most relevant chunk from the collection of chunks
and has the prompt to verify the claims
*  [extract_claims.py](scripts/country_page_review/extract_claims.py)
Extract claims from the content of the Defense Wiki and save them in a json file
Right now done for Singapore and 2 pages of Burundi out of 12 files
* [debug_claim_extraction.py](scripts/debug_claim_extraction.py)
  - <font color="yellow">*TODO: need to debug the Burundi claim extraction as the bullets points are interpreted as new sentences.*</font>
* [verify_claims_one_country.py](scripts/country_page_review/verify_claims.py) also helps verify the claims. calls several functions present in query_database.py

#### C -  Source credibility 
#### D - Legal relevance
#### E - Language accessibility

