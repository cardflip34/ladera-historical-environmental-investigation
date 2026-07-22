#!/usr/bin/env python3
"""Build a ~3-page self-contained HTML project summary report (embeds two capstone figures)."""
import base64, io, os
from PIL import Image
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def b64(path, width=1120, q=74):
    im=Image.open(os.path.join(ROOT,path)).convert("RGB")
    if im.width>width: im=im.resize((width,int(im.height*width/im.width)))
    buf=io.BytesIO(); im.save(buf,"JPEG",quality=q)
    return "data:image/jpeg;base64,"+base64.b64encode(buf.getvalue()).decode()

FIG_MAP=b64("research/statewide/CA_dipping_probability_map.jpg", 900, 72)
FIG_JOPLIN=b64("research/coto_de_caza/joplin_dip_site_then_and_now.jpg", 1120, 74)
FIG_LADERA=b64("research/ladera/imagery/ladera_dip_bestguess_thennow.jpg", 1120, 74)
FIG_LADERA_HOUSES=b64("research/ladera/imagery/ladera_candidates_under_neighborhood.jpg", 1000, 74)

HTML=f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LEHRP — Project Summary</title>
<style>
:root{{--paper:#f7f5f0;--ink:#16233a;--ink2:#48586c;--line:#ddd7ca;--accent:#2f6087;--brass:#a97e1f;--brassbg:#f4ecd6;}}
*{{box-sizing:border-box}}
body{{margin:0;background:#e9e6df;color:var(--ink);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}
.page{{max-width:860px;margin:26px auto;background:var(--paper);padding:52px 60px 46px;box-shadow:0 2px 20px rgba(20,35,58,.12);border-radius:4px}}
.serif{{font-family:"Iowan Old Style",Georgia,"Times New Roman",serif}}
h1{{font-family:"Iowan Old Style",Georgia,serif;font-size:30px;line-height:1.15;margin:0 0 6px;letter-spacing:-.01em}}
.sub{{color:var(--ink2);font-size:16px;margin:0 0 4px;max-width:62ch}}
.meta{{color:#7c8a9c;font-size:12.5px;letter-spacing:.03em;margin:14px 0 0}}
h2{{font-family:"Iowan Old Style",Georgia,serif;font-size:20px;margin:30px 0 8px;color:var(--ink);border-bottom:1px solid var(--line);padding-bottom:5px}}
h3{{font-size:15px;margin:16px 0 3px;color:var(--accent)}}
p{{margin:8px 0}}
.disc{{background:var(--brassbg);border:1px solid var(--line);border-left:3px solid var(--brass);border-radius:6px;padding:12px 16px;margin:16px 0;font-size:13px;color:#5a4a2c}}
.disc b{{color:#3a2e18}}
ul{{margin:8px 0 8px 4px;padding-left:20px}}
li{{margin:5px 0}}
.khead{{font-weight:700;color:var(--ink)}}
figure{{margin:18px 0;border:1px solid var(--line);border-radius:6px;overflow:hidden;background:#fff}}
figure img{{width:100%;display:block}}
figcaption{{font-size:12px;color:var(--ink2);padding:8px 12px;border-top:1px solid var(--line)}}
.lead{{border-left:3px solid var(--brass);background:#faf6ec;padding:10px 16px;border-radius:0 6px 6px 0;margin:14px 0}}
.foot{{margin-top:26px;border-top:1px solid var(--line);padding-top:14px;color:var(--ink2);font-size:11.5px}}
.tag{{display:inline-block;font-size:10.5px;font-weight:700;letter-spacing:.05em;background:var(--accent);color:#fff;padding:1px 7px;border-radius:4px;vertical-align:middle}}
@media print{{body{{background:#fff}}.page{{box-shadow:none;margin:0;max-width:none;padding:0.5in 0.7in}}}}
@media (max-width:640px){{.page{{padding:32px 22px}}}}
</style></head><body><div class="page">

<h1 class="serif">The arsenic under the master plan</h1>
<p class="sub">An independent, hypothesis-neutral investigation into historical arsenical cattle-dipping
(1907–1915) and the South Orange County communities built on the former ranch land — LEHRP project
summary.</p>
<p class="meta">Independent research &amp; data-organization project · Prepared July 2026 · ~3-page summary of the full 288-page investigation and its extensions</p>

<div class="disc"><b>This is an independent research and data-organization project. It does not provide
medical advice and does not establish that any pesticide, property, organization, school, water
provider, agency, or other party caused any illness.</b> Publicly reported health events may not be
independently verified. Geographic and temporal overlap does not establish exposure or causation. No
soil has been tested and no contamination is asserted for any community named here.</div>

<h2>1 · The question</h2>
<p>The project began with reported pediatric cancers (primarily Ewing sarcoma) in Ladera Ranch and a
specific, testable hypothesis: that the <b>state-mandated arsenical cattle-tick dipping program of
1907–1915</b> — which poured a government formula of <b>8 lb of white arsenic per 500 gallons</b>
through vats across Southern California — may have left <b>persistent arsenic in the soil</b> of land
later built into master-planned communities. Arsenic is an element: it does not degrade, it binds
tightly to soil, and it does not wash out to sea. If a vat operated somewhere, its arsenic would still
be there — which makes the question, uniquely, <b>answerable by a soil test.</b></p>
<p>The reason it was never asked is a <b>40-year blind spot</b>: routine environmental review reaches
back to ~1950s aerials, dipping ended ~1912, and California never inventoried its vat sites — so the
general fact and the specific ground were never connected.</p>

<h2>2 · What we built, and how</h2>
<p>A full <b>Version 1.0 investigation</b> (288 pages · 46 graded claims · 97 sources), then a series of
extensions: a statewide screening, an arsenic-science layer, deep dives on individual communities, and
a probability atlas. Every claim carries a source grade (A1–D) and mandatory counter-evidence; findings
were checked by adversarial verification. Methods were documentary and archival — primary USDA and
State Veterinarian records, 1929–2022 aerial imagery, land-grant and homestead records, and live
regulatory databases — never speculation.</p>

<figure><img src="{FIG_MAP}" alt="California dipping-probability map">
<figcaption>Graded <b>probability that the dipping practice occurred</b> across 19 former ranchos, with
today's community on each — from documented (the four named 1908 sites) to plausible. A prioritisation
of an <em>unanswered question</em>, not a contamination map.</figcaption></figure>

<h2>3 · What we discovered</h2>

<h3>The gap is structural, not local</h3>
<p>Run through the same pipeline, <b>eleven communities in five counties</b> share the exact Ladera
review gap; two (Rancho Bernardo, Rancho Santa Fe) were built <b>before CEQA and never reviewed at
all.</b> The Ladera question is the general case.</p>

<h3>The knowledge was never missing — the marking was</h3>
<p>The USDA printed the hazard in 1911, including a warning nailed to every vat (<em>"POISONOUS to man
and all animals… do not allow it to contaminate any feed or water supply"</em>). <b>Australia and
Florida later built registers, buyer-notification, and cleanup programs</b> for former dip sites.
California built none — its one analog soil program explicitly <b>excludes</b> animal-handling sites.
The gap is an administrative marking failure, not ignorance.</p>

<h3>How much arsenic, and what it does <span class="tag">MODEL ESTIMATE</span></h3>
<p>A mass-balance model (bounded by the ~15–75 tons of arsenic the whole California program could ever
have used) puts <b>~100–500 lb of arsenic in the soil around a single heavily-used vat.</b> Arsenic is
a Group-1 human carcinogen; the pathways that matter are <b>children ingesting soil</b> and <b>dust
raised during grading</b>. A dip-level site would run <b>40–270× above California's natural background
arsenic</b> — which is exactly what a soil test is built to reveal.</p>

<h3>Where dipping was actually documented</h3>
<p>Four Orange County dip sites are <b>named in the 1908 press</b> (Joplin/Trabuco Canyon, San Juan
Capistrano, Yorba, Bixby/Santa Ana Canyon), all county-ordered and arsenical. A recovered 1912 state
proclamation fixes the <b>last-held quarantine district in the south/southwest county</b> — nearest
Ladera and the coast.</p>

<h3>The three study communities, honestly</h3>
<p><b>Ladera Ranch</b> — a real gap, no vat located, the arsenic question genuinely open.
<b>Newport Coast</b> — the preconditions, but ~60 million cubic yards of grading rearranged any historic
surface. <b>Irvine</b> — the strongest cattle-<em>operations</em> profile (the Bommer Canyon
headquarters), yet its measured soil arsenic tracks <b>former orchards (lead-arsenate), not grazing</b>
— a crucial competing explanation.</p>

<h3>Ladera Ranch — the best-guess siting, held to graded inference</h3>
<p>The sharpest pre-development aerial (<b>1937–38, 1.15 ft/px</b>) shows open cattle rangeland; the one
resolvable man-made structure inside the footprint sits on the <b>Trabuco Creek corridor</b> — the single
strongest candidate for a ranch working/dip location. It is <b>not</b> an identified vat, and none was
found on any frame 1929–2022. Crucially, that node and the main stock-water cluster are today
<b>preserved greenbelt, not under houses.</b></p>

<figure><img src="{FIG_LADERA}" alt="Ladera best-guess dip siting, 1937-38 vs 2022">
<figcaption>Best-guess siting (<b>graded inference, not a location</b>): the 1937–38 ranch node (A) and
stock-water bodies (B–E) over the <b>1937–38 aerial and 2022 imagery</b>. The strongest candidates lie in
today's Trabuco greenbelt. No vat found; no soil tested.</figcaption></figure>

<p>A fair question is whether any candidate ground lies <em>inside</em> the neighborhoods. Of the 16
surface-water bodies mapped inside the footprint, <b>9 are in greenbelt</b> (including the strongest node)
and <b>6 are now under or beside the central-east villages</b> — smaller stock ponds, with houses as close
as 8–35 m. A ranch's dip was usually one central facility at its working corral (the greenbelt node), so
these are <em>weaker</em> dip candidates — but they are exactly where any built-over ranch ground would now
sit, which is why the concern survives the loss of the "targeting" explanation.</p>

<figure><img src="{FIG_LADERA_HOUSES}" alt="Ladera candidates greenbelt vs under neighborhood">
<figcaption>Which candidates are under houses today: <b>greenbelt (blue)</b> vs <b>under the neighborhood
(orange)</b>, on 2022 imagery. The strongest node is greenbelt; the embedded candidates are smaller ponds
in the east villages. Graded inference; no contamination implied.</figcaption></figure>

<div class="lead"><h3 style="margin-top:0">The single strongest result</h3>
<p>The one place in the entire investigation where a cattle dip is <b>documented</b> — Josiah C.
Joplin's 1908 ranch "in Trabuco canyon" — was identified from the primary record and located to his
<b>Belle (Bell) Canyon homestead</b>. That land is now the <b>National Audubon Society's Starr Ranch
Sanctuary</b> — ~4,000 acres of protected open space. <b>The documented dip site was preserved, not
built over.</b> The adjacent Coto de Caza / Dove Canyon homes sit <em>near</em> it, not on it — and
because the ground is undisturbed, it is the rare documented dip ranch where an authorized soil test
could actually be sited.</p></div>

<figure><img src="{FIG_JOPLIN}" alt="Joplin dip site then and now">
<figcaption>The documented 1908 Joplin dip site: <b>1938</b> open cattle-and-grain ranch land →
<b>today</b> the Starr Ranch Audubon Sanctuary (protected open space), with the Coto/Dove Canyon homes
adjacent on the northwest. Exact vat parcel unknown; no soil tested; no contamination implied.</figcaption></figure>

<h2>4 · What we did <em>not</em> find — the honest limits</h2>
<ul>
<li><span class="khead">No dip vat has been physically located</span> anywhere in the study area.</li>
<li><span class="khead">No soil has been tested</span> for dipping-era arsenic at any community.</li>
<li><span class="khead">No contamination is measured or claimed</span> — "no located record" is not "no fact."</li>
<li>Where arsenic <em>does</em> appear in local soils (school sites), it carries the <span class="khead">orchard lead-arsenate signature (arsenic <em>with</em> lead)</span> — a different, well-explained source than cattle dip.</li>
</ul>

<h2>5 · The bottom line</h2>
<p>The reported pattern warrants investigation, and the available evidence does not yet establish
causation. What the project <em>has</em> established is a structural, statewide blind spot — a documented
hazard whose California sites were never mapped — and, in one case, the actual documented dip ranch, now
sitting undisturbed as a nature preserve. Across every thread the resolver is the same and has been
performed for none of them: <b>a direct soil arsenic test.</b> The Starr Ranch / Joplin site is where
that test could finally, and appropriately, be asked.</p>

<div class="foot">Full materials: the 288-page investigation, the statewide screening records, the arsenic
mass-balance model, the precautions comparison, and the Coto de Caza / Joplin findings are held in the
project repository. Every figure and claim is source-graded (A1–D) with counter-evidence. Model estimates
are labelled as such and are not measurements. Historic imagery: Orange County Survey (1929–1952);
current imagery: Esri World Imagery (Maxar et al.).</div>

</div></body></html>"""
OUT=os.path.join(ROOT,"docs/project_summary_report.html")
open(OUT,"w").write(HTML)
print("wrote",OUT,f"({len(HTML)//1024} KB)")
