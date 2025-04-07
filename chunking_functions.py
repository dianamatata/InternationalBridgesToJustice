# >> Hierarchical chunking with context and metadata inheritance, Chunk from CoTK is perfect.

import re
import hashlib  # get hash

MAX_CHUNK_SIZE = 500  # todo is it words or characters

# FUNCTIONS --------------------

def generate_hash(content):
    """Generate SHA-256 hash of the given content."""
    return hashlib.sha256(content.encode()).hexdigest()



# __init__ method: Initializes a chunk object with the title, content, mime_type, and metadata.
# __repr__ method: Provides a formal string representation of the chunk for debugging.
# __str__ method: Provides a human-readable summary of the chunk, showing the title and a preview of the content.
class Chunk:
    def __init__(self, title: str, content: str, metadata: dict):
        self.title = title  # Title of the chunk (e.g., "Chapter 1")
        self.content = content  # The actual content of the chunk
        self.metadata = metadata  # Additional metadata (e.g., chapters)
        # <__main__.Chunk object at 0x10e407eb0>

    def __repr__(self):
        return f"Chunk(title={self.title!r}, metadata={self.metadata!r})"
        # Chunk(title='Chapter 1: Introduction', mime_type='text/markdown', metadata={'chapters': ['Chapter 1']})

    def __str__(self):
        return f"Title: {self.title}\nContent: {self.content[:100]}..."  # Shows the first 100 characters of content
        # Title: Chapter 1: Introduction
        # Content: This is the introduction content of the chapter....


def extract_chapters(document, headers_to_exclude_from_chunks=None):

    document_sections = {}

    header_pattern = re.compile(
        r"""
        ^\#{1,6}\s+(.*)$ |                     # Markdown headers (e.g., ### Header)
        ^\*\*(.*?)\*\*\s*[\r\n]+[-=]+$ |       # Bold headers followed by ----- or =====
        ^([\w\s().,:'’-]+)[ \t]*[\r\n]+[-=]+$  # Underlined headers (Header ----)
        """,
        re.MULTILINE | re.VERBOSE,
    )

    matches = list(header_pattern.finditer(document))

    for i, match in enumerate(matches):
        # print(f"\033[93m{i}:{match}\033[0m")

        if i == len(matches) - 1:
            end_idx = len(document)
        else:
            end_idx = matches[i + 1].start()

        length_paragraph = end_idx - matches[i].end() - 2
        if length_paragraph > 5:  # if it is a real paragraph
            start_idx = match.start()
            # print(f"\033[92m{match.start()}:{end_idx}\033[0m")
            chunk_text = document[match.start() : end_idx]
            header_text = match.group(1) or match.group(2) or match.group(3)
            if (
                headers_to_exclude_from_chunks is None
                or header_text.strip() not in headers_to_exclude_from_chunks
            ):
                document_sections[header_text.strip()] = chunk_text
                # print(chunk_text[1:100])

    return document_sections


def split_text_into_chunks(
    text, section, parent_dict, max_chunk_size=MAX_CHUNK_SIZE, separator="\n\n"
):
    # Split the text by paragraphs
    paragraphs = text.split(separator)
    chunks = []
    current_chunk = ""
    chunk_count = 0

    def add_chunk():
        nonlocal current_chunk, chunk_count
        # non local: defined in the enclosing split_text_into_chunks , not local to add_chunks
        if current_chunk:
            section_short = ' '.join(section.split()[0:7])
            chunks.append(
                Chunk(
                    title=generate_hash(current_chunk.strip()),
                    content=current_chunk.strip(),
                    metadata={
                        key: parent_dict[key]
                        for key in [
                            'type',
                            "title",
                            "link",
                            "extracted",
                            # "hash",
                            "last-edited",
                            "language",
                            "viewcount",
                        ]
                             } | { # to join 2 dictionaries
                                 "title_bis": f"{parent_dict['type']}.{parent_dict['title']}.{section_short}.{chunk_count}",
                                 "section_short": section_short,
                                 "chunk_count": chunk_count,
                             },
                )
            )
            chunk_count += 1
            current_chunk = ""

    for para in paragraphs:
        # If adding the paragraph exceeds the max_chunk_size, create a new chunk
        # if we want the character count: if len(current_chunk) + len(para) + len(separator) > max_chunk_size:
        # if we want word count:
        if (
            len(current_chunk.split()) + len(para.split()) + len(separator)
            > max_chunk_size
        ):
            add_chunk()
        else:
            if current_chunk:  # Add separator between paragraphs if chunk is not empty
                current_chunk += separator
            current_chunk += para

    add_chunk()  # Add any remaining chunk

    return chunks


# split into chunks but passing all the metadata
def split_text_into_chunks_with_metadata(
    text, section, metadata, title, max_chunk_size=MAX_CHUNK_SIZE, separator="\n\n"
):
    # Split the text by paragraphs
    paragraphs = text.split(separator)
    chunks = []
    current_chunk = ""
    chunk_count = 0

    def add_chunk():
        nonlocal current_chunk, chunk_count
        filtered_metadata = {
            key: metadata.get(key) for key in metadata if key != "content"
        }
        section_short = ' '.join(section.split()[0:7])

        if current_chunk:
            chunks.append(
                Chunk(
                    title=generate_hash(current_chunk.strip()),
                    content=current_chunk.strip(),
                    # metadata=filtered_metadata,  # Pass all received metadata
                    metadata = filtered_metadata | {
                        "title_bis": f"{metadata.get(title, 'Untitled')}.{section_short}.{chunk_count}",
                        "section_short": section_short,
                        "chunk_count": chunk_count,
                    }
                )
            )
            # print(current_chunk.strip())
            chunk_count += 1
            current_chunk = ""

    for para in paragraphs:
        # If adding the paragraph exceeds the max_chunk_size, create a new chunk
        # if we want the character count: if len(current_chunk) + len(para) + len(separator) > max_chunk_size:
        # if we want word count:
        if (
            len(current_chunk.split()) + len(para.split()) + len(separator)
            > max_chunk_size
        ):
            add_chunk()
        else:
            if current_chunk:  # Add separator between paragraphs if chunk is not empty
                current_chunk += separator
            current_chunk += para

    add_chunk()  # Add any remaining chunk

    return chunks

