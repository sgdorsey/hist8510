# Text Reuse

Find passages that one text shares with another, even when the copy isn't exact. Break texts into
overlapping pieces (word n-grams and character shingles) and measure how much the pieces overlap
(Jaccard similarity). Then scale up to a century of North Carolina session laws: compare every
section with every other, with the method Funk and Mullen used for American codes of civil
procedure (MinHash and locality-sensitive hashing), to see what legislators reused, where race
language sits in that reuse, and how one clause changed over time.

| Script | What it does | What you change |
|---|---|---|
| `01_reuse_jaccard_by_hand.py` | N-grams, shingles and Jaccard for two short texts, step by step | `TEXT_A`, `TEXT_B`, `N`, `K`, `CLEAN` |
| `02_reuse_minhash.py` | Compares all 299,194 sections: what did legislators reuse, and where does race language appear? | `MATCH`, `MAX_SECTIONS`, `BANDS`, `LOOK_FOR` |
| `03_reuse_trace_clause.py` | Follows one clause through the sessions and shows what changed | `START`, `SHARE` |
| `common.py` | Reads the corpus into sections (used by 02 and 03) | `RACE_WORDS` |

---

## The corpus

*Session Laws Passed by the North Carolina General Assembly During 1866/67-1967 (plain text format),
version 2*, from the University of North Carolina Libraries' project
[On the Books: Jim Crow and Algorithms of Resistance](https://onthebooks.lib.unc.edu/). The volumes
were scanned by the Internet Archive and OCR'd by the project, which also split every volume into
laws ("chapters") and their sections: 299,194 sections, about 30 million words. The project estimates
84% of words were OCR'd correctly.

License: [CC BY-NC 3.0](https://creativecommons.org/licenses/by-nc/3.0/). Cite it as:

> University Libraries, University of North Carolina at Chapel Hill. Session Laws Passed by the North
> Carolina General Assembly During 1866/67-1967 (plain text format) version 2, from On the Books: Jim
> Crow and Algorithms of Resistance. 2021.

These laws contain the racist language of segregation. That language is what the project, and this
week's scripts, set out to find.

---

## The method

Step 2 follows Kellen Funk and Lincoln Mullen, "The Spine of American Law: Digital Text Analysis and
U.S. Legal Practice," *American Historical Review* 123, no. 1 (2018): 132–164,
[doi:10.1093/ahr/123.1.132](https://doi.org/10.1093/ahr/123.1.132). Their code is at
[lmullen/civil-procedure-codes](https://github.com/lmullen/civil-procedure-codes) (see
`scripts/corpus-lsh.R`); it uses Mullen's R package
[textreuse](https://docs.ropensci.org/textreuse/). We use their settings: sections as the unit,
5-word phrases, 120 minhashes, 60 bands, and each section's best match from an earlier year.

Three differences:

- **Boilerplate.** Session laws repeat formulas thousands of times, so `02` first ignores any phrase
  found in more than `MAX_SECTIONS` sections. Their script has no such step.
- **Scores.** They computed the exact Jaccard similarity of every candidate pair. `02` uses the
  estimate MinHash gives for free (the share of the 120 signature numbers two sections have in
  common), which has a typical error of about 0.05.
- **Threshold.** They kept matches scoring as low as 0.1 and, among close scores, preferred a code
  from the same state and the most recent one. `02` counts a match from 0.5 (`MATCH`) and keeps
  each section's single best match.

`02` writes MinHash out by hand in a few lines of numpy so you can see how it works. The usual Python
library for it is [datasketch](https://ekzhu.com/datasketch/).

---

## Setup

### Step 1: Create the virtual environment

From inside the `11-Text-Reuse` folder:

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt # installs numpy
```

### Step 2: Download and unzip the corpus

The zip is 46 MB (183 MB unzipped), from the
[Carolina Digital Repository](https://cdr.lib.unc.edu/concern/data_sets/v405sk89q). Run these from
inside the `11-Text-Reuse` folder.

**Mac (Terminal):**

```bash
curl -L -o on_the_books_text_v2.zip "https://cdr.lib.unc.edu/downloads/6h4413018"
unzip -q on_the_books_text_v2.zip -d on_the_books_text_v2
```

**Windows (PowerShell):**

```powershell
Invoke-WebRequest -Uri "https://cdr.lib.unc.edu/downloads/6h4413018" -OutFile on_the_books_text_v2.zip
Expand-Archive on_the_books_text_v2.zip -DestinationPath on_the_books_text_v2
```

You should now have an **`on_the_books_text_v2`** folder of 96 text files, one per volume
(plus a readme). If the download doesn't work, open the repository page above in a browser, download
the zip, move it into `11-Text-Reuse`, and run just the unzip command.

---

## Running it

```bash
source venv/bin/activate        # Windows: venv\Scripts\activate
python 01_reuse_jaccard_by_hand.py
python 02_reuse_minhash.py             # about 30 seconds and 1.6 GB of memory
python 03_reuse_trace_clause.py        # opens a page in your browser
```

To follow a different clause, copy a few distinctive words from the output of `02` (or from
`output/02_families.csv`) into `START` in `03`. Results are saved in `output/`.

---

## Things to keep in mind

- **Legal text is full of boilerplate.** "All laws and clauses of laws in conflict with this act are
  hereby repealed" appears more than 10,000 times. `02` ignores phrases found in more than
  `MAX_SECTIONS` sections; without that, every law looks like a copy of every other. Sections left
  with fewer than 10 distinctive phrases (84,317 of them, mostly formulas) aren't compared at all.
- **The search is broad; the keywords only pick what to print.** `02` compares every section.
  `LOOK_FOR` (by default `RACE_WORDS` in `common.py`: *white and colored*, *colored race*, *negro*,
  *separate schools*...) just chooses the second list of results. The keywords are rough: they miss
  laws that classify people in other words (for example, laws about Native Americans). The On the
  Books team used machine learning to identify Jim Crow laws; their results are in the same
  repository.
- **Counting favors routine.** The families found in the most sessions are the revenue act's tax
  procedures, passed again almost every session. Being copied often doesn't make a clause important.
- **Earlier doesn't prove copying.** When two laws share a clause, the earlier one is only the earliest
  surviving version. Drafters may have copied a general statute or a template instead.
- **OCR errors break n-grams.** *That* read as *Phat*, *provided* as *yovtded*. Character shingles cope
  better than word n-grams.
- **Some sections are mis-split.** The project corrected most chapter and section errors, but a few
  remain (a "section" that holds a whole chapter, or a law under the wrong title: in `02`, some
  revenue act sections show up under the title of the act printed before them). `03` shows only the
  sentences around the match for that reason.
