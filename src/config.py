# embeddings, collection, chromadb
path_chromadb = "data/chroma_db"
collection_name = "legal_collection"
path_jsonl_file_raw_embeddings = "data/chroma_db/raw_embeddings.jsonl"

# DefenseWiki
base_url_defense_wiki = "https://defensewiki.ibj.org"
path_folder_defense_wiki = "data/processed/defensewiki.ibj.org"
path_jsonl_file_defensewiki_chunks = "data/processed/defensewiki.ibj.org/chunks_1.jsonl"
path_jsonl_file_defensewiki = "data/interim/defensewiki_all.jsonl"


# ConstitutionProject
start_url_constitutions = "https://www.constituteproject.org/constitutions?lang=en&status=in_force&status=is_draft"
base_url_constitutions = "https://www.constituteproject.org"
path_folder_constitutions_with_md_files = "data/raw/constituteproject.org"
path_folder_constitutions_with_jsonl_files = "data/processed/constituteproject.org"
path_jsonl_file_with_constitutions_all_countries = f"{path_folder_constitutions_with_jsonl_files}/constituteproject.jsonl"
path_jsonl_file_constitution_chunks = "data/processed/constituteproject.org/constitution_chunks.jsonl"

# Keypoints completeness
path_md_file_completeness_keypoints = "data/raw/IBJ_docs/Completeness_checklist.md"
path_json_file_completeness_keypoints = "data/completeness/keypoints.json"
path_folder_completeness = "data/completeness"

# Claim extraction
path_folder_claim_extraction = "data/extracted_claims"
path_jsonl_file_extracted_claims = f"{path_folder_claim_extraction}/claims_chunks_1.jsonl"

# Prompts
path_prompts = "data/prompts"
path_file_prompt_completeness = f"{path_prompts}/prompt_completeness.md"
path_file_prompt_claim_extraction = f"{path_prompts}/prompt_claim_extraction.md"
path_file_prompt_claim_verification = f"{path_prompts}/prompt_claim_verification.md"
path_file_system_prompt_completeness = f"{path_prompts}/system_prompt_completeness.md"
# Others
MAX_CHUNK_SIZE = 500  # these are words
