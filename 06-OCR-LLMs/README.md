## Setup

### Step 1: Get an API key

Go to <https://aistudio.google.com/apikey>, sign in with a Google account, and create a key.

### Step 2: Put the key in a `.env` file

From inside the `06-OCR-LLMs` folder:

```bash
cp .env.example .env
```

Open `.env` and replace `your-api-key-here` with your key. The `.env` file is listed in
`.gitignore`, so it won't be committed. **Never paste your key directly into the script.**

### Step 3: Create a virtual environment and install packages

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Running it

Activate venv if not already running:
```bash
source venv/bin/activate
```

Run:
```bash
python gemini_ocr.py
```

Example output (your numbers will differ):

```
Transcribing IMG_0402.jpg ...
  Saved to ocr-results/IMG_0402.txt
  Input tokens:    1,290
  Output tokens:   812
  Thinking tokens: 0
  Cost:            $0.002417
```

To OCR your own documents, drop `.jpg`, `.png`, or `.webp` files into `images/` and run it again.


