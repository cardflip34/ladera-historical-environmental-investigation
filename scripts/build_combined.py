#!/usr/bin/env python3
"""Build the combined LEHRP report — evidence + hypothetical assessment — as one document.

Emits body-only HTML for publishing as an Artifact (the host supplies the page skeleton).
Mobile-first: single column, responsive type, horizontally scrollable data tables with a
scroll affordance, and a jump-link table of contents.

Part I  — the public evidence (what the data does and does not show)
Part II — the hypothetical causal assessment (forced-conclusion hypothesis ranking)

Usage: python3 scripts/build_combined.py
Output: reports/Ladera-Ranch-Combined-Report.html
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


def b64(rel):
    p = os.path.join(ROOT, rel)
    return base64.b64encode(open(p, "rb").read()).decode() if os.path.exists(p) else ""


sources = rd("research/source_registry/sources.csv")
lit = rd("research/literature/literature_registry.csv")
envs = rd("research/environmental_sites/sites.csv")
landuse = rd("research/land_use/historical_land_use.csv")
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

ALLOC = [("No single environmental cause — chance aggregation, amplified by ascertainment and post-hoc boundary selection", 48),
         ("A real excess whose cause is never identifiable", 22),
         ("Real excess with a contribution from abandoned oil &amp; gas well proximity", 9),
         ("Real excess with a contribution from legacy agricultural soil residue", 9),
         ("Real excess with a contribution from landscape herbicides", 6),
         ("An exposure or mechanism not yet considered", 6)]

SCORE = [("Landscape herbicides", "Moderate", "None", "Poor", "Poor", "Poor", "6%"),
         ("Legacy soil residue", "Moderate", "None", "Good", "Poor", "Weak", "9%"),
         ("Abandoned oil &amp; gas wells", "Weak", "<strong>Suggestive</strong>", "Good", "Unknown", "Weak", "9%"),
         ("Chance + ascertainment", "n/a", "n/a", "n/a", "n/a", "<strong>Strong</strong>", "48%")]

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
    ("Clark 2026 (CA)", "558 cases / 27,800 controls", "Oil &amp; gas proximity", "Active OR 0.88 (0.72–1.08); <strong>abandoned OR 1.27 (0.96–1.66)</strong>", "Does not resolve"),
    ("Clark 2025 (CA)", "388 cases / 19,341 controls", "Perinatal PM₂.₅", "Q4 gestation OR 0.87 (0.61–1.25) — null overall", "Does not resolve"),
    ("Vinson 2011 (meta)", "40 studies", "Parental pesticides", "Leukaemia 1.48 (1.26–1.75); brain 1.49 (1.23–1.79); <strong>Ewing not reported</strong>", "Supports (other cancers)"),
    ("Spector 2021 (CI5)", "15,874 cases", "Ancestry / geography", "Ages 10–19 per million: N. America 4.58; E. Asia 1.59; African IRR 0.16", "Background"),
    ("Bradman 2019", "US cohorts", "Residential mobility", "55–58% of childhood-cancer cases moved between birth and diagnosis", "Methodological"),
]

TOC = [
    ("part1", "Part I — The public evidence", None),
    ("s1", "1. Executive summary", 1), ("s2", "2. Study area", 1),
    ("s3", "3. What the data can and cannot establish", 1),
    ("s4", "4. Population and baseline expectation", 1),
    ("s5", "5. Observed versus expected", 1),
    ("s6", "6. Spatial relationships", 1),
    ("s7", "7. Temporal relationships", 1),
    ("s8", "8. What is actually applied", 1),
    ("s9", "9. Legacy soil arsenic", 1),
    ("s10", "10. Scientific literature", 1),
    ("s11", "11. Claims that remain unproven", 1),
    ("part2", "Part II — Hypothetical causal assessment", None),
    ("s12", "12. The question, decomposed", 2),
    ("s13", "13. Hypothesis scoring", 2),
    ("s14", "14. Hypothesis by hypothesis", 2),
    ("s15", "15. Conclusion", 2),
    ("s16", "16. What would change this conclusion", 2),
    ("s17", "17. What this document does not say", 2),
    ("s18", "18. Evidence quality and provenance", 2),
]

CSS = """
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
.doc{background:var(--paper);color:var(--ink);font-family:var(--serif);
 font-size:17px;line-height:1.62;padding:clamp(18px,4vw,56px) clamp(14px,4vw,32px) 72px;
 display:flex;flex-direction:column;align-items:center;min-height:100vh;
 -webkit-text-size-adjust:100%}
.wrap{width:100%;max-width:46rem}
h1,h2,h3,.eyebrow,th,.meta,.sub,figcaption,.stat,.foot,.tag,.snum,.subtitle,.toc,.partlbl{font-family:var(--sans)}
h1{font-size:clamp(1.6rem,5.4vw,2.3rem);color:var(--navy);margin:0 0 .3rem;line-height:1.14;
 letter-spacing:-.02em;font-weight:660;text-wrap:balance}
.subtitle{font-size:clamp(.98rem,3vw,1.18rem);font-weight:500;color:var(--ink2);line-height:1.35;text-wrap:balance}
h2{font-size:clamp(1.08rem,3.4vw,1.2rem);color:var(--navy);font-weight:650;margin:2.5rem 0 .35rem;
 padding-bottom:.4rem;border-bottom:1px solid var(--rule);text-wrap:balance;scroll-margin-top:1rem}
h3{font-size:1rem;color:var(--navy);font-weight:640;margin:1.6rem 0 .3rem;text-wrap:balance}
p{margin:0 0 .95em;max-width:70ch} strong{color:var(--navy);font-weight:640}
.eyebrow{color:var(--accent);font-size:.7rem;font-weight:700;letter-spacing:.13em;
 text-transform:uppercase;margin-bottom:.7rem}
.cover{border-bottom:3px solid var(--accent);padding-bottom:1rem;margin-bottom:1.2rem}
.meta{font-size:.82rem;color:var(--ink3);margin-top:.7rem;line-height:1.5}
.disc{background:var(--critbg);border-left:4px solid var(--crit);padding:.85rem 1rem;
 font-size:.93rem;border-radius:0 4px 4px 0;margin:1.1rem 0}
.callout{background:var(--sunk);border-left:4px solid var(--accent);padding:.85rem 1rem;
 margin:1rem 0;border-radius:0 4px 4px 0;font-size:.95rem}
.warn{background:var(--warnbg);border-left-color:var(--warn)}
.ok{background:var(--okbg);border-left-color:var(--ok)}
.callout :last-child,.disc :last-child{margin-bottom:0}
.verdict{background:var(--navy);padding:1.05rem 1.2rem;border-radius:5px;margin:1.3rem 0}
.verdict,.verdict *{color:var(--paper)}
.verdict h3{margin:0 0 .4rem;font-size:1.06rem}
.partdiv{margin:3rem 0 1.4rem;padding:1.1rem 1.2rem;background:var(--sunk);
 border-radius:6px;border:1px solid var(--rule);scroll-margin-top:1rem}
