#!/usr/bin/env python3
"""Process California DPR Pesticide Use Report (PUR) data for Orange County.

Extracts Orange County (county_cd = 30) application records from a downloaded PUR annual
archive and summarizes them by chemical, site type, and location precision. Its central
purpose is an EMPIRICAL TEST of the coverage claims in
research/pesticides/data_coverage.md:

  * How much Orange County pesticide use is reported WITHOUT any location (structural pest
    control is a county-level monthly summary — no township/range/section)?
  * How much landscape/ornamental use IS located, and in which sections?
  * Does glufosinate — the active ingredient documented in Ladera Ranch common-area notices
    — appear in Orange County PUR at all?

Usage:
    python3 process_pur.py /path/to/pur2023.zip [--out research/pesticides]

Standard library only. PUR archive layout (2023):
    pur<YYYY>/pur_data/udc<YY>_30.txt      Orange County use records (CSV, header row)
    pur<YYYY>/lookup_tables/PUR_SITE.txt   site_code -> site_name

INTERPRETATION NOTE: PUR under-captures urban landscape use. Homeowner self-application is
exempt entirely. ABSENCE OF A RECORD IS NOT EVIDENCE OF NON-APPLICATION.
"""
import argparse
import csv
import io
import os
import sys
import zipfile
from collections import Counter, defaultdict

ORANGE_CD = "30"
# Active ingredients of interest (substring match against chemname, upper-cased).
WATCH = ["GLUFOSINATE", "GLYPHOSATE", "2,4-D", "ORYZALIN", "PENDIMETHALIN", "TRIFLURALIN",
         "DITHIOPYR", "ISOXABEN", "TRICLOPYR", "IMIDACLOPRID", "BIFENTHRIN", "PERMETHRIN",
         "CYPERMETHRIN", "CARBARYL", "MALATHION", "DIURON", "MSMA"]


def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archive")
    ap.add_argument("--out", default="research/pesticides")
    args = ap.parse_args()
    if not os.path.exists(args.archive):
        sys.exit(f"Archive not found: {args.archive}")

    zf = zipfile.ZipFile(args.archive)
    use_member = next((n for n in zf.namelist()
                       if n.endswith(f"_{ORANGE_CD}.txt") and "/pur_data/" in n), None)
    if not use_member:
        sys.exit("Could not locate Orange County use file (udc*_30.txt) in archive.")
    print(f"Reading {use_member}")

    rows = []
    with zf.open(use_member) as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1")):
            if (r.get("county_cd") or "").strip() == ORANGE_CD:
                rows.append(r)
    print(f"Orange County application records (2023): {len(rows):,}\n")

    chem_recs, chem_lbs = Counter(), defaultdict(float)
    site_recs, site_lbs = Counter(), defaultdict(float)
    located, unlocated = 0, 0
    section_recs = Counter()
    watch_hits = defaultdict(lambda: {"records": 0, "lbs": 0.0, "sites": Counter()})

    for r in rows:
        chem = (r.get("chemname") or "").strip().strip('"')
        site = (r.get("site_name") or "").strip().strip('"')
        lbs = fnum(r.get("lbs_chm_used"))
        chem_recs[chem] += 1
        chem_lbs[chem] += lbs
        site_recs[site] += 1
        site_lbs[site] += lbs

        twp = (r.get("township") or "").strip()
        rng = (r.get("range") or "").strip()
        sec = (r.get("section") or "").strip()
        if twp and rng and sec:
            located += 1
            mtrs = (f"{(r.get('base_ln_mer') or '').strip()}"
                    f"{twp}{(r.get('tship_dir') or '').strip()}"
                    f"{rng}{(r.get('range_dir') or '').strip()}{sec}")
            section_recs[mtrs] += 1
        else:
            unlocated += 1

        up = chem.upper()
        for w in WATCH:
            if w in up:
                watch_hits[w]["records"] += 1
                watch_hits[w]["lbs"] += lbs
                watch_hits[w]["sites"][site] += 1
                break

    pct_un = 100.0 * unlocated / max(len(rows), 1)
    print("=" * 74)
    print("LOCATION PRECISION — the core coverage finding")
    print("=" * 74)
    print(f"  Records WITH township/range/section: {located:,} ({100-pct_un:.1f}%)")
    print(f"  Records WITHOUT any location:        {unlocated:,} ({pct_un:.1f}%)")
    print(f"  Distinct located sections:           {len(section_recs):,}")

    print("\n" + "=" * 74)
    print("TOP SITE TYPES (by application records)")
    print("=" * 74)
    for site, n in site_recs.most_common(15):
        print(f"  {n:7,}  {chem_lbs and round(site_lbs[site],1):>12,} lbs  {site}")

    print("\n" + "=" * 74)
    print("TOP 20 ACTIVE INGREDIENTS (by application records)")
    print("=" * 74)
    for chem, n in chem_recs.most_common(20):
        print(f"  {n:7,}  {round(chem_lbs[chem],1):>12,} lbs  {chem[:60]}")

    print("\n" + "=" * 74)
    print("WATCHED ACTIVE INGREDIENTS (relevant to this investigation)")
    print("=" * 74)
    for w in WATCH:
        d = watch_hits.get(w)
        if not d or not d["records"]:
            print(f"  {w:<16} NOT PRESENT in Orange County 2023 PUR")
            continue
        top = ", ".join(f"{s} ({c})" for s, c in d["sites"].most_common(3))
        print(f"  {w:<16} {d['records']:>6,} records  {round(d['lbs'],1):>10,} lbs  | top sites: {top}")

    os.makedirs(args.out, exist_ok=True)
    out_csv = os.path.join(args.out, "pur_orange_county_2023.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["chemical", "application_records", "total_lbs_applied"])
        for chem, n in chem_recs.most_common():
            w.writerow([chem, n, round(chem_lbs[chem], 2)])
    print(f"\nWrote {out_csv} ({len(chem_recs):,} chemicals)")

    out_sites = os.path.join(args.out, "pur_orange_county_2023_sites.csv")
    with open(out_sites, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["site_type", "application_records", "total_lbs_applied", "location_reported"])
        for site, n in site_recs.most_common():
            w.writerow([site, n, round(site_lbs[site], 2),
                        "no" if site.upper() == "STRUCTURAL PEST CONTROL" else "varies"])
    print(f"Wrote {out_sites} ({len(site_recs):,} site types)")


if __name__ == "__main__":
    main()
