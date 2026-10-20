#!/usr/bin/env python3
"""
Demo 3: NER with Gemini (labels + instructions + historical context)
====================================================================

Same method as Week 8: a codebook becomes a schema, and Gemini must answer
in JSON with exactly that shape. Two additions from the readings:

  1. CONTEXT tells the model what the source is (Hiltmann et al. 2025
     found historical context was the key to good LLM results).
  2. Gemini returns the entity TEXT, not its position. Code then looks for
     each one in the source. Anything it can't find word for word is
     flagged: the model either invented it or "corrected" the source
     (the problem Tudor et al. 2025 found).

Output: output/03_gemini.csv and output/03_gemini.html
"""

import json
import os
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types

from common import SCRIPT_DIR, load_source, save_results

# --- Codebook ---------------------------------------------------------------
# One entry per entity type: (label, instructions). Change these to fit your source.

LABELS = [
    ("PERSON", "A named individual, real or fictional (e.g. a character in a play). "
               "If a person's name is part of a larger name -- a county, school, or "
               "holiday such as 'Washington County' -- do not label it as a person."),
    ("STATE", "A U.S. state (e.g. 'Alabama')."),
    ("COUNTY", "A county, written as in the text (e.g. 'Blount County'). If several "
               "counties share one word 'Counties' (e.g. 'Johnson and Pope Counties'), "
               "label the whole phrase."),
    ("CITY_OR_TOWN", "A city, town, or community (e.g. 'Tuscumbia', 'Little Rock')."),
    ("ORGANIZATION", "A named organization: a government agency, club, church, council, "
                     "business, or radio station (e.g. 'WPA', 'Kiwanis Club', 'Baptist Church')."),
    ("FACILITY", "A named building or site where activities happen: a park, school, "
                 "auditorium, center, or home (e.g. 'Municipal Auditorium', 'Oak Park')."),
]

# What the model should know about the source (Hiltmann et al.: context matters)
CONTEXT = """The text is from a 1937 report on the recreation program of the Works
Progress Administration (WPA), a New Deal agency. It summarizes monthly activities
county by county in Alabama (February 1937) and Arkansas (March 1937). The pages
were typed and then OCR'd, so the text contains OCR errors, stray page numbers,
and some markup such as <u>. The report reflects segregation: it uses the period
terms 'colored' and 'Negro' for programs and facilities for Black residents."""

PROMPT = f"""You are a historian annotating a primary source for named entities.

About the source:
{CONTEXT}

Find every named entity in the text below and give each one a label.

Rules:
- Copy each entity EXACTLY as it is written in the text: same spelling,
  capitalization, and punctuation. Do not correct or modernize anything.
- List every mention in the order it appears, including repeats.
- Only include entities that are actually in the text.

Text:
"""

# --- Settings ---------------------------------------------------------------

MODEL = "gemini-3.5-flash-lite"

# Paid-tier prices in US dollars per 1 million tokens: (input, output).
# Check https://ai.google.dev/gemini-api/docs/pricing -- prices change.
PRICES = {
    "gemini-3.5-flash-lite": (0.30, 2.50),
    "gemini-3.1-flash-lite": (0.25, 1.50),
    "gemini-2.5-flash-lite": (0.10, 0.40),
}

# ----------------------------------------------------------------------------


def build_schema(labels):
    """A list of entities; each label must be one from the codebook (an enum)."""
    label_guide = " ".join(f"{name}: {description}" for name, description in labels)
    return {
        "type": "object",
        "properties": {
            "entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string",
                                 "description": "The entity exactly as written in the text."},
                        "label": {"type": "string",
                                  "enum": [name for name, _ in labels],
                                  "description": label_guide},
                    },
                    "required": ["text", "label"],
                },
            },
        },
        "required": ["entities"],
    }


def find_in_text(text, entities):
    """Gemini gives us entity text, not positions. Find each mention in the
    source, moving forward through the text so repeats land in the right place."""
    found, missing = [], []
    cursor = 0
    for entity in entities:
        # Match the words exactly, but let any space be a line break too
        # ("Young Men's Club" is split across two lines in the source)
        pattern = re.compile(r"\s+".join(re.escape(word) for word in entity["text"].split()))
        match = pattern.search(text, cursor) or pattern.search(text)  # ahead, then from the top
        if not match:                         # not in the text at all
            missing.append(entity)
            continue
        found.append({**entity, "text": match.group(), "start": match.start(), "end": match.end()})
        cursor = match.end()
    return found, missing


def main():
    load_dotenv(SCRIPT_DIR / ".env")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("No API key found. Copy .env.example to .env and add your GEMINI_API_KEY.")
        return

    text = load_source()
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=MODEL,
        contents=PROMPT + text,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_json_schema=build_schema(LABELS),
        ),
    )
    entities = json.loads(response.text)["entities"]
    found, missing = find_in_text(text, entities)

    print(f"Model: {MODEL}")
    save_results("03_gemini", text, found, f"Gemini ({MODEL})")

    if missing:
        print(f"\nNOT FOUND word for word in the source ({len(missing)}):")
        print("(invented, or 'corrected' -- compare with the text)")
        for entity in missing:
            print(f"  {entity['text']}  {entity['label']}")
    else:
        print("\nEvery entity was found word for word in the source.")

    usage = response.usage_metadata
    output_tokens = (usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0)
    input_price, output_price = PRICES[MODEL]
    cost = (usage.prompt_token_count * input_price + output_tokens * output_price) / 1_000_000
    print(f"\nTokens: {usage.prompt_token_count:,} in, {output_tokens:,} out   Cost: ${cost:.6f}")


if __name__ == "__main__":
    main()