.partlbl{font-size:.7rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}
.partdiv h2{border:none;margin:.3rem 0 .3rem;padding:0;font-size:clamp(1.25rem,4.4vw,1.6rem)}
.partdiv p{margin:0;font-size:.92rem;color:var(--ink2)}
nav.toc{border:1px solid var(--rule);border-radius:6px;padding:.9rem 1.1rem;margin:1.3rem 0}
nav.toc h3{margin:0 0 .5rem;font-size:.78rem;text-transform:uppercase;letter-spacing:.09em;color:var(--ink3)}
nav.toc ol{list-style:none;margin:0;padding:0;columns:15rem 2;column-gap:1.6rem}
nav.toc li{margin:0;break-inside:avoid;font-size:.88rem}
nav.toc li.p{font-weight:650;color:var(--navy);margin-top:.5rem;column-span:all;
 font-size:.74rem;text-transform:uppercase;letter-spacing:.06em;color:var(--accent)}
nav.toc a{color:var(--ink);text-decoration:none;display:block;padding:.42rem 0;min-height:2.5rem;line-height:1.35;border-bottom:1px solid transparent}
nav.toc a:hover{border-bottom-color:var(--accent);color:var(--accent)}
.tw{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:.85rem 0 1.1rem;
 border:1px solid var(--rule2);border-radius:5px;
 background:linear-gradient(to right,var(--paper) 30%,rgba(0,0,0,0)),
   linear-gradient(to right,rgba(0,0,0,0),var(--paper) 70%) 100% 0,
   radial-gradient(farthest-side at 0 50%,rgba(17,28,46,.12),transparent),
   radial-gradient(farthest-side at 100% 50%,rgba(17,28,46,.12),transparent) 100% 0;
 background-repeat:no-repeat;background-size:36px 100%,36px 100%,14px 100%,14px 100%;
 background-attachment:local,local,scroll,scroll}
table{width:100%;border-collapse:collapse;font-family:var(--sans);font-size:.83rem;margin:0}
th{background:var(--sunk);color:var(--navy);text-align:left;padding:.45rem .6rem;font-size:.67rem;
 text-transform:uppercase;letter-spacing:.045em;border-bottom:1.5px solid var(--rule);
 font-weight:650;white-space:nowrap}
td{padding:.45rem .6rem;border-bottom:1px solid var(--rule2);vertical-align:top}
tbody tr:last-child td{border-bottom:none}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
tbody tr:nth-child(even) td{background:var(--sunk)}
.sub{font-size:.74rem;color:var(--ink3);margin-top:.1rem;font-weight:400}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(7.5rem,1fr));gap:.65rem;margin:1.3rem 0}
.stat{border:1px solid var(--rule);border-radius:5px;padding:.65rem .8rem}
.stat b{display:block;font-size:1.32rem;color:var(--navy);font-variant-numeric:tabular-nums;
 line-height:1.1;font-weight:660}
.stat span{display:block;font-size:.66rem;color:var(--ink3);text-transform:uppercase;
 letter-spacing:.05em;margin-top:.22rem;text-wrap:balance}
figure{margin:1.2rem 0 1.4rem}
figure img{width:100%;height:auto;display:block;border:1px solid var(--rule);border-radius:5px}
figcaption{font-size:.79rem;color:var(--ink3);margin-top:.55rem;line-height:1.5}
ul,ol{margin:0 0 .95em;padding-left:1.25rem;max-width:70ch} li{margin-bottom:.35em}
.bar{height:12px;background:var(--sunk);border-radius:3px;overflow:hidden;
 border:1px solid var(--rule2);min-width:64px}
.bar i{display:block;height:100%;background:var(--accent)}
.tag{display:inline-block;font-size:.68rem;font-weight:650;padding:.05rem .4rem;border-radius:8px;
 background:var(--sunk);color:var(--ink2);border:1px solid var(--rule);white-space:nowrap}
.foot{margin-top:2.6rem;padding-top:.9rem;border-top:1px solid var(--rule);
 font-size:.78rem;color:var(--ink3);line-height:1.55}
.top{display:inline-block;margin-top:.7rem;padding:.5rem .7rem .5rem 0;font-family:var(--sans);font-size:.76rem;color:var(--ink3);text-decoration:none;min-height:2.5rem}
.top:hover{color:var(--accent)}
a{color:var(--accent)} a:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:2px}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
"""


def T(headers, body, num_from=1):
    th = "".join(f'<th{" class=n" if i >= num_from else ""}>{h}</th>' for i, h in enumerate(headers))
    return f'<div class="tw"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def build():
    img = b64("reports/assets/map_figure_web.jpg")

    sir = ""
    for label, obs, py, rate, note in SCEN:
        exp = py * rate / 1_000_000
        lo, hi = POISSON[obs]
        sir += (f'<tr><td><strong>{label}</strong><div class="sub">{note}</div></td>'
                f'<td class="n">{obs}</td><td class="n">{rate:.2f}</td><td class="n">{exp:.3f}</td>'
                f'<td class="n"><strong>{obs/exp:.1f}</strong></td><td class="n">{lo/exp:.1f} – {hi/exp:.1f}</td></tr>')

    env = "".join(f'<tr><td>{e(x["name"])}</td><td>{e(x["contaminants"])[:60]}</td>'
                  f'<td class="n">{x["approxDistanceMiles"]}</td></tr>'
                  for x in sorted([y for y in envs if y.get("approxDistanceMiles")],
                                  key=lambda y: float(y["approxDistanceMiles"]))[:10])
    wl = "".join(f'<tr><td>{e(w["name"])}</td><td>{e(w["status"])}</td>'
                 f'<td class="n"><strong>{w["distanceMiles"]}</strong></td></tr>' for w in wells)
    lu = "".join(f'<tr><td>{e(x["period"])}</td><td>{e(x["land_use"])}</td>'
                 f'<td>{e(x["confidence"])}</td></tr>' for x in landuse)
    lm = "".join(f'<tr><td>{c}</td><td class="n">{n:,}</td><td class="n">{p:,.1f}</td></tr>'
                 for c, n, p in LM_MIX)
    litr = "".join(f'<tr><td><strong>{a}</strong></td><td>{b}</td><td>{c}</td><td>{d}</td>'
                   f'<td><span class="tag">{f_}</span></td></tr>' for a, b, c, d, f_ in LITROWS)
    sc = "".join(f'<tr><td><strong>{a}</strong></td><td>{b}</td><td>{c}</td><td>{d}</td><td>{f_}</td>'
                 f'<td>{g}</td><td class="n"><strong>{h}</strong></td></tr>' for a, b, c, d, f_, g, h in SCORE)
    al = "".join(f'<tr><td>{n}</td><td class="n"><strong>{p}%</strong></td>'
                 f'<td style="width:88px"><div class="bar"><i style="width:{p*1.75:.0f}%"></i></div></td></tr>'
                 for n, p in ALLOC)

    toc = ""
    for anchor, label, part in TOC:
        cls = ' class="p"' if part is None else ""
        toc += f'<li{cls}><a href="#{anchor}">{label}</a></li>'

    up = '<a class="top" href="#top">↑ Contents</a>'

    return f"""<script>
