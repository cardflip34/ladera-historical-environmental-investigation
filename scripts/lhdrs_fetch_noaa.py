#!/usr/bin/env python3
"""Archive NOAA station metadata and selected Global Hourly wind files."""

from __future__ import annotations

import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import os
from pathlib import Path
import tempfile
import time
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research/development_chronology"
REGISTRY = RESEARCH / "sources.csv"
EVIDENCE = ROOT / "evidence/lhdrs/noaa"
MANIFEST = RESEARCH / "wind_source_manifest.csv"
USER_AGENT = "LHDRS/2.0 public historical-development research"
HISTORY_URL = "https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv"
FORMAT_URL = "https://www.ncei.noaa.gov/data/global-hourly/doc/isd-format-document.pdf"
ACCESS = "https://www.ncei.noaa.gov/data/global-hourly/access"
FILES = {
    **{year: "72297793184" for year in range(1997, 2011)},
}
JOHN_WAYNE_ALTERNATE_FILES = {year: "72297799999" for year in range(2000, 2004)}
EL_TORO_FILES = {1997: "69014093101", 1999: "99999993101", 2000: "99999993101"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        stream.write(content)
        temp_path = Path(stream.name)
    os.replace(temp_path, path)


def download(url: str, path: Path) -> tuple[int, str]:
    if path.exists() and path.stat().st_size > 500:
        return path.stat().st_size, "local_copy_verified"
    last_error = ""
    for attempt in range(1, 4):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=180) as response:
                content = response.read()
            if len(content) < 500:
                raise ValueError(f"response unexpectedly short ({len(content)} bytes)")
            write_atomic(path, content)
            return len(content), "retrieved"
        except (OSError, ValueError, urllib.error.URLError) as exc:
            last_error = str(exc)
            time.sleep(attempt)
    raise RuntimeError(last_error)


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


def update_registry(source_id: str, local_path: Path, status: str, checksum: str | None = None) -> None:
    with REGISTRY.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames or []
        rows = list(reader)
    for row in rows:
        if row["id"] == source_id:
            row["localFilePath"] = str(local_path.relative_to(ROOT))
            row["checksumSha256"] = checksum or sha256(local_path)
            row["archiveStatus"] = status
            break
    else:
        raise RuntimeError(f"{source_id} is absent from sources.csv")
    write_csv_atomic(REGISTRY, rows, fields)


def main() -> int:
    prior = {}
    if MANIFEST.exists():
        with MANIFEST.open(newline="", encoding="utf-8") as stream:
            prior = {row["localFilePath"]: row for row in csv.DictReader(stream)}
    fixed = [
        ("LH-SRC-NOAA-ISD-HISTORY", HISTORY_URL, EVIDENCE / "isd-history.csv"),
        ("LH-SRC-NOAA-ISD-HISTORY", FORMAT_URL, EVIDENCE / "isd-format-document.pdf"),
    ]
    hourly = [
        (
            "LH-SRC-NOAA-GLOBAL-HOURLY",
            f"{ACCESS}/{year}/{station}.csv",
            EVIDENCE / "global_hourly" / str(year) / f"{station}.csv",
        )
        for year, station in sorted(FILES.items())
    ] + [
        (
            "LH-SRC-NOAA-GLOBAL-HOURLY",
            f"{ACCESS}/{year}/{station}.csv",
            EVIDENCE / "global_hourly" / str(year) / f"{station}.csv",
        )
        for year, station in sorted(JOHN_WAYNE_ALTERNATE_FILES.items())
    ] + [
        (
            "LH-SRC-NOAA-GLOBAL-HOURLY",
            f"{ACCESS}/{year}/{station}.csv",
            EVIDENCE / "global_hourly" / str(year) / f"{station}.csv",
        )
        for year, station in sorted(EL_TORO_FILES.items())
    ]
    requested = fixed + hourly
    rows: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(download, url, path): (source_id, url, path) for source_id, url, path in requested}
        for index, future in enumerate(as_completed(futures), start=1):
            source_id, url, path = futures[future]
            try:
                size, status = future.result()
                error = ""
            except RuntimeError as exc:
                size, status, error = 0, "fetch_failed", str(exc)
            relative_path = str(path.relative_to(ROOT))
            prior_row = prior.get(relative_path)
            if (
                prior_row
                and status == "local_copy_verified"
                and prior_row.get("bytes") == str(size)
                and prior_row.get("checksumSha256")
            ):
                checksum = prior_row["checksumSha256"]
            else:
                checksum = sha256(path) if path.exists() else ""
            rows.append(
                {
                    "sourceId": source_id,
                    "url": url,
                    "localFilePath": relative_path,
                    "bytes": size or "",
                    "checksumSha256": checksum,
                    "archiveStatus": status,
                    "error": error,
                }
            )
            print(f"NOAA {index:02d}/{len(requested)} {path.name}: {status}")
    rows.sort(key=lambda row: str(row["localFilePath"]))
    write_csv_atomic(MANIFEST, rows, list(rows[0]))
    failures = sum(row["archiveStatus"] == "fetch_failed" for row in rows)
    update_registry(
        "LH-SRC-NOAA-ISD-HISTORY",
        EVIDENCE / "isd-history.csv",
        "retrieved" if not failures else "partial_collection",
        next(
            row["checksumSha256"]
            for row in rows
            if row["localFilePath"] == "evidence/lhdrs/noaa/isd-history.csv"
        ),
    )
    update_registry(
        "LH-SRC-NOAA-GLOBAL-HOURLY",
        MANIFEST,
        "retrieved_collection" if not failures else "partial_collection",
    )
    print(f"DONE  {len(rows) - failures}/{len(rows)} NOAA files; {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
