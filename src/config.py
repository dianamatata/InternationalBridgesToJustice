class Paths:

    # embeddings, collection, chromadb
    PATH_CHROMADB = "data/chroma_db"
    COLLECTION_NAME = "legal_collection"
    PATH_JSONL_FILE_RAW_EMBEDDINGS = "data/chroma_db/raw_embeddings.jsonl"

    # DefenseWiki
    BASE_URL_DEFENSE_WIKI = "https://defensewiki.ibj.org"
    PATH_FOLDER_DEFENSE_WIKI = "data/processed/defensewiki.ibj.org"
    PATH_JSONL_FILE_DEFENSEWIKI_CHUNKS = "data/processed/defensewiki.ibj.org/chunks_1.jsonl"
    PATH_JSONL_FILE_DEFENSEWIKI = "data/interim/defensewiki_all.jsonl"


    # ConstitutionProject
    START_URL_CONSTITUTIONS = "https://www.constituteproject.org/constitutions?lang=en&status=in_force&status=is_draft"
    BASE_URL_CONSTITUTIONS = "https://www.constituteproject.org"
    PATH_FOLDER_CONSTITUTIONS_WITH_MD_FILES = "data/raw/constituteproject.org"
    PATH_FOLDER_CONSTITUTIONS_WITH_JSONL_FILES = "data/processed/constituteproject.org"
    PATH_JSONL_FILE_WITH_CONSTITUTIONS_ALL_COUNTRIES = f"{PATH_FOLDER_CONSTITUTIONS_WITH_JSONL_FILES}/constituteproject.jsonl"
    PATH_JSONL_FILE_CONSTITUTION_CHUNKS = "data/processed/constituteproject.org/constitution_chunks.jsonl"

    # Keypoints completeness
    PATH_MD_FILE_COMPLETENESS_KEYPOINTS = "data/raw/IBJ_docs/Completeness_checklist.md"
    PATH_JSON_FILE_COMPLETENESS_KEYPOINTS = "data/completeness/keypoints.json"
    PATH_JSON_FILE_DESCRIPTIVE_COMPLETENESS_KEYPOINTS = "data/completeness/descriptive_keypoints.json"
    PATH_FOLDER_COMPLETENESS = "data/completeness"

    # Claim extraction
    PATH_FOLDER_CLAIM_EXTRACTION = "data/extracted_claims"
    PATH_JSONL_FILE_EXTRACTED_CLAIMS = f"{PATH_FOLDER_CLAIM_EXTRACTION}/claims_chunks_1.jsonl"

    # Prompts
    PATH_PROMPTS = "data/prompts"
    PATH_FILE_PROMPT_COMPLETENESS = f"{PATH_PROMPTS}/prompt_completeness.md"
    PATH_FILE_PROMPT_CLAIM_EXTRACTION = f"{PATH_PROMPTS}/prompt_claim_extraction.md"
    PATH_FILE_PROMPT_CLAIM_VERIFICATION = f"{PATH_PROMPTS}/prompt_claim_verification.md"
    PATH_FILE_SYSTEM_PROMPT_COMPLETENESS = f"{PATH_PROMPTS}/system_prompt_completeness.md"

    FILE_COUNTRY_NAMES = "data/interim/country_names_1.txt"


# Others
MAX_CHUNK_SIZE = 500  # these are words