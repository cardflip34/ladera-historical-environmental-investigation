#!/usr/bin/env python3
"""Archive official Mission 4 tract-map documents and imagery-catalog records."""

from __future__ import annotations

import csv
import datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research/development_chronology"
REGISTRY = RESEARCH / "sources.csv"
TRACTS = ROOT / "data/development/tract_maps.geojson"
EVIDENCE = ROOT / "evidence/lhdrs/tract_maps"
MANIFEST = RESEARCH / "tract_map_document_manifest.csv"
USER_AGENT = "LHDRS/2.0 public historical-development research"
LMS_DOWNLOAD = "https://webapps.ocgis.com/box/api/OCPW_Survey/download"
SOURCE_ID = "LH-SRC-OC-LMS-TRACT-PDFS"
MAX_WORKERS = 4


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_bytes_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        stream.write(content)
        temp_path = Path(stream.name)
    os.replace(temp_path, path)


def write_csv_atomic(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", newline="", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(stream.name)
    os.replace(temp_path, path)


def safe_name(value: str) -> str:
    return value.replace(" ", "_").replace("/", "_")


def request_pdf(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        content = response.read()
    if not content.startswith(b"%PDF"):
        raise ValueError(f"response is not a PDF ({len(content)} bytes)")
    return content


def fetch_one(item: dict[str, str]) -> dict[str, object]:
    target = ROOT / item["localFilePath"]
    if target.exists() and target.stat().st_size > 500 and target.read_bytes()[:4] == b"%PDF":
        return {
            **item,
            "bytes": target.stat().st_size,
            "checksumSha256": sha256(target),
            "archiveStatus": "local_copy_verified",
            "error": "",
        }
    error = ""
    for attempt in range(1, 4):
        try:
            content = request_pdf(item["url"])
            write_bytes_atomic(target, content)
            return {
                **item,
                "bytes": len(content),
                "checksumSha256": sha256(target),
                "archiveStatus": "retrieved",
                "error": "",
            }
        except (OSError, ValueError, urllib.error.URLError) as exc:
            error = f"attempt {attempt}: {exc}"
            time.sleep(attempt)
    return {
        **item,
        "bytes": "",
        "checksumSha256": "",
        "archiveStatus": "fetch_failed",
        "error": error,
    }


def tract_documents() -> list[dict[str, str]]:
    source = json.loads(TRACTS.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    for feature in source["features"]:
        props = feature["properties"]
        number = str(props["tractNumber"])
        book_page = str(props["bookPage"])
        filename = f"TR_{number}_{safe_name(book_page)}.pdf"
        url = LMS_DOWNLOAD + "?" + urllib.parse.urlencode({"file": book_page, "doctype": "TR"})
        rows.append(
            {
                "tractId": f"LH-TRACT-{number}",
                "tractNumber": number,
                "bookPage": book_page,
                "recordDate": str(props["recordDate"]),
                "sourceId": SOURCE_ID,
                "url": url,
                "localFilePath": str((EVIDENCE / filename).relative_to(ROOT)),
                "retrievalDate": dt.date.today().isoformat(),
            }
        )
    return sorted(rows, key=lambda row: int(row["tractNumber"]))


def update_registry(status: str) -> None:
    with REGISTRY.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames or []
        rows = list(reader)
    found = False
    for row in rows:
        if row["id"] != SOURCE_ID:
            continue
        found = True
        row["localFilePath"] = str(MANIFEST.relative_to(ROOT))
        row["checksumSha256"] = sha256(MANIFEST)
        row["archiveStatus"] = status
    if not found:
        raise RuntimeError(f"{SOURCE_ID} is absent from sources.csv")
    write_csv_atomic(REGISTRY, rows, fields)


def main() -> int:
    requested = tract_documents()
    completed: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(fetch_one, item): item for item in requested}
        for index, future in enumerate(as_completed(futures), start=1):
            row = future.result()
            completed.append(row)
            print(
                f"TRACT {index:03d}/{len(requested)} {row['tractNumber']}: "
                f"{row['archiveStatus']}"
            )

    completed.sort(key=lambda row: int(str(row["tractNumber"])))
    fields = list(requested[0]) + ["bytes", "checksumSha256", "archiveStatus", "error"]
    write_csv_atomic(MANIFEST, completed, fields)
    failures = sum(row["archiveStatus"] == "fetch_failed" for row in completed)
    update_registry("retrieved_collection" if failures == 0 else "partial_collection")
    total_bytes = sum(int(row["bytes"] or 0) for row in completed)
    print(
        f"DONE  {len(completed) - failures}/{len(completed)} tract PDFs; "
        f"{total_bytes:,} bytes; {failures} failed"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
