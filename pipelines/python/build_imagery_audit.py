#!/usr/bin/env python3
"""Build imagery inventory, measured footprints, and annual coverage gaps."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import tempfile

import geopandas as gpd
import numpy as np
from PIL import Image
from rasterio.features import shapes
from rasterio.transform import from_bounds
from shapely.geometry import shape
from shapely.ops import unary_union


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research/development_chronology"
EVIDENCE = ROOT / "evidence/lhdrs/imagery"
FOOTPRINTS = ROOT / "data/processed/imagery_footprints"
OBSERVATIONS = ROOT / "data/gis/ladera_development/construction_observations"
DOCS = ROOT / "docs/lhdrs"
BOUNDARY = ROOT / "data/development/ladera_ranch_cdp.geojson"
SOURCE_ID = "LH-SRC-OC-IMAGERY"
FRAME_DATA = [
    {
        "id": "LH-IMG-1994-1995",
        "filename": "ladera_1994_1995.png",
        "name": "Antonio Parkway 1995",
        "date_earliest": "1994-01-01",
        "date_latest": "1995-12-31",
        "date_on_map": "1994",
        "date_current": "1995",
        "object_id": "4",
        "review": (
            "Partial eastern strip visually reviewed as a pre-development baseline; ranch roads and "
            "an existing compound are visible, but no Ladera development polygon is inferred."
        ),
    },
    {
        "id": "LH-IMG-1997-1998",
        "filename": "ladera_1997_1998.png",
        "name": "O'Neil Regional Park (June) 1998",
        "date_earliest": "1997-01-01",
        "date_latest": "1998-06-30",
        "date_on_map": "1997",
        "date_current": "1998",
        "object_id": "33",
        "review": (
            "Partial northern coverage visually reviewed. Broad undeveloped terrain is visible, but "
            "no active-construction polygon is digitized without a second adjacent-date image."
        ),
    },
]


def write_csv(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    path = BASE / name
    with tempfile.NamedTemporaryFile(
        mode="w", newline="", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(stream.name)
    os.replace(temp_path, path)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
        temp_path = Path(stream.name)
    os.replace(temp_path, path)


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        stream.write(value)
        temp_path = Path(stream.name)
    os.replace(temp_path, path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def footprint(frame: dict[str, str], boundary: gpd.GeoDataFrame) -> tuple[dict[str, object], float]:
    image_path = EVIDENCE / frame["filename"]
    metadata = json.loads((EVIDENCE / frame["filename"].replace(".png", "_export.json")).read_text())
    image = np.asarray(Image.open(image_path).convert("RGBA"))
    alpha = image[:, :, 3]
    valid = alpha > 0
    xmin, ymin, xmax, ymax = metadata["bbox4326"]
    transform = from_bounds(xmin, ymin, xmax, ymax, image.shape[1], image.shape[0])
    polygons = [shape(geometry) for geometry, value in shapes(valid.astype("uint8"), mask=valid, transform=transform) if value == 1]
    geometry = unary_union(polygons).buffer(0)
    feature = {
        "type": "Feature",
        "geometry": geometry.__geo_interface__,
        "properties": {
            "imageryId": frame["id"],
            "sourceId": SOURCE_ID,
            "dateEarliest": frame["date_earliest"],
            "dateLatest": frame["date_latest"],
            "geometryMethod": "polygonized_nonzero_alpha_mask",
            "originalCrs": "EPSG:4326",
            "spatialPrecision": "export_pixel_footprint",
            "limitations": "Footprint measures image data coverage, not interpretable construction coverage.",
        },
    }
    coverage = gpd.GeoSeries([geometry], crs=4326).to_crs(26946).iloc[0]
    cdp = boundary.to_crs(26946).geometry.union_all()
    pct = coverage.intersection(cdp).area / cdp.area * 100
    return feature, pct


def main() -> int:
    boundary = gpd.read_file(BOUNDARY)
    catalog = json.loads((EVIDENCE / "ladera_intersecting_imagery_catalog.json").read_text())
    catalog_count = len(catalog.get("features", []))
    inventory = []
    review_rows = []
    coverage_by_id = {}
    all_features = []
    for frame in FRAME_DATA:
        feature, coverage_pct = footprint(frame, boundary)
        coverage_by_id[frame["id"]] = coverage_pct
        all_features.append(feature)
        write_json(
            FOOTPRINTS / f"{frame['id'].lower()}.geojson",
            {"type": "FeatureCollection", "features": [feature]},
        )
        image_path = EVIDENCE / frame["filename"]
        inventory.append(
            {
                "id": frame["id"],
                "captureDateEarliest": frame["date_earliest"],
                "captureDateLatest": frame["date_latest"],
                "dateOnMap": frame["date_on_map"],
                "dateCurrent": frame["date_current"],
                "sourceName": frame["name"],
                "sourceObjectId": frame["object_id"],
                "sourceIds": SOURCE_ID,
                "flightOrProjectId": "",
                "imageNumber": "",
                "scale": "",
                "groundResolution": "export approximately 2.0-2.5 m per pixel; native not stated",
                "colorMode": "RGBA service export",
                "coverage": "partial",
                "coveragePctCurrentCdp": f"{coverage_pct:.2f}",
                "originalCrs": "EPSG:4326 service export",
                "georeferencingStatus": "County rectified",
                "controlPoints": "not applicable to County export",
                "transformationMethod": "ImageServer exportImage",
                "rmse": "not published",
                "processingHistory": "PNG32 export; alpha mask polygonized for coverage only",
                "checksumSha256": sha256(image_path),
                "localPath": str(image_path.relative_to(ROOT)),
                "rightsLimitations": "Official public County service; reuse terms not separately stated",
                "interpretiveLimitations": (
                    "Date interval reflects two County catalog fields; partial coverage and no "
                    "adjacent-date image prevent reliable active-construction interval digitization."
                ),
                "interpretationStatus": "reviewed_no_proximity_eligible_polygon",
                "confidence": "high",
                "notes": frame["review"],
            }
        )
        review_rows.append(
            {
                "interpretationId": f"LH-IMG-REVIEW-{frame['object_id']}",
                "imageryId": frame["id"],
                "reviewDate": "2026-07-26",
                "comparisonBeforeId": "",
                "comparisonAfterId": "",
                "observedState": "no_supported_active_construction_polygon_digitized",
                "interpretationMethod": "full-frame visual review with current CDP and tract overlay",
                "geometryId": "",
                "proximityEligible": "false",
                "sourceIds": SOURCE_ID,
                "confidence": "medium",
                "limitations": frame["review"],
                "reviewStatus": "reviewed",
            }
        )

    # Preserve the earlier predevelopment frames as context, with their original archival paths.
    predevelopment = [
        ("LH-IMG-1929", "1929-01-01", "South County Watersheds 1929", "research/historical_imagery/oc_aerials/1929.jpg", "2.6 ft per pixel", "full"),
        ("LH-IMG-1937", "1937-01-01", "Orange County 600 Scale 1938", "research/historical_imagery/oc_aerials/1937.jpg", "1.15 ft per pixel", "full"),
        ("LH-IMG-1946", "1946-01-01", "Orange County 1200 Scale 1947", "research/historical_imagery/oc_aerials/1946b.jpg", "4.3 ft per pixel", "partial"),
    ]
    for imagery_id, capture, name, local_path, resolution, coverage in predevelopment:
        path = ROOT / local_path
        inventory.append(
            {
                "id": imagery_id,
                "captureDateEarliest": capture,
                "captureDateLatest": capture,
                "dateOnMap": capture[:4],
                "dateCurrent": "",
                "sourceName": name,
                "sourceObjectId": "",
                "sourceIds": SOURCE_ID,
                "flightOrProjectId": "",
                "imageNumber": "",
                "scale": "",
                "groundResolution": resolution,
                "colorMode": "historic aerial scan",
                "coverage": coverage,
                "coveragePctCurrentCdp": "",
                "originalCrs": "",
                "georeferencingStatus": "County rectified",
                "controlPoints": "not available",
                "transformationMethod": "County service",
                "rmse": "not published",
                "processingHistory": "Existing first-edition archive",
                "checksumSha256": sha256(path) if path.exists() else "",
                "localPath": local_path,
                "rightsLimitations": "Official public County service; reuse terms not separately stated",
                "interpretiveLimitations": "Predevelopment context; outside Mission 4 construction interval.",
                "interpretationStatus": "reviewed_predevelopment_context",
                "confidence": "high" if coverage == "full" else "medium",
                "notes": "Preserved first-edition context.",
            }
        )
    inventory.sort(key=lambda row: (row["captureDateEarliest"], row["id"]))
    write_csv("imagery_inventory.csv", inventory, list(inventory[0]))
    write_csv("construction_interpretation_log.csv", review_rows, list(review_rows[0]))
    write_json(FOOTPRINTS / "imagery_footprints.geojson", {"type": "FeatureCollection", "features": all_features})
    write_json(
        OBSERVATIONS / "status.geojson",
        {
            "type": "FeatureCollection",
            "features": [],
            "status": "no_supported_active_construction_geometry",
            "notEvidenceOfAbsence": True,
            "sourceImageryIds": [frame["id"] for frame in FRAME_DATA],
            "limitations": (
                "Partial, nonadjacent imagery cannot establish dated active-construction polygons. "
                "An empty feature list means unsupported, not no construction."
            ),
        },
    )

    matrix = []
    for year in range(1997, 2011):
        ids = ["LH-IMG-1997-1998"] if year in {1997, 1998} else []
        matrix.append(
            {
                "year": year,
                "availableImageryIds": ";".join(ids),
                "coverageStatus": "partial_ambiguous_date" if ids else "not_located",
                "coveragePctCurrentCdp": f"{coverage_by_id['LH-IMG-1997-1998']:.2f}" if ids else "0.00",
                "interpretationEligibility": "coverage_context_only" if ids else "unavailable",
                "constructionPolygonStatus": "not_supported",
                "sourceIds": SOURCE_ID if ids else "",
                "publicSearchStatus": (
                    "County_catalog_exhausted_for_intersecting_development_era_frames"
                    if ids
                    else "County_catalog_no_intersecting_frame;USGS_EarthExplorer_account_required"
                ),
                "limitations": (
                    "The County service's 1997 Date_On_Map and 1998 DateCurrent fields do not support "
                    "two separate annual states."
                    if ids
                    else "No public, locally archived image supports an annual state; zero coverage is not evidence of no construction."
                ),
            }
        )
    write_csv("imagery_coverage_matrix.csv", matrix, list(matrix[0]))

    doc = f"""# Historical imagery audit