(function(){{
  try{{
    if(!document.querySelector('meta[name="viewport"]')){{
      var m=document.createElement('meta');
      m.setAttribute('name','viewport');
      m.setAttribute('content','width=device-width, initial-scale=1');
      (document.head||document.documentElement).appendChild(m);
    }}
  }}catch(e){{}}
}})();
</script>
<style>{CSS}</style>
<div class="doc"><div class="wrap" id="top">

<div class="cover">
<div class="eyebrow">Ladera Environmental Health Research Platform</div>
<h1>Reported pediatric cancers in Ladera Ranch</h1>
<div class="subtitle">The public evidence, and a hypothetical assessment of what most probably
explains it</div>
<div class="meta">Combined edition · {GENERATED} · Compiled from {len(sources)} graded sources,
79,473 state pesticide records and {len(lit)} literature entries ·
<strong>Independent research. Not a finding. Not an agency determination.</strong></div>
</div>

<div class="disc">
<p><strong>This report does not provide medical advice and does not establish that any pesticide,
property, organisation, employer, school, water provider, government agency or other party caused
any illness.</strong> Publicly reported health events may not have been independently medically
verified. Geographic and temporal overlap does not establish exposure or causation.</p>
<p>Part II is an <strong>analytical exercise</strong> — a structured ranking of hypotheses, using
elicited subjective probabilities rather than calculation. An official multi-agency review is
underway and has not reported; nothing here anticipates or substitutes for it. Health data is
aggregate-only and no individual is identified.</p>
</div>

<div class="stats">
<div class="stat"><b>{len(sources)}</b><span>Graded sources</span></div>
<div class="stat"><b>79,473</b><span>Pesticide records</span></div>
<div class="stat"><b>{len(lit)}</b><span>Literature entries</span></div>
<div class="stat"><b>{len(envs)}</b><span>Environmental sites</span></div>
</div>

<nav class="toc"><h3>Contents</h3><ol>{toc}</ol></nav>

<div class="partdiv" id="part1">
<div class="partlbl">Part I</div>
<h2>The public evidence</h2>
<p>What the assembled public record does — and does not — show.</p>
</div>

<h2 id="s1">1. Executive summary</h2>
<p><strong>No agency has declared a cluster or identified a cause.</strong> An official multi-agency
review — the Orange County Health Care Agency, the California Cancer Registry, UC Irvine and the
County Agricultural Commissioner — is underway. Its initial pass "did not find a particular
pattern," and findings remain pending. A federal EPA investigation has been <em>requested</em> by the
First Assistant U.S. Attorney but not confirmed opened, and no EPA response was found.</p>
<p><strong>Every pesticide-specific causal claim in circulation is advocacy- or attorney-sourced</strong>,
including the "17 pesticides in June" figure and the naming of glufosinate. No regulator classifies
glufosinate as a carcinogen; its EU non-renewal was on reproductive-toxicity grounds, not cancer.</p>
<p><strong>The most important scientific fact is hypothesis-neutral:</strong> Ewing sarcoma has
<em>no established environmental cause anywhere in the published literature.</em> It is defined by a
gene fusion arising postnatally on a strongly ancestry-patterned germline background, and the
demographic risk factors — European ancestry, male sex, adolescence — are the only ones firmly
established.</p>
<p><strong>A correction to an earlier draft.</strong> This report previously leaned on the
community's 63.6% non-Hispanic-white composition as a major explanatory factor. That was
overstated, and §4.2 now sets out why: ancestry adjusts the <em>expected count</em> by roughly 25%,
but it cannot explain <em>clustering</em>, and 63.6% is barely above the US average of 57.8%.</p>
<p><strong>The strongest testable environmental lead is not active spraying.</strong> It is legacy
agricultural soil residue — though, as Part I §9 sets out, that hypothesis is itself substantially
weakened once background concentrations, bioavailability and crop history are accounted for.</p>
<div class="callout warn"><p><strong>Bottom line.</strong> Under transparent assumptions the
<em>reported</em> count exceeds statistical expectation, which is precisely why the pattern
<strong>warrants investigation</strong>. It is not proof of a cluster: counts are media- and
attorney-reported rather than registry-verified, the boundary was drawn around the observed cases,
and the numbers are small enough that one or two cases move the result dramatically. <strong>The
available evidence does not yet establish causation.</strong></p></div>
{up}

<h2 id="s2">2. Study area</h2>
<figure><img src="data:image/jpeg;base64,{img}" alt="Map of the Ladera Ranch study area showing approximate study zones, DTSC EnviroStor cleanup sites and CalGEM oil and gas wells over an OpenStreetMap basemap">
<figcaption><strong>Figure 1.</strong> Study zones (approximate), <strong>school sites where DTSC
found arsenic in soil</strong> (marked <strong>As</strong>), other school sites with legacy residues,
EnviroStor cleanup sites and CalGEM oil &amp; gas wells. Two plugged exploratory wells lie within roughly a mile of the community
centroid — a relationship that emerged only after correcting a 1.93-mile centroid error inherited
from the original brief. <strong>No patient locations or residential addresses are plotted.</strong>
Basemap © CARTO, © OpenStreetMap contributors.</figcaption></figure>
{up}

<h2 id="s3">3. What the data can and cannot establish</h2>
<div class="callout"><p><strong>On "correlation".</strong> This platform does not compute a
correlation between pesticide use and cancer, and no such figure should be quoted from it. Doing so
would require case-level data the platform does not hold, and an area-level correlation would be an
<em>ecological fallacy</em> — a relationship between aggregates that says nothing about
individuals.</p></div>
{T(["Can be shown", "Cannot be shown"], (
  "<tr><td>Distance from the community to documented sites and wells</td>"
  "<td>That any individual was exposed to anything</td></tr>"
  "<tr><td>Whether land-use eras overlap residency and diagnosis windows</td>"
  "<td>Any dose, or contact between a person and a chemical</td></tr>"
  "<tr><td>Observed versus expected counts under explicit assumptions</td>"
  "<td>That a statistically valid cluster exists</td></tr>"
  "<tr><td>Which chemicals are actually reported in regional landscape use</td>"
  "<td>Any causal link between an exposure and an illness</td></tr>"), num_from=99)}
{up}

