#!/usr/bin/env python3
"""
Step 2: What did North Carolina's legislators reuse?
====================================================

Compares every section of the session laws with every other section, the way
Kellen Funk and Lincoln Mullen compared nineteenth-century codes of civil
procedure in "The Spine of American Law" (2018), with the same settings.
There's no keyword filter: the search covers all 299,194 sections.

Comparing every pair directly would take about two days, so this uses their
shortcut, MinHash and locality-sensitive hashing (LSH):

  0. Boilerplate: break each section into 5-word phrases and ignore any phrase
     found in more than MAX_SECTIONS sections ("all laws and clauses of laws in
     conflict with this act are hereby repealed"). Session laws are full of
     formulas like these; Funk and Mullen's script has no such step.
  1. MinHash: turn each remaining phrase into a number. Then, for each of 120
     hash functions, keep the smallest hashed value. Those 120 numbers are the
     section's signature. The share of signature numbers two sections have in
     common estimates their Jaccard similarity.
  2. LSH: cut each signature into 60 bands of 2 numbers. Sections that match on
     a whole band land in the same bucket and become candidates. Only
     candidates get compared.
  3. For each section, keep its best match from an earlier year (Funk and
     Mullen's rule). Following those matches back to the first version groups
     sections into families.

Prints how much of each decade's law reuses earlier language, the families
found in the most sessions, and then the families whose text matches LOOK_FOR.
LOOK_FOR doesn't change the search; it only picks which results to print.

Results are saved to output/02_families.csv. Takes about 30 seconds (longer on
older laptops) and about 1.6 GB of memory.
"""

import csv
import re
import zlib
from collections import defaultdict

import numpy as np

from common import OUTPUT_FOLDER, RACE_WORDS, SCRIPT_DIR, cite, phrases, read_sections

# --- Change these --------------------------------------------------------------

N = 5                   # words per phrase
HASHES = 120            # numbers in each signature
BANDS = 60              # bands per signature (HASHES / BANDS numbers per band)
MATCH = 0.5             # a match shares at least this share of its phrases (Jaccard)
MAX_SECTIONS = 300      # phrases in more sections than this are boilerplate
LOOK_FOR = RACE_WORDS.pattern   # second list: families with these words (a regex,
                                # e.g. r"\bindians?\b"; case doesn't matter)
TOP_N = 15              # families to print in each list

# -------------------------------------------------------------------------------

MIN_PHRASES = 10        # sections with fewer distinctive phrases get no signature
ROWS = HASHES // BANDS
PRIME = 4294967291      # the largest prime below 2**32

# 120 hash functions of the form (a * x + b) % PRIME, with random a and b.
# (623 is the seed Funk and Mullen used in R; Python's random numbers differ.)
rng = np.random.default_rng(623)
A = rng.integers(1, 2**31, size=(HASHES, 1), dtype=np.uint64)
B = rng.integers(0, 2**32, size=(HASHES, 1), dtype=np.uint64)


def minhash(numbers):
    """A section's signature: for each hash function, the smallest hashed phrase."""
    x = numbers.astype(np.uint64)
    return ((A * x + B) % PRIME).min(axis=1)


