#!/usr/bin/env python3
"""
LHDRS Mission 6 — generate the six local appendices required before any records request.

Reproducible: reads only committed repository data + the verified Mission 6 captures.
Creates nothing that is not traceable to a source. Where a requested field does not exist in
the repository (notably APN), the appendix records the absence explicitly rather than inventing
or inferring a value.

Outputs -> data/development/mission6_appendices/
    appendix_A_canonical_tracts.csv
    appendix_B_address_crosswalk.csv
    appendix_C_aoi.geojson  (+ appendix_C_aoi_summary.json)
    appendix_D_street_tract_crosswalk.csv
    appendix_E_known_identifiers.csv
    appendix_F_party_name_variants.csv
    APPENDICES_README.md

Usage:  python3 scripts/lhdrs_mission6_appendices.py
"""
from __future__ import annotations
import csv, json, os, sys, collections, datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DC   = os.path.join(REPO, "research/development_chronology")
DEV  = os.path.join(REPO, "data/development")
M6   = os.path.join(REPO, "evidence/lhdrs/mission6")
OUT  = os.path.join(DEV, "mission6_appendices")
GENERATED = datetime.date.today().isoformat()

# ---------------------------------------------------------------------------
# Decisions carried forward from Mission 5 / Mission 6 recommendation.
# These are POLICY, applied consistently and stated in the output.
# ---------------------------------------------------------------------------
TR_17588_DECISION = "exclude"   # 2024 Board index says Ladera Ranch; live FeatureServer says
                                # Rancho Mission Viejo. Conflict preserved; excluded from Ladera
                                # counts unless the canonical crosswalk independently includes it.
MULTI_DATE_TRACTS = {"15615", "16116", "16121"}  # never collapse to a single completion date

def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def write_csv(name, rows, cols):
    p = os.path.join(OUT, name)
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})
    print(f"  {name}: {len(rows)} rows")
    return len(rows)

os.makedirs(OUT, exist_ok=True)
stats = {}
print("Mission 6 appendices")

# ---------------------------------------------------------------------------
# APPENDIX A — canonical tract list + aliases
# ---------------------------------------------------------------------------
print("\nA. canonical tract list")
tracts = read_csv(os.path.join(DEV, "tract_maps.csv"))
xwalk  = read_csv(os.path.join(DC,  "tract_crosswalk.csv"))

# alias/lineage from the documented crosswalk
lineage = collections.defaultdict(set)
for r in xwalk:
    a, b, rel = r["fromTractNumber"], r["toTractNumber"], r["relationshipType"]
    if a and b:
        lineage[a].add(f"{rel}:{b}")
        lineage[b].add(f"{rel}:{a}")

rows_a = []
for t in tracts:
    tn = (t.get("tractNumber") or "").strip()
    rows_a.append({
        "tractNumber": tn,
        "tractId": f"LH-TRACT-{tn}",
        "bookPage": t.get("bookPage", ""),
        "recordDate": t.get("recordDate", ""),
        "recordYear": t.get("recordYear", ""),
        "jurisdiction": t.get("jurisdiction", ""),
        "engineeringCompany": t.get("engineeringCompany", ""),
        "aliasesAndLineage": "; ".join(sorted(lineage.get(tn, []))) or "none documented",
        "multiDateAcceptance": "YES - do not collapse to one completion date" if tn in MULTI_DATE_TRACTS else "",
        "inLaderaCanonicalSet": "yes",
        "sourceId": t.get("sourceId", ""),
        "limitations": t.get("knownLimitations", ""),
    })

# TR 17588 recorded explicitly as an excluded, conflicted row
rows_a.append({
    "tractNumber": "17588", "tractId": "LH-TRACT-17588", "bookPage": "", "recordDate": "",
    "recordYear": "", "jurisdiction": "UNINCORPORATED", "engineeringCompany": "",
    "aliasesAndLineage": "CONFLICT: 2024 Board-certified road index labels Ambito Street / TR 17588 "
                         "as Ladera Ranch; live OC FeatureServer labels the same feature Rancho Mission Viejo",
    "multiDateAcceptance": "",
    "inLaderaCanonicalSet": "NO - excluded pending independent confirmation",
    "sourceId": "LH-SRC-M6-LHDRS-ROAD-INDEX-2024; LH-SRC-M6-OC-ROAD-INDEX-TR17588-LIVE",
    "limitations": "Both source versions preserved. Do not include in Ladera counts unless the "
                   "canonical tract/AOI crosswalk independently includes it.",
})
stats["A_tracts_canonical"] = len(tracts)
stats["A_rows_total"] = write_csv("appendix_A_canonical_tracts.csv", rows_a,
    ["tractNumber","tractId","bookPage","recordDate","recordYear","jurisdiction",
     "engineeringCompany","aliasesAndLineage","multiDateAcceptance","inLaderaCanonicalSet",
     "sourceId","limitations"])

