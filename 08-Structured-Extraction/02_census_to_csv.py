#!/usr/bin/env python3
"""
Demo 2: Census of Religious Bodies Schedules to CSV
===================================================

Source: U.S. Census of Religious Bodies, 1926. Each schedule is a printed
form filled in by hand for ONE church, so each image becomes ONE row.

Same method as demo 1 -- codebook -> schema -> JSON -> csv module -- but
here the form itself is the codebook: each question becomes a column.

Every value is saved as text, exactly as written ("None", "no", "663.48").
Turning answers into numbers is interpretation, so it happens in a separate
step: 03_validate_census.py.

Output: output/census.csv (one row per image in images/census/)
"""

import csv
import json
import mimetypes
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

# --- Codebook ---------------------------------------------------------------
# One entry per column: (column name, instructions for the model).
# The question numbers match the printed form.

FIELDS = [
    # Stamps added by the Census Bureau when the form arrived
    ("schedule_number", "The stamped schedule number at the top of the form (e.g. '6553')."),
    ("date_received", "The date stamped at the top right of the form (e.g. 'APR 29 1927')."),

    # a-f: the church
    ("denomination", "a. Denomination."),
    ("association", "b. Association or conference."),
    ("church_name", "c. Local name of church."),
    ("city", "d. City, town, village, or township, including any added words."),
    ("county", "e. County."),
    ("state", "f. State, exactly as written."),

    # 1-6: membership
    ("q1_male", "1. Number of male members."),
    ("q2_female", "2. Number of female members."),
    ("q3_total_by_sex", "3. Total number of members (the total for questions 1 and 2)."),
    ("q4_under_13", "4. Number of members under 13 years of age."),
    ("q5_13_and_over", "5. Number of members 13 years old and over."),
    ("q6_total_by_age", "6. Total number of members (the total for questions 4 and 5)."),

    # 7-12: church buildings
    ("q7_edifices", "7. Number of church edifices."),
    ("q8_value_edifices", "8. Value of church edifices, in dollars."),
    ("q9_debt_edifices", "9. Debt on church edifices, in dollars."),
    ("q10_owns_residence", "10. Does church own pastor's residence (yes or no)."),
    ("q11_value_residence", "11. Value of pastor's residence, in dollars."),
    ("q12_debt_residence", "12. Debt on pastor's residence, in dollars."),

    # 13-15: expenditures
    ("q13_running_expenses", "13. Amount expended for salaries, repairs, running expenses, improvements, and payments on debt."),
    ("q14_benevolences", "14. Amount expended for benevolences, missions, denominational support, and other purposes."),
    ("q15_total_expenditures", "15. Total expenditures during year."),

    # 25: pastor
    ("q25_pastor_name", "25. Name of pastor."),

    # What the model noticed beyond the answers
    ("corrections",
     "Any answer that was crossed out and replaced, written as "
     "'question number: old value -> new value' (e.g. '3: 514 -> 442'). "
     "Separate several with '; '. Empty if none."),
    ("clerk_marks",
     "Marks added by census clerks rather than by the person filling out the form "
     "(often in red or colored pencil: numbers in the margins, check marks, codes), "
     "briefly described. Empty if none."),
]

PROMPT = """This image is a schedule from the 1926 United States Census of Religious
Bodies: a printed form that one church filled in by hand. Transcribe the
handwritten answers into the fields.

Rules:
- Write each answer exactly as written, including words like 'None' or 'no'.
  Do not correct, calculate, or fill in anything that is not written.
- Numbers: copy the digits exactly as written, including any decimal point.
  Do not add dollar signs or commas.
- If an answer space is empty, leave the field empty.
- If an answer space contains only a check mark, write [check].
- If an answer was crossed out and replaced, use the final answer and record
  the change in 'corrections'.
- If you cannot read an answer, write [illegible]. Do not guess."""

# --- Settings ---------------------------------------------------------------

MODEL = "gemini-3.5-flash-lite"

# Paid-tier prices in US dollars per 1 million tokens: (input, output).
# Check https://ai.google.dev/gemini-api/docs/pricing -- prices change.
PRICES = {
    "gemini-3.5-flash-lite": (0.30, 2.50),
    "gemini-3.1-flash-lite": (0.25, 1.50),
    "gemini-2.5-flash-lite": (0.10, 0.40),
}

SCRIPT_DIR = Path(__file__).parent
IMAGE_FOLDER = SCRIPT_DIR / "images" / "census"
OUTPUT_FILE = SCRIPT_DIR / "output" / "census.csv"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# ----------------------------------------------------------------------------


def build_schema(fields):
    """Turn the codebook into a JSON schema: one form, one object."""
    return {
        "type": "object",
        "properties": {
            name: {"type": "string", "description": description}
            for name, description in fields
        },
        "required": [name for name, _ in fields],
    }


def extract_form(client, image_path):
    """Send one image to Gemini and return (parsed data, response)."""
    mime_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"
    image_part = types.Part.from_bytes(data=image_path.read_bytes(), mime_type=mime_type)

    response = client.models.generate_content(
        model=MODEL,
        contents=[image_part, PROMPT],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",   # answer in JSON only...
            response_json_schema=build_schema(FIELDS),  # ...shaped like this
        ),
    )
    return json.loads(response.text), response


def calculate_cost(input_tokens, output_tokens):
    input_price, output_price = PRICES[MODEL]
    return (input_tokens * input_price + output_tokens * output_price) / 1_000_000


def main():
    load_dotenv(SCRIPT_DIR / ".env")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("No API key found. Copy .env.example to .env and add your GEMINI_API_KEY.")
        return

    images = sorted(p for p in IMAGE_FOLDER.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS)
    if not images:
        print(f"No images found in {IMAGE_FOLDER}")
        return

    client = genai.Client(api_key=api_key)
    rows = []
    total_cost = 0.0

    for image_path in images:
        print(f"Extracting {image_path.name} ...")
        data, response = extract_form(client, image_path)
        data["source_image"] = image_path.name   # added by code, not the model
        rows.append(data)

        usage = response.usage_metadata
        output_tokens = (usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0)
        cost = calculate_cost(usage.prompt_token_count or 0, output_tokens)
        total_cost += cost

        print(f"  {data['church_name']}, {data['city']}, {data['state']}")
        if data["corrections"]:
            print(f"  Corrections: {data['corrections']}")
        print(f"  Tokens: {usage.prompt_token_count:,} in, {output_tokens:,} out   "
              f"Cost: ${cost:.6f}\n")

    columns = ["source_image"] + [name for name, _ in FIELDS]
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print("=" * 40)
    print(f"Saved {len(rows)} rows to {OUTPUT_FILE.relative_to(SCRIPT_DIR)}")
    print(f"Total cost: ${total_cost:.6f}")
    print("\nNext: python 03_validate_census.py")


if __name__ == "__main__":
    main()
