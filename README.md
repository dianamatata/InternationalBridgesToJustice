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

#### 1a. [scraping_defensewiki_website.py](scraping_defensewiki_website.py) 
Scrap the Defense Wiki and save content and metadata in a json file
+ Check reference links that are working and outdated
+ [ibj_statistics.py](ibj_statistics.py)
Run statistics on the data extracted on the DefenseWiki website

#### 1b. [scraping_constitution_website.py](scraping_constitution_website.py)
Scrap the Constitution website and save content and metadata in a json file

#### 1c. [scraping_unodc.py](scraping_unodc.py)
TODO!!!

#### 2 [chunking_functions.py](chunking_functions.py)
create functions to cut markrdown text into smaller chunks

#### 2a. [chunking_defensewiki.py](chunking_defensewiki.py)
Chunk the Defense Wiki content into smaller pieces and save them in a json file

#### 2b. [chunking_constitutions.py](chunking_constitutions.py)
Chunk the Constitution content into smaller pieces and save them in a json file


#### 4. [pdf_to_markdown_v2.py](pdf_to_markdown_v2.py)
Extract content from pdf files to markdown and save them with metadata for ground truth

### 2 - Preprocessing

A further challenge lies in content redundancy and divergence. The Defense Wiki contains duplicated pages or sections that could be edited independently, leading to inconsistencies or even contradictory claims.

Detection of duplicates
* Not unique hashes
* Compute similarity looking at the distance between embeddings
* Duplicates: Paragraphs or whole pages? Some countries have duplicated pages, but also some chunks (often the Contents one, which can be ignored)
* Apply many pages for one country protocol (below)


Many pages for one country (duplicates or multilingual): 
* Translate all pages in English. 
* Unify and Synthesize content paragraph-wise using LLM. Ensure alignment of facts and level of detail. Indeed, there might be discrepancies in page details or facts across languages (e.g., Chile in English vs. Spanish)? 
* Careful to preserve references during synthesis.

### 3 - Processing: Key points for each country page

#### A - Completeness
* [ensuring_completeness_country_pages.py](ensuring_completeness_country_pages.py)
* 

#### B - Accuracy

*  [extract_claims.py](extract_claims.py)
Extract claims from the content of the Defense Wiki and save them in a json file
Right now done for Singapore and 2 pages of Burundi out of 12 files

* [verify_claims_one_country.py](verify_claims_one_country.py)
* 
#### C -  Source credibility 
#### D - Legal relevance
#### E - Language accessibility