## Inventory result

The official County catalog query returned **{catalog_count} imagery items** whose footprints intersect the current Ladera Ranch CDP. Only two are development-era candidates: **Antonio Parkway 1995** (`Date_On_Map=1994`, `DateCurrent=1995`) and **O'Neil Regional Park (June) 1998** (`Date_On_Map=1997`, `DateCurrent=1998`). Both are archived as PNG32 exports with alpha transparency.

The measured nontransparent footprint covers **{coverage_by_id['LH-IMG-1994-1995']:.2f}%** of the current CDP for the 1994/1995 frame and **{coverage_by_id['LH-IMG-1997-1998']:.2f}%** for the 1997/1998 frame. These percentages describe pixel availability, not visual interpretability.

## Interpretation decision

Both frames were reviewed with current CDP and tract overlays. The 1994/1995 strip is useful as pre-development context. The 1997/1998 frame shows broad undeveloped terrain in its covered area. Neither has an adjacent-date public image adequate for defensibly separating active disturbance from completed work or ordinary ranch roads. No construction polygon was digitized. The empty construction-observation layer explicitly means **unsupported**, not **no construction**.

## Annual completeness

`imagery_coverage_matrix.csv` contains every year from 1997 through 2010. The single 1997/1998 frame is not duplicated into two annual observations. No County catalog frame intersects Ladera for 1999-2010. USGS confirms that individual historical NAIP download through EarthExplorer requires an account; the public USDA current NAIP service contains no study-period frame at this location. Those access limits remain manual follow-ups.

## Reproducibility

- `research/development_chronology/imagery_inventory.csv`
- `research/development_chronology/imagery_coverage_matrix.csv`
- `research/development_chronology/construction_interpretation_log.csv`
- `data/processed/imagery_footprints/imagery_footprints.geojson`
- `data/gis/ladera_development/construction_observations/status.geojson`
- `research/development_chronology/imagery_source_manifest.csv`
"""
    write_text(DOCS / "HISTORICAL_IMAGERY_AUDIT.md", doc)
    print(f"DONE  imagery: {len(inventory)} inventory rows, {len(matrix)} annual coverage rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
