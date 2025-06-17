def get_completeness_keypoints(completeness_checklist_filepath: str):
    with open(completeness_checklist_filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    completeness_keypoints = []
    for line in lines[2:]:
        stripped = line.strip()
        if line.strip() == "":
            continue
        completeness_keypoints.append(line.replace("  \n", ""))
    return completeness_keypoints


def retrieve_source_titles_from_chunks(
    results: dict, all_chunks: list[dict]
) -> list[str]:
    """
    Retrieves human-friendly source titles for each returned chunk ID.
    Looks up each id from the results in the provided chunks.
    """
    sources = results.get("ids", [[]])[0]
    chunks_for_answer = []
    for source in sources:
        matching_chunks = [
            chunk for chunk in all_chunks if chunk.get("title") == source
        ]
        if matching_chunks:
            title_bis = matching_chunks[0]["metadata"].get("title_bis", source)
            chunks_for_answer.append(title_bis)
        else:
            chunks_for_answer.append(f"No matching chunk found for ID: {source}")
    return chunks_for_answer
