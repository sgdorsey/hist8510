#!/usr/bin/env python3
"""
OCR with an LLM: Gemini Flash-Lite
==================================

Sends every image in the images/ folder to Gemini and asks for a verbatim
transcription that keeps the page's layout (columns, line breaks, spacing).
Each transcription is saved as a .txt file in ocr-results/.

For every image the script prints the tokens used and what the call cost.
At the end it prints the totals.

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

MODEL = "gemini-3.5-flash-lite"

# Paid-tier prices in US dollars per 1 million tokens.
# Check https://ai.google.dev/gemini-api/docs/pricing -- prices change.
INPUT_PRICE_PER_MILLION = 0.30
OUTPUT_PRICE_PER_MILLION = 2.50

SCRIPT_DIR = Path(__file__).parent
IMAGE_FOLDER = SCRIPT_DIR / "cote_lists"
OUTPUT_FOLDER = SCRIPT_DIR / "ocr-results"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}

PROMPT = """Transcribe all of the text in this image exactly as it appears on the page.

Rules:
- Transcribe verbatim. Do NOT correct spelling, grammar, punctuation, or capitalization.
  Keep errors, abbreviations, and archaic spellings exactly as written.
- Do NOT summarize, paraphrase, translate, or add anything that is not on the page.
- Preserve the layout: keep the original line breaks, indentation, and blank lines.
- If the page has multiple columns of running text, transcribe the full left column
  from top to bottom, then the next column, and so on.
- If the page has a table or form, keep each row on its own line and use spaces
  to line the columns up the way they appear on the page.
- Include headers, footers, page numbers, marginal notes, stamps, and handwriting.
- If a word or character cannot be read, write [illegible] in its place.
  Do not guess.
- Output only the transcription: no introduction, no commentary, no markdown formatting."""

# ----------------------------------------------------------------------------


def find_images(folder):
    """Return a sorted list of image files in the folder."""
    return sorted(
        path for path in folder.iterdir()
        if path.suffix.lower() in IMAGE_EXTENSIONS
    )


def ocr_image(client, image_path):
    """Send one image to Gemini and return the response."""
    mime_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"
    image_part = types.Part.from_bytes(data=image_path.read_bytes(), mime_type=mime_type)

    return client.models.generate_content(
        model=MODEL,
        contents=[image_part, PROMPT],
    )


def calculate_cost(input_tokens, output_tokens):
    """Convert token counts into dollars."""
    input_cost = input_tokens / 1_000_000 * INPUT_PRICE_PER_MILLION
    output_cost = output_tokens / 1_000_000 * OUTPUT_PRICE_PER_MILLION
    return input_cost + output_cost


def main():
    load_dotenv(SCRIPT_DIR / ".env")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("No API key found. Copy .env.example to .env and add your GEMINI_API_KEY.")
        return

    client = genai.Client(api_key=api_key)
    OUTPUT_FOLDER.mkdir(exist_ok=True)

    images = find_images(IMAGE_FOLDER)
    if not images:
        print(f"No images found in {IMAGE_FOLDER}")
        return

    print(f"Model: {MODEL}")
    print(f"Found {len(images)} image(s) in {IMAGE_FOLDER.name}/\n")

    total_input = 0
    total_output = 0
    total_cost = 0.0

    for image_path in images:
        print(f"Transcribing {image_path.name} ...")
        response = ocr_image(client, image_path)

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


if __name__ == "__main__":
    main()