<h2 id="s4">4. Population and baseline expectation</h2>
<p>Ladera Ranch CDP (FIPS 0639114), American Community Survey 2020–2024:</p>
{T(["Measure", "Value", "Note"], (
  "<tr><td>Total population</td><td class='n'>23,793</td><td>26,170 at the 2020 Census; 22,980 in 2010</td></tr>"
  "<tr><td>Children aged 0–19</td><td class='n'>9,115</td><td>38.3% — an unusually young community</td></tr>"
  "<tr><td>Aged 10–19 (Ewing peak window)</td><td class='n'>4,906</td><td>Peak incidence falls at 10–15</td></tr>"
  "<tr><td>Non-Hispanic white</td><td class='n'>63.6%</td><td><strong>Materially raises the expected count</strong></td></tr>"
  "<tr><td>Asian / Hispanic / Black (NH)</td><td class='n'>13.6% / 12.9% / 0.9%</td><td>Lower-incidence ancestries</td></tr>"
  f"<tr><td>Person-years 0–19, 2013–2026</td><td class='n'>{PY_A:,}</td><td>Peak-age person-years: {PY_P:,}</td></tr>"), num_from=1)}
<h3>4.1 Reference incidence rates</h3>
{T(["Population", "Rate", "Units", "Basis"], (
  "<tr><td>US, all ages and races</td><td class='n'>2.93</td><td>per million/yr</td><td>SEER 1973–2004</td></tr>"
  "<tr><td>US, ages 0–19</td><td class='n'>3.0</td><td>per million/yr</td><td>SEER-based central estimate</td></tr>"
  "<tr><td>North America, ages 10–19</td><td class='n'>4.58</td><td>per million/yr</td><td>CI5 2003–2012 peak</td></tr>"
  "<tr><td>S. Europe / W. Europe, 10–19</td><td class='n'>7.75 / 6.93</td><td>per million/yr</td><td>Spector 2021</td></tr>"
  "<tr><td>East Asia, ages 10–19</td><td class='n'>1.59</td><td>per million/yr</td><td>Spector 2021</td></tr>"
  "<tr><td>Ancestry IRR vs European</td><td class='n'>0.16</td><td>ratio</td><td>African; E. Asian 0.30; Pacific Islander 2.18</td></tr>"
  "<tr><td>All pediatric cancer, California 0–19</td><td class='n'>18.2</td><td>per 100,000/yr</td><td>CCR/SEER 2012–2016</td></tr>"), num_from=1)}
<h3>4.2 Ancestry: a real correction, but a small one — and not an explanation</h3>
<p>Ewing sarcoma incidence is roughly <strong>nine times higher</strong> in people of European
ancestry than African ancestry, driven by germline GGAA-microsatellite architecture rather than
environment. Applying an all-races rate to a 63.6% non-Hispanic-white population therefore
understates the expected count. That much is sound, and it is why scenario S2 exists.</p>
<div class="callout warn"><p><strong>But this factor was overweighted in earlier drafts, and three
things bound it tightly.</strong></p>
<ol style="margin-bottom:0">
<li><strong>The magnitude is modest.</strong> The ancestry adjustment moves expected cases from
0.383 to 0.510 — SIR from 15.7 to 11.8. That is a <strong>~25% correction against an apparent
excess of roughly 1,000%.</strong> It does not come close to explaining an observed six.</li>
<li><strong>63.6% is unremarkable.</strong> The United States averages <strong>57.8%</strong>
non-Hispanic white; this community sits under six points above the national figure. Thousands of
American communities are 80–95% non-Hispanic white. <strong>If European ancestry produced clusters,
they would concentrate in those places — and they do not.</strong></li>
<li><strong>Baselines do not cluster.</strong> Ancestry raises the underlying rate roughly uniformly
wherever that ancestry lives. A uniform elevation cannot concentrate cases in one subdivision; that
is what "baseline" means. Ancestry can explain the <em>level</em> of expected risk. It cannot
explain <em>why here.</em></li>
</ol></div>
<p>Its correct role is narrow: a technical adjustment to the denominator when computing an SIR, and
a criterion for choosing ancestry-matched comparison communities. It is <strong>not</strong> a
reason to discount the reported pattern, and this report no longer treats it as one. (California,
for context, is 34.7% non-Hispanic white — so this community is well above the <em>state</em>
figure while being ordinary against the national one.)</p>
{up}

<h2 id="s5">5. Observed versus expected</h2>
<p>Expected = person-years × rate. SIR = observed ÷ expected. Intervals are exact Poisson limits on
the observed count.</p>
{T(["Scenario", "Obs.", "Rate /M", "Expected", "SIR", "95% CI"], sir, num_from=1)}
<div class="disc"><p><strong>Hypothetical — not a finding.</strong> Every row uses <em>unverified</em>
public case reports and <em>estimated</em> population. California suppresses any rate built on fewer
than 15 cases or a population under 10,000, so a place-level Ewing sarcoma rate is
<strong>statistically unpublishable</strong>. Compare S4 with S5: the same community moves from SIR
7.8 to 31.3 purely on case definition.</p></div>
<h3>5.1 The numerator problem</h3>
{T(["Reported count", "Scope as stated", "Grade"], (
  "<tr><td><strong>&quot;At least 6&quot;</strong> Ewing sarcoma since 2013</td><td>Ladera Ranch only, Ewing only</td><td>B2 — local TV news</td></tr>"
  "<tr><td>&quot;About a dozen&quot; rare cancers</td><td><strong>Mixed cancer types across multiple cities</strong></td><td>B2 — same outlet</td></tr>"
  "<tr><td>&quot;12 Ewing sarcoma&quot;</td><td>Ladera Ranch, Ewing only</td><td>C — single low-reliability outlet</td></tr>"), num_from=99)}
<p>Only one reported Ewing case carries both a published age and a diagnosis year. The widely
repeated "dozen" explicitly aggregates <em>different cancers in different cities</em> — the signature
of ascertainment inflation rather than of a cluster.</p>
{up}

<h2 id="s6">6. Spatial relationships</h2>
<h3>6.1 Environmental and cleanup sites, by corrected distance</h3>
{T(["Site", "Contaminants recorded", "Miles"], env, num_from=2)}
<p>Every legacy-pesticide record above is a <strong>school</strong> site — not because schools
received worse land, but because California Education Code mandates a Phase I assessment and DTSC
review before a district acquires property, and <strong>no equivalent mandate applies to residential
subdivisions.</strong> The absence of soil data for the residential footprint is a regulatory
artifact, not evidence that the soil is clean.</p>
<h3>6.2 Oil &amp; gas wells (CalGEM)</h3>
{T(["Well", "Status", "Miles"], wl, num_from=2)}
<div class="callout warn"><p>Two plugged wells within one mile; three within 5 km; all six within
10 km — the exposure contrast used by the only published study reporting a Ewing-specific
environmental association.</p></div>
{up}

