# Named Entity Recognition

Three ways to find the people, places, and organizations in a historical text, from least
to most control over what counts as an entity.

| Script | Method | Who decides the entity types? | Runs where? |
|---|---|---|---|
| `01_spacy_ner.py` | spaCy pretrained model | The model (18 fixed labels) | Your computer |
| `02_gliner_ner.py` | GLiNER | You (any labels you type) | Your computer |
| `03_gemini_ner.py` | Gemini + schema | You, with instructions and historical context | Google's servers |

All three read `data/source.txt`, print the entities they found, and save a CSV and a
highlighted HTML page to `output/`. The page opens in your browser automatically.

---

## Setup

From inside the `09-Named-Entity-Recognition` folder:

```bash
cp .env.example .env            # then paste your key into .env
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

**GLiNER (instructor demo only):** it needs PyTorch, a large install. The first run downloads
the model (about 1.6 GB).

```bash
pip install -r requirements-gliner.txt
```

---

## Running it

```bash
source venv/bin/activate
python 01_spacy_ner.py
python 02_gliner_ner.py
python 03_gemini_ner.py
```

---

## Using a different text

Replace `data/source.txt` with any plain-text file. Then update the parts written for the
current source:

- `LABELS` in `02_gliner_ner.py`
- `LABELS` and `CONTEXT` in `03_gemini_ner.py`

The current text is OCR'd pages (21–28) of a 1937 Works Progress Administration report on its
recreation program in Alabama and Arkansas.

---

## Before class

```bash
python reset_for_class.py
```

Clears `output/` so every demo runs fresh, then checks that the API key, packages, spaCy
model, GLiNER model, and backups are all in place. It doesn't call the API.

---

## Backups

`backup-output/` holds results from a run made before class. If the internet, the API, or a
package fails, open the HTML pages there instead.
