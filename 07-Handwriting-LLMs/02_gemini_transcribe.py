#!/usr/bin/env python3
"""
Demo 2: Handwriting Transcription with Gemini
=============================================

Sends every image in the images/ folder to Gemini and asks for a verbatim
transcription that follows our transcription conventions (see the PROMPT
below and the README). Results are saved as .txt files in
ocr-results/<RUN_NAME>/.

For every image the script prints the tokens used and what the call cost.
At the end it prints the totals.

To run an experiment, change MODEL, THINKING_LEVEL, or PROMPT, AND give it a
new RUN_NAME so it doesn't overwrite your earlier results. Then run
03_evaluate.py to compare the runs.

Before running:
  1. Copy .env.example to .env and paste in your Gemini API key.
  2. pip install -r requirements.txt
"""

import mimetypes
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

# --- Settings ---------------------------------------------------------------

# Name of the folder inside ocr-results/ where this run is saved.
# Change it for each experiment, e.g. "high-thinking" or "2.5-lite".
RUN_NAME = "baseline"

MODEL = "gemini-3.5-flash-lite"

# How much the model "thinks" before answering: "minimal", "low", "medium",
# or "high". None uses the model's default (minimal for 3.5 Flash-Lite).
# More thinking costs more -- does it also read handwriting better?
# (Leave this as None for gemini-2.5 models; they use a different setting.)
THINKING_LEVEL = None

# Paid-tier prices in US dollars per 1 million tokens: (input, output).
# Check https://ai.google.dev/gemini-api/docs/pricing -- prices change.
PRICES = {
    "gemini-3.5-flash-lite": (0.30, 2.50),
    "gemini-3.1-flash-lite": (0.25, 1.50),
    "gemini-2.5-flash-lite": (0.10, 0.40),
}

SCRIPT_DIR = Path(__file__).parent
IMAGE_FOLDER = SCRIPT_DIR / "images"
OUTPUT_FOLDER = SCRIPT_DIR / "ocr-results" / RUN_NAME

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}

PROMPT = """Transcribe the handwritten text in this image exactly as it appears on the page.

Rules:
- Transcribe verbatim. Do NOT correct spelling, grammar, punctuation, or capitalization.
  Keep misspellings, abbreviations, and archaic spellings exactly as written.
  Do not expand abbreviations.
- Do NOT summarize, paraphrase, translate, or add anything that is not on the page.
- Keep the original line breaks: start a new line wherever the writer did.
- Words that are crossed out: write [crossed out: word]. If the crossed-out
  text cannot be read, write [crossed out].
- Words added above or below the line: put them where they belong in the
  sentence and write [inserted: word].
- If a word cannot be read, write [illegible] in its place. Do not guess.
- If you can partly read a word but are unsure, write your best reading followed by [?].
- Output only the transcription: no introduction, no commentary, no markdown formatting."""

# ----------------------------------------------------------------------------


def find_images(folder):
    """Return a sorted list of image files in the folder."""
    return sorted(
        path for path in folder.iterdir()
        if path.suffix.lower() in IMAGE_EXTENSIONS
    )


def transcribe_image(client, image_path):
    """Send one image to Gemini and return the response."""
    mime_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"
    image_part = types.Part.from_bytes(data=image_path.read_bytes(), mime_type=mime_type)

    config = None
    if THINKING_LEVEL:
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level=THINKING_LEVEL)
        )

    return client.models.generate_content(
        model=MODEL,
        contents=[image_part, PROMPT],
        config=config,
    )


def calculate_cost(input_tokens, output_tokens):
    """Convert token counts into dollars."""
    input_price, output_price = PRICES[MODEL]
    input_cost = input_tokens / 1_000_000 * input_price
    output_cost = output_tokens / 1_000_000 * output_price
    return input_cost + output_cost


def main():
    load_dotenv(SCRIPT_DIR / ".env")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("No API key found. Copy .env.example to .env and add your GEMINI_API_KEY.")
        return

    if MODEL not in PRICES:
        print(f"No price listed for {MODEL}. Add it to PRICES at the top of the script.")
        return

    images = find_images(IMAGE_FOLDER)
    if not images:
        print(f"No images found in {IMAGE_FOLDER}")
        return

    client = genai.Client(api_key=api_key)
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    print(f"Run:      {RUN_NAME}")
    print(f"Model:    {MODEL}")
    print(f"Thinking: {THINKING_LEVEL or 'model default'}")
    print(f"Found {len(images)} image(s) in {IMAGE_FOLDER.name}/\n")

    total_input = 0
    total_output = 0
    total_cost = 0.0

    for image_path in images:
        print(f"Transcribing {image_path.name} ...")
        response = transcribe_image(client, image_path)

        text = response.text or ""
        output_path = OUTPUT_FOLDER / f"{image_path.stem}.txt"
        output_path.write_text(text, encoding="utf-8")

        # Thinking tokens are billed at the output price, so count them as output.
        usage = response.usage_metadata
        input_tokens = usage.prompt_token_count or 0
        text_tokens = usage.candidates_token_count or 0
        thinking_tokens = usage.thoughts_token_count or 0
        output_tokens = text_tokens + thinking_tokens
        cost = calculate_cost(input_tokens, output_tokens)

        print(f"  Saved to {output_path.relative_to(SCRIPT_DIR)}")
        print(f"  Input tokens:    {input_tokens:,}")
        print(f"  Output tokens:   {text_tokens:,}")
        print(f"  Thinking tokens: {thinking_tokens:,}")
        print(f"  Cost:            ${cost:.6f}\n")

        total_input += input_tokens
        total_output += output_tokens
        total_cost += cost

    print("=" * 40)
    print(f"Images processed:       {len(images)}")
    print(f"Total input tokens:     {total_input:,}")
    print(f"Total output tokens:    {total_output:,}  (includes thinking)")
    print(f"Total cost:             ${total_cost:.6f}")
    print("\nNext: python 03_evaluate.py")


if __name__ == "__main__":
    main()