<h2 id="s7">7. Temporal relationships</h2>
{T(["Period", "Land use", "Confidence"], lu, num_from=99)}
<h3>7.1 Does the timing work? Two mechanisms, opposite predictions</h3>
<p>Grading ran roughly 1999–2006; diagnoses span 2013–2026. Many affected children were not born when
the earth was moved. That objection does real damage — but only to one of two mechanisms that have
been getting conflated.</p>
{T(["", "Construction dust", "Persistent residue"], (
  "<tr><td><strong>What it is</strong></td><td>Grading mobilised buried residue</td><td>Residue remains in surface soil</td></tr>"
  "<tr><td><strong>Time-bound?</strong></td><td><strong>Yes</strong> — an event</td><td><strong>No</strong> — a standing condition</td></tr>"
  "<tr><td><strong>Child present during grading?</strong></td><td>Required</td><td>Not required</td></tr>"
  "<tr><td><strong>Predicts</strong></td><td>Births ≤ ~2007</td><td><strong>All</strong> birth cohorts</td></tr>"), num_from=99)}
{T(["Diagnosis year", "Ages overlapping grading", "Share"], (
  "<tr><td>2013</td><td class='n'>14 of 15</td><td class='n'>93%</td></tr>"
  "<tr><td>2016</td><td class='n'>11 of 15</td><td class='n'>73%</td></tr>"
  "<tr><td>2019</td><td class='n'>8 of 15</td><td class='n'>53%</td></tr>"
  "<tr><td>2022</td><td class='n'>5 of 15</td><td class='n'>33%</td></tr>"
  "<tr><td>2026</td><td class='n'>1 of 15</td><td class='n'><strong>7%</strong></td></tr>"), num_from=1)}
<div class="callout"><p>Only <strong>one</strong> reported Ewing case has both a published age and
diagnosis year, so no birth-cohort distribution can be built from public data. Since the two
mechanisms predict opposite distributions, <strong>birth year is a discriminating test</strong> — and
it is exactly what is missing.</p></div>
{up}

<h2 id="s8">8. What is actually applied</h2>
<p>California's 2023 Pesticide Use Report archive was downloaded and processed in full:
<strong>79,473 Orange County application records</strong> across 382 chemicals and 45 site types.</p>
{T(["Site type", "Records", "Pounds", "Located", "% located"], (
  "<tr><td>Structural pest control</td><td class='n'>55,442</td><td class='n'>403,983</td><td class='n'>0</td><td class='n'>0.0%</td></tr>"
  "<tr><td><strong>Landscape maintenance</strong></td><td class='n'>15,383</td><td class='n'>110,664</td><td class='n'>22</td><td class='n'><strong>0.1%</strong></td></tr>"
  "<tr><td>Nursery — outdoor containers</td><td class='n'>2,990</td><td class='n'>4,788</td><td class='n'>2,982</td><td class='n'>99.7%</td></tr>"
  "<tr><td>Golf course turf</td><td class='n'>1,375</td><td class='n'>56,171</td><td class='n'>0</td><td class='n'>0.0%</td></tr>"
  "<tr><td>Agriculture (fruiting pepper)</td><td class='n'>183</td><td class='n'>13,411</td><td class='n'>183</td><td class='n'>100.0%</td></tr>"), num_from=1)}
<div class="callout warn"><p><strong>94.6% of Orange County pesticide records carry no location at
all.</strong> Landscape maintenance <em>is</em> reported, but 99.9% of those records lack township,
range and section. Compounding this, a federal cadastral query places Ladera Ranch in
<strong>unsectioned former land-grant territory</strong> (T7S R7W / R8W, section 00).
<strong>The state's reporting system is structurally incapable of placing a pesticide application
inside this community.</strong></p></div>
<h3>8.1 Landscape-maintenance chemical mix, Orange County 2023</h3>
{T(["Active ingredient", "Records", "Pounds"], lm, num_from=1)}
<div class="callout ok"><p><strong>Glufosinate in regional context.</strong> The ingredient named in
Ladera Ranch application notices accounts for <strong>442 county records and 10,532 lbs</strong> in
2023, of which <strong>336 records and 10,177 lbs</strong> were landscape maintenance. Glyphosate is
larger across both salts (1,361 records, ~30,052 lbs). The community's herbicide programme is
<strong>unremarkable for the region.</strong> Any causal account must explain why <em>here</em> and
not in every comparable South Orange County community served by the same contractors.</p></div>
{up}

<h2 id="s9">9. Legacy soil arsenic</h2>
<p>A fair objection: the community is fully built — grass, turf, concrete. If legacy soil residue is
the concern, is a child ever in contact with it? And if arsenic is in the soil, wouldn't backyard
produce grown in it carry the arsenic anyway?</p>
<p><strong>Arsenic has no half-life.</strong> It is element 33 and cannot degrade; the health-agency
position is that it "tends to concentrate and remain in upper soil layers indefinitely." The
"6.5 to 16 year half-life" figures in circulation describe loss of the applied compound from the
surface layer, not destruction of arsenic.</p>

<h3>9.1 How would arsenic have got here in the first place?</h3>
<p>The orchard lead-arsenate story that dominates former-farmland literature is probably the
<em>wrong</em> mechanism for this land — California citrus was managed for red scale with cyanide
fumigation and oil sprays, not arsenicals. Two other routes fit considerably better, and one was
compulsory under state law.</p>
{T(["Mechanism", "Period", "Spatial pattern", "Concentration"], (
  "<tr><td><strong>Arsenical cattle dips</strong><div class='sub'>Mandated by CA law, March 1907</div></td>"
  "<td>1907–1917</td><td><strong>Point source</strong> — vats, pens, drain areas</td>"
  "<td>300–1,400 mg/kg at sites elsewhere</td></tr>"
  "<tr><td><strong>Sodium arsenite herbicide / soil sterilant</strong></td><td>~1906–1960</td>"
  "<td>Strips — firebreaks, corrals, roadsides, ditch banks</td><td>Sterilant rates 400–800 lbs/acre</td></tr>"
  "<tr><td>Lead arsenate (orchard insecticide)</td><td>1890s–1950s</td>"
  "<td>Under-tree, orchard blocks</td><td><strong>Probably not used here</strong></td></tr>"), num_from=99)}
