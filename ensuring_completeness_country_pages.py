
# FUNCTIONS ---------------------------------------------------

# 1 extract checklist to ensure completeness of country pages
def get_completeness_checklist():
    completeness_checklist_filepath = "data/raw/IBJ_docs/Completeness_checklist.md"
    with open(completeness_checklist_filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    keypoints = []
    for line in lines[2:]:
        stripped = line.strip()
        if line.strip() == "":
            continue  # skip empty lines
        keypoints.append(line.replace("  \n", ""))
    return keypoints


# 2 - Get country names from the Defense Wiki Country pages
def get_countries():
    country_names_filepath = "data/interim/country_names_1.txt"
    with open(f"{country_names_filepath}", "r", encoding="utf-8") as f:
        country_names = f.read().splitlines()
        len(country_names) # 204
        return country_names

def check_keypoint_covered(country, chapter, point):
    # Query database for the 5 most relevant chunks looking for that country and this specific point
    # check if the point is covered in the database, if yes extract relevant lawys and legal chapters
    # check if the input data on document covers the point
    # with all this info "re"formulate an answer and assess whether we answered well the question
    #

PROMPT_KEYPOINT_COUNTRY  = (
    "You need to determine whether the document contains enough information to validate the point: {point} "
    "and then decide whether the chapter is **Complete**, **Needs refinement**, or **Missing** based on that information."
    "You can cite extract specific laws or legal chapters to justify your decision.\n\n"

    "Very important: Make sure that the information used for verification comes from the correct country. "
    "You can find the country name in the 'metadata':'title' or 'metadata':'country' fields of the context.\n\n"

    "Does the database provide enough information to fact-check the claim? \n"
    "If no, label claim as ###Inconclusive###\n"
    "If yes, state the judgment as one of the following categories, marked with ###:\n\n"

    "###Supported###\n"
    "A claim is supported by the database if everything in the claim is supported and nothing is contradicted by the information in the database. "
    "There can be some results that are not fully related to the claim.\n\n",
    "Claim: {claim})

def format_prompt(prompt_template: str, claim: str, wiki_context: str, database_context: str) -> str:
    """
    Build the final prompt by inserting the claim and context into the template.
    """
    return prompt_template.format(claim=claim, context=wiki_context)

prompt = format_prompt(PROMPT_KEYPOINT_COUNTRY, keypoint=f"{chapter}: {point}", context=context_text, database_context=database_context)


# MAIN ---------------------------------------------------
countries = get_countries()
keypoints = get_completeness_checklist()

chapter = ""
for country in countries:
    for point in keypoints:
        # if point is not a new chapter
        indent = len(point) - len(point.lstrip())  # Capture the indentation (number of leading spaces)
        if indent == 0:
            chapter = point
        if indent > 0:
            result = check_keypoint_covered(country, chapter, point)
            if result:
                print(f"Keypoint '{point}' is covered in {country}.")
            else:
                print(f"Keypoint '{point}' is NOT covered in {country}.")
                # check in database
                # check on internet

# debug
chapter = keypoints[10]
point = keypoints[11]
keypoint_to_check = f"{chapter}: {point}" # '2. Rights of the Accused:    1. Right Against Unlawful Arrests, Searches and Seizures'


