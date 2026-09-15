# OCR with Tesseract

Turning scanned historical documents into searchable text. The demos walk through the
full pipeline: convert PDFs to images, clean the images up, then run OCR.

Good OCR is mostly about **preprocessing**. A clean, high-contrast, properly thresholded
image will out-perform a fancier OCR engine fed a noisy scan, so the preprocessing demos
matter as much as the OCR step.

---

## What you need

Two separate things have to be installed, and they install in different ways:

| | What it is | Installed by |
|---|---|---|
| **Python packages** | `opencv-python`, `pytesseract`, `pdf2image`, etc. | `pip` (handled by the setup script) |
| **System programs** | Tesseract (the OCR engine) and Poppler (reads PDFs) | Homebrew / apt / an installer |

`pytesseract` is only a thin wrapper — it shells out to the real `tesseract` program.
Likewise `pdf2image` calls Poppler's `pdftoppm`. **pip cannot install either one.**
This is the single most common reason setup fails.

---

## Setup

### Step 1 — Install the system programs

**macOS** (needs [Homebrew](https://brew.sh)):

```bash
brew install tesseract poppler
```

**Linux:**

```bash
sudo apt-get install tesseract-ocr poppler-utils
```

**Windows:**
- Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Poppler: https://github.com/oschwartz10612/poppler-windows/releases

Check that it worked:

```bash
tesseract --version
```

### Step 2 — Create the virtual environment

From inside the `05-OCR-Tesseract` folder:

```bash
python3 setup_venv.py
```

This creates a folder called `ocr_env`, installs every Python package into it, and
tests the result. It takes a couple of minutes.

> **Use `python3`, not `python`.** macOS ships no command named plain `python`; typing
> `python` gives you `command not found`.

### Step 3 — Activate the environment

**Every time you sit down to work**, activate it first:

```bash
source ocr_env/bin/activate
```

On Windows: `ocr_env\Scripts\activate`

Your prompt will change to show `(ocr_env)`. That is how you know it is on. Once
activated, plain `python` *does* work, because the environment provides it.

When you are finished:

```bash
deactivate
```

---

## Running the demos

Activate the environment first, then run these in order:

```bash
python pdf_to_images_demo.py
```
Converts the PDF in `pdf/` into page images in `processed-imgs/`. Has a `--quality`
option (`high`/`medium`/`low`) trading file size against detail.

```bash
python 01_noise_reduction_demo.py
```
Removes speckle and scan artifacts — Gaussian, median, and bilateral filtering compared
side by side. Bilateral is usually the one to reach for, since it smooths noise while
keeping letter edges sharp.

```bash
python 02_contrast_enhancement_demo.py
```
Makes faded text legible: histogram equalization, CLAHE, gamma correction.

```bash
python 03_thresholding_demo.py
```
Converts to pure black-and-white. Usually the highest-payoff step. Compares global,
Otsu, and adaptive thresholding — **adaptive** typically wins on historical documents
with uneven lighting or page shadows.

```bash
python ocr_demo.py
```
Runs Tesseract over the images and writes text files to `ocr-results/`. Run
`python ocr_demo.py --check-deps` to verify your setup without doing any OCR.

### Starting over

```bash
python cleanup.py
```
Deletes generated output (`processed-imgs/`, `ocr-results/`). Your originals in
`images/` and `pdf/` are untouched. Add `--dry-run` to preview first.

---

## The files

| File | Purpose |
|---|---|
| `setup_venv.py` | One-time environment setup |
| `pdf_to_images_demo.py` | PDF → page images |
| `01_noise_reduction_demo.py` | Denoising techniques |
| `02_contrast_enhancement_demo.py` | Contrast techniques |
| `03_thresholding_demo.py` | Binarization techniques |
| `ocr_demo.py` | Runs Tesseract (PSM 3) |
| `cleanup.py` | Deletes generated output |
| `fix_dependencies.py` | Troubleshooting helper |
| `requirements.txt` | Python package list |
| `images/`, `pdf/` | Source documents |

---

## Troubleshooting

**`/bin/sh: python: command not found`**

Use `python3` instead of `python`, or activate the virtual environment first
(`source ocr_env/bin/activate`), after which plain `python` works.

**`TesseractNotFoundError`, or "Tesseract OCR not found"**

The Python wrapper is installed but the engine is not. Run `brew install tesseract`
(Step 1 above), then confirm with `tesseract --version`.

**`Unable to get page count. Is poppler installed?`**

Same situation for PDFs. Run `brew install poppler`, then confirm with
`pdftoppm -v`.

**`Could not find a version that satisfies the requirement ...`**

A pinned version does not exist or has no build for your Python. Don't pin old
versions on a new Python — on 3.13+ there are no prebuilt wheels for `numpy` 1.x or
`pandas` 2.x, so pip tries to compile them from source and fails. Let pip choose:
`pip install --upgrade numpy pandas`.

**`ModuleNotFoundError: No module named 'cv2'`**

The environment is not active. Look for `(ocr_env)` in your prompt; if it is missing,
run `source ocr_env/bin/activate`.

**OCR output is garbage**

That is a preprocessing problem, not an OCR problem. Go back to
`03_thresholding_demo.py` and try adaptive thresholding, then re-run the OCR on the
cleaned image rather than the original scan.

---

## Note on `ocr_env`

The virtual environment folder is roughly 300 MB and is excluded from git. Never commit
it — anyone can rebuild it in two minutes with `python3 setup_venv.py`.

If you keep this folder in Dropbox, consider marking `ocr_env` "don't sync" (right-click →
Make online-only) so Dropbox isn't continually syncing thousands of library files.
