#!/usr/bin/env python3
"""Generate the Mission 5 historical evidence atlas and publication export."""

from __future__ import annotations

import csv
import hashlib
from html import escape
import json
import os
from pathlib import Path
import shutil
import tempfile


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research/development_chronology"
DATA = ROOT / "data/development"
EVIDENCE = ROOT / "evidence/lhdrs/mission5"
REPORTS = ROOT / "reports"
ASSETS = REPORTS / "assets/lhdrs_mission5"
EXPORT = ROOT / "data/exports/atlas_mission5"


def read_csv(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        stream.write(value)
        temporary = Path(stream.name)
    os.replace(temporary, path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def html_table(headers: list[str], rows: list[list[object]], classes: str = "") -> str:
    head = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in row) + "</tr>"
        for row in rows
    )
    return f'<div class="table-wrap"><table class="{classes}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    clean = lambda value: str(value).replace("|", "\\|").replace("\n", " ")
    values = ["| " + " | ".join(clean(value) for value in row) + " |" for row in rows]
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |", *values])


def build() -> dict[str, object]:
    summary = json.loads((DATA / "mission5_summary.json").read_text())
    absorption = read_csv("cfd_absorption_chronology.csv")
    products = [row for row in read_csv("builder_product_chronology.csv") if row["cfdPhase"]]
    commercial = read_csv("commercial_asset_chronology_mission5.csv")
    imagery = [row for row in read_csv("imagery_inventory.csv") if row["id"].startswith("LH-IMG-NAIP-")]
    conflicts = [row for row in read_csv("conflict_registry.csv") if row["conflictId"].startswith("LH-CONFLICT-M5-")]
    gaps = read_csv("highest_value_research_queue.csv")
    crosswalk = json.loads((BASE / "tract_neighborhood_crosswalk_summary.json").read_text())
    sources = [row for row in read_csv("sources.csv") if "/mission5/" in row["localFilePath"]]

    ASSETS.mkdir(parents=True, exist_ok=True)
    EXPORT.mkdir(parents=True, exist_ok=True)
    for year in (2005, 2009, 2010):
        shutil.copy2(EVIDENCE / f"imagery/ladera_naip_{year}.jpg", ASSETS / f"ladera_naip_{year}.jpg")
    export_names = [
        "builder_product_chronology.csv", "cfd_absorption_chronology.csv",
        "commercial_asset_chronology_mission5.csv", "neighborhood_chronology_mission5.csv",
        "tract_neighborhood_crosswalk.csv", "tract_lifecycle_reconstruction.csv",
        "imagery_inventory.csv", "imagery_observations_mission5.csv", "highest_value_research_queue.csv",
    ]
    for name in export_names:
        shutil.copy2(BASE / name, EXPORT / name)

    totals: dict[str, int] = {}
    for row in absorption:
        totals[row["district"]] = totals.get(row["district"], 0) + int(row["builtAndOccupiedUnits"])
    absorption_rows = [
        [row["district"], row["year"], row["builtAndOccupiedUnits"], row["confidence"]]
        for row in absorption
    ]
    product_rows = [
        [row["cfdPhase"], row["productName"], row["builder"], row["unitsPlanned"], row["permitsBy2006"], row["escrowsBy2006"], row["escrowsBy2011"] or "-"]
        for row in products
    ]
    commercial_rows = [
        [row["assetName"], row["reportedDevelopmentStatus"], row["totalAcres"], row["occupiedAcres"], row["totalCapacity"] or "-", row["occupiedCapacity"] or "-", row["capacityUnit"]]
        for row in commercial
    ]
    gap_rows = [[row["rank"], row["researchTarget"], row["priority"], row["recommendedRepository"]] for row in gaps]

    figures = "".join(
        f'<figure><img src="assets/lhdrs_mission5/ladera_naip_{year}.jpg" alt="Official {year} NAIP aerial view of Ladera Ranch"><figcaption>{year}: official full-coverage NAIP state. Visible patterns are not permits, certificates of occupancy, or individual occupancy evidence.</figcaption></figure>'
        for year in (2005, 2009, 2010)
    )
    source_links = "".join(
        f'<li><a href="{escape(row["url"], quote=True)}">{escape(row["title"])}</a> <span>{escape(row["reliabilityGrade"])}</span></li>'
        for row in sources
    )
    conflict_items = "".join(
        f'<li><strong>{escape(row["conflictType"].replace("_", " ").title())}:</strong> {escape(row["positionA"])} {escape(row["positionB"])} <em>{escape(row["resolutionRule"])}</em></li>'
        for row in conflicts
    )
    bars = "".join(
        f'<div class="bar-row"><span>{escape(name)}</span><div><i style="width:{min(100, total / 13):.1f}%"></i></div><b>{total:,}</b></div>'
        for name, total in totals.items()
    )

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LHDRS Historical Evidence Atlas, Mission 5</title>
<style>
:root{{--ink:#18242d;--muted:#5b6870;--paper:#f7f8f6;--white:#fff;--teal:#28796f;--coral:#c45b34;--gold:#b78a27;--line:#d8dedc}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 Arial,sans-serif;letter-spacing:0}}
header{{background:#17242c;color:#fff;padding:52px max(24px,calc((100vw - 1180px)/2)) 46px;border-bottom:6px solid var(--coral)}}
header p{{max-width:850px;color:#dbe4e3;margin:10px 0 0}} h1{{font:700 44px/1.08 Georgia,serif;margin:0;letter-spacing:0}} h2{{font:700 29px/1.2 Georgia,serif;margin:0 0 18px}}
main section{{padding:42px max(24px,calc((100vw - 1180px)/2));border-bottom:1px solid var(--line)}} main section:nth-child(even){{background:var(--white)}}
.kpis{{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px}} .kpi{{border-top:4px solid var(--teal);padding:14px 8px 0}} .kpi b{{display:block;font:700 31px/1 Georgia,serif}} .kpi span{{display:block;color:var(--muted);font-size:13px;margin-top:7px}}
.notice{{border-left:5px solid var(--gold);padding:13px 18px;background:#fff9e9;max-width:980px}} .table-wrap{{overflow:auto;border:1px solid var(--line)}}
table{{width:100%;border-collapse:collapse;font-size:13px;background:white}} th{{text-align:left;background:#edf1ef;position:sticky;top:0}} th,td{{padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top;white-space:nowrap}}
.imagery-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}} figure{{margin:0}} figure img{{display:block;width:100%;aspect-ratio:9/10;object-fit:cover;border:1px solid #aeb8b5}} figcaption{{font-size:12px;color:var(--muted);padding-top:8px}}
.bar-row{{display:grid;grid-template-columns:260px 1fr 70px;gap:12px;align-items:center;margin:9px 0;font-size:13px}} .bar-row>div{{height:20px;background:#e5e9e7}} .bar-row i{{display:block;height:100%;background:var(--teal)}}
.conflicts li,.sources li{{margin:9px 0}} .conflicts em{{display:block;color:var(--muted)}} .sources{{columns:2;column-gap:40px}} .sources span{{color:var(--coral);font-weight:bold}}
footer{{padding:30px max(24px,calc((100vw - 1180px)/2));background:#17242c;color:#dbe4e3;font-size:13px}}
@media(max-width:800px){{h1{{font-size:34px}}.kpis{{grid-template-columns:repeat(2,minmax(0,1fr))}}.imagery-grid{{grid-template-columns:1fr}}.sources{{columns:1}}.bar-row{{grid-template-columns:1fr 55px}}.bar-row span{{grid-column:1/-1}}}}
</style></head><body>
<header><h1>Ladera Ranch Historical Evidence Atlas</h1><p>Mission 5 public-evidence reconstruction | Generated 27 July 2026</p><p>Legal maps, present-day geography, dated aerial states, builder/product records, and County monitoring snapshots are kept as distinct evidence classes.</p></header>
<main>
<section><h2>What changed</h2><div class="kpis">
<div class="kpi"><b>{summary['registeredSources']}</b><span>new archived sources</span></div><div class="kpi"><b>{summary['matchedAddressPointRows']:,}</b><span>matched current address points</span></div><div class="kpi"><b>{summary['builderProducts']}</b><span>builder products</span></div><div class="kpi"><b>3</b><span>full-coverage aerial states</span></div><div class="kpi"><b>{summary['newClaims']}</b><span>new bounded claims</span></div>
</div><p class="notice"><strong>Evidence boundary:</strong> {escape(summary['safeguard'])}</p></section>
<section><h2>Tract and neighborhood reconstruction</h2><p>The current address crosswalk links {crosswalk['matchedPointRows']:,} address rows, {crosswalk['distinctNeighborhoods']} named neighborhoods, and {crosswalk['distinctLeafTracts']} of 123 recorded tract records. Seven tract records have no matched current Ladera directory address. These are candidate geographic relationships valid at the retrieval date, not historical parentage.</p>
<p>{summary['tractLifecycleRows']} tract lifecycle records preserve their exact map-recording milestones. {sum(1 for row in read_csv('tract_lifecycle_reconstruction.csv') if row['builderProductCandidates'])} carry product candidates; none receive inferred grading, construction, habitability, or occupancy dates.</p></section>
<section><h2>Built-and-occupied absorption</h2><p>The County reports define absorption as “Built and Occupied.” Counts remain at CFD scale and are not assigned to tracts, addresses, or households.</p><div class="bars">{bars}</div>{html_table(['District','Year','Units','Confidence'], absorption_rows)}</section>
<section><h2>Builder and product chronology</h2><p>County tables control Phase V and Phase VI builder and count snapshots. Secondary assignments remain only where no primary table was found; all twelve substantive disagreements are retained in the conflict registry.</p>{html_table(['CFD phase','Product','County builder','Planned','Permits 2006','Escrows 2006','Escrows 2011'], product_rows)}</section>
<section><h2>Commercial and mixed-use status</h2><p>The CFD 2002-1 table supplies an exact 31 December 2006 snapshot. It does not supply opening dates or historical footprints.</p>{html_table(['Asset','Reported status','Total acres','Occupied acres','Total capacity','Occupied capacity','Unit'], commercial_rows)}</section>
<section><h2>Official aerial states</h2><p>Catalog filenames establish 7 June 2005, 18-22 June 2009, and 1 May 2010 capture dates. Full-resolution inspection supports visible-state and between-capture change observations; no active-construction polygon is published.</p><div class="imagery-grid">{figures}</div></section>
<section><h2>Conflicts retained</h2><ul class="conflicts">{conflict_items}</ul></section>
<section><h2>Highest-value remaining records</h2><p>Public search has reached diminishing returns for these evidence classes. Each row requires an agency, district, association, recorder, or licensed archive request.</p>{html_table(['Rank','Target','Priority','Repository'], gap_rows)}</section>
<section><h2>Mission 5 sources</h2><ul class="sources">{source_links}</ul></section>
</main><footer>LHDRS Mission 5 | Every archived acquisition has a retrieval date and SHA-256 checksum. A blank geometry or date is an unresolved field, not evidence of absence.</footer>
</body></html>"""

    markdown = f"""# Ladera Ranch Historical Evidence Atlas: Mission 5

Generated 2026-07-27

## Evidence boundary

{summary['safeguard']}

## Mission 5 additions

- {summary['registeredSources']} new archived sources with checksums
- {summary['matchedAddressPointRows']:,} matched current address points and {summary['tractNeighborhoodRelationships']} tract-neighborhood relationships
- {summary['builderProducts']} builder products with {summary['builderConflicts']} retained primary/secondary conflicts
- {summary['newClaims']} new bounded claims
- Three full-coverage official aerial states: 2005, 2009, and 2010

## Tract and neighborhood reconstruction

The current crosswalk covers {crosswalk['distinctNeighborhoods']} named neighborhoods and {crosswalk['distinctLeafTracts']} of 123 recorded tract records. It is not a historical lifecycle crosswalk.

## Built-and-occupied absorption

The County definition is `Absorption = Built and Occupied`. Counts remain nonspatial CFD aggregates.

{markdown_table(['District','Year','Units','Confidence'], absorption_rows)}

## County builder and product snapshots

{markdown_table(['CFD phase','Product','County builder','Planned','Permits 2006','Escrows 2006','Escrows 2011'], product_rows)}

## Commercial and mixed-use snapshot

{markdown_table(['Asset','Reported status','Total acres','Occupied acres','Total capacity','Occupied capacity','Unit'], commercial_rows)}

## Official imagery

![2005 official NAIP](assets/lhdrs_mission5/ladera_naip_2005.jpg)

![2009 official NAIP](assets/lhdrs_mission5/ladera_naip_2009.jpg)

![2010 official NAIP](assets/lhdrs_mission5/ladera_naip_2010.jpg)

These images support bounded visible-state observations only. No precise active-construction polygon is published or proximity eligible.

## Remaining manual-record queue

{markdown_table(['Rank','Target','Priority','Repository'], gap_rows)}
"""
    html_path = REPORTS / "LHDRS_Historical_Evidence_Atlas_Mission_5.html"
    md_path = REPORTS / "LHDRS_Historical_Evidence_Atlas_Mission_5.md"
    write_text(html_path, html)
    write_text(md_path, markdown)

    publication_files = [html_path, md_path, *(ASSETS / f"ladera_naip_{year}.jpg" for year in (2005, 2009, 2010)), *(EXPORT / name for name in export_names)]
    manifest = {
        "title": "LHDRS Historical Evidence Atlas, Mission 5",
        "generated": "2026-07-27", "version": "3.0", "firstAndSecondEditionsPreserved": True,
        "proximityResultCount": 0, "files": [
            {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in publication_files
        ],
    }
    write_text(EXPORT / "publication_manifest.json", json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    result = build()
    print(f"DONE  Mission 5 atlas: {len(result['files'])} checksummed publication files")
