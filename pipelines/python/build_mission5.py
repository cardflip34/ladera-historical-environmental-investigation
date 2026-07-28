#!/usr/bin/env python3
"""Build Mission 5 evidence, chronology, and tract crosswalk artifacts."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
from html.parser import HTMLParser
from io import StringIO
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

import pandas as pd
import pdfplumber


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research/development_chronology"
EVIDENCE = ROOT / "evidence/lhdrs/mission5"
DATA = ROOT / "data/development"
PUBLIC = ROOT / "apps/web/public/development"
RETRIEVAL_DATE = "2026-07-27"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or sorted({key for row in rows for key in row})
    with tempfile.NamedTemporaryFile(
        mode="w", newline="", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    os.replace(temporary, path)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
        temporary = Path(stream.name)
    os.replace(temporary, path)


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        stream.write(value)
        temporary = Path(stream.name)
    os.replace(temporary, path)


def upsert(path: Path, new_rows: list[dict[str, object]], key: str) -> list[dict[str, object]]:
    existing: list[dict[str, object]] = read_csv(path) if path.exists() else []
    values = {str(row[key]): row for row in existing}
    for row in new_rows:
        values[str(row[key])] = row
    rows = list(values.values())
    fields = list(existing[0]) if existing else []
    for row in new_rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    write_csv(path, rows, fields)
    return rows


def split_ids(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"[;,]", value or "") if item.strip()]


def slug(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", value.upper()).strip("-")


def normalize_street(value: str) -> str:
    value = re.sub(r"\([^)]*\)", "", value.upper()).replace("’", "'")
    replacements = {
        "AVENUE": "AVE", "BOULEVARD": "BLVD", "CIRCLE": "CIR", "COURT": "CT",
        "DRIVE": "DR", "LANE": "LN", "PARKWAY": "PKWY", "PLACE": "PL",
        "ROAD": "RD", "STREET": "ST", "TRAIL": "TRL", "HEIGHTS": "HTS",
    }
    words = [replacements.get(word, word) for word in re.sub(r"[^A-Z0-9 ]", " ", value).split()]
    return " ".join(words)


def address_constraint(value: str) -> str:
    match = re.search(r"\(([^)]*)\)", value)
    return match.group(1).strip() if match else ""


def address_matches(number: int, constraint: str) -> bool:
    if not constraint:
        return True
    parity_default = "odd" if re.search(r"\bodd\b", constraint, re.I) else (
        "even" if re.search(r"\beven\b", constraint, re.I) else ""
    )
    for part in constraint.split(","):
        part = part.strip()
        parity = "odd" if re.search(r"\bodd\b", part, re.I) else (
            "even" if re.search(r"\beven\b", part, re.I) else parity_default
        )
        values = [int(value) for value in re.findall(r"\d+", part)]
        if len(values) >= 2:
            matched = values[0] <= number <= values[1]
        elif values:
            matched = number == values[0]
        else:
            continue
        if matched and parity == "odd" and number % 2 == 0:
            matched = False
        if matched and parity == "even" and number % 2 != 0:
            matched = False
        if matched:
            return True
    return False


def ring_covers_point(ring: list[list[float]], x: float, y: float) -> bool:
    """Return true for points inside or on the boundary of a GeoJSON linear ring."""
    inside = False
    for index, first in enumerate(ring):
        second = ring[(index + 1) % len(ring)]
        x1, y1 = float(first[0]), float(first[1])
        x2, y2 = float(second[0]), float(second[1])
        cross = (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
        if abs(cross) < 1e-12 and min(x1, x2) - 1e-12 <= x <= max(x1, x2) + 1e-12 \
                and min(y1, y2) - 1e-12 <= y <= max(y1, y2) + 1e-12:
            return True
        if (y1 > y) != (y2 > y):
            intersect_x = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < intersect_x:
                inside = not inside
    return inside


def polygon_covers_point(rings: list[list[list[float]]], x: float, y: float) -> bool:
    if not rings or not ring_covers_point(rings[0], x, y):
        return False
    return not any(ring_covers_point(hole, x, y) for hole in rings[1:])


def geometry_parts(geometry: dict[str, object]) -> list[list[list[list[float]]]]:
    coordinates = geometry["coordinates"]
    if geometry["type"] == "Polygon":
        return [coordinates]  # type: ignore[list-item]
    if geometry["type"] == "MultiPolygon":
        return coordinates  # type: ignore[return-value]
    raise ValueError(f"Unsupported tract geometry: {geometry['type']}")


def geometry_metrics(geometry: dict[str, object]) -> tuple[tuple[float, float, float, float], float]:
    points = [point for polygon in geometry_parts(geometry) for ring in polygon for point in ring]
    xs = [float(point[0]) for point in points]
    ys = [float(point[1]) for point in points]
    area = 0.0
    for polygon in geometry_parts(geometry):
        for ring_number, ring in enumerate(polygon):
            ring_area = abs(sum(
                float(first[0]) * float(second[1]) - float(second[0]) * float(first[1])
                for first, second in zip(ring, ring[1:] + ring[:1])
            )) / 2
            area += ring_area if ring_number == 0 else -ring_area
    return (min(xs), min(ys), max(xs), max(ys)), area


def geometry_covers_point(geometry: dict[str, object], x: float, y: float) -> bool:
    return any(polygon_covers_point(polygon, x, y) for polygon in geometry_parts(geometry))


class VillageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_h2 = False
        self.in_li = False
        self.h2_text: list[str] = []
        self.li_text: list[str] = []
        self.section = ""
        self.neighborhoods: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "h2":
            self.in_h2 = True
            self.h2_text = []
        elif tag == "li":
            self.in_li = True
            self.li_text = []

    def handle_data(self, data: str) -> None:
        if self.in_h2:
            self.h2_text.append(data)
        if self.in_li:
            self.li_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "h2" and self.in_h2:
            self.section = " ".join("".join(self.h2_text).split()).lower()
            self.in_h2 = False
        elif tag == "li" and self.in_li:
            value = " ".join("".join(self.li_text).split())
            if self.section == "neighborhoods" and value:
                self.neighborhoods.append(value)
            self.in_li = False


class TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.hidden_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style", "noscript"}:
            self.hidden_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.hidden_depth and data.strip():
            self.parts.append(" ".join(data.split()))


def source_registry() -> int:
    manifest = read_csv(EVIDENCE / "acquisition_manifest.csv")
    limitations = {
        "official_current_gis_layer": (
            "Current address and street geometry supports a present-day geographic crosswalk only; "
            "it does not date construction, sale, habitability, or occupancy."
        ),
        "official_aerial_imagery": (
            "Flight-date filenames and pixels support visible-state observations; imagery alone does "
            "not establish permits, legal completion, certificates of occupancy, or individual exposure."
        ),
        "official_bond_monitoring_report": (
            "CFD boundaries and product tables do not cover every Ladera tract; aggregate absorption is "
            "used only under the report's explicit built-and-occupied definition."
        ),
        "secondary_real_estate_directory": (
            "Secondary 2010 builder directory conflicts with the County report for several Phase VI products; "
            "the official County report controls those builder assignments."
        ),
        "contemporary_newspaper": (
            "Contemporary reporting is retained as reported evidence; it is not a permit or occupancy ledger."
        ),
    }
    rows = []
    for item in manifest:
        if item["archiveStatus"] != "retrieved":
            continue
        rows.append(
            {
                "id": item["sourceId"],
                "title": item["title"],
                "publisher": item["publisher"],
                "author": "",
                "url": item["url"],
                "archiveUrl": "",
                "publicationDate": item["publicationDate"],
                "retrievalDate": item["retrievalDate"],
                "sourceType": item["sourceType"],
                "geographicCoverage": "Ladera Ranch and relevant Orange County context",
                "timeCoverage": item["publicationDate"],
                "isOfficial": item["isOfficial"],
                "isPrimary": item["isPrimary"],
                "dataFormat": Path(item["localFilePath"]).suffix.lstrip(".").upper() or "JSON",
                "reliabilityGrade": item["reliabilityGrade"],
                "localFilePath": item["localFilePath"],
                "checksumSha256": item["checksumSha256"],
                "archiveStatus": item["archiveStatus"],
                "knownLimitations": limitations.get(item["sourceType"], "Use only for the claim scope documented in Mission 5."),
                "notes": "Mission 5 acquisition manifest retains byte count, URL, retrieval date, and checksum.",
            }
        )
    upsert(BASE / "sources.csv", rows, "id")
    return len(rows)


def parse_street_directory() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    path = EVIDENCE / "pdf/laderalife_street_neighborhood_list_2019.pdf"
    with pdfplumber.open(path) as pdf:
        record_number = 0
        for page_number, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            if not tables:
                continue
            for row in tables[0][1:]:
                if len(row) < 4 or not row[0] or not row[1] or not row[3]:
                    continue
                record_number += 1
                street_label = " ".join(row[0].split())
                rows.append(
                    {
                        "streetNeighborhoodId": f"LH-STREET-XWALK-{record_number:04d}",
                        "streetLabel": street_label,
                        "streetNameNormalized": normalize_street(street_label),
                        "addressConstraint": address_constraint(street_label),
                        "neighborhood": " ".join(row[1].split()),
                        "association": " ".join((row[2] or "").split()),
                        "village": " ".join(row[3].split()),
                        "sourceIds": "LH-SRC-LARMAC-STREETS-2019",
                        "sourceLocator": f"PDF page {page_number}",
                        "statementClass": "documented_exact",
                        "confidence": "high",
                        "limitations": "Directory reflects 2019 naming and does not establish the historical opening date.",
                    }
                )
    write_csv(BASE / "street_neighborhood_registry.csv", rows)
    return rows


def parse_village_directory() -> list[dict[str, object]]:
    village_files = sorted((EVIDENCE / "html").glob("laderalife_village_*.html"))
    rows: list[dict[str, object]] = []
    for path in village_files:
        match = re.match(r"laderalife_village_(\d+)_(.+)\.html", path.name)
        if not match:
            continue
        parser = VillageParser()
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))
        order = int(match.group(1))
        village = match.group(2).replace("-village", "").replace("-district", "").replace("-", " ").title()
        for value in parser.neighborhoods:
            phase_match = re.search(r"\s+-\s+(\d+)$", value)
            official_code = phase_match.group(1) if phase_match else ""
            name = re.sub(r"\s+-\s+\d+$", "", value).strip()
            rows.append(
                {
                    "neighborhoodPhaseId": f"LH-NPH-{order:02d}-{slug(name)}",
                    "neighborhoodName": name,
                    "village": village,
                    "officialVillageCode": official_code,
                    "openingDateEarliest": "",
                    "openingDateLatest": "",
                    "openingDateStatus": "not_located",
                    "sourceIds": f"LH-SRC-LARMAC-VILLAGE-{order}",
                    "statementClass": "documented_exact",
                    "confidence": "high",
                    "limitations": (
                        "Official current membership directory establishes name and village association only; "
                        "the trailing number is retained as the site's village code, not asserted as an opening phase."
                    ),
                }
            )
    write_csv(BASE / "neighborhood_phase_directory.csv", rows)
    return rows


def base_product(name: str) -> str:
    value = re.sub(r"\s*\([^)]*\)", "", name)
    aliases = {
        "EVERGREEN LADERA": "Evergreen", "BANISTER STREET": "Banister Street",
        "THE TRAILS": "The Trails", "SURREY FARM": "Surrey Farms",
        "AMARANTE I & II": "Amarante", "BELLATAIRE I & II": "Bellataire",
        "CLAIRBORNE": "Claiborne", "SAN DONADO": "San Donato",
    }
    if value.strip().upper() in aliases:
        return aliases[value.strip().upper()]
    value = re.sub(r"\s+(?:I\s*&\s*II|I{1,3}|[123])$", "", value, flags=re.I)
    return aliases.get(value.upper(), value.strip())


def canonical_builder(value: str) -> str:
    normalized = slug(value).replace("-HOMES", "").replace("-HOME", "")
    aliases = {
        "CENTEX": "CENTEX", "MBK": "MBK", "STANDARD-PACIFIC": "STANDARD-PACIFIC",
        "STANDAR-PACIFIC": "STANDARD-PACIFIC", "LAING": "JOHN-LAING",
        "JOHN-LAING": "JOHN-LAING", "LYON": "WILLIAM-LYON", "WILLIAM-LYON": "WILLIAM-LYON",
    }
    return aliases.get(normalized, normalized)


PHASE_V = [
    ("Valmont", "D.R. Horton", "Condominiums", 142, 142, 142),
    ("Sutter's Mill", "Centex Homes", "Townhomes", 152, 152, 152),
    ("Briar Rose", "MBK Homes", "Townhomes", 152, 152, 136),
    ("Branches", "Standard Pacific", "Townhomes", 149, 149, 148),
    ("Banister Street", "Standard Pacific", "Townhomes", 24, 24, 24),
    ("Tarleton", "D.R. Horton", "Single Family Detached", 107, 107, 107),
    ("Arborage", "Richmond American", "Single Family Detached", 104, 104, 104),
    ("Walden Park", "William Lyon Homes", "Single Family Detached", 109, 109, 109),
    ("Clairborne", "Pulte Homes", "Single Family Detached", 75, 75, 75),
    ("Mosaic", "K. Hovnanian", "Single Family Detached", 89, 89, 89),
    ("Evergreen", "Pardee Homes", "Single Family Detached", 77, 77, 77),
    ("Sedona", "Shea Homes", "Single Family Detached", 79, 79, 79),
]

PHASE_VI_2006 = [
    ("Castellina", "Centex Homes", "Attached", 82, 82, 80),
    ("Segovia", "Pardee", "Detached", 65, 48, 22),
    ("Amarante I & II", "Lyon Homes", "Detached", 71, 71, 68),
    ("Montanez", "Centex Homes", "Detached", 59, 52, 42),
    ("Meriden", "Warmington", "Detached", 67, 67, 65),
    ("Bellataire I & II", "Lyon Homes", "Detached", 75, 75, 70),
    ("Arboledo", "Warmington Homes", "Detached", 62, 60, 25),
    ("Las Piedras", "Standard Pacific", "Detached", 35, 35, 33),
    ("Sherborne", "Shea Homes", "Detached", 54, 54, 54),
    ("Alisal", "Standard Pacific", "Detached", 48, 48, 48),
    ("Capistrano", "K. Hovnanian", "Detached", 35, 33, 12),
    ("San Donado", "Laing", "Detached", 23, 23, 23),
    ("Encantada", "Pardee", "Detached", 37, 24, 10),
    ("Skye Isle", "K. Hovnanian", "Detached", 61, 59, 50),
    ("DMB-Ladera Custom Lots", "DMB-Ladera", "Custom Lots", 232, 0, 103),
]


def builder_products() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    village_by_table = {
        0: "Avendale", 1: "Covenant Hills", 2: "Echo Ridge", 3: "Flintridge",
        4: "Oak Knoll", 5: "Terramor", 6: "Township", 8: "Wycliffe",
    }
    html = (EVIDENCE / "html/activerain_builder_crosswalk_2010.html").read_text(encoding="utf-8")
    tables = pd.read_html(StringIO(html))
    rows: list[dict[str, object]] = []
    for table_number, village in village_by_table.items():
        table = tables[table_number]
        for values in table.iloc[1:].itertuples(index=False, name=None):
            product, housing_type, units, builder = [str(value).strip() for value in values[:4]]
            if not product or product.lower() == "nan":
                continue
            rows.append(
                {
                    "builderProductId": f"LH-PRODUCT-{slug(village)}-{slug(product)}",
                    "productName": product,
                    "canonicalProductName": base_product(product),
                    "village": village,
                    "cfdPhase": "",
                    "builder": builder,
                    "housingType": housing_type,
                    "unitsPlanned": units if units.isdigit() else "",
                    "permitsBy2006": "",
                    "escrowsBy2006": "",
                    "permitsBy2011": "",
                    "escrowsBy2011": "",
                    "modelOpening": "",
                    "firstSales": "",
                    "completionUpperBound": "",
                    "sourceIds": "LH-SRC-ACTIVERAIN-2010",
                    "statementClass": "reported_secondary",
                    "confidence": "low",
                    "limitations": "Secondary directory; builder assignment requires primary confirmation.",
                }
            )

    by_key = {(str(row["village"]), str(row["canonicalProductName"]).upper()): row for row in rows}
    conflicts: list[dict[str, object]] = []
    primary_sets = [("Terramor", "Phase V", PHASE_V), ("Covenant Hills", "Phase VI", PHASE_VI_2006)]
    for village, phase, products in primary_sets:
        for product, builder, housing_type, planned, permits, escrows in products:
            normalized = base_product(product).upper()
            matches = [
                row for row in rows
                if row["village"] == village
                and base_product(str(row["canonicalProductName"])).upper() == normalized
            ]
            row = matches[0] if matches else {
                "builderProductId": f"LH-PRODUCT-{slug(village)}-{slug(product)}",
                "productName": product,
                "canonicalProductName": base_product(product),
                "village": village,
                "modelOpening": "",
                "firstSales": "",
            }
            secondary_builder = str(row.get("builder", ""))
            if secondary_builder and canonical_builder(secondary_builder) != canonical_builder(builder):
                conflicts.append(
                    {
                        "conflictId": f"LH-CONFLICT-M5-BUILDER-{slug(product)}",
                        "entityId": row["builderProductId"],
                        "conflictType": "builder_assignment",
                        "positionA": f"Secondary 2010 directory assigns {secondary_builder}.",
                        "positionAEvidenceIds": row["builderProductId"],
                        "positionASourceIds": "LH-SRC-ACTIVERAIN-2010",
                        "positionB": f"County bond monitoring report assigns {builder}.",
                        "positionBEvidenceIds": f"County 2006 table for {phase}",
                        "positionBSourceIds": "LH-SRC-OC-BOND-2006Q4",
                        "resolutionRule": "Use the contemporary official County table for the builder claim; retain the secondary report as conflict evidence.",
                        "resolutionConfidence": "high",
                        "reviewStatus": "resolved_by_authoritative_primary_source",
                    }
                )
            row.update(
                {
                    "productName": product,
                    "canonicalProductName": base_product(product),
                    "village": village,
                    "cfdPhase": phase,
                    "builder": builder,
                    "housingType": housing_type,
                    "unitsPlanned": planned,
                    "permitsBy2006": permits,
                    "escrowsBy2006": escrows,
                    "permitsBy2011": planned if phase == "Phase VI" and product != "DMB-Ladera Custom Lots" else "",
                    "escrowsBy2011": planned if phase == "Phase VI" and product != "DMB-Ladera Custom Lots" else (118 if product == "DMB-Ladera Custom Lots" else ""),
                    "completionUpperBound": "2011-12-31" if phase == "Phase VI" and product != "DMB-Ladera Custom Lots" else ("2006-12-31" if planned == permits == escrows else ""),
                    "sourceIds": "LH-SRC-OC-BOND-2006Q4" + (";LH-SRC-OC-BOND-2011Q4" if phase == "Phase VI" else ""),
                    "statementClass": "documented_exact",
                    "confidence": "high",
                    "limitations": (
                        "Counts are CFD product-table permit and closed-escrow milestones. A full count bounds the product's "
                        "reported status but does not date every building completion or individual move-in."
                    ),
                }
            )
            if not matches:
                rows.append(row)

    trails = next((row for row in rows if row["canonicalProductName"] == "The Trails"), None)
    if trails:
        trails.update(
            {
                "modelOpening": "1999-07-31",
                "firstSales": "1999-07-31",
                "sourceIds": "LH-SRC-ACTIVERAIN-2010;LH-SRC-PROB-TRAILS-1999",
                "confidence": "medium",
                "limitations": "Contemporary trade article establishes model availability and 28 sales by 1999-11-03; exact vertical-construction start remains unknown.",
            }
        )

    rows.sort(key=lambda row: (str(row["village"]), str(row["canonicalProductName"])))
    write_csv(BASE / "builder_product_chronology.csv", rows)
    conflict_path = BASE / "conflict_registry.csv"
    retained_conflicts = [
        row for row in read_csv(conflict_path)
        if not row["conflictId"].startswith("LH-CONFLICT-M5-BUILDER-")
    ]
    fields = list(read_csv(conflict_path)[0])
    for conflict in conflicts:
        for field in conflict:
            if field not in fields:
                fields.append(field)
    write_csv(conflict_path, retained_conflicts + conflicts, fields)
    return rows, conflicts


def absorption_chronology() -> list[dict[str, object]]:
    series = {
        "CFD 99-1 Phase I": [(1999, 97), (2000, 557), (2001, 276), (2002, 30), (2003, 0), (2004, 14), (2005, 98), (2006, 57)],
        "CFD 2002-1 Urban Activity Center": [(2003, 158), (2004, 179), (2005, 49)],
        "CFD 2003-1 Phase V": [(2004, 741), (2005, 375), (2006, 126)],
        "CFD 2004-1 Phase VI": [(2005, 312), (2006, 393), (2007, 141), (2008, 31), (2009, 15), (2010, 0)],
    }
    rows = []
    for district, values in series.items():
        for year, count in values:
            rows.append(
                {
                    "absorptionId": f"LH-ABS-{slug(district)}-{year}",
                    "district": district,
                    "year": year,
                    "builtAndOccupiedUnits": count,
                    "definition": "Absorption = Built and Occupied",
                    "sourceIds": "LH-SRC-OC-BOND-2006Q4" + (";LH-SRC-OC-BOND-2011Q4" if "Phase VI" in district else ""),
                    "statementClass": "documented_exact",
                    "confidence": "high",
                    "limitations": "Annual CFD aggregate is nonspatial and cannot be assigned to a tract, address, or household.",
                }
            )
    write_csv(BASE / "cfd_absorption_chronology.csv", rows)
    return rows


def neighborhood_chronology(
    phases: list[dict[str, object]], products: list[dict[str, object]]
) -> list[dict[str, object]]:
    by_key: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for product in products:
        by_key[(str(product["village"]), base_product(str(product["canonicalProductName"])).upper())].append(product)
    rows = []
    for phase in phases:
        matches = by_key.get(
            (str(phase["village"]), base_product(str(phase["neighborhoodName"])).upper()), []
        )
        sources = split_ids(str(phase["sourceIds"]))
        for match in matches:
            sources.extend(split_ids(str(match["sourceIds"])))
        rows.append(
            {
                "neighborhoodPhaseId": phase["neighborhoodPhaseId"],
                "neighborhoodName": phase["neighborhoodName"],
                "village": phase["village"],
                "officialVillageCode": phase["officialVillageCode"],
                "builderProductIds": ";".join(str(row["builderProductId"]) for row in matches),
                "builderCandidates": ";".join(sorted({str(row["builder"]) for row in matches})),
                "modelOrSalesOpening": ";".join(sorted({
                    str(row["modelOpening"] or row["firstSales"]) for row in matches
                    if row["modelOpening"] or row["firstSales"]
                })),
                "completionUpperBound": ";".join(sorted({
                    str(row["completionUpperBound"]) for row in matches if row["completionUpperBound"]
                })),
                "chronologyStatus": "product_level_milestones_available" if matches else "current_name_and_village_only",
                "sourceIds": ";".join(dict.fromkeys(sources)),
                "confidence": "high" if matches and all(row["confidence"] == "high" for row in matches) else "medium",
                "limitations": (
                    "The official directory establishes current naming. Product-level permit or escrow snapshots do not "
                    "establish the opening, construction, completion, habitability, or occupancy date of every numbered phase."
                ),
                "reviewStatus": "bounded_product_crosswalk" if matches else "historical_dates_not_located",
            }
        )
    write_csv(BASE / "neighborhood_chronology_mission5.csv", rows)
    return rows


COMMERCIAL_2006 = [
    ("A", "Laurel Terrace", "apartments", 9.59, 9.59, "Some Built/Leasing", "dwelling_units", 232, 232),
    ("B", "Remington-Active Seniors", "senior_apartments", 5.58, 5.58, "UC/PreLeasing", "dwelling_units", 154, 154),
    ("C", "Ladera Corporate Terrace", "office_and_fitness", 21.32, 6.16, "Under Development", "square_feet", 250000, 88068),
    ("C", "Montessori 2101", "day_care", 0.83, 0.83, "Built/Occupied", "square_feet", 15000, 15000),
    ("C", "Kinder Care 1000", "day_care", 0.55, 0.55, "Built/Occupied", "square_feet", 15000, 15000),
    ("D", "Tract 16036 Lots 40, 41", "mixed_use_retail", 3.57, 0.00, "Not Developed", "not_applicable", 0, 0),
    ("E", "Merchantile East", "shopping_center_retail", 25.11, 23.84, "Mostly Occupied", "square_feet", 276570, 262570),
    ("F", "Ladera UAC Self Storage", "self_storage", 3.73, 3.73, "Built/Occupied", "square_feet", 118000, 118000),
]


def commercial_chronology() -> tuple[list[dict[str, object]], int]:
    rows = []
    asset_rows = []
    observations = []
    claims = []
    convergence = []
    for code, name, asset_class, total_acres, occupied_acres, status, capacity_unit, total, occupied in COMMERCIAL_2006:
        asset_id = f"LH-ASSET-UAC-{slug(name)}"
        chronology_id = f"LH-COMMERCIAL-2006-{slug(name)}"
        rows.append(
            {
                "commercialChronologyId": chronology_id, "mapCode": code, "assetId": asset_id,
                "assetName": name, "assetClass": asset_class, "snapshotDate": "2006-12-31",
                "totalAcres": f"{total_acres:.2f}", "occupiedAcres": f"{occupied_acres:.2f}",
                "reportedDevelopmentStatus": status, "capacityUnit": capacity_unit,
                "totalCapacity": total if total else "", "occupiedCapacity": occupied if occupied else "",
                "sourceIds": "LH-SRC-OC-BOND-2006Q4", "sourceLocator": "PDF page 10, CFD 2002-1 development-status table",
                "statementClass": "documented_exact", "confidence": "high",
                "limitations": "Status is a County monitoring snapshot at 2006-12-31, not an opening date or construction interval.",
            }
        )
        asset_rows.append(
            {
                "assetChronologyId": chronology_id, "assetId": asset_id, "assetName": name,
                "assetClass": asset_class, "milestoneState": status.lower().replace("/", "_").replace(" ", "_"),
                "earliestDate": "2006-12-31", "latestDate": "2006-12-31", "datePrecision": "day",
                "geometryId": "", "geometryStatus": "not_retrieved", "sourceIds": "LH-SRC-OC-BOND-2006Q4",
                "confidence": "high", "limitations": "Snapshot status only; historical footprint and opening or construction dates remain unresolved.",
                "haulRouteStatus": "not_documented", "reviewStatus": "documented_status_snapshot",
            }
        )
        observation_id = f"LH-OBS-{chronology_id}"
        claim_id = f"LH-CLM-{chronology_id}"
        value = f"{name}: {status} at the 2006-12-31 County monitoring snapshot"
        observations.append(
            {
                "observationId": observation_id, "observedEntityId": asset_id,
                "observationType": "commercial_or_mixed_use_status_snapshot", "observedValue": value,
                "dateStart": "2006-12-31", "dateEnd": "", "temporalPrecision": "day",
                "geometryId": "", "geometryType": "", "geometryStatus": "nonspatial_asset_snapshot",
                "method": "direct table transcription verified against rendered PDF",
                "sourceIds": "LH-SRC-OC-BOND-2006Q4", "sourceLocator": "PDF page 10, CFD 2002-1 table",
                "statementClass": "documented_exact", "confidence": "high",
                "limitations": "Snapshot status only; no opening date or historical footprint is inferred.", "notes": "",
            }
        )
        claims.append(
            {
                "claimId": claim_id, "subjectEntityId": asset_id,
                "claimType": "commercial_or_mixed_use_status_snapshot", "claimText": value,
                "dateStart": "2006-12-31", "dateEnd": "", "temporalPrecision": "day",
                "claimScope": "asset_status_snapshot", "supportingObservationIds": observation_id,
                "sourceIds": "LH-SRC-OC-BOND-2006Q4", "supportType": "direct_observation",
                "statementClass": "documented_exact", "confidence": "high",
                "conflictStatus": "no_conflict_identified", "reviewStatus": "reviewed_mission5",
                "limitations": "Snapshot status only; no opening date or historical footprint is inferred.", "notes": "",
            }
        )
        convergence.append(
            {
                "claimId": claim_id, "supportingObservationCount": 1, "independentSourceOrganizationCount": 1,
                "primarySourceCount": 1, "contemporarySourceCount": 1, "visualSourceCount": 0,
                "conflictingObservationCount": 0, "geographicPrecision": "named_asset_nonspatial",
                "temporalPrecision": "day", "directness": "direct_observation", "sourceAuthority": "official_primary",
                "completeness": "claim_bounded", "finalConfidence": "high",
                "confidenceRationale": "The official County table directly reports the status and quantities at the snapshot date.",
                "exhaustionStatus": "authoritative_single_source",
                "limitations": "The County table does not provide opening dates or historical asset footprints.",
            }
        )
    write_csv(BASE / "commercial_asset_chronology_mission5.csv", rows)
    upsert(BASE / "asset_chronology.csv", asset_rows, "assetChronologyId")
    upsert(BASE / "historical_observations.csv", observations, "observationId")
    upsert(BASE / "claim_registry.csv", claims, "claimId")
    upsert(BASE / "source_convergence.csv", convergence, "claimId")
    return rows, len(claims)


def product_evidence(products: list[dict[str, object]]) -> int:
    observations = []
    claims = []
    convergence = []
    for product in products:
        if not product["cfdPhase"]:
            continue
        product_id = str(product["builderProductId"])
        snapshots = [
            (
                "2006", "2006-12-31", "LH-SRC-OC-BOND-2006Q4",
                product["permitsBy2006"], product["escrowsBy2006"],
            )
        ]
        if product["permitsBy2011"] or product["escrowsBy2011"]:
            snapshots.append(
                ("2011", "2011-12-31", "LH-SRC-OC-BOND-2011Q4", product["permitsBy2011"], product["escrowsBy2011"])
            )
        for label, date, source_id, permits, escrows in snapshots:
            observation_id = f"LH-OBS-{slug(product_id)}-{label}"
            claim_id = f"LH-CLM-{slug(product_id)}-{label}"
            permit_text = str(permits) if permits != "" else "not reported"
            value = (
                f"{product['productName']} ({product['builder']}): {product['unitsPlanned']} planned, "
                f"{permit_text} permits, and {escrows} closed escrows at {date}"
            )
            limitations = (
                "Product-level CFD counts are not address-level completion, habitability, or occupancy dates; "
                "closed escrow is not transferred to a tract geometry."
            )
            observations.append(
                {
                    "observationId": observation_id, "observedEntityId": product_id,
                    "observationType": "builder_product_status_snapshot", "observedValue": value,
                    "dateStart": date, "dateEnd": "", "temporalPrecision": "day", "geometryId": "",
                    "geometryType": "", "geometryStatus": "nonspatial_product_snapshot",
                    "method": "direct table transcription verified against rendered PDF", "sourceIds": source_id,
                    "sourceLocator": f"County bond report {product['cfdPhase']} product table",
                    "statementClass": "documented_exact", "confidence": "high",
                    "limitations": limitations, "notes": "",
                }
            )
            claims.append(
                {
                    "claimId": claim_id, "subjectEntityId": product_id, "claimType": "builder_product_status_snapshot",
                    "claimText": value, "dateStart": date, "dateEnd": "", "temporalPrecision": "day",
                    "claimScope": "builder_product", "supportingObservationIds": observation_id,
                    "sourceIds": source_id, "supportType": "direct_observation", "statementClass": "documented_exact",
                    "confidence": "high", "conflictStatus": "conflict_documented" if any(
                        conflict["entityId"] == product_id for conflict in read_csv(BASE / "conflict_registry.csv")
                    ) else "no_conflict_identified",
                    "reviewStatus": "reviewed_mission5", "limitations": limitations, "notes": "",
                }
            )
            convergence.append(
                {
                    "claimId": claim_id, "supportingObservationCount": 1, "independentSourceOrganizationCount": 1,
                    "primarySourceCount": 1, "contemporarySourceCount": 1, "visualSourceCount": 0,
                    "conflictingObservationCount": 1 if claims[-1]["conflictStatus"] == "conflict_documented" else 0,
                    "geographicPrecision": "named_product_nonspatial", "temporalPrecision": "day",
                    "directness": "direct_observation", "sourceAuthority": "official_primary",
                    "completeness": "claim_bounded", "finalConfidence": "high",
                    "confidenceRationale": "Contemporary official County product table controls the builder and count snapshot.",
                    "exhaustionStatus": "authoritative_primary_with_secondary_conflict_retained" if claims[-1]["conflictStatus"] == "conflict_documented" else "authoritative_single_source",
                    "limitations": limitations,
                }
            )
    upsert(BASE / "historical_observations.csv", observations, "observationId")
    upsert(BASE / "claim_registry.csv", claims, "claimId")
    upsert(BASE / "source_convergence.csv", convergence, "claimId")
    return len(claims)


def tract_neighborhood_crosswalk(street_rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    address_data = json.loads((EVIDENCE / "gis/oc_address_points_ladera.json").read_text())
    by_street: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in street_rows:
        by_street[str(row["streetNameNormalized"])].append(row)

    tract_data = json.loads((DATA / "tract_maps.geojson").read_text())
    tract_features = tract_data["features"]
    geometries = [feature["geometry"] for feature in tract_features]
    metrics = [geometry_metrics(geometry) for geometry in geometries]
    point_rows: list[dict[str, object]] = []
    grouped: Counter[tuple[str, str, str]] = Counter()
    neighborhood_total: Counter[tuple[str, str]] = Counter()
    unmatched = 0
    ambiguous = 0
    for feature in address_data["features"]:
        attrs = feature["attributes"]
        key = normalize_street(attrs.get("StreetName") or "")
        candidates = by_street.get(key, [])
        number = attrs.get("AddressNumber")
        if not candidates or number is None:
            unmatched += 1
            continue
        matches = [row for row in candidates if address_matches(int(number), str(row["addressConstraint"]))]
        if not matches:
            unmatched += 1
            continue
        if len(matches) > 1:
            ambiguous += 1
        x = float(feature["geometry"]["x"])
        y = float(feature["geometry"]["y"])
        indexes = [
            index for index, (geometry, (bbox, _)) in enumerate(zip(geometries, metrics))
            if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]
            and geometry_covers_point(geometry, x, y)
        ]
        if not indexes:
            continue
        smallest = min(indexes, key=lambda index: metrics[index][1])
        tract_number = str(tract_features[smallest]["properties"]["tractNumber"])
        for match in matches:
            neighborhood = str(match["neighborhood"])
            village = str(match["village"])
            grouped[(neighborhood, village, tract_number)] += 1
            neighborhood_total[(neighborhood, village)] += 1
            point_rows.append(
                {
                    "addressPointId": attrs.get("AddressPtID") or attrs.get("OBJECTID"),
                    "address": attrs.get("Address", ""),
                    "streetNameNormalized": key,
                    "neighborhood": neighborhood,
                    "village": village,
                    "leafTractId": f"LH-TRACT-{tract_number}",
                    "allContainingTractIds": ";".join(
                        f"LH-TRACT-{tract_features[index]['properties']['tractNumber']}"
                        for index in sorted(indexes, key=lambda index: metrics[index][1])
                    ),
                    "matchStatus": "ambiguous_directory_match" if len(matches) > 1 else "exact_directory_match",
                    "sourceIds": "LH-SRC-LARMAC-STREETS-2019;LH-SRC-OC-ADDRESS-POINTS;LH-SRC-OC-TRACTS",
                }
            )

    crosswalk = []
    for index, ((neighborhood, village, tract_number), count) in enumerate(sorted(grouped.items()), start=1):
        total = neighborhood_total[(neighborhood, village)]
        share = count / total * 100 if total else 0
        crosswalk.append(
            {
                "crosswalkId": f"LH-TRACT-NEIGHBORHOOD-{index:04d}",
                "tractId": f"LH-TRACT-{tract_number}",
                "tractNumber": tract_number,
                "neighborhood": neighborhood,
                "village": village,
                "matchedAddressPointCount": count,
                "neighborhoodMatchedPointSharePct": f"{share:.2f}",
                "relationshipType": "current_address_points_within_smallest_containing_recorded_tract",
                "validAt": RETRIEVAL_DATE,
                "sourceIds": "LH-SRC-LARMAC-STREETS-2019;LH-SRC-OC-ADDRESS-POINTS;LH-SRC-OC-TRACTS",
                "statementClass": "spatial_crosswalk",
                "confidence": "high" if count >= 5 else "medium",
                "reviewStatus": "current_geographic_crosswalk_not_historical_lifecycle",
                "limitations": (
                    "Current address points and 2019 names are joined to the smallest containing County legal-map polygon. "
                    "This does not establish historical opening, construction, sale, habitability, or occupancy dates."
                ),
            }
        )
    write_csv(BASE / "address_neighborhood_tract_points.csv", point_rows)
    write_csv(BASE / "tract_neighborhood_crosswalk.csv", crosswalk)
    write_json(
        BASE / "tract_neighborhood_crosswalk_summary.json",
        {
            "sourceAddressPointCount": address_data["featureCount"],
            "matchedPointRows": len(point_rows),
            "unmatchedOrOutOfScopeAddressPoints": unmatched,
            "ambiguousDirectoryMatches": ambiguous,
            "crosswalkRelationships": len(crosswalk),
            "distinctNeighborhoods": len(neighborhood_total),
            "distinctLeafTracts": len({row["tractId"] for row in crosswalk}),
        },
    )
    return point_rows, crosswalk


def tract_lifecycle(crosswalk: list[dict[str, object]], products: list[dict[str, object]]) -> list[dict[str, object]]:
    audit = read_csv(BASE / "tract_audit.csv")
    by_tract: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in crosswalk:
        by_tract[str(row["tractId"])].append(row)
    product_by_key: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for product in products:
        product_by_key[(str(product["village"]), str(product["canonicalProductName"]).upper())].append(product)
    rows = []
    for tract in audit:
        mappings = by_tract.get(tract["tractId"], [])
        product_matches: dict[str, dict[str, object]] = {}
        for mapping in mappings:
            key = (str(mapping["village"]), base_product(str(mapping["neighborhood"])).upper())
            for product in product_by_key.get(key, []):
                product_matches[str(product["builderProductId"])] = product
        source_ids = ["LH-SRC-OC-TRACTS"]
        if mappings:
            source_ids.extend(["LH-SRC-LARMAC-STREETS-2019", "LH-SRC-OC-ADDRESS-POINTS"])
        if product_matches:
            source_ids.extend(sorted({source for product in product_matches.values() for source in split_ids(str(product["sourceIds"]))}))
        known = []
        if mappings:
            known.append("current_neighborhood_geography")
        if product_matches:
            known.append("builder_product_candidate")
        rows.append(
            {
                "tractId": tract["tractId"],
                "tractNumber": tract["tractNumber"],
                "mapRecordingDate": tract["recordDate"],
                "neighborhoodCandidates": ";".join(sorted({str(row["neighborhood"]) for row in mappings})),
                "villageCandidates": ";".join(sorted({str(row["village"]) for row in mappings})),
                "matchedAddressPointCount": sum(int(row["matchedAddressPointCount"]) for row in mappings),
                "builderProductCandidates": ";".join(sorted(product_matches)),
                "builderCandidates": ";".join(sorted({str(row["builder"]) for row in product_matches.values()})),
                "planning": "not_reconstructed",
                "tentativeMap": "not_reconstructed",
                "finalMap": tract["bookPage"],
                "recording": tract["recordDate"],
                "grading": "unknown",
                "infrastructure": "unknown",
                "roads": "unknown",
                "utilities": "unknown",
                "verticalConstruction": "unknown",
                "modelHomes": "product_level_only" if any(row.get("modelOpening") for row in product_matches.values()) else "unknown",
                "sales": "product_level_only" if any(row.get("firstSales") for row in product_matches.values()) else "unknown",
                "firstOccupancy": "unknown",
                "partialOccupancy": "unknown",
                "substantialOccupancy": "unknown",
                "completion": "product_level_upper_bound_only" if any(row.get("completionUpperBound") for row in product_matches.values()) else "unknown",
                "knownLifecycleAdditions": ";".join(known),
                "sourceIds": ";".join(dict.fromkeys(source_ids)),
                "confidence": "medium" if mappings else "recording_high_physical_lifecycle_unknown",
                "limitations": (
                    "Mission 5 adds current geographic and product associations but does not transfer CFD aggregate dates "
                    "to a tract. Permit, grading, certificate-of-occupancy, and address-level historical records remain required."
                ),
                "reviewStatus": "enriched_but_physical_lifecycle_unresolved" if mappings else "physical_lifecycle_unresolved",
            }
        )
    write_csv(BASE / "tract_lifecycle_reconstruction.csv", rows)
    return rows


def mission5_events_and_evidence(absorption: list[dict[str, object]]) -> tuple[int, int]:
    event_fields = list(read_csv(BASE / "events.csv")[0])
    event_rows = [
        {
            "id": "LH-EVT-M5-001", "dateStart": "1998-01-20", "dateEnd": "", "temporalPrecision": "day",
            "eventType": "builder_selection", "title": "Nine builders selected for the initial approximately 1,000-home phase",
            "placeName": "Ladera Ranch Phase I", "featureId": "LH-PHASE-I", "status": "reported",
            "statementClass": "documented_exact", "confidence": "medium", "sourceIds": "LH-SRC-LAT-BUILDERS-1998",
            "sourceLocator": "Contemporary article dated 1998-01-20", "interpretationMethod": "direct transcription",
            "conflictNotes": "The 1999 announcement lists eight builders and revised allocations; both dated selections are retained.",
            "notes": "Selection is not a construction-start date.",
        },
        {
            "id": "LH-EVT-M5-002", "dateStart": "1999-05-04", "dateEnd": "", "temporalPrecision": "day",
            "eventType": "builder_selection", "title": "Eight Phase I builders and revised unit allocations announced",
            "placeName": "Oak Knoll", "featureId": "LH-VILLAGE-OAK-KNOLL", "status": "reported",
            "statementClass": "documented_exact", "confidence": "medium", "sourceIds": "LH-SRC-LAT-PHASE1-1999",
            "sourceLocator": "Contemporary article dated 1999-05-04", "interpretationMethod": "direct transcription",
            "conflictNotes": "Supersedes or revises the 1998 selection, but the article does not state the legal change mechanism.",
            "notes": "Builder selection is not a physical-construction milestone.",
        },
        {
            "id": "LH-EVT-M5-003", "dateStart": "1999-07-31", "dateEnd": "", "temporalPrecision": "day",
            "eventType": "model_and_sales_opening", "title": "Oak Knoll grand opening and model-home access",
            "placeName": "Oak Knoll", "featureId": "LH-VILLAGE-OAK-KNOLL", "status": "open",
            "statementClass": "documented_exact", "confidence": "high",
            "sourceIds": "LH-SRC-LAT-OPENING-1999;LH-SRC-PROB-TRAILS-1999",
            "sourceLocator": "Contemporary grand-opening and trade reports", "interpretationMethod": "source convergence",
            "conflictNotes": "", "notes": "Opening and sales evidence does not establish occupancy.",
        },
        {
            "id": "LH-EVT-M5-004", "dateStart": "1999-11-29", "dateEnd": "", "temporalPrecision": "day",
            "eventType": "escrow_closing", "title": "Contemporary report dates first Oak Knoll residents' escrow closing",
            "placeName": "Oak Knoll", "featureId": "LH-VILLAGE-OAK-KNOLL", "status": "closed",
            "statementClass": "documented_exact", "confidence": "medium", "sourceIds": "LH-SRC-LAT-FIRST-RESIDENT-1999",
            "sourceLocator": "Contemporary article dated 1999-12-12", "interpretationMethod": "direct transcription",
            "conflictNotes": "Official retrospective instead dates the first resident to 1999-12-14.",
            "notes": "Named-address geometry is not published in the archived article.",
        },
        {
            "id": "LH-EVT-M5-005", "dateStart": "1999-11-30", "dateEnd": "", "temporalPrecision": "day",
            "eventType": "first_reported_overnight_occupancy", "title": "Contemporary report says first Oak Knoll couple spent the night",
            "placeName": "Oak Knoll", "featureId": "LH-VILLAGE-OAK-KNOLL", "status": "occupied_without_full_utilities",
            "statementClass": "documented_exact", "confidence": "medium", "sourceIds": "LH-SRC-LAT-FIRST-RESIDENT-1999",
            "sourceLocator": "Contemporary article dated 1999-12-12", "interpretationMethod": "direct transcription",
            "conflictNotes": "Official retrospective instead dates the first resident to 1999-12-14.",
            "notes": "Article reports no gas or electricity that first night; no habitability conclusion is inferred.",
        },
    ]
    upsert(BASE / "events.csv", event_rows, "id")
    conflict = {
        "conflictId": "LH-CONFLICT-M5-FIRST-RESIDENT",
        "entityId": "LH-VILLAGE-OAK-KNOLL",
        "conflictType": "first_resident_date",
        "positionA": "Contemporary Los Angeles Times reporting dates escrow to 1999-11-29 and first overnight stay to 1999-11-30.",
        "positionAEvidenceIds": "LH-EVT-M5-004;LH-EVT-M5-005",
        "positionASourceIds": "LH-SRC-LAT-FIRST-RESIDENT-1999",
        "positionB": "Official Ladera retrospective states the first resident moved in on 1999-12-14.",
        "positionBEvidenceIds": "LH-EVT-008",
        "positionBSourceIds": "LH-SRC-LARMAC-TIMELINE",
        "resolutionRule": "Retain both. Prefer the contemporary report for the reported overnight event; do not infer certificate of occupancy or habitability from either.",
        "resolutionConfidence": "medium",
        "reviewStatus": "unresolved_definition_or_retrospective_discrepancy",
    }
    upsert(BASE / "conflict_registry.csv", [conflict], "conflictId")

    observations = []
    claims = []
    convergence = []
    for event in event_rows:
        observation_id = f"LH-OBS-{event['id']}"
        claim_id = f"LH-CLM-{event['id']}"
        observations.append(
            {
                "observationId": observation_id, "observedEntityId": event["featureId"],
                "observationType": event["eventType"], "observedValue": event["title"],
                "dateStart": event["dateStart"], "dateEnd": event["dateEnd"],
                "temporalPrecision": event["temporalPrecision"], "geometryId": "", "geometryType": "",
                "geometryStatus": "nonspatial_observation", "method": event["interpretationMethod"],
                "sourceIds": event["sourceIds"], "sourceLocator": event["sourceLocator"],
                "statementClass": event["statementClass"], "confidence": event["confidence"],
                "limitations": event["conflictNotes"], "notes": event["notes"],
            }
        )
        claims.append(
            {
                "claimId": claim_id, "subjectEntityId": event["featureId"], "claimType": event["eventType"],
                "claimText": event["title"], "dateStart": event["dateStart"], "dateEnd": event["dateEnd"],
                "temporalPrecision": event["temporalPrecision"], "claimScope": "historical_event",
                "supportingObservationIds": observation_id, "sourceIds": event["sourceIds"],
                "supportType": "direct_observation", "statementClass": event["statementClass"],
                "confidence": event["confidence"], "conflictStatus": "conflict_documented" if event["conflictNotes"] else "no_conflict_identified",
                "reviewStatus": "reviewed_mission5", "limitations": event["conflictNotes"], "notes": event["notes"],
            }
        )
        orgs = len(split_ids(event["sourceIds"]))
        convergence.append(
            {
                "claimId": claim_id, "supportingObservationCount": 1,
                "independentSourceOrganizationCount": orgs, "primarySourceCount": 0,
                "contemporarySourceCount": orgs, "visualSourceCount": 0,
                "conflictingObservationCount": 1 if event["conflictNotes"] else 0,
                "geographicPrecision": "village_or_phase", "temporalPrecision": event["temporalPrecision"],
                "directness": "direct_observation", "sourceAuthority": "contemporary_publication",
                "completeness": "claim_bounded", "finalConfidence": event["confidence"],
                "confidenceRationale": "Contemporary reporting is bounded to the stated event; legal habitability and address geometry are not inferred.",
                "exhaustionStatus": "source_convergence_reached" if orgs > 1 else "authoritative_or_contemporary_single_source",
                "limitations": event["conflictNotes"] or event["notes"],
            }
        )

    for item in absorption:
        observation_id = f"LH-OBS-{item['absorptionId']}"
        claim_id = f"LH-CLM-{item['absorptionId']}"
        subject = f"LH-{slug(str(item['district']))}"
        value = f"{item['builtAndOccupiedUnits']} units absorbed under the report definition during {item['year']}"
        observations.append(
            {
                "observationId": observation_id, "observedEntityId": subject,
                "observationType": "annual_built_and_occupied_absorption", "observedValue": value,
                "dateStart": f"{item['year']}-01-01", "dateEnd": f"{item['year']}-12-31",
                "temporalPrecision": "year", "geometryId": "", "geometryType": "",
                "geometryStatus": "nonspatial_cfd_aggregate", "method": "direct chart transcription verified against rendered PDF",
                "sourceIds": item["sourceIds"], "sourceLocator": "County bond monitoring absorption chart",
                "statementClass": "documented_exact", "confidence": "high",
                "limitations": item["limitations"], "notes": item["definition"],
            }
        )
        claims.append(
            {
                "claimId": claim_id, "subjectEntityId": subject, "claimType": "annual_built_and_occupied_absorption",
                "claimText": value, "dateStart": f"{item['year']}-01-01", "dateEnd": f"{item['year']}-12-31",
                "temporalPrecision": "year", "claimScope": "cfd_aggregate", "supportingObservationIds": observation_id,
                "sourceIds": item["sourceIds"], "supportType": "direct_observation", "statementClass": "documented_exact",
                "confidence": "high", "conflictStatus": "no_conflict_identified", "reviewStatus": "reviewed_mission5",
                "limitations": item["limitations"], "notes": item["definition"],
            }
        )
        convergence.append(
            {
                "claimId": claim_id, "supportingObservationCount": 1, "independentSourceOrganizationCount": 1,
                "primarySourceCount": 1, "contemporarySourceCount": 1, "visualSourceCount": 0,
                "conflictingObservationCount": 0, "geographicPrecision": "cfd_aggregate", "temporalPrecision": "year",
                "directness": "direct_observation", "sourceAuthority": "official_primary", "completeness": "claim_bounded",
                "finalConfidence": "high", "confidenceRationale": "Official County chart explicitly defines absorption as built and occupied.",
                "exhaustionStatus": "authoritative_single_source", "limitations": item["limitations"],
            }
        )
    upsert(BASE / "historical_observations.csv", observations, "observationId")
    upsert(BASE / "claim_registry.csv", claims, "claimId")
    upsert(BASE / "source_convergence.csv", convergence, "claimId")
    return len(observations), len(claims)


def occupancy_registry(absorption: list[dict[str, object]]) -> None:
    rows = []
    for item in absorption:
        year = int(item["year"])
        rows.append(
            {
                "occupancyEventId": f"LH-OCC-{item['absorptionId']}", "relatedEventId": item["absorptionId"],
                "geographyId": f"LH-{slug(str(item['district']))}", "geographyType": "cfd_nonspatial",
                "eventClass": "built_and_occupied_absorption", "eventTitle": f"{item['builtAndOccupiedUnits']} built-and-occupied units absorbed",
                "earliestDate": f"{year}-01-01", "latestDate": f"{year}-12-31", "datePrecision": "year",
                "homeCount": item["builtAndOccupiedUnits"], "habitabilityConclusion": "not_separately_established",
                "occupancyConclusion": "aggregate_built_and_occupied_count", "geometryId": "", "geometryStatus": "not_available",
                "sourceIds": item["sourceIds"], "statementClass": "documented_exact", "confidence": "high",
                "confidenceRationale": "Official County report explicitly defines absorption as built and occupied.",
                "limitations": item["limitations"], "reviewStatus": "bounded_nonspatial_cfd_record", "proximityEligible": "false",
            }
        )
    rows.extend(
        [
            {
                "occupancyEventId": "LH-OCC-M5-FIRST-OVERNIGHT", "relatedEventId": "LH-EVT-M5-005",
                "geographyId": "LH-VILLAGE-OAK-KNOLL", "geographyType": "village_nonspatial",
                "eventClass": "reported_overnight_occupancy", "eventTitle": "First reported Oak Knoll overnight stay",
                "earliestDate": "1999-11-30", "latestDate": "1999-11-30", "datePrecision": "day", "homeCount": 1,
                "habitabilityConclusion": "not_established", "occupancyConclusion": "reported_overnight_stay",
                "geometryId": "", "geometryStatus": "not_available", "sourceIds": "LH-SRC-LAT-FIRST-RESIDENT-1999",
                "statementClass": "documented_exact", "confidence": "medium",
                "confidenceRationale": "Contemporary report gives an exact overnight date but also reports no gas or electricity.",
                "limitations": "Conflicts with 1999-12-14 official retrospective; no address or certificate-of-occupancy record.",
                "reviewStatus": "conflict_retained_nonspatial", "proximityEligible": "false",
            }
        ]
    )
    upsert(BASE / "occupancy_event_registry.csv", rows, "occupancyEventId")


def imagery_evidence() -> int:
    captures = [
        (2005, "2005-06-07", "2005-06-07", "LH-SRC-CDFW-NAIP-2005"),
        (2009, "2009-06-18", "2009-06-22", "LH-SRC-CDFW-NAIP-2009"),
        (2010, "2010-05-01", "2010-05-01", "LH-SRC-CDFW-NAIP-2010"),
    ]
    manifest = {row["sourceId"]: row for row in read_csv(EVIDENCE / "acquisition_manifest.csv")}
    inventory = []
    coverage = []
    for year, earliest, latest, source_id in captures:
        source = manifest[source_id]
        inventory.append(
            {
                "id": f"LH-IMG-NAIP-{year}", "captureDateEarliest": earliest, "captureDateLatest": latest,
                "dateOnMap": str(year), "dateCurrent": str(year), "sourceName": f"California NAIP {year}",
                "sourceObjectId": "", "sourceIds": source_id,
                "flightOrProjectId": f"USDA-FSA-NAIP-{year}", "imageNumber": "four Ladera-intersecting source tiles",
                "scale": "", "groundResolution": "1 metre native; 3600x4000 archived service export",
                "colorMode": "natural color RGB JPEG", "coverage": "full current Ladera CDP and surrounding AOI",
                "coveragePctCurrentCdp": "100.00", "originalCrs": "EPSG:3857 service; EPSG:4326 export",
                "georeferencingStatus": "official orthorectified service export", "controlPoints": "not applicable",
                "transformationMethod": "ArcGIS ImageServer exportImage", "rmse": "not published",
                "processingHistory": "No pixel alteration; archived direct JPEG service export with request metadata and catalog.",
                "checksumSha256": source["checksumSha256"], "localPath": source["localFilePath"],
                "rightsLimitations": "Official public CDFW/USDA FSA service; source metadata retained.",
                "interpretiveLimitations": (
                    "Visible roofs, roads, disturbed soil, and landscaping do not by themselves establish permits, "
                    "legal completion, certificates of occupancy, or individual occupancy."
                ),
                "interpretationStatus": "reviewed_full_coverage_visual_observations_recorded",
                "confidence": "high", "notes": "Exact tile acquisition dates recovered from official raster catalog filenames.",
            }
        )
        coverage.append(
            {
                "year": year, "availableImageryIds": f"LH-IMG-NAIP-{year}", "coverageStatus": "full",
                "coveragePctCurrentCdp": "100.00", "interpretationEligibility": "visual_state_and_change_interpretation",
                "constructionPolygonStatus": "visible_disturbance_regions_not_proximity_eligible",
                "sourceIds": source_id, "publicSearchStatus": "official_CDFW_NAIP_service_retrieved",
                "limitations": "No precise active-construction polygon is asserted; broad visible disturbance cannot distinguish all active work from prepared or vacant pads.",
            }
        )
    upsert(BASE / "imagery_inventory.csv", inventory, "id")
    upsert(BASE / "imagery_coverage_matrix.csv", coverage, "year")

    visual_rows = [
        ("LH-IMGOBS-M5-2005-01", "LH-COMMUNITY-LADERA-RANCH", "developed_roof_and_street_pattern", "Dense roof, street, and landscaped-block patterns are visible across northern and central Ladera.", "2005-06-07", "2005-06-07", "LH-SRC-CDFW-NAIP-2005", "full community image; northern and central portions", "medium"),
        ("LH-IMGOBS-M5-2005-02", "LH-VILLAGE-COVENANT-HILLS", "broad_visible_land_disturbance", "The southernmost village area contains extensive light-toned disturbed ground, curvilinear roads, and prepared pads.", "2005-06-07", "2005-06-07", "LH-SRC-CDFW-NAIP-2005", "southern image region", "high"),
        ("LH-IMGOBS-M5-2005-03", "LH-VILLAGE-COVENANT-HILLS", "mixed_roofs_and_prepared_pads", "Southern development areas show a mixture of roofed structures, road infrastructure, and unroofed prepared pads.", "2005-06-07", "2005-06-07", "LH-SRC-CDFW-NAIP-2005", "southern image region", "high"),
        ("LH-IMGOBS-M5-2009-01", "LH-VILLAGE-COVENANT-HILLS", "roof_pattern_expansion", "By the 2009 capture, dense roof patterns occupy most production-neighborhood streets that appeared as disturbed or partly built areas in 2005.", "2009-06-18", "2009-06-22", "LH-SRC-CDFW-NAIP-2005;LH-SRC-CDFW-NAIP-2009", "side-by-side southern image comparison", "high"),
        ("LH-IMGOBS-M5-2009-02", "LH-CUSTOM-COVENANT-HILLS", "scattered_roofs_and_vacant_pads", "The southeastern custom-home street loops contain scattered roofs interspersed with numerous visibly vacant prepared lots.", "2009-06-18", "2009-06-22", "LH-SRC-CDFW-NAIP-2009", "southeastern custom-home image region", "high"),
        ("LH-IMGOBS-M5-2010-01", "LH-CUSTOM-COVENANT-HILLS", "scattered_roofs_and_vacant_pads", "The 2010 state continues to show scattered custom-home roofs and numerous vacant prepared lots in the southeastern loops.", "2010-05-01", "2010-05-01", "LH-SRC-CDFW-NAIP-2010", "southeastern custom-home image region", "high"),
        ("LH-IMGOBS-M5-2010-02", "LH-COMMUNITY-LADERA-RANCH", "no_broad_community_scale_earthwork_transition_visible", "No broad community-scale earthwork transition is apparent between the 2009 and 2010 full-coverage states; individual-lot changes may still be present.", "2009-06-18", "2010-05-01", "LH-SRC-CDFW-NAIP-2009;LH-SRC-CDFW-NAIP-2010", "side-by-side full image comparison", "medium"),
    ]
    observations = []
    claims = []
    convergence = []
    for observation_id, entity_id, observation_type, value, start, end, sources, locator, confidence in visual_rows:
        limitations = (
            "Visual classification only. It does not establish legal completion, habitability, occupancy, "
            "permit status, or continuous activity between capture dates."
        )
        observations.append(
            {
                "observationId": observation_id, "observedEntityId": entity_id,
                "observationType": observation_type, "observedValue": value,
                "dateStart": start, "dateEnd": end if end != start else "",
                "temporalPrecision": "date_range" if end != start else "day", "geometryId": "",
                "geometryType": "", "geometryStatus": "visual_region_not_digitized_for_proximity",
                "method": "manual side-by-side inspection of official full-resolution NAIP exports",
                "sourceIds": sources, "sourceLocator": locator, "statementClass": "visual_interpretation",
                "confidence": confidence, "limitations": limitations, "notes": "Mission 5 imagery review",
            }
        )
        claim_id = observation_id.replace("LH-IMGOBS", "LH-CLM-IMG")
        claims.append(
            {
                "claimId": claim_id, "subjectEntityId": entity_id, "claimType": observation_type,
                "claimText": value, "dateStart": start, "dateEnd": end if end != start else "",
                "temporalPrecision": "date_range" if end != start else "day", "claimScope": "imagery_visible_state",
                "supportingObservationIds": observation_id, "sourceIds": sources, "supportType": "visual_observation",
                "statementClass": "visual_interpretation", "confidence": confidence,
                "conflictStatus": "no_conflict_identified", "reviewStatus": "reviewed_mission5",
                "limitations": limitations, "notes": locator,
            }
        )
        convergence.append(
            {
                "claimId": claim_id, "supportingObservationCount": 1,
                "independentSourceOrganizationCount": 1, "primarySourceCount": 1,
                "contemporarySourceCount": 1, "visualSourceCount": len(split_ids(sources)),
                "conflictingObservationCount": 0, "geographicPrecision": "visual_region",
                "temporalPrecision": "date_range" if end != start else "day", "directness": "visual_observation",
                "sourceAuthority": "official_primary_imagery", "completeness": "claim_bounded",
                "finalConfidence": confidence,
                "confidenceRationale": "Official orthorectified imagery directly supports the bounded visible-state description.",
                "exhaustionStatus": "source_convergence_reached" if len(split_ids(sources)) > 1 else "authoritative_single_visual_source",
                "limitations": limitations,
            }
        )
    write_csv(BASE / "imagery_observations_mission5.csv", observations)
    upsert(BASE / "historical_observations.csv", observations, "observationId")
    upsert(BASE / "claim_registry.csv", claims, "claimId")
    upsert(BASE / "source_convergence.csv", convergence, "claimId")

    PUBLIC.mkdir(parents=True, exist_ok=True)
    for year, _, _, _ in captures:
        shutil.copy2(EVIDENCE / f"imagery/ladera_naip_{year}.jpg", PUBLIC / f"ladera_naip_{year}.jpg")
    return len(observations)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def imagery_supporting_records() -> None:
    source_manifest = {row["sourceId"]: row for row in read_csv(EVIDENCE / "acquisition_manifest.csv")}
    manifest_rows = []
    for year in (2005, 2009, 2010):
        source_id = f"LH-SRC-CDFW-NAIP-{year}"
        imagery_id = f"LH-IMG-NAIP-{year}"
        source = source_manifest[source_id]
        service = source["url"].rsplit("/exportImage", 1)[0]
        files = [
            ("jpeg_export", EVIDENCE / f"imagery/ladera_naip_{year}.jpg", source["url"]),
            ("export_metadata", EVIDENCE / f"imagery/ladera_naip_{year}_export.json", f"{service}/exportImage"),
            ("catalog_query", EVIDENCE / f"imagery/naip_{year}_ladera_catalog.json", f"{service}/query"),
            ("service_metadata", EVIDENCE / f"imagery/naip_{year}_service.json", service),
        ]
        for item_type, path, url in files:
            manifest_rows.append(
                {
                    "sourceId": source_id, "imageryId": imagery_id, "itemType": item_type, "url": url,
                    "localFilePath": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
                    "checksumSha256": sha256_file(path), "archiveStatus": "retrieved",
                    "retrievalDate": RETRIEVAL_DATE, "error": "",
                }
            )
    existing = [
        row for row in read_csv(BASE / "imagery_source_manifest.csv")
        if not row["imageryId"].startswith("LH-IMG-NAIP-")
    ]
    write_csv(BASE / "imagery_source_manifest.csv", existing + manifest_rows, list(existing[0]))

    review_rows = [
        {
            "interpretationId": "LH-IMG-REVIEW-M5-2005", "imageryId": "LH-IMG-NAIP-2005",
            "reviewDate": RETRIEVAL_DATE, "comparisonBeforeId": "LH-IMG-1997-1998", "comparisonAfterId": "LH-IMG-NAIP-2009",
            "observedState": "northern_and_central_roof_patterns_with_southern_disturbance_and_mixed_prepared_pads",
            "interpretationMethod": "full-resolution visual review plus southern-region crop comparison",
            "geometryId": "", "proximityEligible": "false", "sourceIds": "LH-SRC-CDFW-NAIP-2005",
            "confidence": "high", "limitations": "Visible disturbance is not classified as a precise active-construction footprint and is not proximity eligible.",
            "reviewStatus": "reviewed_mission5",
        },
        {
            "interpretationId": "LH-IMG-REVIEW-M5-2009", "imageryId": "LH-IMG-NAIP-2009",
            "reviewDate": RETRIEVAL_DATE, "comparisonBeforeId": "LH-IMG-NAIP-2005", "comparisonAfterId": "LH-IMG-NAIP-2010",
            "observedState": "production_neighborhood_roof_pattern_expansion_with_custom_area_vacant_pads",
            "interpretationMethod": "full-resolution side-by-side visual review",
            "geometryId": "", "proximityEligible": "false", "sourceIds": "LH-SRC-CDFW-NAIP-2005;LH-SRC-CDFW-NAIP-2009",
            "confidence": "high", "limitations": "Change is bounded between captures; no continuous activity or individual completion date is inferred.",
            "reviewStatus": "reviewed_mission5",
        },
        {
            "interpretationId": "LH-IMG-REVIEW-M5-2010", "imageryId": "LH-IMG-NAIP-2010",
            "reviewDate": RETRIEVAL_DATE, "comparisonBeforeId": "LH-IMG-NAIP-2009", "comparisonAfterId": "",
            "observedState": "custom_area_scattered_roofs_and_vacant_pads_without_broad_community_transition",
            "interpretationMethod": "full-resolution side-by-side visual review",
            "geometryId": "", "proximityEligible": "false", "sourceIds": "LH-SRC-CDFW-NAIP-2009;LH-SRC-CDFW-NAIP-2010",
            "confidence": "medium", "limitations": "Individual-lot change may exist; no broad active-construction polygon is asserted.",
            "reviewStatus": "reviewed_mission5",
        },
    ]
    upsert(BASE / "construction_interpretation_log.csv", review_rows, "interpretationId")


def construction_and_roads(street_rows: list[dict[str, object]]) -> tuple[int, int]:
    activities = [
        {
            "constructionActivityId": "LH-CONSTRUCTION-M5-COVENANT-2005",
            "activityClass": "imagery_visible_development_state", "canonicalName": "Covenant Hills visible disturbed ground, roads, prepared pads, and roofs",
            "relatedTractIds": "", "relatedNeighborhoodIds": "LH-VILLAGE-COVENANT-HILLS", "relatedPlanningAreaIds": "",
            "relatedBuilderIds": "", "geometryId": "", "geometryMethod": "visual_region_not_digitized",
            "geometrySource": "LH-IMG-NAIP-2005", "earliestStart": "2005-06-07", "latestStart": "2005-06-07",
            "earliestEnd": "", "latestEnd": "", "datePrecision": "day", "lifecycleState": "visible_mixed_development_state",
            "intensityClass": "not_quantified", "evidenceIds": "LH-IMGOBS-M5-2005-02;LH-IMGOBS-M5-2005-03",
            "sourceIds": "LH-SRC-CDFW-NAIP-2005", "confidence": "high",
            "confidenceRationale": "Official imagery directly shows the bounded visible state on the capture date.",
            "limitations": "Broad disturbed ground and prepared pads are not assumed to be continuously active construction.",
            "reviewStatus": "bounded_visual_state_not_proximity_eligible", "version": "3.0", "proximityEligible": "false",
        },
        {
            "constructionActivityId": "LH-CONSTRUCTION-M5-COVENANT-2005-2009-CHANGE",
            "activityClass": "imagery_visible_development_change", "canonicalName": "Covenant Hills production-neighborhood roof-pattern expansion",
            "relatedTractIds": "", "relatedNeighborhoodIds": "LH-VILLAGE-COVENANT-HILLS", "relatedPlanningAreaIds": "",
            "relatedBuilderIds": "", "geometryId": "", "geometryMethod": "visual_region_not_digitized",
            "geometrySource": "LH-IMG-NAIP-2005;LH-IMG-NAIP-2009", "earliestStart": "2005-06-07", "latestStart": "2009-06-22",
            "earliestEnd": "", "latestEnd": "", "datePrecision": "range", "lifecycleState": "visible_change_between_captures",
            "intensityClass": "not_quantified", "evidenceIds": "LH-IMGOBS-M5-2009-01",
            "sourceIds": "LH-SRC-CDFW-NAIP-2005;LH-SRC-CDFW-NAIP-2009", "confidence": "high",
            "confidenceRationale": "Official before-and-after imagery supports roof-pattern change within the bounded interval.",
            "limitations": "No exact construction start, completion date, or active footprint is inferred within the interval.",
            "reviewStatus": "bounded_visual_change_not_proximity_eligible", "version": "3.0", "proximityEligible": "false",
        },
        {
            "constructionActivityId": "LH-CONSTRUCTION-M5-CROWN-VALLEY-2008",
            "activityClass": "road_widening_reported_ongoing", "canonicalName": "Crown Valley Parkway widening",
            "relatedTractIds": "", "relatedNeighborhoodIds": "", "relatedPlanningAreaIds": "", "relatedBuilderIds": "",
            "geometryId": "", "geometryMethod": "historical_geometry_not_retrieved", "geometrySource": "",
            "earliestStart": "2008-05-12", "latestStart": "2008-05-12", "earliestEnd": "", "latestEnd": "",
            "datePrecision": "day", "lifecycleState": "reported_ongoing_on_document_date", "intensityClass": "not_quantified",
            "evidenceIds": "LH-EVT-M5-006", "sourceIds": "LH-SRC-OC-TRANSPORT-2008", "confidence": "medium",
            "confidenceRationale": "The dated community survey packet repeatedly describes the widening as incomplete and ongoing.",
            "limitations": "The report date is an observation date, not the construction start; current centerlines are not historical work geometry.",
            "reviewStatus": "bounded_nonspatial_report", "version": "3.0", "proximityEligible": "false",
        },
    ]
    upsert(BASE / "construction_activity_registry.csv", activities, "constructionActivityId")

    event = {
        "id": "LH-EVT-M5-006", "dateStart": "2008-05-12", "dateEnd": "", "temporalPrecision": "day",
        "eventType": "road_construction_status", "title": "Crown Valley Parkway widening reported incomplete and ongoing",
        "placeName": "Crown Valley Parkway", "featureId": "LH-ROAD-CROWN-VALLEY-PKWY", "status": "reported_ongoing",
        "statementClass": "documented_exact", "confidence": "medium", "sourceIds": "LH-SRC-OC-TRANSPORT-2008",
        "sourceLocator": "Transportation survey packet pages 1-2 and comment summary",
        "interpretationMethod": "direct transcription of dated status reporting", "conflictNotes": "",
        "notes": "Observation date only; exact construction start, end, and historical work geometry are unresolved.",
    }
    upsert(BASE / "events.csv", [event], "id")
    road_rows = [
        {
            "roadChronologyId": "LH-ROAD-M5-CROWN-VALLEY-2008", "roadName": "Crown Valley Parkway",
            "observedDate": "2008-05-12", "observedState": "widening_reported_incomplete_and_ongoing",
            "sourceIds": "LH-SRC-OC-TRANSPORT-2008", "confidence": "medium",
            "limitations": "Dated status observation only; start, completion, acceptance, and work limits are not established.",
        },
        {
            "roadChronologyId": "LH-ROAD-M5-OSO-WALKWAY-2008", "roadName": "Oso Grande to Covenant Hills Clubhouse walkway",
            "observedDate": "2008-05-12", "observedState": "recently_approved_by_LARMAC_as_reported",
            "sourceIds": "LH-SRC-OC-TRANSPORT-2008", "confidence": "medium",
            "limitations": "Approval is reported as recent; exact approval, construction, and opening dates were not published.",
        },
    ]
    write_csv(BASE / "road_chronology_mission5.csv", road_rows)

    street_data = json.loads((EVIDENCE / "gis/oc_street_centerlines_ladera.json").read_text())
    official_names = {str(row["streetNameNormalized"]) for row in street_rows}
    counts: Counter[str] = Counter()
    display: dict[str, str] = {}
    for feature in street_data["features"]:
        attrs = feature["attributes"]
        name = " ".join(str(attrs.get(field) or "").strip() for field in ("PREFIX", "STREETNAME", "SUFFIX")).strip()
        normalized = normalize_street(name)
        if normalized in official_names:
            counts[normalized] += 1
            display[normalized] = name
    current_rows = []
    for index, normalized in enumerate(sorted(counts), start=1):
        villages = sorted({str(row["village"]) for row in street_rows if row["streetNameNormalized"] == normalized})
        current_rows.append(
            {
                "currentRoadId": f"LH-CURRENT-ROAD-{index:04d}", "roadName": display[normalized],
                "streetNameNormalized": normalized, "currentCenterlineSegmentCount": counts[normalized],
                "currentVillageDirectoryAssociations": ";".join(villages), "validAt": RETRIEVAL_DATE,
                "sourceIds": "LH-SRC-OC-STREET-CENTERLINES;LH-SRC-LARMAC-STREETS-2019",
                "confidence": "high", "limitations": "Current geometry and 2019 naming only; no historical opening or County-acceptance date is inferred.",
            }
        )
    write_csv(BASE / "current_road_registry_mission5.csv", current_rows)
    return len(activities), len(current_rows)


def lifecycle_additions(absorption: list[dict[str, object]]) -> int:
    rows = []
    for item in absorption:
        year = int(item["year"])
        rows.append(
            {
                "intervalId": f"LH-LIFE-{item['absorptionId']}",
                "entityId": f"LH-{slug(str(item['district']))}", "stateDimension": "built_and_occupied_absorption",
                "stateValue": str(item["builtAndOccupiedUnits"]), "validFrom": f"{year}-01-01", "validTo": f"{year}-12-31",
                "startBoundType": "calendar_year_start", "endBoundType": "calendar_year_end", "temporalPrecision": "year",
                "geometryId": "", "geometryStatus": "nonspatial_cfd_aggregate", "sourceIds": item["sourceIds"],
                "supportingClaimIds": f"LH-CLM-{item['absorptionId']}", "statementClass": "documented_exact",
                "confidence": "high", "proximityEligible": "false", "limitations": item["limitations"],
                "notes": item["definition"],
            }
        )
    upsert(BASE / "lifecycle_intervals.csv", rows, "intervalId")
    return len(rows)


def archive_text_extractions() -> int:
    output_dir = EVIDENCE / "text"
    output_dir.mkdir(parents=True, exist_ok=True)
    log_rows = []
    for item in read_csv(EVIDENCE / "acquisition_manifest.csv"):
        path = ROOT / item["localFilePath"]
        if path.suffix.lower() not in {".pdf", ".html"}:
            continue
        output = output_dir / f"{path.stem}.txt"
        try:
            if path.suffix.lower() == ".pdf":
                with pdfplumber.open(path) as pdf:
                    pages = [page.extract_text(x_tolerance=2, y_tolerance=3) or "" for page in pdf.pages]
                text_value = "\n\n".join(pages)
                method = "pdfplumber_embedded_text_extraction"
                page_count = len(pages)
            else:
                parser = TextParser()
                parser.feed(path.read_text(encoding="utf-8", errors="replace"))
                text_value = "\n".join(parser.parts)
                method = "html_parser_visible_text_extraction"
                page_count = 0
            write_text(output, text_value.strip() + "\n")
            status = "extracted" if text_value.strip() else "no_embedded_text"
            error = ""
        except Exception as exc:  # preserve a reproducible failure record without stopping other extraction
            text_value = ""
            method = "failed"
            page_count = 0
            status = "failed"
            error = str(exc)
        log_rows.append(
            {
                "sourceId": item["sourceId"], "inputFile": item["localFilePath"],
                "outputFile": str(output.relative_to(ROOT)) if output.exists() else "",
                "method": method, "ocrUsed": "false", "pageCount": page_count,
                "characterCount": len(text_value), "outputChecksumSha256": sha256_file(output) if output.exists() else "",
                "status": status, "extractionDate": RETRIEVAL_DATE, "error": error,
                "limitations": "Text extraction preserves discoverable text but is not a substitute for visual table and image review.",
            }
        )
    write_csv(EVIDENCE / "extraction_log.csv", log_rows)
    return len(log_rows)


def update_unresolved_questions() -> None:
    path = BASE / "unresolved_questions.csv"
    rows = read_csv(path)
    updates = {
        "LH-TODO-003": (
            "partially_answered_current_geography_and_product_candidates",
            "Use the Mission 5 address/tract crosswalk and County product tables as candidates; obtain tract-keyed historical permit or final-map records for legal confirmation.",
        ),
        "LH-TODO-005": (
            "partially_answered_cfd_aggregate_only",
            "Use County built-and-occupied absorption only at CFD aggregate scale; obtain certificates of occupancy or assessor improvements for tract/address geometry.",
        ),
        "LH-TODO-006": (
            "partially_answered_2008_status_and_current_geometry_only",
            "Request improvement-plan acceptance resolutions and maintenance logs; do not date roads from current centerlines.",
        ),
        "LH-TODO-008": (
            "partially_answered_2005_2009_2010_full_coverage",
            "Request or license full-coverage 1999-2004 and 2006-2008 frames; preserve official flight metadata.",
        ),
        "LH-TODO-010": (
            "partially_answered_opening_milestones_only",
            "Request LARMAC board packets and recorded common-area plats for exact facility dates and historical footprints.",
        ),
        "LH-TODO-011": (
            "partially_answered_2006_status_snapshot",
            "Use the CFD 2002-1 table for the 2006-12-31 status only; obtain permits, tenant announcements, and assessor records for openings and footprints.",
        ),
        "LH-TODO-013": (
            "partially_answered_product_level_builder_tables",
            "Retain County-over-secondary conflict resolutions; obtain tract-keyed builder filings and brochures for exact tract assignment.",
        ),
        "LH-TODO-014": (
            "partially_answered_production_products_custom_lots_unresolved",
            "Treat full Phase VI production permit and escrow counts by 2011 as an upper bound only; obtain custom-lot final permits and assessor years.",
        ),
    }
    for row in rows:
        if row["id"] in updates:
            row["status"], row["nextAction"] = updates[row["id"]]
    write_csv(path, rows, list(rows[0]))


def research_logs_and_queue() -> None:
    dead_ends = [
        {
            "deadEndId": "LH-DEADEND-M5-001", "avenue": "Orange County public tentative-map services",
            "searchDate": RETRIEVAL_DATE, "result": "Publicly exposed service coverage located was post-development-era and did not supply the 1997-2010 tentative-map chronology.",
            "impact": "Tentative approvals remain unresolved.", "nextAction": "Request historical planning case files and Board records by tract number.",
        },
        {
            "deadEndId": "LH-DEADEND-M5-002", "avenue": "Legacy LaderaLife number-of-homes route",
            "searchDate": RETRIEVAL_DATE, "result": "Legacy route returned no usable page; current official village pages and the archived 2019 street directory replaced it for current names only.",
            "impact": "No historical opening dates recovered from the route.", "nextAction": "Use archived brochures or LARMAC board packets.",
        },
        {
            "deadEndId": "LH-DEADEND-M5-003", "avenue": "Public annual aerial coverage",
            "searchDate": RETRIEVAL_DATE, "result": "Full official 2005, 2009, and 2010 states were recovered; public full-coverage annual states for 1999-2004 and 2006-2008 were not located in the reviewed services.",
            "impact": "Annual construction geometry cannot be reconstructed.", "nextAction": "Request County flight frames or license commercial historical imagery.",
        },
        {
            "deadEndId": "LH-DEADEND-M5-004", "avenue": "Public historical CUSD attendance boundaries",
            "searchDate": RETRIEVAL_DATE, "result": "Opening and administrative project records were available, but dated attendance-area polygons were not located publicly.",
            "impact": "Historical school assignment remains blocked.", "nextAction": "Submit a district records request for annual boundary maps and Board actions.",
        },
        {
            "deadEndId": "LH-DEADEND-M5-005", "avenue": "Public address-level grading, building, and occupancy ledgers",
            "searchDate": RETRIEVAL_DATE, "result": "No complete downloadable development-era permit, grading-closeout, or certificate-of-occupancy ledger was located.",
            "impact": "Tract/address construction and occupancy geometry remains blocked.", "nextAction": "Request County permit index exports and scanned case files.",
        },
    ]
    write_csv(BASE / "dead_end_log_mission5.csv", dead_ends)
    queue = [
        (1, "County permit and occupancy index", "tract_lifecycle;occupancy_geometry;construction_geometry", "Building permits, grading permits, inspection closeouts, certificates of occupancy, assessor improvement years", "Orange County Planning/Public Works records request", "critical"),
        (2, "Historical aerial gap fill", "historical_imagery;construction_geometry", "Full-coverage 1999-2004 and 2006-2008 frames with flight metadata", "OC Survey, USGS/EarthExplorer, USDA, or licensed imagery", "critical"),
        (3, "Historical planning crosswalk", "tract_hierarchy", "Planning-area/village maps, tract-keyed final-map files, improvement agreements", "Orange County Clerk of the Board and Development Services", "high"),
        (4, "Historical school boundaries", "school_boundaries", "Annual attendance maps and adoption actions for 1997-2010", "Capistrano Unified School District records request", "high"),
        (5, "Road and utility acceptance", "roads;haul_routes", "Improvement-plan acceptance, maintenance, traffic-control, and approved haul-route records", "Orange County Public Works and SMWD", "high"),
        (6, "Facility and commercial openings", "parks_facilities;commercial", "Board packets, leases, tenant announcements, permits, and historical footprints", "LARMAC, County, Recorder, developer archives", "medium"),
        (7, "Custom-lot completion", "tract_lifecycle", "Final permits and assessor years for Covenant Hills custom lots after 2010", "County building and assessor records", "medium"),
    ]
    rows = [
        {
            "rank": rank, "researchTarget": target, "gapTopics": topics, "evidenceNeeded": needed,
            "recommendedRepository": repository, "priority": priority, "publicSearchStatus": "public_avenues_exhausted_or_diminishing_returns",
            "manualRecordRequired": "true", "reasonForRank": "Unlocks the largest remaining chronological or spatial evidence gap.",
        }
        for rank, target, topics, needed, repository, priority in queue
    ]
    write_csv(BASE / "highest_value_research_queue.csv", rows)


def research_gaps(crosswalk: list[dict[str, object]]) -> None:
    existing = read_csv(BASE / "research_gaps.csv")
    for row in existing:
        if row["topic"] == "tract_hierarchy":
            row.update(
                {
                    "searchOrAccessStatus": "partially_reduced_by_public_current_crosswalk",
                    "analyticalImpact": "Current neighborhood and village associations now cover matched leaf tracts; historical legal assignment and lifecycle dates remain unresolved.",
                    "recommendedFollowUp": "Obtain subdivision improvement, building-permit, and certificate-of-occupancy records keyed by tract/address.",
                    "reviewStatus": "partially_resolved_mission5",
                }
            )
        elif row["topic"] == "historical_imagery":
            row.update(
                {
                    "searchOrAccessStatus": "public_full_coverage_found_2005_2009_2010_other_years_unresolved",
                    "analyticalImpact": "Three development-era full-coverage aerial states now support visible-change interpretation; annual 1999-2004 and 2006-2008 states remain missing.",
                    "recommendedFollowUp": "Request County/Eagle/USGS frames for missing years and archive acquisition metadata.",
                    "reviewStatus": "partially_resolved_mission5",
                }
            )
        elif row["topic"] in {"occupancy_geometry", "construction_geometry"}:
            row["searchOrAccessStatus"] = "aggregate_public_evidence_added_manual_address_level_records_still_required"
            row["reviewStatus"] = "partially_reduced_but_still_blocking"
        elif row["topic"] == "tract_lifecycle":
            row.update(
                {
                    "searchOrAccessStatus": "public_recording_current_crosswalk_and_product_snapshots_added_manual_permit_records_required",
                    "analyticalImpact": "All 123 legal recording dates remain intact; 116 tracts gain current neighborhood candidates and 97 gain product candidates, but physical lifecycle remains unresolved.",
                    "recommendedFollowUp": "Request grading, building, inspection-closeout, certificate-of-occupancy, and assessor records by tract and address.",
                    "reviewStatus": "partially_reduced_but_still_blocking",
                }
            )
        elif row["topic"] == "school_boundaries":
            row.update(
                {
                    "searchOrAccessStatus": "public_opening_and_project_records_exhausted_historical_boundaries_require_district_request",
                    "analyticalImpact": "School opening chronology is supported, but annual attendance assignment remains unknown.",
                    "recommendedFollowUp": "Request 1997-2010 attendance-area maps and adoption actions from CUSD.",
                    "reviewStatus": "manual_record_blocker_preserved",
                }
            )
        elif row["topic"] == "roads":
            row.update(
                {
                    "searchOrAccessStatus": "current_centerlines_and_2008_status_found_historical_acceptance_records_manual",
                    "analyticalImpact": "Current road names/geometries and one dated widening status are available; annual road opening states remain unknown.",
                    "recommendedFollowUp": "Request improvement-plan acceptance resolutions and maintenance logs by tract and street.",
                    "reviewStatus": "partially_resolved_mission5",
                }
            )
        elif row["topic"] == "haul_routes":
            row["searchOrAccessStatus"] = "not_located_publicly_manual_grading_plan_request_required"
            row["reviewStatus"] = "manual_record_blocker_preserved"
        elif row["topic"] == "parks_facilities":
            row.update(
                {
                    "searchOrAccessStatus": "official_retrospective_opening_milestones_available_exact_boundaries_and_construction_records_manual",
                    "analyticalImpact": "Named opening milestones exist, but construction windows and historical footprints remain unresolved.",
                    "recommendedFollowUp": "Request LARMAC board packets, original brochures, and recorded common-area plats.",
                    "reviewStatus": "partially_resolved_mission5",
                }
            )
        elif row["topic"] == "commercial":
            row.update(
                {
                    "searchOrAccessStatus": "official_2006_asset_status_snapshot_found_opening_dates_and_footprints_manual",
                    "analyticalImpact": "Eight UAC residential/commercial assets now have exact 2006-12-31 status and quantity snapshots; openings and historical footprints remain unresolved.",
                    "recommendedFollowUp": "Obtain tenant permits, leases, assessor records, and historical parcel/site plans.",
                    "reviewStatus": "partially_resolved_mission5",
                }
            )
    write_csv(BASE / "research_gaps.csv", existing, list(existing[0]))


def main() -> int:
    source_count = source_registry()
    streets = parse_street_directory()
    neighborhood_phases = parse_village_directory()
    products, conflicts = builder_products()
    neighborhoods = neighborhood_chronology(neighborhood_phases, products)
    absorption = absorption_chronology()
    points, crosswalk = tract_neighborhood_crosswalk(streets)
    tracts = tract_lifecycle(crosswalk, products)
    observation_count, claim_count = mission5_events_and_evidence(absorption)
    occupancy_registry(absorption)
    product_claim_count = product_evidence(products)
    commercial_assets, commercial_claim_count = commercial_chronology()
    imagery_observation_count = imagery_evidence()
    imagery_supporting_records()
    construction_count, current_road_count = construction_and_roads(streets)
    lifecycle_count = lifecycle_additions(absorption)
    extraction_count = archive_text_extractions()
    research_gaps(crosswalk)
    update_unresolved_questions()
    research_logs_and_queue()
    summary = {
        "version": "Mission 5",
        "generated": RETRIEVAL_DATE,
        "registeredSources": source_count,
        "streetDirectoryRows": len(streets),
        "neighborhoodPhaseRows": len(neighborhood_phases),
        "neighborhoodChronologyRows": len(neighborhoods),
        "builderProducts": len(products),
        "builderConflicts": len(conflicts),
        "absorptionRows": len(absorption),
        "matchedAddressPointRows": len(points),
        "tractNeighborhoodRelationships": len(crosswalk),
        "tractLifecycleRows": len(tracts),
        "newObservations": observation_count,
        "newClaims": claim_count + product_claim_count + commercial_claim_count + imagery_observation_count,
        "builderProductSnapshotClaims": product_claim_count,
        "commercialAssetSnapshots": len(commercial_assets),
        "imageryObservations": imagery_observation_count,
        "constructionStatusRecords": construction_count,
        "currentRoadRegistryRows": current_road_count,
        "newLifecycleIntervals": lifecycle_count,
        "textExtractions": extraction_count,
        "safeguard": "Aggregate, current, or legal-map evidence is not promoted to address-level historical construction, habitability, or occupancy geometry.",
    }
    write_json(DATA / "mission5_summary.json", summary)
    write_json(PUBLIC / "mission5_summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
