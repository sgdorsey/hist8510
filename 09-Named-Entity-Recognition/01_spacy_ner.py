#!/usr/bin/env python3
"""
Demo 1: NER with spaCy's pretrained model
=========================================

spaCy comes with ready-made models trained on modern English text
(news, blogs, web pages). The model decides what counts as an entity
and which of its 18 fixed labels to use -- we don't get a say.

Run it, then look at output/01_spacy.html:
  - What did it get right?
  - What did it label in a way a historian wouldn't?
  - What did it miss entirely?

Output: output/01_spacy.csv and output/01_spacy.html
"""

import spacy

from common import load_source, save_results

# Larger models are slower but usually more accurate:
#   en_core_web_sm  (small, ~12 MB)    en_core_web_md  (medium)
#   en_core_web_lg  (large)            en_core_web_trf (transformer; needs PyTorch)
MODEL = "en_core_web_sm"


def main():
    text = load_source()

    nlp = spacy.load(MODEL)   # load the trained model
    doc = nlp(text)           # run the whole pipeline on our text

    # doc.ents holds every entity the model found
    entities = [
        {"text": ent.text, "label": ent.label_,
         "start": ent.start_char, "end": ent.end_char}
        for ent in doc.ents
    ]

    print(f"Model: {MODEL}")
    save_results("01_spacy", text, entities, f"spaCy ({MODEL})")

    # spaCy's labels are abbreviations -- spacy.explain() spells them out
    print("\nWhat the labels mean:")
    for label in sorted({e["label"] for e in entities}):
        print(f"  {label:10} {spacy.explain(label)}")


if __name__ == "__main__":
    main()
