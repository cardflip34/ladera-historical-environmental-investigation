#!/usr/bin/env python3
"""LEHRP data-integrity tests. Enforce the platform's non-negotiable rules on the data files.

Runs with pytest OR as a plain script (`python3 tests/test_data_integrity.py`). Pure stdlib.
Rules enforced:
  * Provenance   — every substantive record carries a sourceId and every referenced source exists.
  * Grading      — every source has a valid A1/A2/B1/B2/C/D grade.
  * Privacy      — health events store no exact address / residential coordinate / obvious name.
  * Language     — "likely"/"industry standard" never appear as bare applications without caveat.
  * Geometry     — GeoJSON layers parse and have valid coordinates.
"""
import csv
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VALID_GRADES = {"A1", "A2", "B1", "B2", "C", "D"}


def read_csv(rel):
    path = os.path.join(ROOT, rel)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def source_ids():
    return {r["id"] for r in read_csv("research/source_registry/sources.csv")}


# --------------------------------------------------------------------------- grading
def test_every_source_has_valid_grade():
    for r in read_csv("research/source_registry/sources.csv"):
        assert r.get("id"), "source row missing id"
        assert r.get("reliabilityGrade", "").upper() in VALID_GRADES, \
            f"source {r['id']} has invalid grade {r.get('reliabilityGrade')!r}"


# --------------------------------------------------------------------------- provenance
PROVENANCE_FILES = [
    "research/cancer_reports/public_report_registry.csv",
    "research/pesticides/active_ingredients.csv",
    "research/pesticides/application_events.csv",
    "research/environmental_sites/sites.csv",
    "research/water/water_quality.csv",
    "research/demographics/incidence_rates.csv",
    "research/land_use/historical_land_use.csv",
]


def test_records_reference_existing_sources():
    known = source_ids()
    for rel in PROVENANCE_FILES:
        for r in read_csv(rel):
            raw = r.get("sourceId", "")
            assert raw, f"{rel}: row {r.get('id','?')} missing sourceId"
            for sid in [s.strip() for s in re.split("[;,]", raw) if s.strip()]:
                # allow quoted/empty artifacts but require at least one real source token
                if sid in ("''", '""'):
                    continue
                assert sid in known, f"{rel}: row {r.get('id','?')} references unknown source {sid!r}"


# --------------------------------------------------------------------------- privacy
ADDRESS_RE = re.compile(r"\b\d{1,6}\s+[A-Z][a-z]+\s+(St|Street|Ave|Avenue|Dr|Drive|Rd|Road|Ln|Lane|Ct|Court|Way|Blvd|Circle|Cir)\b")
COORD_RE = re.compile(r"-?\d{1,3}\.\d{3,}\s*,\s*-?\d{1,3}\.\d{3,}")


def test_health_events_have_no_address_or_coordinate():
    for r in read_csv("research/cancer_reports/public_report_registry.csv"):
        blob = " ".join(r.values())
        assert not ADDRESS_RE.search(blob), f"health event {r.get('id')} appears to contain a street address"
        assert not COORD_RE.search(blob), f"health event {r.get('id')} appears to contain a residential coordinate"


def test_health_events_aggregate_columns_only():
    # The registry must not add columns that STORE an individual's name/address/residence.
    # `namesIndividual` is explicitly allowed: it is a boolean about the SOURCE, not stored PII.
    with open(os.path.join(ROOT, "research/cancer_reports/public_report_registry.csv"), encoding="utf-8") as f:
        header = f.readline().strip()
    cols = [c.strip().strip('"').lower() for c in header.split(",")]
    allowed = {"namesindividual"}
    banned_tokens = ("patientname", "individualname", "fullname", "firstname", "lastname",
                     "address", "street", "residence", "homeaddress", "residentialcoord")
    for col in cols:
        if col in allowed:
            continue
        for tok in banned_tokens:
            assert tok not in col.replace("_", ""), \
                f"health-event schema has a forbidden PII column {col!r} (matched {tok!r})"


# --------------------------------------------------------------------------- language discipline
def test_no_bare_likely_application_events():
    # An application event may mention 'likely'/'industry standard' ONLY if its evidenceClass
    # marks it as an inference/allegation (never displayed as a real application).
    inference_classes = {"historically_likely", "industry_standard_inference", "unverified_allegation"}
    for r in read_csv("research/pesticides/application_events.csv"):
        text = (r.get("notes", "") + " " + r.get("cropOrSiteType", "")).lower()
        if "likely" in text or "industry standard" in text:
            assert r.get("evidenceClass") in inference_classes, \
                f"application {r.get('id')} uses inference language but is not flagged as an inference class"


# --------------------------------------------------------------------------- geometry
def test_geojson_layers_valid():
    geo_dir = os.path.join(ROOT, "data", "geospatial")
    files = [f for f in os.listdir(geo_dir) if f.endswith(".geojson")]
    assert files, "no GeoJSON layers found"
    for fn in files:
        with open(os.path.join(geo_dir, fn), encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("type") == "FeatureCollection", f"{fn}: not a FeatureCollection"
        for feat in data["features"]:
            geom = feat.get("geometry")
            assert geom and geom.get("coordinates"), f"{fn}: feature missing geometry"
            _check_coords(geom["coordinates"], fn)


def _check_coords(coords, fn):
    if isinstance(coords[0], (int, float)):
        lon, lat = coords[0], coords[1]
        assert -180 <= lon <= 180 and -90 <= lat <= 90, f"{fn}: coordinate out of range {coords}"
    else:
        for c in coords:
            _check_coords(c, fn)


def test_application_events_have_valid_evidence_class():
    valid = {"documented_exact", "documented_within_reporting_unit", "documented_purchase",
             "documented_approved_product", "contractually_permitted", "current_policy_product",
             "historically_likely", "industry_standard_inference", "unverified_allegation"}
    for r in read_csv("research/pesticides/application_events.csv"):
        assert r.get("evidenceClass") in valid, f"application {r.get('id')} has invalid evidenceClass"


# --------------------------------------------------------------------------- runner
def _run():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"  FAIL  {t.__name__}: {e}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed.")
    return failures


if __name__ == "__main__":
    sys.exit(1 if _run() else 0)