# ---------------------------------------------------------------------------
# APPENDIX B — address crosswalk (deduplicated).  NOTE: no APN in repository.
# ---------------------------------------------------------------------------
print("\nB. address crosswalk (APN absent from repository - disclosed)")
addrs = read_csv(os.path.join(DC, "address_neighborhood_tract_points.csv"))
seen, rows_b = set(), []
for a in addrs:
    addr = " ".join((a.get("address") or "").split())  # collapse padding whitespace
    key = (addr, a.get("leafTractId", ""))
    if not addr or key in seen:
        continue
    seen.add(key)
    leaf = (a.get("leafTractId") or "").replace("LH-TRACT-", "")
    rows_b.append({
        "address": addr,
        "addressPointId": a.get("addressPointId", ""),
        "apn": "",  # deliberately empty: no APN data exists in this repository
        "apnStatus": "NOT_IN_REPOSITORY - request APN from County; do not infer",
        "leafTractNumber": leaf,
        "allContainingTractIds": a.get("allContainingTractIds", ""),
        "streetNameNormalized": a.get("streetNameNormalized", ""),
        "neighborhood": a.get("neighborhood", ""),
        "village": a.get("village", ""),
        "matchStatus": a.get("matchStatus", ""),
        "sourceIds": a.get("sourceIds", ""),
    })
stats["B_input_rows"] = len(addrs)
stats["B_dedup_rows"] = write_csv("appendix_B_address_crosswalk.csv", rows_b,
    ["address","addressPointId","apn","apnStatus","leafTractNumber","allContainingTractIds",
     "streetNameNormalized","neighborhood","village","matchStatus","sourceIds"])

# ---------------------------------------------------------------------------
# APPENDIX C — AOI polygon
# ---------------------------------------------------------------------------
print("\nC. AOI polygon")
with open(os.path.join(DEV, "ladera_ranch_cdp.geojson"), encoding="utf-8") as f:
    aoi = json.load(f)
with open(os.path.join(OUT, "appendix_C_aoi.geojson"), "w", encoding="utf-8") as f:
    json.dump(aoi, f)
feats = aoi.get("features", [])
def ring_count(g):
    if not g: return 0
    if g["type"] == "Polygon": return len(g["coordinates"])
    if g["type"] == "MultiPolygon": return sum(len(p) for p in g["coordinates"])
    return 0
