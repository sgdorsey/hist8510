#!/usr/bin/env python3
"""Extract archive(s) and merge all .txt files inside them into one text file.

Accepts either a single archive file or a directory containing multiple
archives. Supported archive types: .zip, .tar.bz2/.tbz2, .tar.gz/.tgz, .tar.

Usage:
    python zip_txt_merge.py <archive_or_dir> [output_txt_path]

If output_txt_path is omitted, the merged file is written next to the
input as "<name>_merged.txt".
"""

import sys
import tarfile
import zipfile
from pathlib import Path

ARCHIVE_SUFFIXES = (".zip", ".tar.bz2", ".tbz2", ".tar.gz", ".tgz", ".tar")


def _archive_suffix(path: Path) -> str | None:
    name = path.name.lower()
    for suffix in ARCHIVE_SUFFIXES:
        if name.endswith(suffix):
            return suffix
    return None


def _extract_archive(archive_path: Path, dest_dir: Path) -> None:
    suffix = _archive_suffix(archive_path)
    dest_dir.mkdir(parents=True, exist_ok=True)

    if suffix == ".zip":
        with zipfile.ZipFile(archive_path) as zf:
            zf.extractall(dest_dir)
    elif suffix in (".tar.bz2", ".tbz2", ".tar.gz", ".tgz", ".tar"):
        with tarfile.open(archive_path) as tf:
            tf.extractall(dest_dir, filter="data")
    else:
        raise ValueError(f"Unsupported archive type: {archive_path}")


def merge_txt_files(input_path: str, output_path: str | None = None) -> Path:
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Path not found: {input_path}")

    if input_path.is_dir() and _archive_suffix(input_path) is None:
        archives = sorted(
            p for p in input_path.iterdir() if p.is_file() and _archive_suffix(p)
        )
        if not archives:
            raise FileNotFoundError(f"No supported archives found in: {input_path}")
        base_name = input_path.name
        extract_root = input_path.parent / f"{base_name}_extracted"
    else:
        if _archive_suffix(input_path) is None:
            raise ValueError(f"Unsupported or unrecognized archive: {input_path}")
        archives = [input_path]
        base_name = input_path.name
        for suffix in ARCHIVE_SUFFIXES:
            if base_name.lower().endswith(suffix):
                base_name = base_name[: -len(suffix)]
                break
        extract_root = input_path.parent / f"{base_name}_extracted"

    for archive in archives:
        archive_base = archive.name
        for suffix in ARCHIVE_SUFFIXES:
            if archive_base.lower().endswith(suffix):
                archive_base = archive_base[: -len(suffix)]
                break
        _extract_archive(archive, extract_root / archive_base)

    txt_files = sorted(extract_root.rglob("*.txt"))

    out_path = Path(output_path) if output_path else input_path.parent / f"{base_name}_merged.txt"

    with out_path.open("w", encoding="utf-8") as out_file:
        for txt_file in txt_files:
            out_file.write(f"----- {txt_file.relative_to(extract_root)} -----\n")
            out_file.write(txt_file.read_text(encoding="utf-8", errors="replace"))
            out_file.write("\n\n")

    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python zip_txt_merge.py <archive_or_dir> [output_txt_path]")
        sys.exit(1)

    input_arg = sys.argv[1]
    output_arg = sys.argv[2] if len(sys.argv) > 2 else None

    result_path = merge_txt_files(input_arg, output_arg)
    print(f"Merged text written to: {result_path}")
