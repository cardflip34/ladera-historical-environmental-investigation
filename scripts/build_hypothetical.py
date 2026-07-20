#!/usr/bin/env python3
"""Build the HYPOTHETICAL forced-conclusion causal assessment — formal edition.

A structured hypothesis-ranking exercise answering a counterfactual: "if forced to name the
single most probable explanation for the reported Ewing sarcoma pattern, what would it be?"

It is NOT a finding, NOT an agency determination, and it accuses no party. Probabilities are
elicited subjective judgement, not calculation.

Design follows the LEHRP visual system (CLAUDE.md): light ground, dark navy type, restrained
blue accent, serif body for sustained reading, no fear-based graphics.

Usage: python3 scripts/build_hypothetical.py
Output: reports/LEHRP_Hypothetical_Causal_Assessment.{html,pdf}
"""
import base64
import csv
import html
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
GENERATED = "18 July 2026"


def rd(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def e(s):
    return html.escape(str(s or ""))


def b64(rel):
    p = os.path.join(ROOT, rel)
    return base64.b64encode(open(p, "rb").read()).decode() if os.path.exists(p) else ""


sources = rd("research/source_registry/sources.csv")
lit = rd("research/literature/literature_registry.csv")
envs = rd("research/environmental_sites/sites.csv")
grades = {}
for s in sources:
    g = (s.get("reliabilityGrade") or "?").upper()
    grades[g] = grades.get(g, 0) + 1

wells = []
wp = os.path.join(ROOT, "data/geospatial/oil_gas_wells.geojson")
if os.path.exists(wp):
    wells = sorted([f["properties"] for f in json.load(open(wp))["features"]],
                   key=lambda p: float(p.get("distanceMiles", 99)))

PY_A, PY_P = 9115 * 14, 4906 * 14
POISSON = {4: (1.0899, 10.2416), 5: (1.6235, 11.6683), 6: (2.2019, 13.0595), 12: (6.2006, 20.9616)}
SCEN = [("S1 · Central", 6, PY_A, 3.0, "6 reported cases, ages 0–19, all-races SEER rate"),
        ("S2 · Ancestry-adjusted", 6, PY_A, 4.0, "rate raised for a 63.6% non-Hispanic-white population"),
        ("S3 · Peak-age window", 6, PY_P, 4.58, "ages 10–19 only, North American peak-age rate"),
        ("S4 · Conservative count", 4, PY_A, 4.0, "case definition tightened to 4"),
        ("S5 · Outlier count", 12, PY_A, 3.0, "the single-source '12 Ewing' figure"),
        ("S6 · Leave-one-out", 5, PY_A, 4.0, "one reported case removed as non-resident")]

# Elicited subjective probabilities — calibrated judgement, not calculation.
ALLOC = [
    ("No single environmental cause — chance aggregation in a high-baseline-risk population, amplified by ascertainment and post-hoc boundary selection", 55),
    ("A real excess whose cause is never identifiable", 20),
    ("Real excess with a contribution from abandoned oil &amp; gas well proximity", 8),
    ("Real excess with a contribution from legacy agricultural soil residue", 7),
    ("Real excess with a contribution from landscape herbicides", 5),
    ("An exposure or mechanism not yet considered", 5),
]

SCORE = [
    ("Landscape herbicides", "Moderate", "None", "Poor", "Poor", "Poor", "5%"),
    ("Legacy soil residue", "Moderate", "None", "Good", "Poor", "Weak", "7%"),
    ("Abandoned oil &amp; gas wells", "Weak", "<strong>Suggestive</strong>", "Good", "Unknown", "Weak", "8%"),
    ("Chance + ascertainment", "n/a", "n/a", "n/a", "n/a", "<strong>Strong</strong>", "55%"),
]

LM_MIX = [("Glyphosate, isopropylamine salt", 942, 22048.8), ("Diphacinone", 834, 1.8),
          ("Imidacloprid", 599, 1098.4), ("Bifenthrin", 558, 799.9), ("Dicamba", 520, 95.9),
          ("Carfentrazone-ethyl", 485, 53.5), ("2,4-D, 2-ethylhexyl ester", 479, 1315.4),
          ("Glyphosate, potassium salt", 419, 8002.8), ("Triclopyr, butoxyethyl ester", 362, 1329.4),
          ("<strong>Glufosinate-ammonium</strong>", 336, 10177.1), ("Strychnine", 331, 32.0),
          ("Trinexapac-ethyl", 316, 596.0)]

LITROWS = [
    ("Kendall 2020 (GB)", "5,369 sarcoma cases", "Paternal occupational", "Textile dust OR 1.93 (1.01–3.68); <strong>no agriculture/agrochemical association</strong>", "Weakens"),
    ("Valery 2002 (AU)", "106 cases / 344 controls", "Parental farming", "Farm residence OR 2.0 (1.0–3.9); farming father OR 3.5 (1.0–11.9)", "Supports"),
    ("Valery 2005 (pooled)", "199 cases / 1,451 controls", "Parental farming", "Paternal OR 2.3 (1.3–4.1); maternal OR 3.9 (1.6–9.9)", "Supports"),
    ("Clark 2026 (CA)", "558 cases / 27,800 controls", "Oil &amp; gas proximity", "Active wells OR 0.88 (0.72–1.08); <strong>abandoned OR 1.27 (0.96–1.66)</strong>", "Does not resolve"),
    ("Clark 2025 (CA)", "388 cases / 19,341 controls", "Perinatal PM₂.₅", "Q4 gestation OR 0.87 (0.61–1.25) — null overall", "Does not resolve"),
    ("Vinson 2011 (meta)", "40 studies", "Parental pesticides", "Leukaemia 1.48 (1.26–1.75); brain 1.49 (1.23–1.79); <strong>Ewing not reported</strong>", "Supports (other cancers)"),
    ("Spector 2021 (CI5)", "15,874 cases", "Ancestry / geography", "Ages 10–19 per million: N. America 4.58; E. Asia 1.59; African IRR 0.16", "Background"),
    ("Bradman 2019", "US cohorts", "Residential mobility", "55–58% of childhood-cancer cases moved between birth and diagnosis", "Methodological"),
]

CSS = """
@page { size: Letter; margin: 15mm 16mm 17mm; }
:root { color-scheme: light only;
  --paper:#ffffff; --sunk:#f4f7fb; --ink:#111c2e; --ink2:#46566d; --ink3:#6d7d93;
  --navy:#0b1e38; --accent:#1d4f8f; --rule:#c9d4e2; --rule2:#e3eaf3;
  --crit:#9a3030; --critbg:#fbeced; --warn:#a35f0c; --warnbg:#fdf4e8; --ok:#156132; --okbg:#eaf4ee;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }
* { box-sizing:border-box; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
html, body { background:#fff !important; color:var(--ink) !important; }
body { font-family:var(--serif); font-size:10.2pt; line-height:1.55; margin:0; }
@media (prefers-color-scheme: dark) {
  html, body { background:#fff !important; color:#111c2e !important; }
  h1,h2,h3,h4,p,li,td,th,div,span,strong,em,figcaption { color:#111c2e !important; }
  h1,h2,h3 { color:#0b1e38 !important; } .eyebrow,.snum { color:#1d4f8f !important; }
  th { background:#e8eef6 !important; } .verdict,.verdict * { color:#fff !important; }
}
h1,h2,h3,h4,.eyebrow,th,.meta,.sub,figcaption,.stat,.foot,.tag,.snum { font-family:var(--sans); }
h1 { font-size:21pt; color:var(--navy); margin:0 0 5pt; line-height:1.15; letter-spacing:-.3pt; font-weight:660; }
h2 { font-size:12.6pt; color:var(--navy); font-weight:650; margin:20pt 0 5pt; padding-bottom:3.5pt;
  border-bottom:1.5px solid var(--rule); page-break-after:avoid; }
h2 .snum { color:var(--accent); font-size:9.6pt; font-variant-numeric:tabular-nums; margin-right:6pt; }
h3 { font-size:10.6pt; color:var(--navy); font-weight:640; margin:13pt 0 4pt; page-break-after:avoid; }
p { margin:0 0 7pt; } strong { color:var(--navy); font-weight:640; }
.subtitle { font-family:var(--sans); font-size:13pt; font-weight:500; color:var(--ink2); margin-top:3pt; line-height:1.3; }
.eyebrow { color:var(--accent); font-size:7.8pt; font-weight:700; letter-spacing:.13em; text-transform:uppercase; }
.cover { border-bottom:3px solid var(--accent); padding-bottom:10pt; margin-bottom:12pt; }
.meta { font-size:8.6pt; color:var(--ink3); margin-top:6pt; }
.disc { background:var(--critbg); border-left:4px solid var(--crit); padding:8pt 10pt; font-size:9pt;
  border-radius:0 3px 3px 0; margin:10pt 0; }
.callout { background:#e9f1fb; border-left:4px solid var(--accent); padding:8pt 10pt; margin:9pt 0;
  border-radius:0 3px 3px 0; font-size:9.4pt; }
.warn { background:var(--warnbg); border-left-color:var(--warn); }
.ok { background:var(--okbg); border-left-color:var(--ok); }
.callout :last-child, .disc :last-child { margin-bottom:0; }
.verdict { background:var(--navy); color:#fff; padding:12pt 14pt; border-radius:4px; margin:12pt 0; }
.verdict * { color:#fff; } .verdict h3 { margin:0 0 5pt; font-size:11.4pt; }
table { width:100%; border-collapse:collapse; font-family:var(--sans); font-size:8.3pt;
  margin:7pt 0 10pt; page-break-inside:avoid; }
th { background:var(--sunk); color:var(--navy); text-align:left; padding:4pt 6pt; font-size:7.3pt;
  text-transform:uppercase; letter-spacing:.045em; border-bottom:1.5px solid var(--rule); font-weight:650; }
td { padding:4pt 6pt; border-bottom:1px solid var(--rule2); vertical-align:top; }
td.n, th.n { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
tbody tr:nth-child(even) td { background:#f8fafd; }
.sub { font-size:7.4pt; color:var(--ink3); margin-top:1pt; }
.stats { display:grid; grid-template-columns:repeat(4,1fr); gap:7pt; margin:10pt 0; }
.stat { border:1px solid var(--rule); border-radius:4px; padding:6pt 8pt; }
.stat b { display:block; font-size:14pt; color:var(--navy); font-variant-numeric:tabular-nums; line-height:1.05; font-weight:660; }
.stat span { display:block; font-size:6.9pt; color:var(--ink3); text-transform:uppercase; letter-spacing:.045em; margin-top:2pt; }
figure { margin:9pt 0 12pt; page-break-inside:avoid; }
figure img { width:100%; border:1px solid var(--rule); border-radius:4px; }
figcaption { font-size:8pt; color:var(--ink3); margin-top:5pt; line-height:1.45; }
ul, ol { margin:0 0 7pt; padding-left:15pt; } li { margin-bottom:3pt; }
.bar { height:11px; background:var(--sunk); border-radius:2px; overflow:hidden; border:1px solid var(--rule2); }
.bar i { display:block; height:100%; background:var(--accent); }
.tag { display:inline-block; font-size:7pt; font-weight:650; padding:1pt 5pt; border-radius:8pt;
  background:var(--sunk); color:var(--ink2); border:1px solid var(--rule); }
.pb { page-break-before:always; }
.foot { margin-top:16pt; padding-top:8pt; border-top:1px solid var(--rule); font-size:7.8pt; color:var(--ink3); line-height:1.5; }
"""


def rows(data):
    return "".join("<tr>" + "".join(c if isinstance(c, str) and c.startswith("<td") else f"<td>{c}</td>"
                                    for c in r) + "</tr>" for r in data)


def build_body():
    img = b64("reports/assets/map_figure_web.jpg")

    sir = ""
    for label, obs, py, rate, note in SCEN:
        exp = py * rate / 1_000_000
        lo, hi = POISSON[obs]
        sir += (f'<tr><td><strong>{label}</strong><div class="sub">{note}</div></td>'
                f'<td class="n">{obs}</td><td class="n">{rate:.2f}</td><td class="n">{exp:.3f}</td>'
                f'<td class="n"><strong>{obs/exp:.1f}</strong></td>'
                f'<td class="n">{lo/exp:.1f} – {hi/exp:.1f}</td></tr>')

    env = "".join(f'<tr><td>{e(x["name"])}</td><td>{e(x["contaminants"])[:64]}</td>'
                  f'<td class="n">{x["approxDistanceMiles"]}</td></tr>'
                  for x in sorted([y for y in envs if y.get("approxDistanceMiles")],
                                  key=lambda y: float(y["approxDistanceMiles"]))[:10])

    wl = "".join(f'<tr><td>{e(w["name"])}</td><td>{e(w["status"])}</td>'
                 f'<td class="n"><strong>{w["distanceMiles"]}</strong></td></tr>' for w in wells)

    lm = "".join(f'<tr><td>{c}</td><td class="n">{n:,}</td><td class="n">{p:,.1f}</td></tr>'
                 for c, n, p in LM_MIX)

    litr = "".join(f'<tr><td><strong>{a}</strong></td><td>{b}</td><td>{c}</td><td>{d}</td>'
                   f'<td><span class="tag">{f_}</span></td></tr>' for a, b, c, d, f_ in LITROWS)

    sc = "".join(f'<tr><td><strong>{a}</strong></td><td>{b}</td><td>{c}</td><td>{d}</td>'
                 f'<td>{f_}</td><td>{g}</td><td class="n"><strong>{h}</strong></td></tr>'
                 for a, b, c, d, f_, g, h in SCORE)

    al = "".join(f'<tr><td>{n}</td><td class="n"><strong>{p}%</strong></td>'
                 f'<td style="width:96pt"><div class="bar"><i style="width:{p*1.75:.0f}%"></i></div></td></tr>'
                 for n, p in ALLOC)

    return f"""<div class="cover">
<div class="eyebrow">Ladera Environmental Health Research Platform · Analytical Exercise</div>
<h1>Hypothetical causal assessment</h1>
<div class="subtitle">If forced to name a single most probable explanation for the reported
Ewing sarcoma pattern</div>
<div class="meta">Formal edition · {GENERATED} · Companion to Preliminary Report v0.7 ·
Compiled from {len(sources)} graded sources · <strong>Not a finding. Not an agency determination.</strong></div>
</div>

<div class="disc">
<p><strong>Read this first.</strong> This document answers a counterfactual question: <em>if one had
to commit to a single most probable explanation using only the assembled evidence, what would it
be?</em> It is an exercise in <strong>structured hypothesis ranking</strong> — the reasoning an
epidemiological consultant performs before any determination exists.</p>
<p>It does <strong>not</strong> establish causation. It does <strong>not</strong> accuse any
organisation, contractor, manufacturer, agency or individual of causing any illness. The
probabilities are <strong>elicited subjective judgement</strong>, not calculations. An official
multi-agency review — Orange County Health Care Agency, California Cancer Registry, UC Irvine, and
the County Agricultural Commissioner — is underway and has not reported; nothing here anticipates or
substitutes for it. Health data is aggregate-only; no individual is identified.</p>
</div>

<div class="stats">
<div class="stat"><b>{len(sources)}</b><span>Graded sources</span></div>
<div class="stat"><b>79,473</b><span>Pesticide records</span></div>
<div class="stat"><b>{len(lit)}</b><span>Literature entries</span></div>
<div class="stat"><b>{len(envs)}</b><span>Environmental sites</span></div>
</div>

<h2><span class="snum">1</span>The question, decomposed</h2>
<p>"What caused the cluster?" smuggles in two assumptions — that a cluster exists, and that it has an
identifiable cause. A disciplined answer must address both. The question is therefore split:</p>
<ol>
<li><strong>Is there a real excess?</strong> Do registry-verifiable Ewing sarcoma diagnoses exceed the
correctly age- and ancestry-adjusted expectation?</li>
<li><strong>If so, is it attributable?</strong> Does any candidate survive both an
<em>exposure-opportunity</em> test and a <em>disease-specificity</em> test?</li>
<li><strong>Which candidate is most probable?</strong></li>
</ol>
<p>Public discussion collapses these into one. Keeping them apart is what makes a defensible
conclusion possible.</p>

<h3>1.1 Scoring criteria</h3>
<table><thead><tr><th style="width:26%">Criterion</th><th>What it asks</th></tr></thead><tbody>
<tr><td><strong>Exposure opportunity</strong></td><td>Could children plausibly have contacted this at all?</td></tr>
<tr><td><strong>Disease specificity</strong></td><td>Any established or suggested link to <em>Ewing sarcoma</em> — not to cancer generally?</td></tr>
<tr><td><strong>Temporal fit</strong></td><td>Does the exposure window overlap the relevant birth cohorts?</td></tr>
<tr><td><strong>Dose plausibility</strong></td><td>Are concentration, persistence and bioavailability sufficient to matter?</td></tr>
<tr><td><strong>Base-rate fit</strong></td><td>How often has this <em>class</em> of explanation proved correct in comparable investigations?</td></tr>
</tbody></table>
<p>The fifth criterion is the one usually omitted, and it carries the most weight. Cluster
investigations have a long and consistent track record; ignoring it is the principal route by which
motivated reasoning enters.</p>

<h2><span class="snum">2</span>Population and baseline expectation</h2>
<p>Ladera Ranch CDP (FIPS 0639114), American Community Survey 2020–2024:</p>
<table><thead><tr><th>Measure</th><th class="n">Value</th><th>Note</th></tr></thead><tbody>
<tr><td>Total population</td><td class="n">23,793</td><td>26,170 at the 2020 Census; 22,980 in 2010</td></tr>
<tr><td>Children aged 0–19</td><td class="n">9,115</td><td>38.3% of population — an unusually young community</td></tr>
<tr><td>Aged 10–19 (Ewing peak window)</td><td class="n">4,906</td><td>Peak incidence falls at 10–15</td></tr>
<tr><td>Non-Hispanic white</td><td class="n">63.6%</td><td><strong>Materially raises the expected count</strong></td></tr>
<tr><td>Asian / Hispanic / Black (NH)</td><td class="n">13.6% / 12.9% / 0.9%</td><td>Lower-incidence ancestries</td></tr>
<tr><td>Median household income</td><td class="n">$184,458</td><td>68% hold a bachelor's degree or above</td></tr>
<tr><td>Person-years, ages 0–19, 2013–2026</td><td class="n">{PY_A:,}</td><td>Peak-age person-years: {PY_P:,}</td></tr>
</tbody></table>

<h3>2.1 Reference incidence rates</h3>
<table><thead><tr><th>Population</th><th class="n">Rate</th><th>Units</th><th>Source basis</th></tr></thead><tbody>
<tr><td>US, all ages and races</td><td class="n">2.93</td><td>per million/yr</td><td>SEER 1973–2004</td></tr>
<tr><td>US, ages 0–19 (central estimate)</td><td class="n">3.0</td><td>per million/yr</td><td>SEER-based</td></tr>
<tr><td>North America, ages 10–19</td><td class="n">4.58</td><td>per million/yr</td><td>CI5 2003–2012 peak</td></tr>
<tr><td>Southern Europe / Western Europe, 10–19</td><td class="n">7.75 / 6.93</td><td>per million/yr</td><td>Spector 2021</td></tr>
<tr><td>East Asia, ages 10–19</td><td class="n">1.59</td><td>per million/yr</td><td>Spector 2021</td></tr>
<tr><td>Ancestry IRR vs European</td><td class="n">0.16</td><td>ratio</td><td>African; East Asian 0.30; Pacific Islander 2.18</td></tr>
<tr><td>All pediatric cancer, California 0–19</td><td class="n">18.2</td><td>per 100,000/yr</td><td>CCR/SEER 2012–2016</td></tr>
</tbody></table>
<div class="callout"><p><strong>Why ancestry governs this analysis.</strong> Ewing sarcoma incidence
is roughly <strong>nine times higher</strong> in people of European ancestry than African ancestry —
a differential driven by germline GGAA-microsatellite architecture, not environment. Applying an
all-races rate to a 63.6% non-Hispanic-white population <em>understates the expected count and
inflates every standardised incidence ratio downstream.</em></p></div>

<h2 class="pb"><span class="snum">3</span>Observed versus expected</h2>
<p>Expected = person-years × rate. SIR = observed ÷ expected. Intervals are exact Poisson limits on
the observed count.</p>
<table><thead><tr><th>Scenario</th><th class="n">Obs.</th><th class="n">Rate /M</th><th class="n">Expected</th>
<th class="n">SIR</th><th class="n">95% CI</th></tr></thead><tbody>{sir}</tbody></table>
<div class="disc"><p><strong>Hypothetical — not a finding.</strong> Every row uses
<em>unverified</em> public case reports and <em>estimated</em> population. California suppresses any
rate built on fewer than 15 cases or a population under 10,000, so a place-level Ewing sarcoma rate
is <strong>statistically unpublishable</strong>. Compare S4 with S5: the same community moves from
SIR 7.8 to 31.3 purely on case definition.</p></div>

<h3>3.1 The numerator problem</h3>
<table><thead><tr><th>Reported count</th><th>Scope as stated</th><th>Source grade</th></tr></thead><tbody>
<tr><td><strong>"At least 6"</strong> Ewing sarcoma since 2013</td><td>Ladera Ranch only, Ewing only</td><td>B2 — local TV news</td></tr>
<tr><td>"About a dozen" rare cancers</td><td><strong>Mixed cancer types across multiple cities</strong></td><td>B2 — same outlet</td></tr>
<tr><td>"12 Ewing sarcoma"</td><td>Ladera Ranch, Ewing only</td><td>C — single low-reliability outlet</td></tr>
</tbody></table>
<p>Only one of the reported Ewing cases carries both a published age and a diagnosis year. The widely
repeated "dozen" explicitly aggregates <em>different cancers in different cities</em> — the textbook
signature of ascertainment inflation rather than of a cluster. No count has been registry-verified,
and the county's initial review, conducted with registry access, "did not find a particular
pattern."</p>

<h2><span class="snum">4</span>The evidence base</h2>
<figure><img src="data:image/jpeg;base64,{img}" alt="Map of the Ladera Ranch study area showing study zones, DTSC EnviroStor cleanup sites and CalGEM oil and gas wells">
<figcaption><strong>Figure 1.</strong> Study zones (approximate), DTSC EnviroStor cleanup sites, and
CalGEM oil &amp; gas wells. Two plugged exploratory wells lie within roughly a mile of the community
centroid — a relationship that emerged only after correcting a 1.93-mile centroid error inherited
from the original project brief. No patient locations are plotted. Basemap © CARTO, ©
OpenStreetMap contributors.</figcaption></figure>

<h3>4.1 Environmental and cleanup sites, by corrected distance</h3>
<table><thead><tr><th>Site</th><th>Contaminants recorded</th><th class="n">Miles</th></tr></thead><tbody>{env}</tbody></table>
<p>Every legacy-pesticide record above is a <strong>school</strong> site. Not because schools received
worse land, but because California Education Code §§17210 / 17213.1 mandates a Phase I assessment and
DTSC review before a district acquires property — and <strong>no equivalent mandate applies to
residential subdivisions.</strong> The absence of soil data for the residential footprint is a
regulatory artifact, not evidence that the soil is clean.</p>

<h3>4.2 Oil &amp; gas wells (CalGEM)</h3>
<table><thead><tr><th>Well</th><th>Status</th><th class="n">Miles</th></tr></thead><tbody>{wl}</tbody></table>
<p>Two plugged wells within one mile; three within 5 km; all six within 10 km — the exposure contrast
used by the only published study reporting a Ewing-specific environmental association.</p>

<h2 class="pb"><span class="snum">5</span>What is actually applied</h2>
<p>California's 2023 Pesticide Use Report archive was downloaded and processed in full:
<strong>79,473 Orange County application records</strong> across 382 chemicals and 45 site types.</p>
<table><thead><tr><th>Site type</th><th class="n">Records</th><th class="n">Pounds</th><th class="n">Located</th><th class="n">% located</th></tr></thead><tbody>
<tr><td>Structural pest control</td><td class="n">55,442</td><td class="n">403,983</td><td class="n">0</td><td class="n">0.0%</td></tr>
<tr><td><strong>Landscape maintenance</strong></td><td class="n">15,383</td><td class="n">110,664</td><td class="n">22</td><td class="n"><strong>0.1%</strong></td></tr>
<tr><td>Nursery — outdoor containers</td><td class="n">2,990</td><td class="n">4,788</td><td class="n">2,982</td><td class="n">99.7%</td></tr>
<tr><td>Golf course turf</td><td class="n">1,375</td><td class="n">56,171</td><td class="n">0</td><td class="n">0.0%</td></tr>
<tr><td>Rights of way</td><td class="n">1,130</td><td class="n">34,192</td><td class="n">48</td><td class="n">4.2%</td></tr>
<tr><td>Agriculture (fruiting pepper)</td><td class="n">183</td><td class="n">13,411</td><td class="n">183</td><td class="n">100.0%</td></tr>
</tbody></table>
<div class="callout warn"><p><strong>Overall, 94.6% of Orange County pesticide records carry no
location at all.</strong> Landscape maintenance <em>is</em> reported — but 99.9% of those records lack
township, range and section. Only agricultural and nursery categories are reliably geolocated.
Compounding this, a federal cadastral query places Ladera Ranch in <strong>unsectioned former
land-grant territory</strong> (T7S R7W / R8W, section 00). <strong>The state's reporting system is
structurally incapable of placing a pesticide application inside this community.</strong></p></div>

<h3>5.1 Landscape-maintenance chemical mix, Orange County 2023</h3>
<table><thead><tr><th>Active ingredient</th><th class="n">Records</th><th class="n">Pounds</th></tr></thead><tbody>{lm}</tbody></table>
<div class="callout ok"><p><strong>Glufosinate in regional context.</strong> The ingredient named in
Ladera Ranch application notices accounts for <strong>442 county records and 10,532 lbs</strong> in
2023, of which <strong>336 records and 10,177 lbs</strong> were landscape maintenance — 97% of its
poundage. Glyphosate remains larger across both salts (1,361 records, ~30,052 lbs). The community's
herbicide programme is <strong>unremarkable for the region.</strong> Any causal account must explain
why <em>here</em> and not in every comparable South Orange County community served by the same
contractors and products.</p></div>

<h2><span class="snum">6</span>Temporal analysis</h2>
<p>Mass grading of the former agricultural land ran roughly <strong>1999–2006</strong>; reported
diagnoses span <strong>2013–2026</strong>. A child could have been present during grading, including
in utero, only if born on or before about 2007.</p>
<table><thead><tr><th>Diagnosis year</th><th class="n">Pediatric ages whose birth cohort overlaps grading</th><th class="n">Share</th></tr></thead><tbody>
<tr><td>2013</td><td class="n">14 of 15</td><td class="n">93%</td></tr>
<tr><td>2016</td><td class="n">11 of 15</td><td class="n">73%</td></tr>
<tr><td>2019</td><td class="n">8 of 15</td><td class="n">53%</td></tr>
<tr><td>2022</td><td class="n">5 of 15</td><td class="n">33%</td></tr>
<tr><td>2024</td><td class="n">3 of 15</td><td class="n">20%</td></tr>
<tr><td>2026</td><td class="n">1 of 15</td><td class="n"><strong>7%</strong></td></tr>
</tbody></table>
<p>This separates two mechanisms that are routinely conflated. <strong>Construction-era dust</strong>
is a time-bound event requiring presence during grading — substantially weakened for recent
diagnoses, and unavailable for children born after ~2007. <strong>Persistent soil residue</strong> is
a standing condition, unaffected by how long ago grading occurred. The single datable Ewing case
(diagnosed August 2024, age ~17, implying birth between about August 2006 and August 2007) sits
precisely on the boundary and discriminates nothing.</p>

<h2><span class="snum">7</span>Quantitative context for the soil hypothesis</h2>
<table><thead><tr><th>Benchmark</th><th class="n">Value</th><th>Significance</th></tr></thead><tbody>
<tr><td>Southern California background arsenic (mean)</td><td class="n">1.51 mg/kg</td><td>DTSC, n = 1,086 school-site samples</td></tr>
<tr><td><strong>Background upper bound</strong></td><td class="n"><strong>12 mg/kg</strong></td><td>The operative comparison for any local result</td></tr>
<tr><td>EPA residential screening level</td><td class="n">0.68 mg/kg</td><td><em>Below</em> virtually all natural background</td></tr>
<tr><td>California DTSC screening level</td><td class="n">0.11 mg/kg</td><td>~100× below typical ambient concentrations</td></tr>
<tr><td>Washington State cleanup trigger</td><td class="n">20 ppm</td><td>Formal former-orchard programme</td></tr>
<tr><td>Measured bioavailability, former orchard</td><td class="n">0.31</td><td>Barber Orchard — total overstates dose ~3×</td></tr>
<tr><td>Child soil / dust ingestion, ages 1–6</td><td class="n">50 / 60 mg/day</td><td>Regulators weight dust <em>above</em> soil</td></tr>
</tbody></table>
<div class="callout warn"><p><strong>Exceeding a screening level in Orange County is normal, not
evidence of contamination.</strong> Only a result above roughly 12 mg/kg would signify anything. At a
comparable community, soil arsenic of 19.9 mg/kg produced <strong>no significant correlation</strong>
with children's urinary arsenic (r = 0.137, p = 0.39); rice consumption was the significant
predictor. Arsenic's established cancers are bladder, lung and skin — in adults, after decades.</p></div>

<h2 class="pb"><span class="snum">8</span>Literature bearing on the question</h2>
<table><thead><tr><th>Study</th><th>Size</th><th>Exposure</th><th>Effect estimate</th><th>Direction</th></tr></thead><tbody>{litr}</tbody></table>
<p>Ewing sarcoma has <strong>no established environmental cause anywhere in the published
literature.</strong> It is defined by an EWSR1-FLI1 fusion (~85% of tumours) arising postnatally on a
strongly ancestry-patterned germline background. The strongest positive signals are parental-farming
<em>proxies</em> with confidence intervals touching 1.0; the largest and most rigorous occupational
study found <strong>no</strong> agriculture or agrochemical association. No study links Ewing sarcoma
to glyphosate, glufosinate, 2,4-D, or any specific pyrethroid.</p>

<h3>8.1 Precedent from comparable investigations</h3>
<table><thead><tr><th>Investigation</th><th>Finding</th></tr></thead><tbody>
<tr><td>CDC / CSTE guidance</td><td>~1,000 inquiries per year; investigations "unlikely to find an associated environmental contaminant"</td></tr>
<tr><td>Wake County, NC (Ewing sarcoma)</td><td>Observed did <strong>not</strong> exceed expected; no common exposure identified</td></tr>
<tr><td>Washington County, PA (Ewing sarcoma)</td><td>Local excess ~3× expected noted; <strong>not attributed</strong> to any environmental cause</td></tr>
<tr><td>McFarland, CA (mixed pediatric)</td><td>~3× expected; investigation <strong>unresolved</strong>; four pesticides examined and dismissed</td></tr>
</tbody></table>

<h2><span class="snum">9</span>Hypothesis scoring</h2>
<table><thead><tr><th>Hypothesis</th><th>Exposure</th><th>Disease fit</th><th>Temporal</th><th>Dose</th><th>Base rate</th><th class="n">P</th></tr></thead><tbody>{sc}</tbody></table>

<h3>9.1 Landscape herbicides</h3>
<p>The dominant public hypothesis and, on evidence, the <strong>weakest</strong> environmental
candidate. Exposure opportunity is genuine — children play on treated turf and residues track indoors.
Everything else fails. No regulator classifies glufosinate as a carcinogen; glyphosate's IARC 2A
concerns lymphoma; none is linked to Ewing sarcoma. Glufosinate's soil half-life is ~7.4 days, so
exposure is pulsed rather than cumulative. Documented applications (2023–25) largely post-date the
relevant windows for diagnoses in 2013–24. And the state's own data shows the practice is regionally
ordinary.</p>

<h3>9.2 Legacy agricultural soil residue</h3>
<p>Stronger on exposure logic — arsenic never degrades, so it is a standing condition, and house dust,
gardening and produce uptake survive surface cover. But background swamps the screening levels;
measured bioavailability is ~0.31; lead arsenate was an <em>apple and pear</em> insecticide whereas
this was citrus, barley and cattle land; mass grading likely diluted the plough layer; biomarker
studies at comparable concentrations are null; and a systematic review found the childhood-cancer
literature does not support an arsenic association.</p>

<h3>9.3 Abandoned oil &amp; gas well proximity</h3>
<p>The <strong>only candidate carrying a disease-matched published signal</strong>: OR 1.27 (95% CI
0.96–1.66) for abandoned wells within 10 km, from a 558-case California study. The corrected geography
places this community inside that contrast. Against it — the association is <strong>not statistically
significant</strong>, the interval crosses 1, the effect was stronger in Hispanic children (12.9% of
this population), the same study found <em>no</em> association with active wells, and these are
mid-century plugged dry holes rather than production wells. Local groundwater is not used for supply.</p>

<h3>9.4 Chance in a high-baseline-risk population</h3>
<p>Not a fallback but a substantive hypothesis, usually dismissed without examination because it is
unsatisfying. The base rate is decisive; the expected count is higher than public framing assumes
because of ancestry; the numerator is inflated by construction; the boundary was drawn around the
observed cases; and rare-disease small numbers are inherently unstable — moving from 6 cases to 4
halves the apparent ratio.</p>

<h2><span class="snum">10</span>Conclusion</h2>
<div class="verdict">
<h3>Most probable explanation</h3>
<p style="margin-bottom:0"><strong>That there is no single environmental cause — that the apparent
excess is most likely chance aggregation in a population with an elevated ancestry-specific baseline,
amplified by media- and attorney-driven case ascertainment and a boundary drawn around the observed
cases.</strong></p>
</div>
<p>Forced to name one answer, that is it, and it is not a hedge. It carries the strongest base-rate
support, aligns with the county's own initial review, and is the only explanation that does not
require positing a mechanism never demonstrated for this cancer anywhere in the literature.</p>
<p><strong>If the premise is granted — that a real, registry-confirmed excess exists — the most
probable environmental contributor is proximity to abandoned oil and gas wells</strong>, solely
because it is the only candidate with a Ewing-specific published association and the corrected
geography places the community inside that exposure contrast. That signal is weak, non-significant,
and held weakly.</p>
<p><strong>The dominant public hypothesis — landscape herbicides — is the least probable of the
environmental candidates.</strong></p>

<h3>10.1 Probability allocation</h3>
<p class="sub" style="font-size:8.4pt">Elicited subjective judgement, not calculation. Sums to 100%.</p>
<table><thead><tr><th>Explanation</th><th class="n">P</th><th></th></tr></thead><tbody>{al}</tbody></table>

<h2><span class="snum">11</span>What would change this conclusion</h2>
<ol>
<li><strong>Registry confirmation of counts and residency.</strong> Six or more Ewing sarcoma
diagnoses confirmed among children resident during 2013–2026 would drop the chance allocation from
55% to plausibly below 30%, making "real excess" the leading branch. <em>This single dataset moves
more probability than everything else combined.</em></li>
<li><strong>Birth years.</strong> Cases clustered in births ≤2007 would revive construction-era dust;
cases spread across birth years would eliminate it while leaving persistent residue intact.</li>
<li><strong>Soil and house-dust sampling.</strong> Arsenic above ~12 mg/kg on the footprint, with the
bioavailable fraction measured, would raise the soil branch materially.</li>
<li><strong>HOA and vendor application records.</strong> Evidence of application intensity genuinely
anomalous <em>for the region</em> — not merely present — would raise the herbicide branch.</li>
<li><strong>Well-integrity data.</strong> Documented leakage or soil-gas anomalies at the two nearest
plugged wells would strengthen the only disease-matched candidate.</li>
</ol>

<h2><span class="snum">12</span>What this document does not say</h2>
<div class="callout warn"><ul style="margin-bottom:0">
<li>It does <strong>not</strong> state that any illness was caused by any party, product or practice.</li>
<li>It does <strong>not</strong> conclude that the families' concerns are unfounded. A low prior on a
specific mechanism is a statement about evidence, not a verdict that nothing happened. These
illnesses warrant investigation; that is why the official review exists.</li>
<li>It does <strong>not</strong> anticipate that review. The agencies hold registry data this project
cannot access, and their findings supersede this entirely.</li>
<li>It is <strong>not</strong> evidence in any proceeding and should not be represented as such.</li>
</ul></div>

<p class="foot">Ladera Environmental Health Research Platform · Hypothetical causal assessment, formal
edition, generated {GENERATED} from {len(sources)} graded sources
(A1 {grades.get('A1',0)} · A2 {grades.get('A2',0)} · B1 {grades.get('B1',0)} · B2 {grades.get('B2',0)} ·
C {grades.get('C',0)} · D {grades.get('D',0)}). Probabilities are elicited judgement, not calculation.
An analytical exercise — not a finding, not an agency determination. Do not represent it as evidence
of causation.</p>"""




WEB_CSS = """
:root{ color-scheme:light;
  --paper:#fff; --sunk:#f4f7fb; --ink:#111c2e; --ink2:#46566d; --ink3:#6d7d93;
  --navy:#0b1e38; --accent:#1d4f8f; --rule:#c9d4e2; --rule2:#e3eaf3;
  --crit:#9a3030; --critbg:#fbeced; --warn:#a35f0c; --warnbg:#fdf4e8; --ok:#156132; --okbg:#eaf4ee;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }
@media (prefers-color-scheme:dark){ :root{
  --paper:#0e141d; --sunk:#161e29; --ink:#dde5ef; --ink2:#a3b1c4; --ink3:#7d8b9f;
  --navy:#e8eef6; --accent:#7fa9dd; --rule:#2b3646; --rule2:#212b38;
  --crit:#e08585; --critbg:#2a1719; --warn:#e0a760; --warnbg:#2a2114; --ok:#7fc79a; --okbg:#152418; } }
:root[data-theme="dark"]{
  --paper:#0e141d; --sunk:#161e29; --ink:#dde5ef; --ink2:#a3b1c4; --ink3:#7d8b9f;
  --navy:#e8eef6; --accent:#7fa9dd; --rule:#2b3646; --rule2:#212b38;
  --crit:#e08585; --critbg:#2a1719; --warn:#e0a760; --warnbg:#2a2114; --ok:#7fc79a; --okbg:#152418; }
:root[data-theme="light"]{
  --paper:#fff; --sunk:#f4f7fb; --ink:#111c2e; --ink2:#46566d; --ink3:#6d7d93;
  --navy:#0b1e38; --accent:#1d4f8f; --rule:#c9d4e2; --rule2:#e3eaf3;
  --crit:#9a3030; --critbg:#fbeced; --warn:#a35f0c; --warnbg:#fdf4e8; --ok:#156132; --okbg:#eaf4ee; }
*{box-sizing:border-box}
.doc{background:var(--paper);color:var(--ink);font-family:var(--serif);font-size:17px;
  line-height:1.6;padding:clamp(20px,5vw,60px) clamp(16px,5vw,36px) 80px;
  display:flex;flex-direction:column;align-items:center;min-height:100vh}
.wrap{width:100%;max-width:46rem}
h1,h2,h3,.eyebrow,th,.meta,.sub,figcaption,.stat,.foot,.tag,.snum,.subtitle{font-family:var(--sans)}
h1{font-size:clamp(1.7rem,4.2vw,2.3rem);color:var(--navy);margin:0 0 .3rem;line-height:1.15;
  letter-spacing:-.02em;font-weight:660;text-wrap:balance}
.subtitle{font-size:clamp(1rem,2.2vw,1.2rem);font-weight:500;color:var(--ink2);line-height:1.35;text-wrap:balance}
h2{font-size:1.14rem;color:var(--navy);font-weight:650;margin:2.6rem 0 .35rem;padding-bottom:.4rem;
  border-bottom:1px solid var(--rule);text-wrap:balance}
h2 .snum{color:var(--accent);font-size:.86rem;font-variant-numeric:tabular-nums;margin-right:.55rem}
h3{font-size:1rem;color:var(--navy);font-weight:640;margin:1.7rem 0 .3rem}
p{margin:0 0 .95em;max-width:70ch} strong{color:var(--navy);font-weight:640}
.eyebrow{color:var(--accent);font-size:.7rem;font-weight:700;letter-spacing:.13em;text-transform:uppercase;margin-bottom:.7rem}
.cover{border-bottom:3px solid var(--accent);padding-bottom:1rem;margin-bottom:1.3rem}
.meta{font-size:.82rem;color:var(--ink3);margin-top:.7rem}
.disc{background:var(--critbg);border-left:4px solid var(--crit);padding:.85rem 1rem;
  font-size:.93rem;border-radius:0 4px 4px 0;margin:1.1rem 0}
.callout{background:#e9f1fb;border-left:4px solid var(--accent);padding:.85rem 1rem;margin:1rem 0;
  border-radius:0 4px 4px 0;font-size:.95rem}
@media (prefers-color-scheme:dark){.callout{background:#16202e}}
:root[data-theme="dark"] .callout{background:#16202e}
.warn{background:var(--warnbg);border-left-color:var(--warn)}
.ok{background:var(--okbg);border-left-color:var(--ok)}
.callout :last-child,.disc :last-child{margin-bottom:0}
.verdict{background:var(--navy);padding:1.1rem 1.25rem;border-radius:5px;margin:1.3rem 0}
.verdict,.verdict *{color:#fff}
:root[data-theme="dark"] .verdict,:root[data-theme="dark"] .verdict *{color:#0e141d}
@media (prefers-color-scheme:dark){.verdict,.verdict *{color:#0e141d}}
.verdict h3{margin:0 0 .4rem;font-size:1.08rem}
.scroll,.tw{overflow-x:auto;-webkit-overflow-scrolling:touch}
table{width:100%;border-collapse:collapse;font-family:var(--sans);font-size:.83rem;margin:.8rem 0 1.1rem}
th{background:var(--sunk);color:var(--navy);text-align:left;padding:.45rem .6rem;font-size:.68rem;
  text-transform:uppercase;letter-spacing:.045em;border-bottom:1.5px solid var(--rule);font-weight:650;white-space:nowrap}
td{padding:.45rem .6rem;border-bottom:1px solid var(--rule2);vertical-align:top}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
tbody tr:nth-child(even) td{background:var(--sunk)}
.sub{font-size:.74rem;color:var(--ink3);margin-top:.1rem}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(8rem,1fr));gap:.7rem;margin:1.3rem 0}
.stat{border:1px solid var(--rule);border-radius:5px;padding:.7rem .85rem}
.stat b{display:block;font-size:1.35rem;color:var(--navy);font-variant-numeric:tabular-nums;line-height:1.1;font-weight:660}
.stat span{display:block;font-size:.67rem;color:var(--ink3);text-transform:uppercase;letter-spacing:.05em;margin-top:.25rem;text-wrap:balance}
figure{margin:1.2rem 0 1.4rem}
figure img{width:100%;height:auto;display:block;border:1px solid var(--rule);border-radius:5px}
figcaption{font-size:.79rem;color:var(--ink3);margin-top:.55rem;line-height:1.5}
ul,ol{margin:0 0 .95em;padding-left:1.2rem;max-width:70ch} li{margin-bottom:.35em}
.bar{height:12px;background:var(--sunk);border-radius:3px;overflow:hidden;border:1px solid var(--rule2);min-width:70px}
.bar i{display:block;height:100%;background:var(--accent)}
.tag{display:inline-block;font-size:.68rem;font-weight:650;padding:.05rem .4rem;border-radius:8px;
  background:var(--sunk);color:var(--ink2);border:1px solid var(--rule);white-space:nowrap}
.pb{display:none}
.foot{margin-top:2.6rem;padding-top:.9rem;border-top:1px solid var(--rule);font-size:.78rem;color:var(--ink3);line-height:1.55}
a{color:var(--accent)} a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""


def build_print():
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="color-scheme" content="light only">'
            '<title>LEHRP \u2014 Hypothetical Causal Assessment</title>'
            f'<style>{CSS}</style></head><body>{build_body()}</body></html>')


def build_web():
    """Body-only HTML for publishing as an Artifact (host supplies the skeleton)."""
    body = build_body().replace('<table>', '<div class="tw"><table>').replace('</table>', '</table></div>')
    return f'<style>{WEB_CSS}</style>\n<div class="doc"><div class="wrap">\n{body}\n</div></div>'


if __name__ == "__main__":
    out = os.path.join(ROOT, "reports")
    h = os.path.join(out, "LEHRP_Hypothetical_Causal_Assessment.html")
    p = os.path.join(out, "LEHRP_Hypothetical_Causal_Assessment.pdf")
    with open(h, "w", encoding="utf-8") as f:
        f.write(build_print())
    w = os.path.join(out, "Ladera-Ranch-Hypothetical-Assessment.html")
    with open(w, "w", encoding="utf-8") as f:
        f.write(build_web())
    print(f"Wrote {w} ({os.path.getsize(w)//1024} KB)  [web / artifact variant]")
    print(f"Wrote {h} ({os.path.getsize(h)//1024} KB)")
    if not os.path.exists(CHROME):
        sys.exit("Chrome not found.")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                    "--no-pdf-header-footer", f"--print-to-pdf={p}",
                    "--virtual-time-budget=20000", f"file://{h}"], check=True, capture_output=True)
    print(f"Wrote {p} ({os.path.getsize(p)//1024} KB)")