<p>California was under cattle-tick quarantine from 1895; <strong>Orange County was among the last
counties released</strong> (still quarantined in April 1910, programme ending June 1917). A March
1907 state law compelled arsenical dipping — cattlemen "were given no choice as to its use." That
window sits entirely inside Jerome O'Neill's management of the Rancho Mission Viejo cattle operation
(1907–1926), then Southern California's largest.</p>
<h3>9.2 Can the dip sites actually be located?</h3>
<p>If arsenical dipping is the leading route, the obvious next question is <em>where</em>. This was
searched directly, and the honest answer is that it could not be resolved from public sources.</p>
{T(["Line of enquiry", "Result"], (
  "<tr><td><strong>California dip-vat inventory</strong></td>"
  "<td><strong>None exists.</strong> Florida maintains a published vat list; California has no equivalent public inventory.</td></tr>"
  "<tr><td>Were vat locations recorded at the time?</td>"
  "<td><strong>Generally not.</strong> Most operators abandoned vats without recording them. Florida found 3,000+ vats named in meeting minutes — with no directions to any of them.</td></tr>"
  "<tr><td>Ranch working centre</td>"
  "<td><strong>Cow Camp</strong> is Rancho Mission Viejo’s documented cattle-working hub — vaquero quarters, tack room, large corrals. It lies on the remaining ranch toward Ortega Highway, <em>not</em> on the Ladera Ranch footprint.</td></tr>"
  "<tr><td>Historic topographic maps</td>"
  "<td><strong>Available.</strong> The footprint falls in the USGS <em>San Juan Capistrano</em> 7.5-minute quad; editions exist for 1948, 1949, 1968 and 1974. Retrieved but not yet visually analysed — the sheets are scanned rasters, and dip vats were rarely labelled even when present.</td></tr>"
  "<tr><td>Historic aerial imagery</td>"
  "<td>Frames exist for 1952, 1959, 1973, 1977, 1981, 1983, 1999 and 2002 — the method most likely to reveal corrals, pens and vat structures.</td></tr>"), num_from=99)}
<div class="disc"><p><strong>No dip-vat location on or near the Ladera Ranch footprint has been
identified, and none is plotted on the map above.</strong> Marking speculative points would
manufacture false precision about a question that public records cannot currently answer. What can
be said is that the <em>method</em> is defined: overlay the 1948–1974 topographic sheets and the
1952–2002 aerial series on the developed footprint, identify corrals, holding pens, water points
and rectangular structures, and sample those locations. That is a tractable piece of work for anyone
with the imagery and a GIS.</p></div>

<div class="callout warn"><p><strong>So was the land "covered" with arsenic? Probably not
uniformly — and that changes the search.</strong> The expected pattern is <strong>hot spots</strong>
where cattle were worked and chemicals mixed, <strong>elevated strips</strong> where vegetation was
deliberately killed, and <strong>open grazing land near background.</strong> A uniform grid survey
across a 4,000-acre subdivision would dilute a hot spot into the mean and miss it. The correct method
is to locate historic corrals, water points and vat structures from the aerial series first
(1952–2002 imagery exists), then sample those. <strong>No dip-vat location on this footprint has been
identified — this is a testable hypothesis, not a finding.</strong></p></div>
{T(["", "Arsenic (legacy soil)", "Landscape herbicides"], (
  "<tr><td><strong>Persistence</strong></td><td>Permanent — cannot degrade</td><td>Days to months</td></tr>"
  "<tr><td><strong>Exposure pattern</strong></td><td>Continuous while resident</td><td>Pulses, decaying between</td></tr>"
  "<tr><td><strong>Dominant route</strong></td><td>Soil &amp; house-dust ingestion</td><td>Dermal contact with treated turf</td></tr>"
  "<tr><td><strong>Effect of turf</strong></td><td><strong>Barrier</strong></td><td><strong>Source</strong></td></tr>"
  "<tr><td><strong>Ewing sarcoma link</strong></td><td><strong>None established</strong></td><td><strong>None established</strong></td></tr>"), num_from=99)}
<div class="callout"><p><strong>The asymmetry that answers the question.</strong> <strong>For arsenic,
turf is a barrier. For turf herbicides, turf is the source.</strong> Arsenic sits beneath the grass,
so sod and hardscape put distance between a child and the affected layer. Herbicides are applied
<em>onto</em> the grass children then play on.</p></div>
<p>What surface cover does not close: the indoor house-dust reservoir; gardening and digging; produce
uptake; and disturbance events. <strong>Backyard produce is a real pathway</strong> — soil-to-plant
transfer is <em>more</em> efficient for arsenic than lead, ranking lettuce &gt; carrot &gt; bean &gt;
tomato. Fruiting vegetables stay safe even on quite contaminated soil; leafy greens may not.</p>
{T(["Benchmark", "Value", "Significance"], (
  "<tr><td>SoCal background arsenic (mean)</td><td class='n'>1.51 mg/kg</td><td>DTSC, n = 1,086 school-site samples</td></tr>"
  "<tr><td><strong>Background upper bound</strong></td><td class='n'><strong>12 mg/kg</strong></td><td>The operative comparison for any local result</td></tr>"
  "<tr><td>EPA residential screening level</td><td class='n'>0.68 mg/kg</td><td><em>Below</em> virtually all natural background</td></tr>"
  "<tr><td>California DTSC screening level</td><td class='n'>0.11 mg/kg</td><td>~100× below typical ambient concentrations</td></tr>"
  "<tr><td>Measured bioavailability, former orchard</td><td class='n'>0.31</td><td>Barber Orchard — total overstates dose ~3×</td></tr>"), num_from=1)}
<div class="disc"><p><strong>Revised standing: a low-prior hypothesis.</strong> Background swamps the
screening levels; measured bioavailability is 0.31; lead arsenate was an <em>apple and pear</em>
insecticide whereas this was citrus, barley and cattle land; mass grading likely diluted the plough
layer; at a comparable community soil arsenic of 19.9 mg/kg produced <strong>no significant
correlation</strong> with children's urinary arsenic; and a systematic review found the
childhood-cancer literature does not support an arsenic association. <strong>Not excluded — never
measured here — but no longer the leading environmental explanation.</strong></p></div>
{up}

