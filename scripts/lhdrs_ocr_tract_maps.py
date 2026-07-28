#!/usr/bin/env python3
"""Render and OCR the first sheet of each archived County tract map."""

from __future__ import annotations

import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/development_chronology/tract_map_document_manifest.csv"
RENDER_DIR = ROOT / "tmp/pdfs/mission4-title-sheets"
OCR_OUTPUT = ROOT / "evidence/lhdrs/tract_maps/title_sheet_ocr.txt"


def render(row: dict[str, str], renderer: str) -> tuple[str, str]:
    tract = row["tractNumber"]
    source = ROOT / row["localFilePath"]
    prefix = RENDER_DIR / f"TR_{tract}"
    target = prefix.with_suffix(".jpg")
    if target.exists() and target.stat().st_size > 10_000:
        return tract, "cached"
    subprocess.run(
        [
            renderer,
            "-f", "1", "-l", "1", "-singlefile", "-jpeg",
            "-jpegopt", "quality=88", "-r", "150", str(source), str(prefix),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    return tract, "rendered"


def main() -> int:
    renderer = shutil.which("pdftoppm")
    swift = shutil.which("swift")
    if not renderer or not swift:
        raise SystemExit("pdftoppm and swift are required")
    with MANIFEST.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or any(row["archiveStatus"] == "fetch_failed" for row in rows):
        raise SystemExit("Run scripts/lhdrs_mission4_fetch.py successfully first")

    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(render, row, renderer): row for row in rows}
        for index, future in enumerate(as_completed(futures), start=1):
            tract, status = future.result()
            print(f"RENDER {index:03d}/{len(rows)} {tract}: {status}")

    expected = {f"TR_{row['tractNumber']}.jpg" for row in rows}
    for path in RENDER_DIR.iterdir():
        if path.suffix.lower() in {".png", ".jpg", ".jpeg"} and path.name not in expected:
            path.unlink()

    OCR_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [swift, str(ROOT / "scripts/ocr_pdf_vision.swift"), str(RENDER_DIR), str(OCR_OUTPUT)],
        check=True,
    )
    print(f"OCR output: {OCR_OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
