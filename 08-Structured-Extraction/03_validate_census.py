#!/usr/bin/env python3
"""
Demo 3: Validating the Census Data
==================================

The 1926 schedule has its own built-in check. Under question 6 it says:

  "The total given under Question 6 should be the same as the total
   of males and females given under Question 3."

Census clerks checked forms like this by hand. This script does the same
arithmetic for every row in output/census.csv and flags anything that
doesn't add up -- a way to catch errors WITHOUT a ground truth.

A mismatch can mean three things, and only a person can tell which:
  - the model misread a number
  - the person who filled out the form made a mistake
  - the form was corrected and the model picked the wrong value

No API key needed -- this script only reads the CSV.

Output: output/census_checked.csv (the data plus one column per check)
"""

import csv
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
INPUT_FILE = SCRIPT_DIR / "output" / "census.csv"
OUTPUT_FILE = SCRIPT_DIR / "output" / "census_checked.csv"

# (check name, columns that should add up, column with the total)
CHECKS = [
    ("q1+q2=q3", ["q1_male", "q2_female"], "q3_total_by_sex"),
    ("q3=q6", ["q3_total_by_sex"], "q6_total_by_age"),
    ("q4+q5=q6", ["q4_under_13", "q5_13_and_over"], "q6_total_by_age"),
    ("q13+q14=q15", ["q13_running_expenses", "q14_benevolences"], "q15_total_expenditures"),
]


def to_number(value):
    """Turn a transcribed answer into a number, or None if it isn't one.

    These are interpretive decisions -- change them if you disagree:
      - 'None' written on the form counts as 0
      - empty, [check], and [illegible] count as missing
      - dollar signs, commas, and spaces are ignored
    """
    value = value.strip()
    if value.lower() == "none":
        return 0.0
    value = value.replace("$", "").replace(",", "").replace(" ", "")
    try:
        return float(value)
    except ValueError:
        return None


def run_check(row, parts, total_column):
    """Return 'ok', 'missing', or a description of the mismatch."""
    numbers = [to_number(row[column]) for column in parts]
    total = to_number(row[total_column])
    if total is None or None in numbers:
        return "missing"
    if abs(sum(numbers) - total) < 0.01:   # allow for rounding of cents
        return "ok"
    return f"MISMATCH: adds up to {sum(numbers):g}, form says {total:g}"


def main():
    if not INPUT_FILE.exists():
        print(f"{INPUT_FILE.relative_to(SCRIPT_DIR)} not found. Run 02_census_to_csv.py first.")
        return

    with open(INPUT_FILE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Checking {len(rows)} schedule(s)\n")
    mismatches = 0

    for row in rows:
        print(f"{row['source_image']}: {row['church_name']}, {row['city']}, {row['state']}")
        for name, parts, total_column in CHECKS:
            result = run_check(row, parts, total_column)
            row[name] = result
            if result.startswith("MISMATCH"):
                mismatches += 1
            print(f"  {name:12} {result}")
        if row["corrections"]:
            print(f"  corrections  {row['corrections']}")
        print()

    columns = list(rows[0].keys()) if rows else []
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print("=" * 40)
    print(f"Mismatches found: {mismatches}")
    print("For each mismatch, look at the image: did the model misread it,")
    print("or does the form itself not add up?")
    print(f"\nSaved to {OUTPUT_FILE.relative_to(SCRIPT_DIR)}")


if __name__ == "__main__":
    main()