<h2 id="s10">10. Scientific literature</h2>
{T(["Study", "Size", "Exposure", "Effect estimate", "Direction"], litr, num_from=99)}
<p>Ewing sarcoma has <strong>no established environmental cause anywhere in the published
literature.</strong> It is defined by an EWSR1-FLI1 fusion (~85% of tumours) arising postnatally on a
strongly ancestry-patterned germline background. The strongest positive signals are parental-farming
<em>proxies</em> with confidence intervals touching 1.0; the largest and most rigorous occupational
study found <strong>no</strong> agriculture or agrochemical association. No study links Ewing sarcoma
to glyphosate, glufosinate, 2,4-D or any specific pyrethroid.</p>
<h3>10.1 Precedent from comparable investigations</h3>
{T(["Investigation", "Finding"], (
  "<tr><td>CDC / CSTE guidance</td><td>~1,000 inquiries per year; investigations &quot;unlikely to find an associated environmental contaminant&quot;</td></tr>"
  "<tr><td>Wake County, NC (Ewing)</td><td>Observed did <strong>not</strong> exceed expected; no common exposure identified</td></tr>"
  "<tr><td>Washington County, PA (Ewing)</td><td>Local excess ~3× expected; <strong>not attributed</strong> to any environmental cause</td></tr>"
  "<tr><td>McFarland, CA (mixed pediatric)</td><td>~3× expected; <strong>unresolved</strong>; four pesticides examined and dismissed</td></tr>"), num_from=99)}
{up}

<h2 id="s11">11. Claims that remain unproven</h2>
<ul>
<li>Causation by any exposure.</li>
<li>That a true epidemiological cluster exists.</li>
<li>The specific role of glufosinate or any named chemical.</li>
<li>The "17 pesticides" figure and the higher "12 Ewing" case count.</li>
<li>That legacy soil residue is present on the residential footprint.</li>
<li>That recycled irrigation water carries any hazard.</li>
</ul>
{up}

<div class="partdiv" id="part2">
<div class="partlbl">Part II</div>
<h2>Hypothetical causal assessment</h2>
<p>A structured hypothesis-ranking exercise. Not a finding, not an agency determination, and it
accuses no party.</p>
</div>

<h2 id="s12">12. The question, decomposed</h2>
<p>"What caused the cluster?" smuggles in two assumptions — that a cluster exists, and that it has an
identifiable cause. A disciplined answer must address both:</p>
<ol>
<li><strong>Is there a real excess?</strong> Do registry-verifiable diagnoses exceed the correctly
age- and ancestry-adjusted expectation?</li>
<li><strong>If so, is it attributable?</strong> Does any candidate survive both an
<em>exposure-opportunity</em> test and a <em>disease-specificity</em> test?</li>
<li><strong>Which candidate is most probable?</strong></li>
</ol>
{T(["Criterion", "What it asks"], (
  "<tr><td><strong>Exposure opportunity</strong></td><td>Could children plausibly have contacted this at all?</td></tr>"
  "<tr><td><strong>Disease specificity</strong></td><td>Any link to <em>Ewing sarcoma</em> — not to cancer generally?</td></tr>"
  "<tr><td><strong>Temporal fit</strong></td><td>Does the exposure window overlap the relevant birth cohorts?</td></tr>"
  "<tr><td><strong>Dose plausibility</strong></td><td>Are concentration, persistence and bioavailability sufficient?</td></tr>"
  "<tr><td><strong>Base-rate fit</strong></td><td>How often has this <em>class</em> of explanation proved correct?</td></tr>"), num_from=99)}
<p>The fifth criterion is the one usually omitted, and it carries the most weight. Ignoring it is the
principal route by which motivated reasoning enters.</p>
{up}

<h2 id="s13">13. Hypothesis scoring</h2>
{T(["Hypothesis", "Exposure", "Disease fit", "Temporal", "Dose", "Base rate", "P"], sc, num_from=6)}
{up}

<h2 id="s14">14. Hypothesis by hypothesis</h2>
<h3>14.1 Landscape herbicides</h3>
<p>The dominant public hypothesis and, on evidence, the <strong>weakest</strong> environmental
candidate. Exposure opportunity is genuine. Everything else fails: no regulator classifies
glufosinate as a carcinogen; glyphosate's IARC 2A concerns lymphoma; none is linked to Ewing sarcoma.
Glufosinate's soil half-life is ~7.4 days, so exposure is pulsed rather than cumulative. Documented
applications (2023–25) largely post-date the relevant windows. And state data shows the practice is
regionally ordinary.</p>
<h3>14.2 Legacy agricultural soil residue</h3>
<p>Stronger on exposure logic — arsenic never degrades, and house dust, gardening and produce uptake
survive surface cover. But background swamps the screening levels; bioavailability is ~0.31; the crop
history doesn't match lead arsenate; grading likely diluted the layer; and biomarker studies at
comparable concentrations are null.</p>
<h3>14.3 Abandoned oil &amp; gas wells</h3>
<p>The <strong>only candidate carrying a disease-matched published signal</strong>: OR 1.27 (95% CI
0.96–1.66) for abandoned wells within 10 km, from a 558-case California study, and the corrected
geography places this community inside that contrast. Against it — the association is <strong>not
statistically significant</strong>, the interval crosses 1, the effect was stronger in Hispanic
children (12.9% here), the same study found <em>no</em> association with active wells, and these are
mid-century plugged dry holes.</p>
<h3>14.4 Chance in a high-baseline-risk population</h3>
<p>Not a fallback but a substantive hypothesis, usually dismissed without examination because it is
unsatisfying. The base rate is decisive; the expected count is higher than public framing assumes;
the numerator is inflated by construction; the boundary was drawn around the observed cases; and
moving from 6 cases to 4 halves the apparent ratio.</p>
{up}

<h2 id="s15">15. Conclusion</h2>
<div class="verdict"><h3>Most probable explanation</h3>
<p style="margin-bottom:0"><strong>That there is no single environmental cause — that the apparent
excess is most likely chance aggregation in a population with an elevated ancestry-specific baseline,
amplified by media- and attorney-driven case ascertainment and a boundary drawn around the observed
cases.</strong></p></div>
<p>Forced to name one answer, that is it, and it is not a hedge. It carries the strongest base-rate
support, aligns with the county's own initial review, and is the only explanation that does not
require positing a mechanism never demonstrated for this cancer anywhere in the literature.</p>
<p><strong>If the premise is granted — that a real, registry-confirmed excess exists — the most
probable environmental contributor is proximity to abandoned oil and gas wells</strong>, solely
because it is the only candidate with a Ewing-specific published association. That signal is weak,
non-significant, and held weakly. <strong>The dominant public hypothesis — landscape herbicides — is
the least probable of the environmental candidates.</strong></p>
<h3>15.1 Probability allocation</h3>
<p class="sub" style="font-size:.82rem">Elicited subjective judgement, not calculation. Sums to 100%.</p>
{T(["Explanation", "P", ""], al, num_from=1)}
{up}

