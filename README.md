# Artificial intelligence for legal assistance in developing countries

## Objectives

This project seeks to enhance access to legal resources for defenders and citizens in developing countries, where such resources are often fragmented or outdated. By integrating cutting-edge artificial intelligence (AI) technologies, including large language models (LLMs), into the public DefenseWiki platform, the project aims to automate and optimize the curation of legal knowledge.
 
The primary objective is to enhance DefenseWiki’s capabilities by incorporating AI to systematically improve the quality and relevance of its content. This will be achieved through web scraping of documents from DefenseWiki and external sources, combined with the implementation of an LLM-based agentic framework to verify and update legal claims.
 
Additionally, this project will lay the foundation for the future development of a virtual assistant that delivers tailored legal information to users. The end goal is to provide accurate and up-to-date legal knowledge across more than 130 countries, significantly reducing the time defenders spend on legal research. This will empower legal professionals, improve legal literacy, and promote a more equitable justice system globally.


## Steps

1. Web-scraping: Download the Defense Wiki (https://defensewiki.ibj.org/) in a json file with metadata + content
2. Run statistics on the pages of the Defense Wiki
3. Check functional and faulty links in the cited references in the Defense Wiki
4. Download ground truth documents i.e. constitution + penal code of various countries
5. Pick a LLM to extract claims from text
5. Extract facts (=claims) from the content downloaded from The Defense Wiki
6. Pick a LLM good a verifying claims
7. Verify facts with a LLM comparing them to ground truth
8. RAG


## Repository overview

### 1 - Data Collection and Preparation

To ensure the reliability of the Defense Wiki, it is essential to create a structured legal database to verify and cross-check its content. Since the platform is open and collaborative, and legal frameworks evolve over time, some entries may be incomplete, outdated, or inaccurate. Therefore, it is essential that all legal information in the Defense Wiki remains precise, verifiable, and current, supported by trustworthy sources and rigorous fact-checking.

#### 1 - Establish a comprehensive list of sources from which legal information can be retrieved. 

#### 2 - Scrape the content of these sources and save it in a structured format (JSON, JSONL) for easy access and analysis.

Important Metadata: When integrating a document, add its publication date, its country of application/ legal type/ source type, its legal status (in force, amended, draft, its legal relevance (national vs. regional laws, soft law vs. hard law), its original language, the website from where the document has been retrieved.

* [scraping_defensewiki_website.py](scripts/scraping_defensewiki_website.py) 
Scrap the Defense Wiki and save content and metadata in a json file
+ Check reference links that are working and outdated
+ [plot_ibj_statistics.ipynb](notebooks%2Fplot_ibj_statistics.ipynb)
Run statistics on the data extracted on the DefenseWiki website

* [scraping_constitution_website.py](scripts/scraping_constitution_website.py)
Scrap the Constitution website and save content and metadata in a json file

* [scraping_unodc.py](scripts/scraping_unodc.py) <font color="yellow">*TODO !!!*</font>
<font color="yellow">*TODO: documents not extracted yet*</font>

* [chunking_functions.py](src/chunking_functions.py)
create functions to cut markrdown text into smaller chunks

* [chunking_defensewiki.py](scripts/chunking_defensewiki.py)
Chunk the Defense Wiki content into smaller pieces and save them in a json file

* [chunking_constitutions.py](scripts/chunking_constitutions.py)
Chunk the Constitution content into smaller pieces and save them in a json file

* [translation_batches.py](scripts/translation_batches.py)
Translate all the chunks to English

* [documents_to_extract.py](scripts/documents_to_extract.py) <font color="yellow">*TODO: documents we need to scrape and add to the collection as well*</font>

* [create_embedding_database.py](scripts/create_embedding_database.py) create the embedding database for the Defense Wiki and legal database content

### 2 - Preprocessing

A further challenge lies in content redundancy and divergence. The Defense Wiki contains duplicated pages or sections that could be edited independently, leading to inconsistencies or even contradictory claims.

Detection of duplicates
* Not unique hashes
hashes defined in [chunking_functions.py](src/chunking_functions.py) 
  - <font color="yellow">*TODO manage hashes*</font>
  - [country_pages.py](scripts/country_pages.py) were we discovered that some hashes are repeated
* Compute similarity looking at the distance between embeddings
* Duplicates: Paragraphs or whole pages? Some countries have duplicated pages, but also some chunks (often the Contents one, which can be ignored)
* Apply many pages for one country protocol (below)


Many pages for one country (duplicates or multilingual): 
* Translate all pages in English. 
  - <font color="yellow">*TODO: should we translate every chunk before building the collection?*</font>

[gather_all_pages_per_country.py](scripts/gather_all_pages_per_country.py) 
beggining of script to gather all the different versions. If we want to process them together?


* Unify and Synthesize content paragraph-wise using LLM. Ensure alignment of facts and level of detail. Indeed, there might be discrepancies in page details or facts across languages (e.g., Chile in English vs. Spanish)? 
* Careful to preserve references during synthesis.


### 3 - Processing: Key points for each country page

#### A - Completeness
* [prompt_completeness.md](data/prompts/prompt_completeness.md) the prompt to check the completeness of the page
* [ensuring_completeness_country_pages.py](scripts/ensuring_completeness_country_pages.py)
* [keypoint_evaluation.py](scripts/keypoint_evaluation.py)  creates a class KeypointEvaluation to simplify the code of ensuring_completeness_country_pages.py and be able to send batch requests
* [openai_batch_manager.py](src%2Fopenai_batch_manager.py) to submit batch requests to OpenAI API after creating a json file
* [process_batch_results.py](scripts/process_batch_results.py) to process the results once the batch requests are done
  - <font color="yellow">*TODO: run it in India to check that no bugs in optimization*</font>
  - <font color="orange">*TODO: need to loop over all the outputs from one country and build the new page from it. maybe somehow keep the labels "missing", "complete", "need refinement" and the titles
and create a new md page*</font>

#### B - Accuracy
* [query_database.py](scripts/claim_verification.py) has the perform_similarity_search_with_country_filter function, to retrieve the 5 most relevant chunk from the collection of chunks
and has the prompt to verify the claims
*  [extract_claims.py](scripts/extract_claims.py)
Extract claims from the content of the Defense Wiki and save them in a json file
Right now done for Singapore and 2 pages of Burundi out of 12 files
* [debug_claim_extraction.py](scripts/debug_claim_extraction.py)
  - <font color="yellow">*TODO: need to debug the Burundi claim extraction as the bullets points are interpreted as new sentences.*</font>
* [verify_claims_one_country.py](scripts/verify_claims_one_country.py) also helps verify the claims. calls several functions present in query_database.py

#### C -  Source credibility 
#### D - Legal relevance
#### E - Language accessibility

