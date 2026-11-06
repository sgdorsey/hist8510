#!/usr/bin/env python3
"""
Convert a PDF into one image file per page.

Uses Poppler's `pdftoppm` (install on macOS with: brew install poppler).

Examples:
    python3 pdf_to_images.py 11-Text-Reuse/sc_minutes_1904.pdf
    python3 pdf_to_images.py some.pdf -o pages --dpi 300 --format jpg
    python3 pdf_to_images.py some.pdf --first 2 --last 5
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def pdf_to_images(pdf_path: Path, out_dir: Path, dpi: int = 200,
                  fmt: str = "png", first: int | None = None,
                  last: int | None = None) -> list[Path]:
    """Render each page of pdf_path to its own image in out_dir.

    Returns the list of image paths that were created.
    """
    if shutil.which("pdftoppm") is None:
        sys.exit("Error: 'pdftoppm' not found. Install Poppler: brew install poppler")

    if not pdf_path.is_file():
        sys.exit(f"Error: PDF not found: {pdf_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = out_dir / f"{pdf_path.stem}_page"

    # Map our format names to pdftoppm's flags and the extensions it writes.
    flag, ext = {
        "png": ("-png", "png"),
        "jpg": ("-jpeg", "jpg"),
        "tiff": ("-tiff", "tif"),
    }[fmt]

    cmd = ["pdftoppm", flag, "-r", str(dpi)]
    if first is not None:
        cmd += ["-f", str(first)]
    if last is not None:
        cmd += ["-l", str(last)]
    cmd += [str(pdf_path), str(prefix)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"Error running pdftoppm:\n{result.stderr.strip()}")

    # pdftoppm writes files named <prefix>-<page>.<ext>, zero-padded as needed.
    return sorted(out_dir.glob(f"{pdf_path.stem}_page-*.{ext}"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Split a PDF into one image per page.")
    parser.add_argument("pdf", type=Path, help="Path to the PDF file")
    parser.add_argument("-o", "--out-dir", type=Path, default=None,
                        help="Output folder (default: <pdf name>_pages next to the PDF)")
    parser.add_argument("--dpi", type=int, default=200,
                        help="Resolution in dots per inch (default: 200)")
    parser.add_argument("--format", choices=["png", "jpg", "tiff"], default="png",
                        help="Image format (default: png)")
    parser.add_argument("--first", type=int, default=None, help="First page to convert (1-based)")
    parser.add_argument("--last", type=int, default=None, help="Last page to convert (1-based)")
    args = parser.parse_args()

    pdf_path = args.pdf.expanduser().resolve()
    out_dir = args.out_dir or pdf_path.parent / f"{pdf_path.stem}_pages"
    out_dir = out_dir.expanduser().resolve()

    images = pdf_to_images(pdf_path, out_dir, dpi=args.dpi, fmt=args.format,
                           first=args.first, last=args.last)

    print(f"Wrote {len(images)} page image(s) to {out_dir}")
    for img in images:
        print(f"  {img.name}")


if __name__ == "__main__":
    main()
