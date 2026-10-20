#!/usr/bin/env python3
"""
Demo 2: NER with GLiNER (you choose the labels)
===============================================

GLiNER is a small model (Zaratiana et al. 2023) that finds entities of
whatever types you name -- "steamboat", "newspaper", "railroad" -- without
any extra training. It runs on your own computer: free, and your text
never leaves your machine.

For each entity it also gives a confidence score from 0 to 1. Anything
below THRESHOLD is thrown away. Try raising or lowering it.

Setup (instructor demo -- this installs PyTorch, a large download):
    pip install -r requirements-gliner.txt
The first run also downloads the model (about 1.6 GB) -- do this before class.

Output: output/02_gliner.csv and output/02_gliner.html
"""

import warnings

warnings.filterwarnings("ignore")   # hide harmless warnings from PyTorch

from gliner import GLiNER

from common import load_source, save_results, split_into_chunks

MODEL = "urchade/gliner_medium-v2.1"

# The entity types to look for. Plain English -- change them to fit your source.
LABELS = ["person", "state", "county", "city or town", "organization", "facility"]

# How confident the model must be (0 to 1) to keep an entity
THRESHOLD = 0.5


def main():
    text = load_source()

    print(f"Loading {MODEL} ...")
    model = GLiNER.from_pretrained(MODEL)

    # GLiNER reads about 300 words at a time, so we give it one
    # paragraph at a time and shift each result back to its place in the text.
    entities = []
    for offset, chunk in split_into_chunks(text):
        for entity in model.predict_entities(chunk, LABELS, threshold=THRESHOLD):
            entities.append({
                "text": entity["text"],
                "label": entity["label"].upper(),
                "start": offset + entity["start"],
                "end": offset + entity["end"],
                "score": round(entity["score"], 2),
            })

    print(f"Labels: {', '.join(LABELS)}   Threshold: {THRESHOLD}")
    save_results("02_gliner", text, entities, f"GLiNER ({MODEL})")


if __name__ == "__main__":
    main()
