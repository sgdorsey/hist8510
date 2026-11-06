#!/usr/bin/env python3
"""
Step 1: N-grams, shingles, and Jaccard similarity
=================================================

Breaks two short texts into overlapping pieces, two ways:

  - word n-grams:       runs of N words       ("the white", "white and", ...)
  - character shingles: runs of K characters  ("the", "he ", "e w", ...)

then measures how much the two sets of pieces overlap with Jaccard similarity:

    pieces the two texts share / all the different pieces in either text

0 = nothing in common, 1 = the same set of pieces.

Change TEXT_A and TEXT_B (and N, K, CLEAN) and run it again.
"""

import re

# --- Change these --------------------------------------------------------------

# North Carolina's militia law, as enacted in 1893 and in 1907
TEXT_A = ("That the white and colored militia shall be separately enrolled and shall never "
          "be compelled to serve in the same companies, battalions, regiments or brigades.")
TEXT_B = ("The white and colored militia shall be separately enrolled, and shall never "
          "be compelled to serve in the same organization.")

N = 2           # words per n-gram
K = 5           # characters per shingle
CLEAN = True    # lowercase and drop punctuation before comparing?

# -------------------------------------------------------------------------------


def clean(text):
    """Lowercase, drop punctuation (both kinds of apostrophe included),
    and squeeze runs of spaces down to one."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())


def word_ngrams(text, n):
    """Every run of n words, as a set."""
    words = text.split()
    starts = range(len(words) - n + 1)
    return {" ".join(words[i:i + n]) for i in starts}


def char_shingles(text, k):
    """Every run of k characters (spaces included), as a set."""
    return {text[i:i + k] for i in range(len(text) - k + 1)}


def jaccard(a, b):
    """Shared pieces / all the different pieces.
    If neither text has any pieces (say, word pairs from two one-word names),
    there's nothing to compare, so the score is 0, not a match."""
    if not a | b:
        return 0.0
    return len(a & b) / len(a | b)


def show(label, a, b):
    shared, everything = a & b, a | b
    print(f"\n{label}")
    print(f"  A ({len(a)}): {sorted(a)}")
    print(f"  B ({len(b)}): {sorted(b)}")
    print(f"  shared ({len(shared)}): {sorted(shared)}")
    print(f"  Jaccard = {len(shared)} shared / {len(everything)} total = {jaccard(a, b):.2f}")


def main():
    a, b = (clean(TEXT_A), clean(TEXT_B)) if CLEAN else (TEXT_A, TEXT_B)
    print(f"A: {a!r}")
    print(f"B: {b!r}")

    show(f"Word {N}-grams", word_ngrams(a, N), word_ngrams(b, N))
    show(f"Character {K}-shingles", char_shingles(a, K), char_shingles(b, K))


if __name__ == "__main__":
    main()
