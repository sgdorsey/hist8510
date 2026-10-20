#!/usr/bin/env python3
"""
Reset for class
===============

Run this before class (or between practice runs) to:
  1. clear output/ so every demo is generated fresh, live
  2. check that everything the live demos need is ready

It never touches data/, backup-output/, or .env. It doesn't call the
Gemini API, so it's free to run as often as you like.

    python reset_for_class.py
"""

import importlib.util
import os
import re
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
OUTPUT_FOLDER = SCRIPT_DIR / "output"
BACKUP_FOLDER = SCRIPT_DIR / "backup-output"
SOURCE_FILE = SCRIPT_DIR / "data" / "source.txt"
ENV_FILE = SCRIPT_DIR / ".env"

problems = 0


def check(description, ok, fix=""):
    """Print one line of the checklist."""
    global problems
    print(f"  [{'OK' if ok else '!!'}] {description}")
    if not ok:
        problems += 1
        if fix:
            print(f"        fix: {fix}")


def clear_outputs():
    print("Clearing old results")
    removed = 0
    if OUTPUT_FOLDER.exists():
        removed = sum(1 for path in OUTPUT_FOLDER.iterdir() if path.is_file())
        shutil.rmtree(OUTPUT_FOLDER)
    shutil.rmtree(SCRIPT_DIR / "__pycache__", ignore_errors=True)
    print(f"  removed {removed} file(s) from output/\n")


def check_ready():
    print("Checking the demos are ready")

    # The source text
    if SOURCE_FILE.exists():
        words = len(SOURCE_FILE.read_text(encoding="utf-8").split())
        check(f"data/source.txt ({words:,} words)", words > 0, "the file is empty")
    else:
        check("data/source.txt", False, "add the text to analyze")

    # The API key (for 03_gemini_ner.py) -- checked, never printed
    key = ""
    if ENV_FILE.exists():
        match = re.search(r"^GEMINI_API_KEY=(.*)$", ENV_FILE.read_text(), re.MULTILINE)
        key = match.group(1).strip() if match else ""
    check("Gemini API key in .env", key not in ("", "your-api-key-here"),
          "cp .env.example .env, then paste in your key")

    # Packages for scripts 01 and 03
    for module, package in [("spacy", "spacy"), ("google.genai", "google-genai"),
                            ("dotenv", "python-dotenv")]:
        check(f"{package} installed", importlib.util.find_spec(module) is not None,
              "pip install -r requirements.txt")

    # spaCy's trained model (01_spacy_ner.py)
    if importlib.util.find_spec("spacy"):
        import spacy
        check("spaCy model en_core_web_sm", spacy.util.is_package("en_core_web_sm"),
              "python -m spacy download en_core_web_sm")

    # GLiNER and its model (02_gliner_ner.py)
    check("gliner installed", importlib.util.find_spec("gliner") is not None,
          "pip install -r requirements-gliner.txt")
    gliner_script = (SCRIPT_DIR / "02_gliner_ner.py").read_text(encoding="utf-8")
    model = re.search(r'^MODEL = "(.+)"', gliner_script, re.MULTILINE).group(1)
    hf_home = Path(os.getenv("HF_HOME", Path.home() / ".cache" / "huggingface"))
    model_folder = hf_home / "hub" / f"models--{model.replace('/', '--')}"
    check(f"GLiNER model downloaded ({model})", model_folder.exists(),
          "run python 02_gliner_ner.py once at home (about 1.6 GB)")

    # Backups in case something fails live
    backups = sorted(path.name for path in BACKUP_FOLDER.glob("*.html"))
    check(f"backup pages ({len(backups)} of 3)", len(backups) == 3,
          "run all three scripts, then copy output/ into backup-output/")


def main():
    clear_outputs()
    check_ready()
    print()
    if problems:
        print(f"{problems} thing(s) to fix before class.")
    else:
        print("Ready for class. Run the demos in order: 01, 02, 03.")


if __name__ == "__main__":
    main()