summary_c = {
    "generated": GENERATED,
    "aoiSource": "data/development/ladera_ranch_cdp.geojson (existing repository AOI - reused, not redrawn)",
    "featureCount": len(feats),
    "geometryTypes": sorted({(f.get("geometry") or {}).get("type","none") for f in feats}),
    "ringCount": sum(ring_count(f.get("geometry")) for f in feats),
    "note": "Census CDP boundary used as the project AOI. It is an administrative/statistical "
            "boundary, not a legal subdivision or service-area boundary, and does not by itself "
            "establish tract membership.",
}
with open(os.path.join(OUT, "appendix_C_aoi_summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary_c, f, indent=2)
print(f"  appendix_C_aoi.geojson: {len(feats)} feature(s)")
stats["C_features"] = len(feats)

# ---------------------------------------------------------------------------
# APPENDIX D — street-to-tract crosswalk (road index; multi-date rows preserved)
# ---------------------------------------------------------------------------
print("\nD. street-to-tract crosswalk")
with open(os.path.join(M6, "gis/oc_road_index_ladera_2026-07-27.geojson"), encoding="utf-8") as f:
    road = json.load(f)

def epoch_to_date(v):
    if v in (None, "", 0): return ""
    try: return datetime.datetime.utcfromtimestamp(int(v)/1000).date().isoformat()
    except Exception: return str(v)

rows_d, tract_dates = [], collections.defaultdict(set)
for feat in road.get("features", []):
    p = feat.get("properties", {})
    tno = (p.get("TRACTNO") or "").strip()
    accept = epoch_to_date(p.get("TRACT_ACCEPT_DATE"))
    digits = "".join(ch for ch in tno if ch.isdigit())
    if tno.upper().startswith("TR") and digits:
        tract_dates[digits].add(accept)
    rows_d.append({
        "roadName": p.get("ROADNAME",""),
        "tractSource": tno,
        "tractNumberParsed": digits if tno.upper().startswith("TR") else "",
        "tractAcceptanceDate": accept,
        "serviceArea": p.get("SERVICE_AREA",""),
        "limits": p.get("LIMITS",""),
        "objectId": p.get("OBJECTID",""),
        "keyNum": p.get("KEYNUM",""),
        "gisMiles": p.get("GIS_MILES",""),
        "status": p.get("STATUS",""),
        "isMultiDateTract": "",   # filled below
        "sourceId": "LH-SRC-M6-OC-ROAD-INDEX-LADERA-LIVE",
        "doNotClaim": "Road acceptance is NOT a certificate of occupancy.",
    })

multi = {t for t, ds in tract_dates.items() if len({d for d in ds if d}) > 1}
for r in rows_d:
    if r["tractNumberParsed"] in multi:
        r["isMultiDateTract"] = "YES - multiple acceptance dates; preserved as separate rows"
stats["D_features"] = len(rows_d)
stats["D_multi_date_tracts"] = sorted(multi)
write_csv("appendix_D_street_tract_crosswalk.csv", rows_d,
    ["roadName","tractSource","tractNumberParsed","tractAcceptanceDate","serviceArea","limits",
     "objectId","keyNum","gisMiles","status","isMultiDateTract","sourceId","doNotClaim"])
print(f"  multi-date tracts detected: {sorted(multi) or 'none'}")

# ---------------------------------------------------------------------------
# APPENDIX E — known identifiers
# ---------------------------------------------------------------------------
print("\nE. known identifiers")
rows_e = []
for t in tracts:
    tn = t.get("tractNumber","")
    if t.get("bookPage"):
        rows_e.append({"identifierType":"tract_map_book_page","identifier":t["bookPage"],
            "relatedTract":tn,"description":f"Recorded tract map for TR {tn}",
            "sourceId":t.get("sourceId",""),"origin":"data/development/tract_maps.csv"})
for r in rows_d:
    if r["tractSource"] and not r["tractSource"].upper().startswith("TR"):
        rows_e.append({"identifierType":"board_resolution_or_other_road_source",
            "identifier":r["tractSource"],"relatedTract":"",
            "description":f"Road-index source for {r['roadName']}",
            "sourceId":r["sourceId"],"origin":"OC road index (Mission 6 capture)"})
try:
    for s in read_csv(os.path.join(DC, "sources.csv")):
        sid = s.get("sourceId") or s.get("id") or ""
        if sid:
            rows_e.append({"identifierType":"repository_source_id","identifier":sid,
                "relatedTract":"","description":s.get("title",""),
                "sourceId":sid,"origin":"research/development_chronology/sources.csv"})
except Exception as e:
    print("  (sources.csv not read:", e, ")")
# dedupe
seen_e, ded_e = set(), []
for r in rows_e:
    k = (r["identifierType"], r["identifier"], r["relatedTract"])
    if k in seen_e: continue
    seen_e.add(k); ded_e.append(r)
stats["E_identifiers"] = write_csv("appendix_E_known_identifiers.csv", ded_e,
    ["identifierType","identifier","relatedTract","description","sourceId","origin"])

# ---------------------------------------------------------------------------
# APPENDIX F — party name variants
# ---------------------------------------------------------------------------
print("\nF. party name variants")
rows_f, seen_f = [], set()
def add_party(name, role, source, origin):
    n = (name or "").strip()
    if not n or (n.lower(), role) in seen_f: return
    seen_f.add((n.lower(), role))
    rows_f.append({"partyName":n,"role":role,"nameVariantsToSearch":"","sourceId":source,"origin":origin})

for b in read_csv(os.path.join(DC, "builder_product_chronology.csv")):
    add_party(b.get("builder"), "builder", b.get("sourceIds",""), "builder_product_chronology.csv")
for t in tracts:
    add_party(t.get("engineeringCompany"), "engineering_company", t.get("sourceId",""), "tract_maps.csv")
    add_party(t.get("engineerSurveyor"), "engineer_surveyor", t.get("sourceId",""), "tract_maps.csv")
for name, role in [
    ("Ladera Ranch Maintenance Corporation (LARMAC)","hoa_master_association"),
    ("Santa Margarita Water District (SMWD)","utility_water_district"),
    ("County of Orange","public_agency"),
    ("OC Public Works","public_agency"),
    ("OC Development Services","public_agency"),
    ("Capistrano Unified School District (CUSD)","school_district"),
    ("Rancho Mission Viejo","landowner_developer"),
]:
    add_party(name, role, "LH-SRC-M6-*", "Mission 6 capture set / known project parties")

for r in rows_f:
    n = r["partyName"]
    v = {n}
    for suf in [" INC"," INC."," LLC"," LP"," COMPANY"," CO"," CORPORATION"," CORP"]:
        if n.upper().endswith(suf): v.add(n[: -len(suf)].strip())
    if "(" in n and ")" in n:
        v.add(n[: n.index("(")].strip()); v.add(n[n.index("(")+1 : n.index(")")].strip())
    r["nameVariantsToSearch"] = "; ".join(sorted({x for x in v if x}))
stats["F_parties"] = write_csv("appendix_F_party_name_variants.csv", rows_f,
    ["partyName","role","nameVariantsToSearch","sourceId","origin"])

# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------
readme = f"""# Mission 6 local appendices

**Generated:** {GENERATED} by `scripts/lhdrs_mission6_appendices.py` (reproducible; re-run to regenerate).
These are the six attachments required before any Mission 6 records request may be submitted.

**Nothing here has been submitted to any agency.** These are working attachments only.

| Appendix | File | Rows |
|---|---|---|
| A — canonical tract list + aliases | `appendix_A_canonical_tracts.csv` | {stats['A_rows_total']} ({stats['A_tracts_canonical']} canonical + 1 excluded/conflicted) |
| B — address crosswalk | `appendix_B_address_crosswalk.csv` | {stats['B_dedup_rows']} (from {stats['B_input_rows']} points) |
| C — project AOI | `appendix_C_aoi.geojson` + `_summary.json` | {stats['C_features']} feature(s) |
| D — street-to-tract crosswalk | `appendix_D_street_tract_crosswalk.csv` | {stats['D_features']} |
| E — known identifiers | `appendix_E_known_identifiers.csv` | {stats['E_identifiers']} |
| F — party name variants | `appendix_F_party_name_variants.csv` | {stats['F_parties']} |

## Disclosed limitations — read before sending anything

1. **No APN data exists in this repository.** Appendix B therefore has an empty `apn` column with
   `apnStatus = NOT_IN_REPOSITORY`. APNs must be obtained from the County; they must **not** be
   inferred, derived, or back-filled from address or tract data. The priority-1 request asks the
   County to supply APN linkage.
2. **TR 17588 is excluded from the canonical Ladera set** (decision: `{TR_17588_DECISION}`), and is
   carried as an explicit conflict row. The 2024 Board-certified road index labels it Ladera Ranch;
   the live FeatureServer labels the same feature Rancho Mission Viejo. Both preserved.
3. **Multi-date tracts are preserved as separate rows, never collapsed.** Detected from the road
   index: {stats['D_multi_date_tracts']}. A tract with several road-segment acceptance dates has no
   single "completion date" without a documented rule.
4. **Appendix C reuses the existing repository AOI** (Census CDP boundary). It was not redrawn. A
   CDP is an administrative/statistical boundary, not a legal subdivision or service-area boundary.
5. **Road acceptance, map recordation, sales dates, year-built values, school/facility openings, and
   aerial observations are NOT certificates of occupancy** and must never be substituted for one.

## Gate status — unchanged

Permit/occupancy: not satisfied · Address lifecycle: not satisfied ·
Construction-interval aerial: not satisfied · **Proximity analysis: BLOCKED**

Generating these appendices does not satisfy any gate. It unblocks *requesting* the records that
could.
"""
with open(os.path.join(OUT, "APPENDICES_README.md"), "w", encoding="utf-8") as f:
    f.write(readme)

with open(os.path.join(OUT, "generation_stats.json"), "w", encoding="utf-8") as f:
    json.dump({"generated": GENERATED, "tr17588Decision": TR_17588_DECISION, **stats}, f, indent=2)

print("\nDone ->", OUT)