def main():
    print("Reading the corpus...")
    sections = read_sections()
    years = np.array([s["year"] for s in sections])

    # Every section's phrases, each turned into a number (crc32 is a quick,
    # standard way to turn text into a number)
    numbered = []
    for s in sections:
        phrase_set = phrases(s["text"], N)
        numbers = [zlib.crc32(p.encode()) for p in phrase_set]
        numbered.append(np.array(numbers, dtype=np.uint32))

    print(f"0. Boilerplate: phrases found in more than {MAX_SECTIONS} sections...")
    all_numbers = np.concatenate(numbered)
    values, counts = np.unique(all_numbers, return_counts=True)
    boilerplate = set(values[counts > MAX_SECTIONS].tolist())
    print(f"   {len(boilerplate):,} phrases ignored")

    print("1. MinHash: a signature for every section...")
    signatures = np.zeros((len(sections), HASHES), dtype=np.uint32)
    usable = []
    for i, numbers in enumerate(numbered):
        distinctive = [x for x in numbers.tolist()
                       if x not in boilerplate]
        if len(distinctive) >= MIN_PHRASES:
            signatures[i] = minhash(np.array(distinctive))
            usable.append(i)

    print(f"2. LSH: {BANDS} bands, comparing the sections in each bucket...")
    best_score = np.zeros(len(sections))
    best_match = np.full(len(sections), -1)
    for band in range(BANDS):
        columns = signatures[:, band * ROWS:(band + 1) * ROWS]
        buckets = defaultdict(list)
        for i in usable:
            buckets[columns[i].tobytes()].append(i)
        for members in buckets.values():
            if len(members) < 2:
                continue
            m = np.array(members)
            sig = signatures[m]
            # A table with a row and a column for each section in the bucket:
            # the share of signature numbers they have in common (≈ Jaccard)
            score = (sig[:, None, :] == sig[None, :, :]).mean(axis=2)
            # Each row (section) only looks at columns from earlier years
            earlier = years[m][None, :] < years[m][:, None]
            score[~earlier] = 0
            # Keep each section's best earlier match so far
            top = score.argmax(axis=1)
            top_score = score.max(axis=1)
            better = top_score > best_score[m]
            best_score[m[better]] = top_score[better]
            best_match[m[better]] = m[top[better]]

    # 3. Each section that matches an earlier one points to it; follow the
    # pointers back to the first version
    matched = best_score >= MATCH
    first = list(range(len(sections)))
    for i in sorted(np.flatnonzero(matched), key=lambda k: years[k]):
        first[i] = first[best_match[i]]
    families = defaultdict(list)
    for i in np.flatnonzero(matched):
        families[first[i]].append(i)

    print(f"\n{matched.sum():,} sections share at least {MATCH:.0%} of their phrases "
          f"with a section from an earlier year.\n")
    print("Share of each decade's sections that reuse earlier language:")
    for decade in range(1860, 1970, 10):
        in_decade = (years // 10 * 10) == decade
        print(f"  {decade}s  {matched[in_decade].mean():4.0%}  of {in_decade.sum():,}")

    def members(root):
        return sorted(families[root] + [root], key=lambda k: (years[k], k))

    def sessions(root):
        return len({sections[k]["session"] for k in members(root)})

    ranked = sorted(families, key=lambda root: -sessions(root))
    rank = {root: r for r, root in enumerate(ranked, 1)}
    look_for = re.compile(LOOK_FOR, re.IGNORECASE)
    looked_for = [root for root in ranked
                  if any(look_for.search(sections[k]["text"]) for k in members(root))]

    rows = []
    for heading, roots in [("Families found in the most sessions", ranked),
                           ("Families with LOOK_FOR words (numbered by rank in the list above)",
                            looked_for)]:
        print(f"\n{heading}:\n")
        for root in roots[:TOP_N]:
            family = members(root)
            s = sections[root]
            print(f"{rank[root]:5d}. {len(family)} sections in {sessions(root)} "
                  f"sessions, {years[family[0]]}-{years[family[-1]]}")
            print(f"       first: {cite(s)}  {s['title'][:60]}")
            print(f"       \"{s['text'][:180]}...\"\n")
            for k in family:
                rows.append({"family": rank[root], "section": cite(sections[k]),
                             "year": years[k], "title": sections[k]["title"],
                             "text": sections[k]["text"],
                             "best_match": cite(sections[best_match[k]]) if k != root else "",
                             "score": round(best_score[k], 2) if k != root else ""})

    OUTPUT_FOLDER.mkdir(exist_ok=True)
    path = OUTPUT_FOLDER / "02_families.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {path.relative_to(SCRIPT_DIR)}")
    print("Follow one clause through time with 03_reuse_trace_clause.py.")


if __name__ == "__main__":
    main()
