#!/usr/bin/env python3
"""
Demo 3: Evaluating Transcriptions (CER and WER)
===============================================

Compares Gemini's transcriptions in ocr-results/ against the hand-checked
transcriptions in ground-truth/ and reports character and word error rates.

Every run folder in ocr-results/ (baseline, high-thinking, ...) is scored,
so you can compare experiments side by side.

Two scores are reported for each page:
  raw         - exact text; case, punctuation, and line breaks all count
  normalized  - lowercased, punctuation removed, all whitespace collapsed,
                so only the words themselves count

The gap between the two shows how much of the "error" was really formatting.

Output:
  - a table printed to the terminal
  - evaluation/results.csv with every score
  - evaluation/<run>/<page>_alignment.txt showing exactly where the errors are

No API key needed -- this script only reads files, so you can rerun it for free.
"""

import csv
import re
from pathlib import Path

import jiwer

SCRIPT_DIR = Path(__file__).parent
GROUND_TRUTH_FOLDER = SCRIPT_DIR / "ground-truth"
RESULTS_FOLDER = SCRIPT_DIR / "ocr-results"
EVAL_FOLDER = SCRIPT_DIR / "evaluation"


def clean_raw(text):
    """Light cleanup that shouldn't count as an error: Windows line endings,
    invisible spaces at the ends of lines, and blank lines at start/end."""
    text = text.replace("\r\n", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    return "\n".join(lines).strip()


def normalize(text):
    """Lowercase, remove punctuation, and collapse all whitespace
    (including line breaks) to single spaces."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def score(references, hypotheses):
    """Return (CER, WER) for a list of page texts.
    With several pages this is total edits / total length, so long pages
    count for more than short ones."""
    cer = jiwer.cer(references, hypotheses)
    wer = jiwer.wer(references, hypotheses)
    return cer, wer


def format_alignment(reference, hypothesis):
    """Word-by-word comparison, wrapped to fit on screen, with error counts."""
    # Line breaks would scramble the display (and don't affect WER),
    # so show everything as one flowing paragraph.
    reference = " ".join(reference.split())
    hypothesis = " ".join(hypothesis.split())

    output = jiwer.process_words(reference, hypothesis)
    # skip_correct=False so a perfect page still shows its text instead of nothing
    alignment = jiwer.visualize_alignment(output, show_measures=False,
                                          skip_correct=False, line_width=80)
    alignment = alignment.replace("=== SENTENCE 1 ===\n\n", "")

    counts = (f"substitutions={output.substitutions}  deletions={output.deletions}  "
              f"insertions={output.insertions}  correct={output.hits}")
    return f"{counts}\n\n{alignment.rstrip()}"


def save_alignment(path, raw_ref, raw_hyp, norm_ref, norm_hyp):
    """Write a word-by-word comparison so students can see each error."""
    path.write_text(
        "Word alignment. REF = ground truth, HYP = transcription.\n"
        "S = substitution, D = deletion, I = insertion, * = nothing there.\n\n"
        "===== RAW (case and punctuation count) =====\n"
        f"{format_alignment(raw_ref, raw_hyp)}\n\n"
        "===== NORMALIZED (words only) =====\n"
        f"{format_alignment(norm_ref, norm_hyp)}\n",
        encoding="utf-8",
    )


def find_runs():
    """Every folder in ocr-results/ that has .txt files in it."""
    if not RESULTS_FOLDER.exists():
        return []
    return sorted(
        folder for folder in RESULTS_FOLDER.iterdir()
        if folder.is_dir() and any(folder.glob("*.txt"))
    )


def evaluate_run(run_folder, ground_truth_files):
    """Score one run. Prints a table and returns rows for the CSV."""
    run_name = run_folder.name
    alignment_folder = EVAL_FOLDER / run_name
    alignment_folder.mkdir(parents=True, exist_ok=True)

    name_width = max(len(f.stem) for f in ground_truth_files)
    name_width = max(name_width, len("All pages"))

    print(f"\nRun: {run_name}")
    print(f"{'':{name_width}}   ------ raw ------   -- normalized --")
    print(f"{'Page':{name_width}}      CER      WER       CER      WER")

    raw_refs, raw_hyps, norm_refs, norm_hyps = [], [], [], []
    rows = []
    missing = []

    for gt_path in ground_truth_files:
        result_path = run_folder / gt_path.name
        if not result_path.exists():
            missing.append(gt_path.stem)
            continue

        raw_ref = clean_raw(gt_path.read_text(encoding="utf-8"))
        raw_hyp = clean_raw(result_path.read_text(encoding="utf-8"))
        norm_ref = normalize(raw_ref)
        norm_hyp = normalize(raw_hyp)

        raw_cer, raw_wer = score(raw_ref, raw_hyp)
        norm_cer, norm_wer = score(norm_ref, norm_hyp)

        print(f"{gt_path.stem:{name_width}}   {raw_cer:6.1%}   {raw_wer:6.1%}"
              f"    {norm_cer:6.1%}   {norm_wer:6.1%}")

        save_alignment(alignment_folder / f"{gt_path.stem}_alignment.txt",
                       raw_ref, raw_hyp, norm_ref, norm_hyp)

        raw_refs.append(raw_ref)
        raw_hyps.append(raw_hyp)
        norm_refs.append(norm_ref)
        norm_hyps.append(norm_hyp)
        rows.append([run_name, gt_path.stem, raw_cer, raw_wer, norm_cer, norm_wer])

    if not rows:
        print("  No transcriptions match the ground-truth file names.")
        return rows

    raw_cer, raw_wer = score(raw_refs, raw_hyps)
    norm_cer, norm_wer = score(norm_refs, norm_hyps)
    print("-" * (name_width + 38))
    print(f"{'All pages':{name_width}}   {raw_cer:6.1%}   {raw_wer:6.1%}"
          f"    {norm_cer:6.1%}   {norm_wer:6.1%}")
    rows.append([run_name, "ALL PAGES", raw_cer, raw_wer, norm_cer, norm_wer])

    if missing:
        print(f"  No transcription for: {', '.join(missing)}")
    print(f"  Alignments saved to {alignment_folder.relative_to(SCRIPT_DIR)}/")

    return rows


def main():
    ground_truth_files = sorted(
        path for path in GROUND_TRUTH_FOLDER.glob("*.txt")
        if path.read_text(encoding="utf-8").strip()
    )
    if not ground_truth_files:
        print(f"No ground-truth .txt files found in {GROUND_TRUTH_FOLDER.name}/")
        print("Each file should have the same name as its image, e.g. letter1.jpg -> letter1.txt")
        return

    runs = find_runs()
    if not runs:
        print(f"No transcriptions found in {RESULTS_FOLDER.name}/. Run 02_gemini_transcribe.py first.")
        return

    print(f"Ground truth: {len(ground_truth_files)} page(s)")
    print(f"Runs found:   {', '.join(run.name for run in runs)}")

    all_rows = []
    for run_folder in runs:
        all_rows.extend(evaluate_run(run_folder, ground_truth_files))

    # Side-by-side summary when there's more than one run to compare
    totals = [row for row in all_rows if row[1] == "ALL PAGES"]
    if len(totals) > 1:
        run_width = max(len(row[0]) for row in totals)
        print("\nComparison of runs (all pages, normalized)")
        print(f"{'Run':{run_width}}      CER      WER")
        for run_name, _, _, _, norm_cer, norm_wer in totals:
            print(f"{run_name:{run_width}}   {norm_cer:6.1%}   {norm_wer:6.1%}")

    csv_path = EVAL_FOLDER / "results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["run", "page", "raw_cer", "raw_wer", "normalized_cer", "normalized_wer"])
        for row in all_rows:
            writer.writerow(row[:2] + [round(value, 4) for value in row[2:]])
    print(f"\nAll scores saved to {csv_path.relative_to(SCRIPT_DIR)}")


if __name__ == "__main__":
    main()
