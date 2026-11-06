"""
Shared helpers for this week's scripts.

The On the Books corpus has one text file per volume of North Carolina session
laws (1866-1967). Every law starts with "CHAPTER" and every section of a law
starts with "Sec.":

    Session: 1909
    CHAPTER 22 AN ACT TO AUTHORIZE THE CLERK ... The General Assembly of North Carolina do enact:
    Sec. 1 That the Clerk of the Superior Court of Northampton County shall ...
    Sec. 2 That this act shall be in force from and after its ratification. ...

read_sections() turns all of that into a list of sections, each a dictionary like

    {"session": "1909", "year": 1909, "chapter": "22", "section": "1",
     "title": "AN ACT TO AUTHORIZE THE CLERK ...",
     "text": "That the Clerk of the Superior Court ...",
     "volume": "publiclawsresolu1909nort"}
"""

import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CORPUS_FOLDER = SCRIPT_DIR / "on_the_books_text_v2"
OUTPUT_FOLDER = SCRIPT_DIR / "output"

# Same word pattern as Week 10: runs of letters, with apostrophes and hyphens inside
WORD = re.compile(r"[a-z]+(?:['-][a-z]+)*")

# Rough keywords for sections that sort people by race. Step 2 searches every
# section; it uses these only to pick which results to print. (The On the Books
# team used machine learning to find Jim Crow laws; see the README.)
RACE_WORDS = re.compile(
    r"\b(colou?red (?:race|people|persons|children|schools?|population)|negro(?:es)?|mulatto|"
    r"white (?:and|or) colou?red|colou?red (?:and|or) white|white race|"
    r"separate (?:schools|coaches|accommodations|waiting)|segregat\w*)\b",
    re.IGNORECASE)

CHAPTER = re.compile(r"^CHAPTER\s+(\S+)\s+(.*)")
SECTION = re.compile(r"^Sec\.\s+(\S+)\s+(.*)")


def read_sections():
    """Every section of every law in the corpus, in the order they appear."""
    files = sorted(p for p in CORPUS_FOLDER.rglob("*.txt") if "readme" not in p.name)
    if not files:
        raise SystemExit(f"No text files in {CORPUS_FOLDER.name}/. See the README for the download.")
    sections = []
    for path in files:
        session, chapter, title = "", "", ""
        text = path.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("Session:"):
                # e.g. "1909", "1866/67", "1913 extra"
                session = line.split(":", 1)[1].strip()
                continue
            match = CHAPTER.match(line)
            if match:
                chapter, title = match.groups()
                continue
            match = SECTION.match(line)
            if match:
                sections.append({"volume": path.stem, "session": session, "year": int(session[:4]),
                                 "chapter": chapter, "section": match.group(1),
                                 "title": title, "text": match.group(2)})
    return sections


def phrases(text, n):
    """Every run of n words in the text, as a set."""
    words = WORD.findall(text.lower())
    starts = range(len(words) - n + 1)
    return {" ".join(words[i:i + n]) for i in starts}


def jaccard(a, b):
    """Shared pieces / all the different pieces (0 if neither has any)."""
    if not a | b:
        return 0.0
    return len(a & b) / len(a | b)


def cite(s):
    """A short citation for a section, e.g. '1909, ch. 22, sec. 1'."""
    return f"{s['session']}, ch. {s['chapter']}, sec. {s['section']}"
