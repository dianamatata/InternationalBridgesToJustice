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
