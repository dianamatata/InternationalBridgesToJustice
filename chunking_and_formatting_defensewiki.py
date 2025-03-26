# >>> - Transform the json file in jsonl file

import json # save in json files
input_data = "/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/data/interim/defensewiki_all.json"

# 1 - Load JSON
with open(input_data, "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

records = data["https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=1300&offset=0"]

# 2 - Write each dictionary as a new line in JSONL format
with open(f"{input_data}l", "w", encoding="utf-8") as jsonl_file:
    for record in records:
        jsonl_file.write(json.dumps(records[record]) + "\n")

# 3 - Read JSONL file line by line
with open(f"{input_data}l", "r", encoding="utf-8") as jsonl_file:
    defense_wiki_all = [json.loads(line) for line in jsonl_file]  # Convert each line to a dictionary

# 4 - Now `data1` is a list of dictionaries
print(len(defense_wiki_all))  # Should print 1252 if correctly processed
print(f"{json.dumps(defense_wiki_all[0], indent=4)}")

# 5 - Loop over Defensewiki to extract all the pages as markdown
path="/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/data/raw/defensewiki.ibj.org"

with open(f"{input_data}l", "r", encoding="utf-8") as jsonl_file:
    defense_wiki_all = [json.loads(line) for line in jsonl_file]  # Convert each line to a dictionary

for page in range(1, len(defense_wiki_all)):
    title_value = defense_wiki_all[page]["title"]
    filename = f"{path}/{title_value}.md"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(defense_wiki_all[page]["content"])



# >> Hierarchical chunking with context and metadata inheritance, Chunk from CoTK is perfect.

# 1 - Create chunk class

# __init__ method: Initializes a chunk object with the title, content, mime_type, and metadata.
# __repr__ method: Provides a formal string representation of the chunk for debugging.
# __str__ method: Provides a human-readable summary of the chunk, showing the title and a preview of the content.
class Chunk:
    def __init__(self, title: str, content: str, mime_type: str, metadata: dict):
        self.title = title  # Title of the chunk (e.g., "Chapter 1")
        self.content = content  # The actual content of the chunk
        self.mime_type = mime_type  # MIME type (e.g., "text/markdown")
        self.metadata = metadata  # Additional metadata (e.g., chapters)
        # <__main__.Chunk object at 0x10e407eb0>

    def __repr__(self):
        return f"Chunk(title={self.title!r}, mime_type={self.mime_type!r}, metadata={self.metadata!r})"
        # Chunk(title='Chapter 1: Introduction', mime_type='text/markdown', metadata={'chapters': ['Chapter 1']})

    def __str__(self):
        return f"Title: {self.title}\nContent: {self.content[:100]}..."  # Shows the first 100 characters of content
        # Title: Chapter 1: Introduction
        # Content: This is the introduction content of the chapter....

# Example of usage
header_line = "Chapter 1: Introduction"
processed_chunk_text = "This is the introduction content of the chapter."
current_chapters = ["Chapter 1"]

chunk = Chunk(
    title=header_line,
    content=processed_chunk_text,
    mime_type="text/markdown",
    metadata={"chapters": current_chapters.copy()},
)

# Print chunk to see output
print(chunk)


# 2 - Create chunking function
import re
with open(f"{input_data}l", "r", encoding="utf-8") as jsonl_file:
    defense_wiki_all = [json.loads(line) for line in jsonl_file]  # Convert each line to a dictionary

    document = defense_wiki_all[1]["content"] # Singapore




chunks: list[Chunk] = []
current_chapters: list[str] = []
markdown = document

def normalize_newlines(text: str) -> str:
    """normalize_newlines removes single newlines within paragraphs while preserving paragraph breaks."""
    paragraphs = text.split("\n\n")
    processed_paragraphs = [para.replace("\n", " ") for para in paragraphs]
    return "\n\n".join(processed_paragraphs)

def extract_chapters(document):

    document_sections = {}

    header_pattern = re.compile(
        r"""
        ^\#{1,6}\s+(.*)$ |               # Markdown headers (e.g., ### Header)
        ^\*\*(.*?)\*\*\s*[\r\n]+[-]+$ |  # Bold headers followed by ----- or ===== [-=]
        ^([A-Za-z0-9\s]+)\s*[\r\n]+[-]+$ # Underlined headers (e.g., Header ----) [-=]
        """,
        re.MULTILINE | re.VERBOSE
    )

    headers_to_exclude_from_chunks = {
        "REFERENCES", "Referencias", "References", "Navigation menu", "Page actions", "Personal tools",
        "Navigation", "Search", "Glossary", "Tools"
    }

    matches = list(header_pattern.finditer(document))

    for i, match in enumerate(matches):
        print(f"\033[93m{i}:{match}\033[0m")  # green color

        if i == len(matches) - 1:
            end_idx = len(markdown)
        else:
            end_idx = matches[i + 1].start()
        print(end_idx)

        length_paragraph = end_idx - matches[i].end() - 2
        if length_paragraph > 5:  # if it is a real paragraph
            start_idx = match.start()
            print(f"\033[92m{match.start()}:{end_idx}\033[0m")  # green color
            chunk_text = markdown[match.start():end_idx]
            header_text = match.group(1) or match.group(2) or match.group(3)
            if header_text.strip() not in headers_to_exclude_from_chunks:
                document_sections[header_text.strip()] = chunk_text
                print(chunk_text[1:100])

    return document_sections


#processed_text = normalize_newlines(document)
document_sections = extract_chapters(document)

# TODO: check chunk size, if it is + than threshold, chunk into smaller chunk
# TODO inherit metadata

document_sections['HISTORICAL CONTEXT']

max_chunk_size = 1500
separators=["\n\n"]  # Splits by paragraphs

text = normalize_newlines(document_sections['HISTORICAL CONTEXT'])


# -------
text = normalize_newlines(document_sections['HISTORICAL CONTEXT'])

len(chunk_text) #  3340
separator="\n\n"
paragraphs = text.split(separator)
chunks = []
current_chunk = ""


# cut this in paragraphs
def split_text_into_chunks(text, max_chunk_size=1500, separator="\n\n"):
    # Split the text by paragraphs
    paragraphs = text.split(separator)
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        print(para)
        # If adding the paragraph exceeds the max_chunk_size, create a new chunk
        if len(current_chunk) + len(para) + len(separator) > max_chunk_size:
            chunks.append(current_chunk.strip())
            current_chunk = para
        else:
            if current_chunk:  # Add separator between paragraphs if chunk is not empty
                current_chunk += separator
            current_chunk += para

    if current_chunk:  # Add any remaining chunk
        chunks.append(current_chunk.strip())
        # TODO: get rid of empty paragraphs!!
        # TODO: why text = normalize_newlines(document_sections['HISTORICAL CONTEXT']) do not work
        # TODO: metadata handling
        # TODO save in jsonl

    return chunks



# Example usage:
sections = split_text(chunk_text, max_chunk_size)
for i, section in enumerate(sections):
    print(f"Section {i+1}: {len(section)} chars\n{section}\n{'-'*50}")




# put all the content in one huge chunk. we would expect to break it into paragraphs

if not matches:
    processed_text = normalize_newlines(markdown)
    chunk = Chunk(title="", content=processed_text, mime_type="text/markdown", metadata={"chapters": []})
    # TODO : cut the chunks, should we look at paragraphs? otherwise arbitrary chunking?
    return [chunk]

