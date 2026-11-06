#!/usr/bin/env python3
"""
Step 3: How did one clause change over time?
============================================

Finds every section that contains most of the words of START (a few words from
the clause you want to follow), puts them in order by session, and compares
each version with the one before it: how similar they are, and which words
were added or cut.

OCR errors are fine: a section only needs SHARE of START's 3-word phrases.
Some "sections" are whole rewritten chapters thousands of words long, so each
version is cut down to the sentence that matches START plus the next one.

The page (output/03_trace.html) shows every version, with the changes from the
version before highlighted, and opens in your browser.
"""

import difflib
import html
import re
import webbrowser

from common import OUTPUT_FOLDER, SCRIPT_DIR, cite, jaccard, phrases, read_sections

# --- Change these --------------------------------------------------------------

START = "white and colored militia shall be separately enrolled"
SHARE = 0.6             # share of START's 3-word phrases a section must contain
SENTENCES = 2           # how many sentences to show, starting with the match

OPEN_IN_BROWSER = True

# -------------------------------------------------------------------------------

TOKEN = re.compile(r"\S+")


def excerpt(text, target):
    """The sentence that best matches START, plus the ones after it."""
    sentences = re.split(r"(?<=[.:;])\s+", text)
    scores = [len(target & phrases(s, 3)) for s in sentences]
    best = scores.index(max(scores))
    return " ".join(sentences[best:best + SENTENCES])


def changes(old, new):
    """The new text as HTML: words added since the old version in green,
    words cut from it in red (struck through)."""
    a, b = TOKEN.findall(old), TOKEN.findall(new)
    out = []
    matcher = difflib.SequenceMatcher(None, [w.lower() for w in a], [w.lower() for w in b],
                                      autojunk=False)
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            out.append(html.escape(" ".join(b[j1:j2])))
            continue
        if i2 > i1:
            out.append(f'<del>{html.escape(" ".join(a[i1:i2]))}</del>')
        if j2 > j1:
            out.append(f'<ins>{html.escape(" ".join(b[j1:j2]))}</ins>')
    return " ".join(out)


def main():
    sections = read_sections()
    target = phrases(START, 3)
    found = []
    for s in sections:
        shared = target & phrases(s["text"], 3)
        if len(shared) / len(target) >= SHARE:
            found.append(s)
    found.sort(key=lambda s: s["year"])
    if not found:
        print("No sections found. Try a lower SHARE or different words in START.")
        return

    print(f"\"{START}\": {len(found)} sections\n")
    parts, previous = [], None
    for s in found:
        text = excerpt(s["text"], target)
        if previous is None:
            similarity, body = "", html.escape(text)
            print(f"  {cite(s):32s}       {text[:90]}")
        else:
            score = jaccard(phrases(previous, 3), phrases(text, 3))
            similarity = f" &middot; 3-gram Jaccard with the version before: {score:.2f}"
            body = changes(previous, text)
            print(f"  {cite(s):32s} {score:.2f}  {text[:90]}")
        parts.append(f"<h2>{html.escape(cite(s))}</h2>"
                     f"<p class='title'>{html.escape(s['title'])}{similarity}</p><p>{body}</p>")
        previous = text

    page = f"""<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(START)}</title>
<style>
 body {{ font-family: Georgia, serif; max-width: 900px; margin: 2em auto; padding: 0 1em;
        line-height: 1.6; color: #141d2e; }}
 h1, h2, .title {{ font-family: Helvetica, Arial, sans-serif; }}
 h2 {{ margin-top: 2em; border-top: 1px solid #ddd; padding-top: 1em; }}
 .title {{ color: #555; font-size: 0.9em; }}
 ins {{ background: #c6f6d5; text-decoration: none; }}
 del {{ background: #fed7d7; }}
</style></head><body>
<h1>“{html.escape(START)}”</h1>
<p>{len(found)} versions, in order. <ins>Green</ins>: added since the version before.
<del>Red</del>: cut since the version before.</p>
{''.join(parts)}
</body></html>"""
    OUTPUT_FOLDER.mkdir(exist_ok=True)
    path = OUTPUT_FOLDER / "03_trace.html"
    path.write_text(page, encoding="utf-8")
    print(f"\nSaved {path.relative_to(SCRIPT_DIR)}")
    if OPEN_IN_BROWSER:
        webbrowser.open(path.resolve().as_uri())


if __name__ == "__main__":
    main()
