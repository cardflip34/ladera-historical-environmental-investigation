#!/usr/bin/env python3
"""Generate the LEHRP preliminary report as HTML, then PDF (via headless Chrome).

Reads the live research registries so the report always reflects current data.

Usage:
    python3 scripts/build_report.py            # HTML + PDF
    python3 scripts/build_report.py --html     # HTML only

Output: reports/LEHRP_Preliminary_Report.{html,pdf}
"""
import argparse
import base64
import csv
import html
import json
import math
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
GENERATED = "2026-07-18"


def rd(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def e(s):
    return html.escape(str(s or ""))


def b64img(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return ""
    return base64.b64encode(open(p, "rb").read()).decode()


# ---------------------------------------------------------------- data ------
sources = rd("research/source_registry/sources.csv")
events = rd("research/cancer_reports/public_report_registry.csv")
lit = rd("research/literature/literature_registry.csv")
chems = rd("research/pesticides/active_ingredients.csv")
apps_ = rd("research/pesticides/application_events.csv")
envs = rd("research/environmental_sites/sites.csv")
water = rd("research/water/water_quality.csv")
demo = rd("research/demographics/population_estimates.csv")
rates = rd("research/demographics/incidence_rates.csv")
landuse = rd("research/land_use/historical_land_use.csv")
pur_chem = rd("research/pesticides/pur_orange_county_2023.csv")

grades = {}
for s in sources:
    g = (s.get("reliabilityGrade") or "?").upper()
    grades[g] = grades.get(g, 0) + 1

wells = []
wp = os.path.join(ROOT, "data/geospatial/oil_gas_wells.geojson")
if os.path.exists(wp):
    wells = [f["properties"] for f in json.load(open(wp))["features"]]
    wells.sort(key=lambda p: float(p.get("distanceMiles", 99)))


# ------------------------------------------------------- SIR scenarios ------
POISSON = {4: (1.0899, 10.2416), 5: (1.6235, 11.6683), 6: (2.2019, 13.0595),
           12: (6.2006, 20.9616)}
PY_0_19, PY_10_19 = 9115 * 14, 4906 * 14
SCENARIOS = [
    ("S1 central", 6, PY_0_19, 3.0, "6 cases, ages 0–19, all-races SEER rate"),
    ("S2 ancestry-adjusted", 6, PY_0_19, 4.0, "rate raised for a non-Hispanic-white-majority community"),
    ("S3 peak-age", 6, PY_10_19, 4.58, "ages 10–19 only, peak-age rate"),
    ("S4 conservative count", 4, PY_0_19, 4.0, "case-definition sensitivity"),
    ("S5 higher count", 12, PY_0_19, 3.0, "single-source outlier count"),
    ("S6 leave-one-out", 5, PY_0_19, 4.0, "one reported case removed"),
]


def sir_rows():
    out = []
    for label, obs, py, rate, note in SCENARIOS:
        exp = py * rate / 1_000_000
        lo, hi = POISSON[obs]
        out.append((label, obs, rate, exp, obs / exp, lo / exp, hi / exp, note))
    return out


# ------------------------------------------------------------- render ------
def table(headers, rows, cls="", aligns=None):
    aligns = aligns or []
    th = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = ""
    for r in rows:
        tds = ""
        for i, c in enumerate(r):
            a = ' class="num"' if i < len(aligns) and aligns[i] == "n" else ""
            tds += f"<td{a}>{c}</td>"
        body += f"<tr>{tds}</tr>"
    return f'<table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>'


def build_html():
    map_b64 = b64img("reports/assets/map_figure.png")

    sir_tbl = table(
        ["Scenario", "Observed", "Rate /M/yr", "Expected", "SIR", "95% CI"],
        [(f"<strong>{e(l)}</strong><br><span class='sm'>{e(n)}</span>", o, f"{r:.1f}",
          f"{ex:.3f}", f"<strong>{s:.1f}</strong>", f"{lo:.1f} – {hi:.1f}")
         for l, o, r, ex, s, lo, hi, n in sir_rows()],
        aligns=["", "n", "n", "n", "n", "n"])

    env_sorted = sorted([x for x in envs if x.get("approxDistanceMiles")],
                        key=lambda x: float(x["approxDistanceMiles"]))
    env_tbl = table(
        ["Site", "Type / database", "Contaminants", "Miles"],
        [(e(x["name"]), f"{e(x['siteType'])}<br><span class='sm'>{e(x['database'])}</span>",
          e(x["contaminants"]), x["approxDistanceMiles"]) for x in env_sorted],
        aligns=["", "", "", "n"])

    well_tbl = table(
        ["Well (CalGEM)", "Status", "Miles from centroid"],
        [(e(w["name"]), e(w["status"]), f"<strong>{w['distanceMiles']}</strong>") for w in wells],
        aligns=["", "", "n"])

    pur_tbl = table(
        ["Site type", "Records", "Located", "% located"],
        [("Structural pest control", "55,442", "0", "0.0%"),
         ("<strong>Landscape maintenance</strong>", "15,383", "22", "<strong>0.1%</strong>"),
         ("Nursery — outdoor containers", "2,990", "2,982", "99.7%"),
         ("Golf course turf", "1,375", "0", "0.0%"),
         ("Rights of way", "1,130", "48", "4.2%"),
         ("Agriculture (fruiting pepper)", "183", "183", "100.0%")],
        aligns=["", "n", "n", "n"])

    lu_tbl = table(["Period", "Land use", "Confidence"],
                   [(e(x["period"]), e(x["land_use"]), e(x["confidence"])) for x in landuse])

    dir_counts = {}
    for l in lit:
        d = l.get("evidence_direction", "—")
        dir_counts[d] = dir_counts.get(d, 0) + 1
    lit_tbl = table(["Evidence direction", "Papers"],
                    [(e(k), v) for k, v in sorted(dir_counts.items(), key=lambda x: -x[1])],
                    aligns=["", "n"])

    grade_tbl = table(["Grade", "Meaning", "Count"],
                      [("A1", "Official dataset / peer-reviewed / registry", grades.get("A1", 0)),
                       ("A2", "Official government webpage, filing, meeting doc", grades.get("A2", 0)),
                       ("B1", "University / research-institution report", grades.get("B1", 0)),
                       ("B2", "Reputable news quoting named sources", grades.get("B2", 0)),
                       ("C", "Advocacy, law-firm, petition, unverified counts", grades.get("C", 0)),
                       ("D", "Speculation / unsourced reposts", grades.get("D", 0))],
                      aligns=["", "", "n"])

    top_pur = table(["Active ingredient", "Records", "Pounds"],
                    [(e(r["chemical"][:46]), f"{int(r['application_records']):,}",
                      f"{float(r['total_lbs_applied']):,.0f}") for r in pur_chem[:12]],
                    aligns=["", "n", "n"])

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light only">
<meta name="supported-color-schemes" content="light">
<title>LEHRP Preliminary Report</title>
<style>
@page {{ size: Letter; margin: 16mm 15mm 18mm; }}
:root {{ color-scheme: light only; --ink:#111c2e; --ink2:#3d4a5d; --navy:#0b1e38;
  --blue:#1d4f8f; --line:#c9d4e2; --paper:#ffffff; }}
* {{ box-sizing:border-box; -webkit-print-color-adjust:exact; print-color-adjust:exact;
  forced-color-adjust:none; }}
html, body {{ background:var(--paper) !important; color:var(--ink) !important; }}
body {{ font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size:10.4pt; line-height:1.58; margin:0; }}
/* Defeat forced dark-mode inversion in mobile/app WebViews. */
@media (prefers-color-scheme: dark) {{
  html, body {{ background:#ffffff !important; color:#111c2e !important; }}
  h1,h2,h3,h4,p,li,td,th,div,span,strong,em,figcaption,footer {{ color:#111c2e !important; }}
  h1,h2,h3 {{ color:#0b1e38 !important; }}
  .eyebrow {{ color:#1d4f8f !important; }}
  .sm,.muted,.meta,figcaption,footer {{ color:#3d4a5d !important; }}
  th {{ background:#e8eef6 !important; color:#0b1e38 !important; }}
  .card,.kpi div {{ background:#ffffff !important; }}
  .disc {{ background:#fbeaea !important; }} .callout {{ background:#e9f1fb !important; }}
  .warn {{ background:#fdf3e6 !important; }} .ok {{ background:#e9f5ed !important; }}
}}
h1 {{ font-size:23pt; color:var(--navy); margin:0 0 5pt; line-height:1.15; letter-spacing:-.2pt; }}
h2 {{ font-size:14pt; color:var(--navy); margin:22pt 0 7pt; padding-bottom:4pt;
  border-bottom:2.5px solid var(--blue); page-break-after:avoid; }}
h3 {{ font-size:11.2pt; color:var(--navy); margin:14pt 0 5pt; page-break-after:avoid; }}
p {{ margin:0 0 8pt; }}
strong {{ color:var(--navy); }}
.sm {{ font-size:8.8pt; color:var(--ink2); }}
.muted {{ color:var(--ink2); }}
.cover {{ border-bottom:3px solid var(--blue); padding-bottom:11pt; margin-bottom:13pt; }}
.eyebrow {{ color:var(--blue); font-size:8.4pt; font-weight:700; letter-spacing:.12em; text-transform:uppercase; }}
.meta {{ font-size:9pt; color:var(--ink2); margin-top:7pt; }}
.disc {{ background:#fbeaea; border-left:5px solid #9a3030; padding:9pt 11pt; font-size:9.4pt;
  border-radius:0 4px 4px 0; margin:11pt 0; }}
.callout {{ background:#e9f1fb; border-left:5px solid var(--blue); padding:9pt 11pt; margin:10pt 0;
  border-radius:0 4px 4px 0; font-size:9.8pt; }}
.warn {{ background:#fdf3e6; border-left-color:#a35f0c; }}
.ok {{ background:#e9f5ed; border-left-color:#156132; }}
table {{ width:100%; border-collapse:collapse; font-size:9.2pt; margin:8pt 0 11pt;
  page-break-inside:avoid; }}
th {{ background:#e8eef6; color:var(--navy); text-align:left; padding:5pt 7pt; font-size:8.2pt;
  text-transform:uppercase; letter-spacing:.04em; border-bottom:2px solid var(--line); }}
td {{ padding:5pt 7pt; border-bottom:1px solid #dbe3ed; vertical-align:top; color:var(--ink); }}
td.num, th.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
tbody tr:nth-child(even) td {{ background:#f6f9fc; }}
figure {{ margin:11pt 0 15pt; page-break-inside:avoid; }}
figure img {{ width:100%; border:1px solid var(--line); border-radius:5px; }}
figcaption {{ font-size:8.8pt; color:var(--ink2); margin-top:6pt; line-height:1.45; }}
.grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:11pt; }}
.card {{ border:1px solid var(--line); border-radius:5px; padding:9pt 11pt; background:#fff; }}
.card h3 {{ margin-top:0; }}
ul, ol {{ margin:0 0 8pt; padding-left:16pt; }}
li {{ margin-bottom:4pt; }}
.kpi {{ display:grid; grid-template-columns:repeat(4,1fr); gap:9pt; margin:11pt 0; }}
.kpi div {{ border:1px solid var(--line); border-radius:5px; padding:8pt 10pt; background:#fff; }}
.kpi .n {{ font-size:17pt; font-weight:700; color:var(--navy); line-height:1; }}
.kpi .l {{ font-size:7.8pt; color:var(--ink2); text-transform:uppercase; letter-spacing:.04em; margin-top:4pt; }}
.pb {{ page-break-before:always; }}
footer {{ margin-top:20pt; padding-top:9pt; border-top:1px solid var(--line); font-size:8.4pt; color:var(--ink2); }}
@media screen and (max-width:700px) {{
  body {{ font-size:12pt; padding:14px; }}
  .grid2, .kpi {{ grid-template-columns:1fr; }}
  table {{ font-size:10.5pt; }}
  h1 {{ font-size:20pt; }}
}}
</style></head><body>

<div class="cover">
  <div class="eyebrow">Ladera Environmental Health Research Platform · Preliminary Report</div>
  <h1>Reported pediatric cancers in Ladera Ranch:<br>what the public evidence does and does not show</h1>
  <div class="meta">Independent public-source research · Generated {GENERATED} · Version 0.5.0 ·
  Hypothesis-neutral · Aggregate-only</div>
</div>

<div class="disc">
<strong>This report does not provide medical advice and does not establish that any pesticide,
property, organization, employer, school, water provider, government agency, or other party
caused any illness.</strong> Publicly reported health events may not have been independently
medically verified. Geographic and temporal overlap does not establish exposure or causation.
Formal conclusions require authorized epidemiological analysis, verified medical information,
exposure assessment, toxicological review, and independent scientific evaluation. Health data
here is aggregate-only; no individual is identified.
</div>

<div class="kpi">
  <div><div class="n">{len(sources)}</div><div class="l">Sources graded A1–D</div></div>
  <div><div class="n">79,473</div><div class="l">PUR records analyzed</div></div>
  <div><div class="n">{len(lit)}</div><div class="l">Literature entries</div></div>
  <div><div class="n">{len(envs)}</div><div class="l">Environmental sites</div></div>
</div>

<h2>1. Executive summary</h2>
<p><strong>No agency has declared a cluster or identified a cause.</strong> An official
multi-agency review — Orange County Health Care Agency, the California Cancer Registry, UC
Irvine, and the OC Agricultural Commissioner — is underway; its initial pass "did not find a
particular pattern," and findings remain pending. A federal EPA investigation has been
<em>requested</em> by the First Assistant U.S. Attorney but not confirmed opened, and no EPA
response was found.</p>

<p><strong>Every pesticide-specific causal claim in circulation is advocacy- or
attorney-sourced (grade C)</strong> — including the "17 pesticides in June" figure and the
naming of glufosinate. No regulator classifies glufosinate as a carcinogen; its EU
non-renewal was on reproductive-toxicity grounds, not cancer.</p>

<p><strong>The single most important scientific fact is hypothesis-neutral:</strong> Ewing
sarcoma is strongly ancestry-patterned through germline biology — roughly nine times more
common in people of European ancestry than African ancestry. A community that is 63.6%
non-Hispanic white therefore carries an <em>elevated baseline expectation</em>, which must be
modelled before any excess is attributed to the environment.</p>

<p><strong>The strongest testable environmental lead is not active spraying.</strong> It is
<em>legacy agricultural soil residue</em>: the community was built on former citrus, grain and
nursery land, and neighbouring former-farm school sites in the state's own database
repeatedly test positive for DDT, toxaphene, chlordane and arsenic — yet the footprint itself
appears never to have been tested.</p>

<div class="callout warn"><strong>Bottom line.</strong> Under transparent assumptions the
<em>reported</em> count exceeds statistical expectation, which is precisely why the pattern
<strong>warrants investigation</strong>. It is not proof of a cluster: the counts are
media/attorney-reported rather than registry-verified, the boundary was drawn around the
observed cases, and the numbers are small enough that one or two cases move the result
dramatically. <strong>The available evidence does not yet establish causation.</strong></div>

<h2>2. Study area and environmental context</h2>
<figure>
  <img src="data:image/png;base64,{map_b64}" alt="Ladera Ranch study area map">
  <figcaption><strong>Figure 1.</strong> Study zones with DTSC EnviroStor cleanup sites and
  CalGEM oil &amp; gas wells. Zone A (solid) is an approximate ~2.5 × 2 mile screening boundary
  centred on the Ladera Ranch CDP centroid; Zone B (dashed) is a 5-mile exposure ring. Site and
  well points use real database coordinates. <strong>No patient locations or residential
  addresses are plotted.</strong> Basemap © CARTO, © OpenStreetMap contributors.</figcaption>
</figure>

<h2>3. What relationships the data can — and cannot — establish</h2>
<div class="callout"><strong>On "correlation".</strong> This platform does not compute a
correlation between pesticide use and cancer, and no such figure should be quoted from it.
Doing so would require case-level data the platform does not hold, and an area-level
correlation would be an <em>ecological fallacy</em> — an association between aggregates that
does not imply anything about individuals. What the public data <em>can</em> support is
described below: spatial co-location, distance, timing overlap, and an observed-versus-expected
comparison under stated assumptions. Each is a screening signal, not evidence of cause.</div>

<div class="grid2">
  <div class="card"><h3>What can be shown</h3><ul>
    <li>Distance from the community to documented environmental sites and wells.</li>
    <li>Whether land-use eras overlap the residency and diagnosis window.</li>
    <li>Observed vs expected case counts under explicit, varied assumptions.</li>
    <li>Which chemicals are actually reported in regional landscape use.</li>
    <li>What the peer-reviewed literature does and does not support.</li>
  </ul></div>
  <div class="card"><h3>What cannot be shown</h3><ul>
    <li>That any individual was exposed to anything.</li>
    <li>Any dose, or contact between a person and a chemical.</li>
    <li>That a statistically valid cluster exists.</li>
    <li>Any causal link between an exposure and an illness.</li>
    <li>A meaningful pesticide↔cancer correlation coefficient.</li>
  </ul></div>
</div>

<h2 class="pb">4. Spatial relationships</h2>
<h3>4.1 Environmental and cleanup sites, by distance</h3>
{env_tbl}
<div class="callout"><strong>Pattern worth noting.</strong> The nearest former-agricultural
school sites — Plant Depot (arsenic, nitrate), Ambuehl (DDT, toxaphene) and San Juan Elementary
(arsenic, chlordane, DDT) — lie roughly 2.9–3.2 miles away and carry exactly the legacy residue
profile expected on former California citrus and row-crop land. Ladera Ranch was built on
comparable land. This is a <em>testable hypothesis</em>, not a finding.</div>

<h3>4.2 Oil &amp; gas wells (CalGEM)</h3>
{well_tbl}
<div class="callout warn"><strong>Corrected finding.</strong> Two plugged/abandoned exploratory
wells lie within about one mile of the community centroid — one at ~0.25 miles, effectively
within the footprint. A 2026 peer-reviewed California study reported a <em>suggestive,
non-significant</em> association between proximity to <strong>abandoned</strong> wells within
10 km and childhood Ewing sarcoma (OR 1.27, 95% CI 0.96–1.66), stronger in Hispanic children.
This places the community inside that exposure contrast and raises the priority of
characterising these wells. It does <strong>not</strong> establish exposure or causation: these
are mid-century plugged dry holes, and local groundwater is not used for supply.</div>

<h2>5. Temporal relationships</h2>
{lu_tbl}
<p>The community was built out roughly 1999–2006 on land used for cattle grazing with pockets
of dry-farmed barley, lemon/citrus orchard and tree nurseries. Children lived in Ladera Ranch
during active mass grading of that former agricultural land — a mechanistically coherent route
by which any legacy soil residue could have been mobilised as dust. Reported diagnoses span
2013–2026. The overlap is <em>plausible</em> and worth a residency-versus-construction timeline
analysis; it is not evidence that any exposure occurred.</p>

<h3>5.1 Does the timing actually work? Two mechanisms, opposite predictions</h3>
<p>Grading occurred ~1999–2006; diagnoses span 2013–2026. Many affected children were not born
when the earth was moved. That objection does real damage — but only to one of two mechanisms
that have been getting conflated.</p>
{table(["", "M1 — Construction-era dust", "M2 — Persistent soil residue"],
       [("<strong>What it is</strong>", "Grading mobilised buried residue as dust",
         "Arsenic &amp; organochlorines remain in surface soil"),
        ("<strong>Time-bound?</strong>", "<strong>Yes</strong> — an event, 1999–2006",
         "<strong>No</strong> — a standing condition"),
        ("<strong>Child present during grading?</strong>", "Required (incl. in utero)", "Not required"),
        ("<strong>Predicts</strong>", "Cases in birth cohorts ≤ ~2007",
         "Cases across <strong>all</strong> birth cohorts"),
        ("<strong>Effect of time passing</strong>", "Weakens steadily", "Does not weaken")])}
<p><strong>Why M2 does not decay.</strong> Arsenic is a chemical element — it never degrades,
and lead-arsenate orchard residues persist indefinitely. Organochlorines persist for decades,
and the evidence here is local and empirical rather than theoretical: DTSC found DDT, toxaphene
and arsenic in soil at former-farm school sites roughly three miles away, decades after
cultivation ceased. A child born in 2012 playing in that soil has the same contact opportunity
as one born in 2000.</p>
<p><strong>The arithmetic on M1.</strong> A child could have been present during grading only if
born on or before ~2007. The share of plausible pediatric ages (5–19) whose birth cohort
overlaps grading falls from <strong>93% for a 2013 diagnosis to 7% for a 2026 diagnosis</strong>.
By 2026 a case would have to be ~19 to have been present at all.</p>
<div class="callout warn"><strong>Net effect.</strong> "Grading mobilised dust and caused these
cancers" is <em>substantially weakened</em> for recent diagnoses and unavailable for children
born after ~2007. "The community sits on soil that may still contain arsenic and organochlorine
residues, which children contact through ordinary play" is <strong>untouched</strong> by the
timing objection. The leading hypothesis survives — in narrowed form.</div>
<div class="callout"><strong>The one datable Ewing case is a boundary case.</strong> Diagnosed
August 2024 at age ~17 implies birth roughly Aug 2006 – Aug 2007 — either in utero during the
final months of grading, or just after it ended. It cannot discriminate between M1 and M2.
<strong>Only one of the reported Ewing cases has both a published age and diagnosis year</strong>,
so no birth-cohort distribution can be built from public data. Since M1 and M2 predict opposite
distributions, birth year is a <em>discriminating test</em> — and it is exactly what is missing.
A further caveat cuts both ways: Ewing sarcoma's etiologic window is <strong>unknown</strong>, so
no latency assumption can rule either mechanism in or out.</div>

<h2>6. Observed versus expected — hypothetical scenarios</h2>
<p class="sm">Person-years, ages 0–19, 2013–2026 ≈ {PY_0_19:,}; peak-age (10–19) ≈ {PY_10_19:,}.
Expected = person-years × rate. SIR = observed ÷ expected. Intervals are exact Poisson limits
on the observed count.</p>
{sir_tbl}
<div class="disc"><strong>HYPOTHETICAL — not a finding.</strong> These scenarios use
<em>unverified</em> public case reports and <em>estimated</em> population. They do not confirm
a cluster and cannot substitute for an authorized California Cancer Registry analysis. Note
that California suppresses any rate built on fewer than 15 cases or a population under 10,000,
so a place-level Ewing sarcoma rate is <strong>statistically unpublishable</strong> — expected
counts must be modelled from national rates, not queried locally. Compare S4 with S5 to see how
severely a few cases move the result.</div>

<h2 class="pb">7. What is actually applied — the state's own pesticide data</h2>
<p>We downloaded and processed California DPR's 2023 Pesticide Use Report archive (official
machine-readable dataset, grade A1) — <strong>79,473 Orange County application records</strong>
— to test, rather than assume, how much reported use can be placed on a map.</p>
{pur_tbl}
<div class="callout warn"><strong>This corrected an earlier assumption.</strong> Landscape
maintenance <em>is</em> reported — 15,383 records, 110,664 lbs — but <strong>99.9% of those
records carry no township, range or section</strong>. Overall, 94.6% of Orange County records
have no location at all. Only agricultural and nursery categories are reliably geolocated.
Separately, a federal cadastral lookup places Ladera Ranch in unsectioned former land-grant
territory (T7S R7W / R8W, section 00). <strong>Taken together, the state's pesticide reporting
system is structurally incapable of placing an application inside Ladera Ranch.</strong> That
makes the HOA's own posted notices the only public location-specific evidence — and makes
obtaining the HOA and vendor application logs the highest-value near-term request.</div>

<h3>Top reported active ingredients, Orange County 2023</h3>
{top_pur}
<div class="callout ok"><strong>Glufosinate in context.</strong> The active ingredient named in
Ladera Ranch common-area notices is independently confirmed in the state dataset: 442 Orange
County records, 10,532 lbs, of which 336 records (10,177 lbs) were landscape maintenance. That
corroborates the documented application pattern as <strong>ordinary regional practice</strong>
— not as evidence of anything unusual, and not as evidence of causation. Glyphosate remains the
larger landscape herbicide (~30,052 lbs).</div>

<h2 class="pb">8. Legacy soil arsenic — does a developed surface matter?</h2>
<p>A fair objection: the community is fully built — grass, turf, concrete, asphalt. If legacy soil
residue is the concern, is a child ever in contact with it? And if arsenic is in the soil, wouldn't
lawn and backyard produce grown in that soil carry it anyway?</p>

<p><strong>Arsenic has no half-life.</strong> It is element 33 and cannot degrade. ATSDR states it
plainly: arsenic <em>"cannot be destroyed in the environment"</em> and <em>"tends to concentrate and
remain in upper soil layers indefinitely."</em> The "6.5 to 16 year half-life" figures in
circulation describe loss of the applied compound from the surface layer, not destruction of
arsenic, and should not be used. This is the fundamental contrast with the herbicides in use here,
which degrade in days to months.</p>

<table><thead><tr><th></th><th>Arsenic (legacy soil)</th><th>Landscape herbicides</th></tr></thead>
<tbody>
<tr><td><strong>Persistence</strong></td><td>Permanent — cannot degrade</td><td>Days to months (glufosinate ~7.4 d)</td></tr>
<tr><td><strong>Exposure pattern</strong></td><td>Continuous while resident</td><td>Repeated pulses, decaying between</td></tr>
<tr><td><strong>Dominant route</strong></td><td>Soil &amp; house-dust ingestion</td><td>Dermal contact with treated turf; track-in</td></tr>
<tr><td><strong>Effect of turf/hardscape</strong></td><td><strong>Barrier</strong> — reduces exposure</td><td><strong>Source</strong> — is the contact surface</td></tr>
<tr><td><strong>Established cancers</strong></td><td>Bladder, lung, skin (adults, decades)</td><td>Glyphosate: NHL (IARC 2A); glufosinate: none</td></tr>
<tr><td><strong>Ewing sarcoma link</strong></td><td><strong>None established</strong></td><td><strong>None established</strong></td></tr>
</tbody></table>

<div class="callout"><strong>The asymmetry that answers the question.</strong>
<strong>For arsenic, turf is a barrier. For turf herbicides, turf is the source.</strong> Arsenic sits
beneath the grass, so sod and hardscape put distance between a child and the affected layer. Herbicides
are applied <em>onto</em> the grass children then play on. "It's all paved over" cannot be evaluated
without first saying which hazard is being asked about.</div>

<p><strong>What surface cover does not close:</strong> the indoor house-dust reservoir (EPA weights
dust <em>above</em> soil — 60 vs 50 mg/day for ages 1–6 — and a randomised trial found yard coverings
cut track-in ~50% while entryway dust lead did not significantly change over a year); gardening and
digging; produce uptake; and disturbance events such as trenching or re-landscaping.</p>

<p><strong>Backyard produce is real but crop-dependent.</strong> Soil-to-plant transfer is
<em>more</em> efficient for arsenic than lead, ranking lettuce &gt; carrot &gt; bean &gt; tomato.
Fruiting vegetables can be grown safely even on substantially contaminated soil; leafy greens may
exceed standards where soil arsenic is elevated.</p>

<div class="callout warn"><strong>But context reframes all of it.</strong> Southern California
background arsenic — from 1,086 DTSC school-site samples across Orange and neighbouring counties —
has a mean of <strong>1.51 mg/kg</strong> and an upper bound of <strong>12 mg/kg</strong>. The
risk-based screening levels are <strong>0.11–0.68 mg/kg</strong>, i.e. roughly 18–110× <em>below</em>
natural background. DTSC notes the risk-based number sits "100-times below typical ambient
concentrations." <strong>Exceeding a screening level in Orange County is normal, not evidence of
contamination.</strong> Only a result above ~12 mg/kg would signify anything.</div>

<div class="disc"><strong>Revised standing: a LOW-PRIOR hypothesis.</strong> Six independent lines
lower it. (1) Background swamps the screening levels. (2) Measured bioavailability at the closest
analogue — Barber Orchard, a former lead-arsenate site — is <strong>0.31</strong>, so total soil
arsenic overstates dose ~3×. (3) The crop history doesn't match: lead arsenate was an
<em>apple and pear</em> insecticide, while this was citrus, barley and cattle land — any arsenical
here more plausibly came from sodium-arsenite <em>herbicide</em> use. (4) Mass grading in 1999–2006
likely diluted the historic plough layer. (5) At Middleport NY, soil arsenic of 19.9 mg/kg produced
<strong>no significant correlation</strong> with children's urinary arsenic (r = 0.137, p = 0.39);
rice consumption was the significant predictor. (6) A systematic review found the childhood-cancer
literature "does not seem to support an association between arsenic exposure and childhood cancers."
<strong>It is not excluded — it has never been measured here — but it should no longer be carried as
the leading environmental explanation.</strong></div>

<h2>9. Scientific literature</h2>
{lit_tbl}
<p>Ewing sarcoma is a genetically and ancestry-driven, overwhelmingly sporadic cancer with
<strong>no established environmental cause</strong>. Evidence tying pesticides specifically to
Ewing sarcoma is weak, mixed and farming-<em>proxy</em> based: the strongest positive signals
come from parental-farming studies with wide confidence intervals, while the largest and
highest-quality occupational study (Great Britain, 5,369 sarcoma cases) found <strong>no</strong>
pesticide or agriculture association. Two large California registry studies — on air pollution
and on oil/gas proximity — were null overall. <strong>No study links Ewing sarcoma to
glyphosate, glufosinate, 2,4-D, or any specific pyrethroid.</strong></p>

<h2>10. Alternative hypotheses that remain viable</h2>
<div class="grid2">
  <div class="card"><h3>Non-environmental</h3><ul>
    <li>Chance aggregation in a high-baseline-risk population.</li>
    <li>Germline susceptibility (GGAA-microsatellite / EWSR1 biology).</li>
    <li>Post-hoc boundary and ascertainment artifact.</li>
    <li>Exposure misclassification from residential mobility.</li>
  </ul></div>
  <div class="card"><h3>Environmental</h3><ul>
    <li>Legacy agricultural soil residue (highest priority, testable).</li>
    <li>Abandoned oil/gas well proximity.</li>
    <li>Construction-era soil disturbance and dust.</li>
    <li>Recycled irrigation water (under-characterised).</li>
    <li>Traffic-related air pollution (SR-241 corridor).</li>
  </ul></div>
</div>

<h2>11. Claims that remain unproven</h2>
<ul>
  <li>Causation by any exposure.</li>
  <li>That a true epidemiological cluster exists.</li>
  <li>The specific role of glufosinate or any named chemical.</li>
  <li>The "17 pesticides" figure and the higher "12 Ewing" case count.</li>
  <li>That legacy soil residue is present on the residential footprint.</li>
  <li>That recycled irrigation water carries any hazard.</li>
</ul>

<h2>12. What would most improve the analysis</h2>
<ol>
  <li><strong>Registry-confirmed case data</strong> from the California Cancer Registry —
      counts, diagnosis dates, ages, ancestry, and critically <strong>birth year</strong>.
      Birth year alone would discriminate between the two leading environmental mechanisms
      (see §5.1). Highest ability to change conclusions.</li>
  <li><strong>Individual residence histories</strong> across the etiologic window (consented,
      IRB-governed).</li>
  <li><strong>Soil sampling</strong> of the footprint and common areas for arsenic, DDT/DDE and
      toxaphene — the decisive test of the leading environmental hypothesis.</li>
  <li><strong>HOA and vendor application logs</strong> — now the <em>only</em> possible source
      of location-specific application data, and at risk of routine disposal.</li>
  <li><strong>The entitlement/EIR soil-testing record</strong> — did anyone ever test this land
      before building on it?</li>
</ol>

<h2>13. Evidence quality</h2>
{grade_tbl}
<p class="sm">Lower-grade sources are retained as leads and never silently promoted. Where
sources conflict — as they do on case counts — both values are recorded with their grades, and
the discrepancy is treated as a finding about data quality rather than smoothed away.</p>

<div class="callout"><strong>Correction log.</strong> An inherited study centroid was found to
be ~1.93 miles too far north; it was caught when this report's map figure showed the study zone
sitting north of the community. All site and well distances were recomputed. Former-agricultural
sites are closer than previously recorded, and two abandoned wells moved from ~2–2.7 miles to
~0.25 and ~0.77 miles. Full record: <code>research/CORRECTIONS.md</code>.</div>

<footer>
LEHRP — Ladera Environmental Health Research Platform · Independent research and
data-organization project · Generated {GENERATED} from {len(sources)} graded sources.
Reproduce: <code>python3 scripts/build_report.py</code>. This report is hypothesis-neutral and
privacy-protecting; health data is aggregate-only and no individual is identified.
Do not draw causal conclusions prematurely.
</footer>
</body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", action="store_true", help="HTML only, skip PDF")
    args = ap.parse_args()

    out_dir = os.path.join(ROOT, "reports")
    os.makedirs(out_dir, exist_ok=True)
    html_path = os.path.join(out_dir, "LEHRP_Preliminary_Report.html")
    pdf_path = os.path.join(out_dir, "LEHRP_Preliminary_Report.pdf")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(build_html())
    print(f"Wrote {html_path} ({os.path.getsize(html_path)//1024} KB)")

    if args.html:
        return
    if not os.path.exists(CHROME):
        sys.exit("Chrome not found; run with --html and convert manually.")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                    "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}",
                    "--virtual-time-budget=20000", f"file://{html_path}"],
                   check=True, capture_output=True)
    print(f"Wrote {pdf_path} ({os.path.getsize(pdf_path)//1024} KB)")


if __name__ == "__main__":
    main()
