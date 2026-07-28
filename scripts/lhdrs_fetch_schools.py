#!/usr/bin/env python3
"""Archive official DSA project pages for the three original Ladera campuses."""

from __future__ import annotations

import csv
import hashlib
import http.cookiejar
import os
from pathlib import Path
import tempfile
import time
from urllib.request import HTTPCookieProcessor, Request, build_opener


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence/lhdrs/schools/dsa"
RESEARCH = ROOT / "research/development_chronology"
MANIFEST = RESEARCH / "school_source_manifest.csv"
REGISTRY = RESEARCH / "sources.csv"
BASE = "https://www.apps2.dgs.ca.gov/DSA/Tracker"
SOURCE_ID = "LH-SRC-DGS-DSA-TRACKER"
PROJECTS = {
    "101335": "chaparral_original_campus",
    "102435": "ladera_shared_original_campus",
    "105541": "oso_grande_original_campus",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_atomic(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        stream.write(value)
        temp_path = Path(stream.name)
    os.replace(temp_path, path)


def fetch(opener, url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "LHDRS-Mission4/1.0"})
    for attempt in range(4):
        try:
            with opener.open(request, timeout=90) as response:
                return response.read()
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("unreachable")


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


def manifest_row(url: str, path: Path, project_id: str, page_type: str) -> dict[str, object]:
    return {
        "sourceId": SOURCE_ID,
        "dsaApplicationId": f"04-{project_id}",
        "pageType": page_type,
        "url": url,
        "localFilePath": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "checksumSha256": sha256(path),
        "archiveStatus": "retrieved",
        "retrievalDate": "2026-07-26",
        "error": "",
    }


def update_registry() -> None:
    with REGISTRY.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    row = {field: "" for field in fields}
    row.update(
        {
            "id": SOURCE_ID,
            "title": "DSA eTracker school construction project records",
            "publisher": "California Department of General Services, Division of the State Architect",
            "url": f"{BASE}/ProjectStatus.aspx",
            "publicationDate": "current",
            "retrievalDate": "2026-07-26",
            "sourceType": "official_school_construction_registry",
            "geographicCoverage": "California public schools; selected Ladera Ranch campuses",
            "timeCoverage": "1999-2006",
            "isOfficial": "true",
            "isPrimary": "true",
            "dataFormat": "HTML collection and CSV manifest",
            "reliabilityGrade": "A1",
            "localFilePath": str(MANIFEST.relative_to(ROOT)),
            "checksumSha256": sha256(MANIFEST),
            "archiveStatus": "retrieved_collection",
            "knownLimitations": (
                "Plan receipt, approval, field-review, closeout, and certification dates are distinct "
                "administrative milestones; none is automatically the exact physical construction start."
            ),
            "notes": (
                "Original-campus applications identified by project name, scope, address, and chronology; "
                "later alteration projects are not used as original construction."
            ),
        }
    )
    for index, prior in enumerate(rows):
        if prior["id"] == SOURCE_ID:
            rows[index] = row
            break
    else:
        rows.append(row)
    write_csv_atomic(REGISTRY, rows, fields)


def main() -> int:
    rows = []
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    for app_id, stem in PROJECTS.items():
        opener = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
        pages = [
            (
                "application_summary",
                f"{BASE}/ApplicationSummary.aspx?OriginId=04&AppId={app_id}",
                EVIDENCE / f"{stem}_04_{app_id}_application_summary.html",
            ),
            (
                "field_review_status",
                f"{BASE}/FieldReviewStatus.aspx",
                EVIDENCE / f"{stem}_04_{app_id}_field_review_status.html",
            ),
            (
                "project_certification",
                f"{BASE}/ProjectCloseout.aspx",
                EVIDENCE / f"{stem}_04_{app_id}_project_certification.html",
            ),
        ]
        for page_type, url, path in pages:
            value = fetch(opener, url)
            if app_id.encode() not in value:
                raise RuntimeError(f"DSA session lost while retrieving {page_type} for {app_id}")
            write_atomic(path, value)
            rows.append(manifest_row(url, path, app_id, page_type))
    rows.sort(key=lambda row: str(row["localFilePath"]))
    write_csv_atomic(MANIFEST, rows, list(rows[0]))
    update_registry()
    print(f"DONE  archived {len(rows)} DSA pages for {len(PROJECTS)} original-campus projects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
