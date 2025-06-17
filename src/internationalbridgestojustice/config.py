import os


class Paths:
    # embeddings, collection, chromadb
    PATH_CHROMADB = "data/chroma_db"
    COLLECTION_NAME = "legal_collection"
    PATH_JSONL_FILE_RAW_EMBEDDINGS = "data/chroma_db/raw_embeddings.jsonl"
    PATH_CHROMADB_v5 = "data/chroma_db_v5"
    COLLECTION_NAME_v5 = "legal_collection_v5"
    PATH_JSONL_FILE_RAW_EMBEDDINGS_v5 = "data/chroma_db_v5/raw_embeddings.jsonl"

    # DefenseWiki
    BASE_URL_DEFENSE_WIKI = "https://defensewiki.ibj.org"
    PATH_FOLDER_DEFENSE_WIKI = "data/processed/defensewiki.ibj.org"
    PATH_JSONL_FILE_DEFENSEWIKI_CHUNKS = (
        "data/processed/defensewiki.ibj.org/chunks_1.jsonl"
    )
    PATH_JSONL_FILE_DEFENSEWIKI = "data/interim/defensewiki_all.jsonl"

    # ConstitutionProject
    START_URL_CONSTITUTIONS = "https://www.constituteproject.org/constitutions?lang=en&status=in_force&status=is_draft"
    BASE_URL_CONSTITUTIONS = "https://www.constituteproject.org"
    PATH_FOLDER_CONSTITUTIONS_WITH_MD_FILES = "data/raw/constituteproject.org"
    PATH_FOLDER_CONSTITUTIONS_WITH_JSONL_FILES = "data/processed/constituteproject.org"
    PATH_JSONL_FILE_WITH_CONSTITUTIONS_ALL_COUNTRIES = (
        f"{PATH_FOLDER_CONSTITUTIONS_WITH_JSONL_FILES}/constituteproject.jsonl"
    )
    PATH_JSONL_FILE_CONSTITUTION_CHUNKS = (
        "data/processed/constituteproject.org/constitution_chunks.jsonl"
    )

    # Legal documents
    PATH_FOLDER_LEGAL_FILES_PDF = "data/raw/legal_countries_docs_pdfs"
    PATH_FOLDER_LEGAL_FILES_JSONL = "data/processed/legal_countries_docs"
    PATH_JSONL_FILE_WITH_LEGAL_FILES = (
        "data/processed/legal_countries_docs/other_legal_docs.jsonl"
    )
    PATH_JSONL_FILE_LEGAL_OTHERS = (
        "data/processed/legal_countries_docs/other_legal_docs_chunks.jsonl"
    )

    # Translated chunks
    PATH_TRANSLATED_CHUNKS = "data/translated_chunks/Burundi_chunks_in_english.jsonl"

    # Keypoints completeness
    PATH_MD_FILE_COMPLETENESS_KEYPOINTS = "data/raw/IBJ_docs/Completeness_checklist.md"
    PATH_JSON_FILE_COMPLETENESS_KEYPOINTS = "data/completeness/keypoints.json"
    PATH_JSON_FILE_DESCRIPTIVE_COMPLETENESS_KEYPOINTS = (
        "data/completeness/descriptive_keypoints.json"
    )
    PATH_FOLDER_COMPLETENESS = "data/completeness"

    # Claim extraction
    PATH_FOLDER_CLAIM_EXTRACTION = "data/extracted_claims"
    PATH_JSONL_FILE_EXTRACTED_CLAIMS = (
        f"{PATH_FOLDER_CLAIM_EXTRACTION}/claims_chunks_1.jsonl"
    )
    PATH_FOLDER_CLAIM_VERIFICATION = "data/verified_claims"

    # Prompts
    PATH_PROMPTS = "data/prompts"
    PATH_FILE_PROMPT_COMPLETENESS = f"{PATH_PROMPTS}/prompt_completeness.md"
    PATH_FILE_PROMPT_CLAIM_EXTRACTION = f"{PATH_PROMPTS}/prompt_claim_extraction.md"
    PATH_FILE_PROMPT_CLAIM_VERIFICATION = f"{PATH_PROMPTS}/prompt_claim_verification.md"
    PATH_FILE_SYSTEM_PROMPT_COMPLETENESS = (
        f"{PATH_PROMPTS}/system_prompt_completeness.md"
    )

    FILE_COUNTRY_NAMES = "data/interim/country_names_1.txt"

    # V2 ChromaDB
    PATH_CHROMADB_v2 = "data/chroma_db_v2"
    COLLECTION_NAME_v2 = "legal_collection_v2"
    PATH_CACHE = "data/cache"


# Others
MAX_CHUNK_SIZE = 500  # these are words
MODEL_NAME = "gpt-4o-mini"

legal_files_info_list = [
    {
        "filename": "Indian_penal_code.pdf",
        "path": os.path.join(
            Paths.PATH_FOLDER_LEGAL_FILES_PDF, "Indian_penal_code.pdf"
        ),
        "country": "India",
        "language": "en",
        "legal_type": "penal_code",
        "publication_date": "1860-10-06",
        "year": "1860",
        "legal_relevance": "national",
        "website": "",
        "legal_status": "",
    },
    {
        "filename": "Burundi_Penal-Code-Revised_2009_FRENCH-1.pdf",
        "path": os.path.join(
            Paths.PATH_FOLDER_LEGAL_FILES_PDF,
            "Burundi_Penal-Code-Revised_2009_FRENCH-1.pdf",
        ),
        "country": "Burundi",
        "language": "fr",
        "legal_type": "penal_code",
        "publication_date": "2009-05-22",
        "year": "2009",
        "legal_relevance": "national",
        "website": "",
        "legal_status": "",
    },
    {
        "filename": "Accord_Arusha_Burundi.pdf",
        "path": os.path.join(
            Paths.PATH_FOLDER_LEGAL_FILES_PDF, "Accord_Arusha_Burundi.pdf"
        ),
        "country": "Burundi",
        "language": "fr",
        "legal_type": "peace_agreement",
        "publication_date": "2000-08-28",
        "year": "2000",
        "legal_relevance": "national",
        "website": "",
        "legal_status": "",
    },
    {
        "filename": "Burundi-Code-2018-procedure-penale.pdf",
        "path": os.path.join(
            Paths.PATH_FOLDER_LEGAL_FILES_PDF, "Burundi-Code-2018-procedure-penale.pdf"
        ),
        "country": "Burundi",
        "language": "fr",
        "legal_type": "penal_procedure",
        "publication_date": "2018-05-11",
        "year": "2018",
        "legal_relevance": "national",
        "website": "",
        "legal_status": "",
    },
    {
        "filename": "Burundi_Charte-de-l-Unite-nationale-1991.pdf",
        "path": os.path.join(
            Paths.PATH_FOLDER_LEGAL_FILES_PDF,
            "Burundi_Charte-de-l-Unite-nationale-1991.pdf",
        ),
        "country": "Burundi",
        "language": "fr",
        "legal_type": "",
        "publication_date": "2006-12-31",
        "year": "2006",
        "legal_relevance": "national",
        "website": "",
        "legal_status": "",
    },
    {
        "filename": "China_penal_code.pdf",
        "path": os.path.join(
            Paths.PATH_FOLDER_LEGAL_FILES_PDF, "China_penal_code1.pdf"
        ),
        "country": "China",
        "language": "en",
        "legal_type": "",
        "publication_date": "1997-03-14",
        "year": "1997",
        "legal_relevance": "national",
        "website": "",
        "legal_status": "",
    },
]
