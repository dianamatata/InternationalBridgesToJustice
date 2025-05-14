import re

file = "data/completeness/Burundi_answer.md"
with open(file, "r", encoding="utf-8") as file:
    content = file.read()

# Find all matches
pattern = r"(## .+?)\n\n.*?\*\*REWRITTEN wiki chapter\*\*:\s*(.*?)(?:\n{4}|\Z)"
matches = re.findall(pattern, content, re.DOTALL)

# Write to new markdown file
with open("data/completeness/rewritten_extracted.md", "w", encoding="utf-8") as f:
    for title, rewritten in matches:
        f.write(f"{title}\n\n{rewritten.strip()}\n\n")