<h2 id="s16">16. What would change this conclusion</h2>
<ol>
<li><strong>Registry confirmation of counts and residency.</strong> Six or more Ewing diagnoses
confirmed among resident children during 2013–2026 would drop the chance allocation from 55% to
plausibly below 30%. <em>This single dataset moves more probability than everything else
combined.</em></li>
<li><strong>Birth years.</strong> Cases clustered in births ≤2007 would revive construction-era dust;
cases spread across birth years would eliminate it while leaving persistent residue intact.</li>
<li><strong>Soil and house-dust sampling.</strong> Arsenic above ~12 mg/kg on the footprint, with the
bioavailable fraction measured, would raise the soil branch materially.</li>
<li><strong>HOA and vendor application records.</strong> Evidence of application intensity genuinely
anomalous <em>for the region</em> — not merely present — would raise the herbicide branch.</li>
<li><strong>Well-integrity data.</strong> Documented leakage or soil-gas anomalies at the two nearest
plugged wells would strengthen the only disease-matched candidate.</li>
</ol>
{up}

<h2 id="s17">17. What this document does not say</h2>
<div class="callout warn"><ul style="margin-bottom:0">
<li>It does <strong>not</strong> state that any illness was caused by any party, product or practice.</li>
<li>It does <strong>not</strong> conclude that the families' concerns are unfounded. A low prior on a
specific mechanism is a statement about evidence, not a verdict that nothing happened. These
illnesses warrant investigation; that is why the official review exists.</li>
<li>It does <strong>not</strong> anticipate that review. The agencies hold registry data this project
cannot access, and their findings supersede this entirely.</li>
<li>It is <strong>not</strong> evidence in any proceeding and should not be represented as such.</li>
</ul></div>
{up}

<h2 id="s18">18. Evidence quality and provenance</h2>
{T(["Grade", "Meaning", "Count"], (
  f"<tr><td>A1</td><td>Official dataset, peer-reviewed research, or registry</td><td class='n'>{grades.get('A1',0)}</td></tr>"
  f"<tr><td>A2</td><td>Official government page, filing, or meeting document</td><td class='n'>{grades.get('A2',0)}</td></tr>"
  f"<tr><td>B1</td><td>University or research-institution report</td><td class='n'>{grades.get('B1',0)}</td></tr>"
  f"<tr><td>B2</td><td>Reputable news quoting named sources</td><td class='n'>{grades.get('B2',0)}</td></tr>"
  f"<tr><td>C</td><td>Advocacy, law firm, petition, unverified counts</td><td class='n'>{grades.get('C',0)}</td></tr>"
  f"<tr><td>D</td><td>Speculation or unsourced reposts</td><td class='n'>{grades.get('D',0)}</td></tr>"), num_from=2)}
<p>Lower-grade sources are retained as leads and never silently promoted. Where sources conflict — as
they do on case counts — both values are recorded with their grades, and the discrepancy is treated
as a finding about data quality rather than smoothed away. A correction log records material
revisions, including a 1.93-mile centroid error that, once fixed, moved two abandoned wells from
~2–2.7 miles to 0.25 and 0.77 miles.</p>
{up}

<p class="foot">Ladera Environmental Health Research Platform · Combined edition, {GENERATED},
generated from {len(sources)} graded sources (A1 {grades.get('A1',0)} · A2 {grades.get('A2',0)} ·
B1 {grades.get('B1',0)} · B2 {grades.get('B2',0)} · C {grades.get('C',0)} · D {grades.get('D',0)}).
Part I is descriptive; Part II is an analytical exercise using elicited judgement rather than
calculation. Neither is a finding or an agency determination. Health data is aggregate-only and no
individual is identified. Do not draw causal conclusions prematurely.</p>

</div></div>
"""




def build_standalone():
    """Fully self-contained single-file HTML. No external requests: CSS is inline, the map is a
    base64 data URI, and fonts are system stacks. Opens by double-click on any OS, or from the
    Files app on a phone. Safe to email, AirDrop, or drop on a static host."""
    body = build()
    # A real <head> means the viewport shim is unnecessary; strip it.
    if "<script>" in body:
        body = body[body.index("</script>") + len("</script>"):].lstrip()
    return (
        '<!doctype html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="color-scheme" content="light dark">\n'
        '<meta name="description" content="Independent public-source research on reported '
        'pediatric cancers in Ladera Ranch, California. Part I: the public evidence. '
        'Part II: a hypothetical assessment. Not a finding; not an agency determination.">\n'
        '<meta name="robots" content="noindex">\n'
        '<title>Reported pediatric cancers in Ladera Ranch — LEHRP combined report</title>\n'
        '<style>html,body{margin:0;padding:0}</style>\n'
        '</head>\n<body>\n' + body + '\n</body>\n</html>\n'
    )




def build_unpacked(out_dir):
    """Emit a 'Save Page As -> Webpage, Complete' style export: an HTML file plus a sibling
    _files/ directory holding the stylesheet and image as separate assets."""
    import re as _re, shutil as _sh
    name = "Ladera-Ranch-Report"
    assets = os.path.join(out_dir, name + "_files")
    os.makedirs(assets, exist_ok=True)

    body = build()
    if "<script>" in body:
        body = body[body.index("</script>") + len("</script>"):].lstrip()

    # Pull the inline <style> out to its own file.
    m = _re.search(r"<style>(.*?)</style>", body, _re.S)
    css = m.group(1) if m else ""
    body = body[:m.start()] + body[m.end():] if m else body
    with open(os.path.join(assets, "report.css"), "w", encoding="utf-8") as f:
        f.write(css.strip() + "\n")

    # Replace the inline data-URI image with a real file reference.
    src = os.path.join(ROOT, "reports/assets/map_figure_web.jpg")
    if os.path.exists(src):
        _sh.copy2(src, os.path.join(assets, "map.jpg"))
    body = _re.sub(r'src="data:image/jpeg;base64,[A-Za-z0-9+/=]+"',
                   f'src="{name}_files/map.jpg"', body)

    doc = (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="color-scheme" content="light dark">\n'
        '<meta name="robots" content="noindex">\n'
        '<title>Reported pediatric cancers in Ladera Ranch — LEHRP combined report</title>\n'
        f'<link rel="stylesheet" href="{name}_files/report.css">\n'
        '<style>html,body{margin:0;padding:0}</style>\n'
        '</head>\n<body>\n' + body + '\n</body>\n</html>\n'
    )
    html_path = os.path.join(out_dir, name + ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(doc)
    return html_path, assets


if __name__ == "__main__":
    out = os.path.join(ROOT, "reports", "Ladera-Ranch-Combined-Report.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(build())
    print(f"Wrote {out} ({os.path.getsize(out)//1024} KB)  [artifact / body-only]")

    sa = os.path.join(ROOT, "reports", "Ladera-Ranch-Report-STANDALONE.html")
    with open(sa, "w", encoding="utf-8") as f:
        f.write(build_standalone())
    print(f"Wrote {sa} ({os.path.getsize(sa)//1024} KB)  [self-contained, opens anywhere]")
