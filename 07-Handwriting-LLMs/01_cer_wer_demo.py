#!/usr/bin/env python3
"""
Demo 1: Character and Word Error Rates
======================================

How do we measure whether a transcription is "good"? We compare it to a
ground truth -- a transcription a person made and checked by hand -- and
count the smallest number of edits that turn one into the other:

  S = substitution  (a wrong character or word)
  D = deletion      (something on the page is missing from the output)
  I = insertion     (the output has something that isn't on the page)

  CER = character edits / characters in the ground truth
  WER = word edits / words in the ground truth

No API key needed -- this script just runs the math on a few short examples.
Edit the EXAMPLES list to try your own.
"""

import jiwer

# (label, ground truth, transcription)
EXAMPLES = [
    ("One misread letter",
     "the army moved",
     "the arrny moved"),

    ("Skipped a word (deletion)",
     "we marched at dawn to the river",
     "we marched at dawn to river"),

    ("Invented a word (insertion)",
     "the letter arrived",
     "the long letter arrived"),

    ("'Corrected' a period spelling",
     "the publick house was full",
     "the public house was full"),

    ("Only case and punctuation differ",
     "Monday, June 3rd.",
     "monday june 3rd"),
]


def show(label, reference, hypothesis):
    words = jiwer.process_words(reference, hypothesis)
    chars = jiwer.process_characters(reference, hypothesis)

    print(f"--- {label} ---")
    print(f"Ground truth:  {reference}")
    print(f"Transcription: {hypothesis}\n")

    print("Word alignment:")
    # skip_correct=False so a perfect match still prints; drop jiwer's header line
    alignment = jiwer.visualize_alignment(words, show_measures=False, skip_correct=False)
    print(alignment.replace("=== SENTENCE 1 ===\n\n", "").rstrip() + "\n")

    print(f"  CER: {chars.cer:6.1%}   "
          f"(S={chars.substitutions}, D={chars.deletions}, I={chars.insertions} "
          f"out of {chars.hits + chars.substitutions + chars.deletions} characters)")
    print(f"  WER: {words.wer:6.1%}   "
          f"(S={words.substitutions}, D={words.deletions}, I={words.insertions} "
          f"out of {words.hits + words.substitutions + words.deletions} words)\n")


def main():
    for label, reference, hypothesis in EXAMPLES:
        show(label, reference, hypothesis)

    print("Things to notice:")
    print("  - WER is harsher than CER: one wrong letter makes the whole word wrong.")
    print("  - A 'corrected' spelling counts as an error -- the page didn't say that.")
    print("  - The last example has no real reading errors, only formatting.")
    print("    That's why 03_evaluate.py reports a raw AND a normalized score.")


if __name__ == "__main__":
    main()
