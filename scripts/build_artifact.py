#!/usr/bin/env python3
"""Build the web-readable LEHRP report for publishing as an Artifact.

Body-only HTML (no doctype/html/head/body — the host wraps it). Honours the LEHRP visual
system defined in CLAUDE.md: light ground, dark navy type, restrained blue accent, no
fear-based graphics. Reads the live registries so the page reflects current data.

Usage: python3 scripts/build_artifact.py   ->  reports/lehrp_report_web.html
"""
import base64
import csv
import html
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GENERATED = "18 July 2026"


def rd(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def e(s):
    return html.escape(str(s or ""))


sources = rd("research/source_registry/sources.csv")
lit = rd("research/literature/literature_registry.csv")
envs = rd("research/environmental_sites/sites.csv")
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

img = ""
ip = os.path.join(ROOT, "reports/assets/map_figure_web.jpg")
if os.path.exists(ip):
    img = base64.b64encode(open(ip, "rb").read()).decode()

POISSON = {4: (1.0899, 10.2416), 5: (1.6235, 11.6683), 6: (2.2019, 13.0595), 12: (6.2006, 20.9616)}
PY_A, PY_P = 9115 * 14, 4906 * 14
SCEN = [("Central", 6, PY_A, 3.0, "6 cases, ages 0–19, all-races rate"),
        ("Ancestry-adjusted", 6, PY_A, 4.0, "rate raised for a non-Hispanic-white-majority community"),
        ("Peak-age", 6, PY_P, 4.58, "ages 10–19 only, peak-age rate"),
        ("Conservative count", 4, PY_A, 4.0, "case-definition sensitivity"),
        ("Higher count", 12, PY_A, 3.0, "single-source outlier count"),
        ("Leave-one-out", 5, PY_A, 4.0, "one reported case removed")]


def sir_rows():
    for label, obs, py, rate, note in SCEN:
        exp = py * rate / 1_000_000
        lo, hi = POISSON[obs]
        yield label, note, obs, rate, exp, obs / exp, lo / exp, hi / exp


def tbl(headers, rows, num_from=1):
    th = "".join(f'<th{" class=n" if i >= num_from else ""}>{e(h)}</th>' for i, h in enumerate(headers))
    body = "".join("<tr>" + "".join(
        f'<td{" class=n" if i >= num_from else ""}>{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="scroll"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


env_rows = [(e(x["name"]), e(x["contaminants"]), x["approxDistanceMiles"])
            for x in sorted([y for y in envs if y.get("approxDistanceMiles")],
                            key=lambda y: float(y["approxDistanceMiles"]))]
well_rows = [(e(w["name"]), e(w["status"]), f'{w["distanceMiles"]}') for w in wells]
lu_rows = [(e(x["period"]), e(x["land_use"]), e(x["confidence"])) for x in landuse]
pur_rows = [(e(r["chemical"][:44]), f'{int(r["application_records"]):,}',
             f'{float(r["total_lbs_applied"]):,.0f}') for r in pur_chem[:10]]
sir_tbl_rows = [(f'<strong>{e(l)}</strong><div class=sub>{e(n)}</div>', o, f"{rt:.1f}",
                 f"{ex:.3f}", f"<strong>{s:.1f}</strong>", f"{lo:.1f}–{hi:.1f}")
                for l, n, o, rt, ex, s, lo, hi in sir_rows()]

CSS = """
<style>
:root{
  --paper:#ffffff; --sunk:#f4f7fb; --ink:#111c2e; --ink-2:#46566d; --ink-3:#6d7d93;
  --navy:#0b1e38; --accent:#1d4f8f; --rule:#c9d4e2; --rule-2:#e3eaf3;
  --crit:#9a3030; --crit-bg:#fbeced; --warn:#a35f0c; --warn-bg:#fdf4e8;
  --ok:#156132; --ok-bg:#eaf4ee;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
@media (prefers-color-scheme:dark){
  :root{
    --paper:#0e141d; --sunk:#161e29; --ink:#dde5ef; --ink-2:#a3b1c4; --ink-3:#7d8b9f;
    --navy:#e8eef6; --accent:#7fa9dd; --rule:#2b3646; --rule-2:#212b38;
    --crit:#e08585; --crit-bg:#2a1719; --warn:#e0a760; --warn-bg:#2a2114;
    --ok:#7fc79a; --ok-bg:#152418;
  }
}
:root[data-theme="dark"]{
  --paper:#0e141d; --sunk:#161e29; --ink:#dde5ef; --ink-2:#a3b1c4; --ink-3:#7d8b9f;
  --navy:#e8eef6; --accent:#7fa9dd; --rule:#2b3646; --rule-2:#212b38;
  --crit:#e08585; --crit-bg:#2a1719; --warn:#e0a760; --warn-bg:#2a2114;
  --ok:#7fc79a; --ok-bg:#152418;
}
:root[data-theme="light"]{
  --paper:#ffffff; --sunk:#f4f7fb; --ink:#111c2e; --ink-2:#46566d; --ink-3:#6d7d93;
  --navy:#0b1e38; --accent:#1d4f8f; --rule:#c9d4e2; --rule-2:#e3eaf3;
  --crit:#9a3030; --crit-bg:#fbeced; --warn:#a35f0c; --warn-bg:#fdf4e8;
  --ok:#156132; --ok-bg:#eaf4ee;
}
*{box-sizing:border-box}
.doc{background:var(--paper);color:var(--ink);font-family:var(--serif);
  font-size:17px;line-height:1.62;padding:clamp(20px,5vw,64px) clamp(18px,5vw,40px) 80px;
  display:flex;flex-direction:column;align-items:center;min-height:100vh}
.wrap{width:100%;max-width:44rem;display:flex;flex-direction:column;gap:0}
.doc p{margin:0 0 1.05em;max-width:68ch}
.doc h1,.doc h2,.doc h3,.doc .eyebrow,.doc th,.doc .badge,.doc .sub,.doc figcaption,
.doc .meta,.doc .foot{font-family:var(--sans)}
.eyebrow{font-size:.7rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
  color:var(--accent);margin-bottom:.9rem}
h1{font-family:var(--sans);font-size:clamp(1.75rem,4.4vw,2.5rem);line-height:1.14;
  letter-spacing:-.02em;color:var(--navy);margin:0 0 .5rem;text-wrap:balance;font-weight:660}
.meta{font-size:.83rem;color:var(--ink-3);margin:0 0 1.6rem;letter-spacing:.01em}
.rule{height:3px;background:var(--accent);width:100%;margin:0 0 1.9rem}
h2{font-family:var(--sans);font-size:1.16rem;color:var(--navy);font-weight:650;
  letter-spacing:-.005em;margin:2.9rem 0 .3rem;padding-bottom:.45rem;
  border-bottom:1px solid var(--rule);text-wrap:balance;display:flex;gap:.6rem;align-items:baseline}
h2 .num{font-variant-numeric:tabular-nums;color:var(--accent);font-size:.9rem;flex:none}
h3{font-family:var(--sans);font-size:.98rem;color:var(--navy);font-weight:640;margin:1.8rem 0 .35rem}
.doc ul,.doc ol{margin:0 0 1.05em;padding-left:1.2rem;max-width:68ch}
.doc li{margin-bottom:.42em}
strong{color:var(--navy);font-weight:640}
em{font-style:italic}
.note{border-left:3px solid var(--accent);background:var(--sunk);padding:.85rem 1.05rem;
  margin:1.2rem 0;font-size:.94rem;border-radius:0 4px 4px 0}
.note.crit{border-left-color:var(--crit);background:var(--crit-bg)}
.note.warn{border-left-color:var(--warn);background:var(--warn-bg)}
.note.ok{border-left-color:var(--ok);background:var(--ok-bg)}
.note :last-child{margin-bottom:0}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(8.5rem,1fr));gap:.7rem;margin:1.5rem 0 .4rem}
.stat{border:1px solid var(--rule);border-radius:5px;padding:.7rem .85rem;background:var(--paper)}
.stat b{font-family:var(--sans);display:block;font-size:1.4rem;color:var(--navy);
  font-variant-numeric:tabular-nums;line-height:1.1;font-weight:660}
.stat span{font-family:var(--sans);display:block;font-size:.68rem;color:var(--ink-3);
  text-transform:uppercase;letter-spacing:.05em;margin-top:.25rem;text-wrap:balance}
.scroll{overflow-x:auto;margin:1rem 0 1.3rem;border:1px solid var(--rule-2);border-radius:5px}
table{width:100%;border-collapse:collapse;font-family:var(--sans);font-size:.83rem}
th{background:var(--sunk);color:var(--navy);text-align:left;padding:.5rem .65rem;
  font-size:.67rem;text-transform:uppercase;letter-spacing:.05em;font-weight:650;
  border-bottom:1px solid var(--rule);white-space:nowrap}
td{padding:.5rem .65rem;border-bottom:1px solid var(--rule-2);vertical-align:top;color:var(--ink)}
tbody tr:last-child td{border-bottom:none}
th.n,td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.sub{font-size:.74rem;color:var(--ink-3);font-weight:400;margin-top:.1rem}
figure{margin:1.4rem 0 1.6rem}
figure img{width:100%;height:auto;display:block;border:1px solid var(--rule);border-radius:5px}
figcaption{font-size:.78rem;color:var(--ink-3);margin-top:.6rem;line-height:1.5;max-width:68ch}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:1rem;margin:1.1rem 0}
.card{border:1px solid var(--rule);border-radius:5px;padding:.85rem 1rem;background:var(--paper)}
.card h3{margin-top:0}
.card ul{font-size:.92rem;margin-bottom:0}
.foot{margin-top:3.2rem;padding-top:1rem;border-top:1px solid var(--rule);
  font-size:.78rem;color:var(--ink-3);line-height:1.55}
a{color:var(--accent)}
a:focus-visible,summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:2px}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
"""


def build():
    return f"""{CSS}
<div class="doc"><div class="wrap">

<div class="eyebrow">Ladera Environmental Health Research Platform · Preliminary Report</div>
<h1>Reported pediatric cancers in Ladera Ranch: what the public evidence does and does not show</h1>
<p class="meta">Independent public-source research · {GENERATED} · Version 0.7 · Hypothesis-neutral · Aggregate-only</p>
<div class="rule"></div>

<div class="note crit">
<p><strong>This report does not provide medical advice and does not establish that any pesticide,
property, organization, employer, school, water provider, government agency, or other party caused
any illness.</strong> Publicly reported health events may not have been independently medically
verified. Geographic and temporal overlap does not establish exposure or causation. Health data
here is aggregate-only; no individual is identified.</p>
</div>

<div class="stats">
  <div class="stat"><b>{len(sources)}</b><span>Graded sources</span></div>
  <div class="stat"><b>79,473</b><span>Pesticide records</span></div>
  <div class="stat"><b>{len(lit)}</b><span>Literature entries</span></div>
  <div class="stat"><b>{len(envs)}</b><span>Environmental sites</span></div>
</div>

<h2><span class="num">1</span> Executive summary</h2>
<p><strong>No agency has declared a cluster or identified a cause.</strong> An official multi-agency
review — the Orange County Health Care Agency, the California Cancer Registry, UC Irvine, and the
County Agricultural Commissioner — is underway. Its initial pass "did not find a particular
pattern," and findings remain pending. A federal EPA investigation has been <em>requested</em> by the
First Assistant U.S. Attorney but not confirmed opened, and no EPA response was found.</p>

<p><strong>Every pesticide-specific causal claim in circulation is advocacy- or attorney-sourced.</strong>
That includes the "17 pesticides in June" figure and the naming of glufosinate. No regulator
classifies glufosinate as a carcinogen; its EU non-renewal was on reproductive-toxicity grounds,
not cancer.</p>

<p><strong>The most important scientific fact is hypothesis-neutral.</strong> Ewing sarcoma is
strongly ancestry-patterned through germline biology — roughly nine times more common in people of
European ancestry than African ancestry. A community that is 63.6% non-Hispanic white therefore
carries an <em>elevated baseline expectation</em>, which must be modelled before any excess is
attributed to the environment.</p>

<div class="note warn">
<p><strong>Bottom line.</strong> Under transparent assumptions the <em>reported</em> count exceeds
statistical expectation, which is precisely why the pattern <strong>warrants investigation</strong>.
It is not proof of a cluster: the counts are media- and attorney-reported rather than
registry-verified, the boundary was drawn around the observed cases, and the numbers are small
enough that one or two cases move the result dramatically. <strong>The available evidence does not
yet establish causation.</strong></p>
</div>

<h2><span class="num">2</span> Study area</h2>
<figure>
  <img src="data:image/jpeg;base64,{img}" alt="Map of the Ladera Ranch study area showing approximate study zones, DTSC EnviroStor cleanup sites, and CalGEM oil and gas wells over an OpenStreetMap basemap">
  <figcaption>Study zones with DTSC EnviroStor cleanup sites and CalGEM oil &amp; gas wells. Zone A
  (solid) is an approximate 2.5 × 2 mile screening boundary on the community centroid; Zone B
  (dashed) is a five-mile ring. Site and well points use real database coordinates.
  <strong>No patient locations or residential addresses are plotted.</strong>
  Basemap © CARTO, © OpenStreetMap contributors.</figcaption>
</figure>

<h2><span class="num">3</span> What the data can — and cannot — establish</h2>
<div class="note">
<p><strong>On "correlation".</strong> This platform does not compute a correlation between pesticide
use and cancer, and no such figure should be quoted from it. Doing so would require case-level data
the platform does not hold, and an area-level correlation would be an <em>ecological fallacy</em> —
a relationship between aggregates that says nothing about individuals.</p>
</div>
<div class="cols">
  <div class="card"><h3>What can be shown</h3><ul>
    <li>Distance from the community to documented sites and wells.</li>
    <li>Whether land-use eras overlap the residency and diagnosis window.</li>
    <li>Observed versus expected counts under explicit assumptions.</li>
    <li>Which chemicals are actually reported in regional landscape use.</li>
  </ul></div>
  <div class="card"><h3>What cannot be shown</h3><ul>
    <li>That any individual was exposed to anything.</li>
    <li>Any dose, or contact between a person and a chemical.</li>
    <li>That a statistically valid cluster exists.</li>
    <li>Any causal link between an exposure and an illness.</li>
  </ul></div>
</div>

<h2><span class="num">4</span> Spatial relationships</h2>
<h3>Environmental and cleanup sites, by distance</h3>
{tbl(["Site", "Contaminants", "Miles"], env_rows, num_from=2)}
<div class="note"><p><strong>Pattern worth noting.</strong> The nearest former-agricultural school
sites carry exactly the legacy residue profile expected on former California citrus and row-crop
land. Ladera Ranch was built on comparable land. This is a <em>testable hypothesis</em>, not a
finding.</p></div>

<h3>Oil &amp; gas wells</h3>
{tbl(["Well (CalGEM)", "Status", "Miles"], well_rows, num_from=2)}
<div class="note warn"><p><strong>Corrected finding.</strong> Two plugged exploratory wells lie
within about a mile of the community centroid — one at roughly a quarter-mile, effectively within
the footprint. A 2026 California study reported a <em>suggestive, non-significant</em> association
between proximity to <strong>abandoned</strong> wells within 10 km and childhood Ewing sarcoma
(OR 1.27, 95% CI 0.96–1.66). This places the community inside that exposure contrast and raises the
priority of characterising these wells. It does <strong>not</strong> establish exposure or
causation.</p></div>

<h2><span class="num">5</span> Temporal relationships</h2>
{tbl(["Period", "Land use", "Confidence"], lu_rows, num_from=3)}

<h3>Does the timing work? Two mechanisms, opposite predictions</h3>
<p>Grading occurred around 1999–2006; diagnoses span 2013–2026. Many affected children were not born
when the earth was moved. That objection does real damage — but only to one of two mechanisms that
have been getting conflated.</p>
{tbl(["", "Construction dust", "Persistent residue"], [
  ("<strong>What it is</strong>", "Grading mobilised buried residue", "Residue remains in surface soil"),
  ("<strong>Time-bound?</strong>", "<strong>Yes</strong> — an event", "<strong>No</strong> — a standing condition"),
  ("<strong>Child present during grading?</strong>", "Required", "Not required"),
  ("<strong>Predicts</strong>", "Births ≤ ~2007", "<strong>All</strong> birth cohorts"),
], num_from=99)}
<p>The share of plausible pediatric ages whose birth cohort overlaps grading falls from
<strong>93% for a 2013 diagnosis to 7% for a 2026 diagnosis</strong>. The dust mechanism is
substantially weakened for recent diagnoses and unavailable for children born after about 2007.
The persistent-residue mechanism is untouched by the timing objection.</p>
<div class="note"><p>Only <strong>one</strong> reported Ewing case has both a published age and
diagnosis year, so no birth-cohort distribution can be built from public data. Since the two
mechanisms predict opposite distributions, <strong>birth year is a discriminating test</strong> — and
it is exactly what is missing.</p></div>

<h2><span class="num">6</span> Observed versus expected</h2>
<p>Person-years for ages 0–19 over 2013–2026 ≈ {PY_A:,}; peak-age (10–19) ≈ {PY_P:,}. Intervals are
exact Poisson limits on the observed count.</p>
{tbl(["Scenario", "Observed", "Rate /M/yr", "Expected", "SIR", "95% CI"], sir_tbl_rows, num_from=1)}
<div class="note crit"><p><strong>Hypothetical — not a finding.</strong> These scenarios use
<em>unverified</em> public case reports and <em>estimated</em> population. California suppresses any
rate built on fewer than 15 cases or a population under 10,000, so a place-level Ewing sarcoma rate
is <strong>statistically unpublishable</strong>. Compare the conservative and higher-count rows to
see how severely a few cases move the result.</p></div>

<h2><span class="num">7</span> What is actually applied</h2>
<p>We downloaded and processed California's 2023 Pesticide Use Report archive — <strong>79,473 Orange
County application records</strong> — to test, rather than assume, how much reported use can be
placed on a map.</p>
{tbl(["Site type", "Records", "Located", "% located"], [
  ("Structural pest control", "55,442", "0", "0.0%"),
  ("<strong>Landscape maintenance</strong>", "15,383", "22", "<strong>0.1%</strong>"),
  ("Nursery — outdoor containers", "2,990", "2,982", "99.7%"),
  ("Golf course turf", "1,375", "0", "0.0%"),
  ("Agriculture (fruiting pepper)", "183", "183", "100.0%"),
], num_from=1)}
<div class="note warn"><p><strong>This corrected an earlier assumption.</strong> Landscape
maintenance <em>is</em> reported — 15,383 records — but <strong>99.9% carries no township, range or
section</strong>. Overall, 94.6% of Orange County records have no location at all. Ladera Ranch also
sits in unsectioned former land-grant territory. <strong>The state's pesticide reporting system is
structurally incapable of placing an application inside this community</strong>, which makes the
HOA's own posted notices the only public location-specific evidence.</p></div>
<h3>Top reported active ingredients, Orange County 2023</h3>
{tbl(["Active ingredient", "Records", "Pounds"], pur_rows, num_from=1)}
<div class="note ok"><p><strong>Glufosinate in context.</strong> The ingredient named in Ladera Ranch
notices is confirmed in the state dataset: 442 county records, 10,532 lbs, of which 336 records were
landscape maintenance. That corroborates the documented pattern as <strong>ordinary regional
practice</strong> — not as evidence of anything unusual, and not as evidence of causation.</p></div>

<h2><span class="num">8</span> Legacy soil arsenic — does a developed surface matter?</h2>
<p>A fair objection: the community is fully built. If legacy soil residue is the concern, is a child
ever in contact with it? And if arsenic is in the soil, wouldn't lawn and backyard produce grown in
it carry the arsenic anyway?</p>
<p><strong>Arsenic has no half-life.</strong> It is element 33 and cannot degrade. The health agency
position is blunt: arsenic "cannot be destroyed in the environment" and "tends to concentrate and
remain in upper soil layers indefinitely." The "6.5 to 16 year half-life" figures in circulation
describe loss of the applied compound from the surface layer, not destruction of arsenic.</p>
{tbl(["", "Arsenic (legacy soil)", "Landscape herbicides"], [
  ("<strong>Persistence</strong>", "Permanent — cannot degrade", "Days to months"),
  ("<strong>Exposure pattern</strong>", "Continuous while resident", "Pulses, decaying between"),
  ("<strong>Dominant route</strong>", "Soil &amp; house-dust ingestion", "Dermal contact with treated turf"),
  ("<strong>Effect of turf</strong>", "<strong>Barrier</strong>", "<strong>Source</strong>"),
  ("<strong>Ewing sarcoma link</strong>", "<strong>None established</strong>", "<strong>None established</strong>"),
], num_from=99)}
<div class="note"><p><strong>The asymmetry that answers the question.</strong> <strong>For arsenic,
turf is a barrier. For turf herbicides, turf is the source.</strong> Arsenic sits beneath the grass,
so sod and hardscape put distance between a child and the affected layer. Herbicides are applied
<em>onto</em> the grass children then play on.</p></div>
<p><strong>What surface cover does not close:</strong> the indoor house-dust reservoir (regulators
weight dust <em>above</em> soil for young children, and a randomised trial found yard coverings cut
track-in by half while entryway dust did not significantly change over a year); gardening and
digging; produce uptake; and disturbance events. <strong>Backyard produce is a real pathway</strong>
— soil-to-plant transfer is <em>more</em> efficient for arsenic than lead, ranking lettuce &gt; carrot
&gt; bean &gt; tomato. Fruiting vegetables stay safe even on quite contaminated soil; leafy greens
may not.</p>
<div class="note warn"><p><strong>But context reframes all of it.</strong> Southern California
background arsenic — from 1,086 state school-site samples across Orange and neighbouring counties —
averages <strong>1.51 mg/kg</strong> with an upper bound of <strong>12 mg/kg</strong>. The risk-based
screening levels are <strong>0.11–0.68 mg/kg</strong>, roughly 18–110× <em>below</em> natural
background. <strong>Exceeding a screening level in Orange County is normal, not evidence of
contamination.</strong></p></div>
<div class="note crit"><p><strong>Revised standing: a low-prior hypothesis.</strong> Six independent
lines lower it. Background swamps the screening levels. Measured bioavailability at the closest
analogue site is <strong>0.31</strong>, so total soil arsenic overstates dose roughly threefold. The
crop history doesn't match — lead arsenate was an <em>apple and pear</em> insecticide, while this was
citrus, barley and cattle land. Mass grading likely diluted the historic plough layer. At a
comparable community, soil arsenic of 19.9 mg/kg produced <strong>no significant correlation</strong>
with children's urinary arsenic. And a systematic review found the childhood-cancer literature does
not support an arsenic association. <strong>It is not excluded — it has never been measured here —
but it should no longer be carried as the leading environmental explanation.</strong></p></div>

<h2><span class="num">9</span> Scientific literature</h2>
<p>Ewing sarcoma is a genetically and ancestry-driven, overwhelmingly sporadic cancer with
<strong>no established environmental cause</strong>. Evidence tying pesticides specifically to Ewing
sarcoma is weak, mixed and farming-<em>proxy</em> based: the strongest positive signals come from
parental-farming studies with wide confidence intervals, while the largest and highest-quality
occupational study — 5,369 sarcoma cases in Great Britain — found <strong>no</strong> pesticide or
agriculture association. Two large California registry studies, on air pollution and on oil and gas
proximity, were null overall. <strong>No study links Ewing sarcoma to glyphosate, glufosinate, 2,4-D,
or any specific pyrethroid.</strong></p>

<h2><span class="num">10</span> Claims that remain unproven</h2>
<ul>
  <li>Causation by any exposure.</li>
  <li>That a true epidemiological cluster exists.</li>
  <li>The specific role of glufosinate or any named chemical.</li>
  <li>The "17 pesticides" figure and the higher "12 Ewing" case count.</li>
  <li>That legacy soil residue is present on the residential footprint.</li>
  <li>That recycled irrigation water carries any hazard.</li>
</ul>

<h2><span class="num">11</span> What would most improve the analysis</h2>
<ol>
  <li><strong>Registry-confirmed case data</strong> — counts, diagnosis dates, ages, ancestry, and
      critically <strong>birth year</strong>, which alone would discriminate between the two leading
      environmental mechanisms.</li>
  <li><strong>Individual residence histories</strong> across the etiologic window, consented and
      IRB-governed.</li>
  <li><strong>Soil and house-dust sampling</strong> for arsenic and organochlorines, measuring
      bioavailable as well as total fractions.</li>
  <li><strong>HOA and vendor application logs</strong> — now the only possible source of
      location-specific application data, and at risk of routine disposal.</li>
  <li><strong>The entitlement soil-testing record</strong> — was this land ever tested before homes
      were built on it?</li>
</ol>
<div class="note"><p><strong>A structural finding worth noting.</strong> Every legacy-pesticide soil
record near Ladera Ranch is a <em>school</em> site. Not because schools got worse land — because
California law mandates an environmental assessment before a district buys property, and
<strong>no equivalent mandate applies to residential subdivisions</strong>. The absence of soil data
for the neighbourhood is a regulatory artifact, not evidence that it is clean.</p></div>

<h2><span class="num">12</span> Evidence quality</h2>
{tbl(["Grade", "Meaning", "Count"], [
  ("A1", "Official dataset, peer-reviewed research, or registry", grades.get("A1", 0)),
  ("A2", "Official government page, filing, or meeting document", grades.get("A2", 0)),
  ("B1", "University or research-institution report", grades.get("B1", 0)),
  ("B2", "Reputable news quoting named sources", grades.get("B2", 0)),
  ("C", "Advocacy, law firm, petition, unverified counts", grades.get("C", 0)),
  ("D", "Speculation or unsourced reposts", grades.get("D", 0)),
], num_from=2)}
<p>Lower-grade sources are retained as leads and never silently promoted. Where sources conflict — as
they do on case counts — both values are recorded with their grades, and the discrepancy is treated
as a finding about data quality rather than smoothed away.</p>

<p class="foot">Ladera Environmental Health Research Platform · Independent research and
data-organization project · Generated {GENERATED} from {len(sources)} graded sources. This report is
hypothesis-neutral and privacy-protecting; health data is aggregate-only and no individual is
identified. Do not draw causal conclusions prematurely.</p>

</div></div>
"""


if __name__ == "__main__":
    out = os.path.join(ROOT, "reports", "lehrp_report_web.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(build())
    print(f"Wrote {out} ({os.path.getsize(out)//1024} KB)")
