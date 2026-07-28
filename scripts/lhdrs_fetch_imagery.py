#!/usr/bin/env python3
"""Archive the complete County imagery catalog result and usable Ladera-era frames."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence/lhdrs/imagery"
RESEARCH = ROOT / "research/development_chronology"
BOUNDARY = ROOT / "data/development/ladera_ranch_cdp.geojson"
MANIFEST = RESEARCH / "imagery_source_manifest.csv"
REGISTRY = RESEARCH / "sources.csv"
SOURCE_ID = "LH-SRC-OC-IMAGERY"
SERVICE = "https://ocgis.com/arcpub/rest/services/Historic_Imagery/Historic_Imagery_v2/ImageServer"
FRAMES = {
    4: ("LH-IMG-1994-1995", "ladera_1994_1995.png", "Antonio Parkway 1995", 1994, 1995),
    33: (
        "LH-IMG-1997-1998",
        "ladera_1997_1998.png",
        "O'Neil Regional Park (June) 1998",
        1997,
        1998,
    ),
}


def request_bytes(url: str, params: dict[str, Any] | None = None) -> bytes:
    if params:
        url = f"{url}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": "LHDRS-Mission4/1.0"})
    for attempt in range(4):
        try:
            with urlopen(request, timeout=120) as response:
                return response.read()
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("unreachable")


def write_atomic(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        stream.write(value)
        temp_path = Path(stream.name)
    os.replace(temp_path, path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bbox() -> tuple[float, float, float, float]:
    data = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    points = []

    def walk(value):
        if (
            isinstance(value, list)
            and len(value) >= 2
            and isinstance(value[0], (int, float))
            and isinstance(value[1], (int, float))
        ):
            points.append((float(value[0]), float(value[1])))
        elif isinstance(value, list):
            for item in value:
                walk(item)

    for feature in data["features"]:
        walk(feature["geometry"]["coordinates"])
    return (
        min(item[0] for item in points) - 0.002,
        min(item[1] for item in points) - 0.002,
        max(item[0] for item in points) + 0.002,
        max(item[1] for item in points) + 0.002,
    )


def write_csv_atomic(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", newline="", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(stream.name)
    os.replace(temp_path, path)


def manifest_row(url: str, path: Path, frame_id: str, item_type: str) -> dict[str, object]:
    return {
        "sourceId": SOURCE_ID,
        "imageryId": frame_id,
        "itemType": item_type,
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
    for row in rows:
        if row["id"] != SOURCE_ID:
            continue
        row.update(
            {
                "localFilePath": str(MANIFEST.relative_to(ROOT)),
                "checksumSha256": sha256(MANIFEST),
                "archiveStatus": "retrieved_collection",
                "knownLimitations": (
                    "Service catalog dates distinguish Date_On_Map from DateCurrent; both usable "
                    "development-era frames have partial coverage and scan or flight-footprint gaps."
                ),
                "notes": (
                    "Catalog query and 1994/1995 plus 1997/1998 PNG32 exports are archived with alpha "
                    "transparency and measured coverage footprints."
                ),
            }
        )
        break
    write_csv_atomic(REGISTRY, rows, fields)


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    xmin, ymin, xmax, ymax = bbox()
    bounds = f"{xmin},{ymin},{xmax},{ymax}"
    rows = []

    service_path = EVIDENCE / "historic_imagery_v2_service.json"
    service_raw = request_bytes(SERVICE, {"f": "pjson"})
    write_atomic(service_path, (json.dumps(json.loads(service_raw), indent=2, sort_keys=True) + "\n").encode())
    rows.append(manifest_row(SERVICE, service_path, "", "service_metadata"))

    query_params = {
        "where": "1=1",
        "geometry": bounds,
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "*",
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "json",
    }
    catalog_path = EVIDENCE / "ladera_intersecting_imagery_catalog.json"
    catalog_raw = request_bytes(f"{SERVICE}/query", query_params)
    catalog = json.loads(catalog_raw)
    write_atomic(catalog_path, (json.dumps(catalog, indent=2, sort_keys=True) + "\n").encode())
    rows.append(manifest_row(f"{SERVICE}/query", catalog_path, "", "catalog_query"))

    export_url = f"{SERVICE}/exportImage"
    for object_id, (imagery_id, filename, name, date_on_map, date_current) in FRAMES.items():
        path = EVIDENCE / filename
        params = {
            "bbox": bounds,
            "bboxSR": "4326",
            "imageSR": "4326",
            "size": "1800,2400",
            "format": "png32",
            "transparent": "true",
            "interpolation": "RSP_BilinearInterpolation",
            "mosaicRule": json.dumps(
                {"mosaicMethod": "esriMosaicLockRaster", "lockRasterIds": [object_id]},
                separators=(",", ":"),
            ),
            "f": "image",
        }
        value = request_bytes(export_url, params)
        if not value.startswith(b"\x89PNG") or len(value) < 10_000:
            raise RuntimeError(f"Unexpected imagery response for OBJECTID {object_id}")
        write_atomic(path, value)
        rows.append(manifest_row(export_url, path, imagery_id, "png32_export"))
        metadata_path = EVIDENCE / filename.replace(".png", "_export.json")
        metadata = {
            "imageryId": imagery_id,
            "sourceId": SOURCE_ID,
            "sourceObjectId": object_id,
            "sourceName": name,
            "dateOnMap": date_on_map,
            "dateCurrent": date_current,
            "bbox4326": [xmin, ymin, xmax, ymax],
            "size": [1800, 2400],
            "parameters": params,
        }
        write_atomic(metadata_path, (json.dumps(metadata, indent=2, sort_keys=True) + "\n").encode())
        rows.append(manifest_row(export_url, metadata_path, imagery_id, "export_metadata"))

    rows.sort(key=lambda row: str(row["localFilePath"]))
    write_csv_atomic(MANIFEST, rows, list(rows[0]))
    update_registry()
    print(f"DONE  archived {len(rows)} imagery records; {len(catalog.get('features', []))} catalog intersections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
