"""
Shared helpers for the three NER demos.

Every demo works the same way: read data/source.txt, find entities, then
call save_results() to print them, save a CSV, and save a highlighted HTML
page. Each entity is a dictionary like:

    {"text": "Memphis", "label": "PLACE", "start": 512, "end": 519}

where start and end are character positions in the source text.
"""

import csv
import re
import webbrowser
from pathlib import Path

from spacy import displacy

SCRIPT_DIR = Path(__file__).parent
SOURCE_FILE = SCRIPT_DIR / "data" / "source.txt"
OUTPUT_FOLDER = SCRIPT_DIR / "output"

OPEN_IN_BROWSER = True   # open each highlighted page automatically

# Highlight colors, assigned to labels in the order they appear
COLORS = ["#fbd38d", "#9ae6b4", "#90cdf4", "#fbb6ce", "#d6bcfa",
          "#feb2b2", "#b2f5ea", "#e2e8f0", "#c6f6d5", "#fefcbf"]


def load_source():
    """Read the historical text we're analyzing."""
    return SOURCE_FILE.read_text(encoding="utf-8")


def split_into_chunks(text, max_chars=1000):
    """Split text into paragraph-sized pieces, keeping track of where each
    piece starts. Some models can only read a few hundred words at once."""
    chunks = []
    for match in re.finditer(r"\S(?:.|\n(?!\n))*", text):   # paragraphs
        start, paragraph = match.start(), match.group()
        while len(paragraph) > max_chars:                    # long paragraph:
            cut = paragraph.rfind(". ", 0, max_chars) + 1 or max_chars  # split at a sentence
            chunks.append((start, paragraph[:cut]))
            start, paragraph = start + cut, paragraph[cut:]
        chunks.append((start, paragraph))
    return chunks


def remove_overlaps(entities):
    """displaCy can't draw overlapping highlights, so keep the first one."""
    kept, last_end = [], -1
    for entity in sorted(entities, key=lambda e: (e["start"], -e["end"])):
        if entity["start"] >= last_end:
            kept.append(entity)
            last_end = entity["end"]
    return kept


def save_results(method, text, entities, title):
    """Print the entities, then save them as a CSV and a highlighted HTML page."""
    entities = sorted(entities, key=lambda e: e["start"])

    # 1. Print a table
    print(f"\nFound {len(entities)} entities:\n")
    width = max((len(e["text"].replace("\n", " ")) for e in entities), default=10)
    for entity in entities:
        extra = f"  ({entity['score']:.2f})" if "score" in entity else ""
        print(f"  {entity['text'].replace(chr(10), ' '):{width}}  {entity['label']}{extra}")

    # 2. Save a CSV
    OUTPUT_FOLDER.mkdir(exist_ok=True)
    csv_path = OUTPUT_FOLDER / f"{method}.csv"
    columns = ["text", "label", "start", "end", "score"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(entities)

    # 3. Save a highlighted page with displaCy (spaCy's visualizer).
    # Single line breaks become spaces so paragraphs wrap to fit the screen
    # (same length, so the entity positions still line up).
    display_text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    labels = list(dict.fromkeys(e["label"] for e in entities))
    colors = {label: COLORS[i % len(COLORS)] for i, label in enumerate(labels)}
    page = displacy.render(
        {"text": display_text, "ents": remove_overlaps(entities), "title": title},
        style="ent", manual=True, page=True, options={"colors": colors},
    )
    html_path = OUTPUT_FOLDER / f"{method}.html"
    html_path.write_text(page, encoding="utf-8")

    print(f"\nSaved {csv_path.relative_to(SCRIPT_DIR)} and {html_path.relative_to(SCRIPT_DIR)}")
    if OPEN_IN_BROWSER:
        webbrowser.open(html_path.resolve().as_uri())
