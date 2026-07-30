# Horno Creek — phased investigation plan

**Written 2026-07-30.** Hypothesis-neutral. Nothing in this plan assumes arsenic is present in the
drainage, and nothing in it assumes any exposure or health effect.

---

## Why the creek is worth investigating at all

Not because we have evidence of arsenic in it. We have none. It is worth investigating because of
three documented facts that make it the **highest-value untested medium** in the study area:

1. **It is a continuous transport path across the whole community.** Horno Creek in the south hands
   off at lat 33.5366/33.5368 to the Acjachema Storm Drain through the built core, and at
   33.5625/33.5627 to Cañada Chiquita. One line, three names, crossing 75% of the study frame and
   continuing 2.6 km south beyond it. *(A+ — OC Flood_Channels as-built layer)*
2. **Water ran through it during every month of grading.** The Landsat series shows the drainage
   threading directly through the bright bare-earth zone in 2001–2002, when in-CDP ground
   disturbance peaked at 52.8%. *(A+ — Landsat C2 L2, 102 cloud-free months)*
3. **Children are near it now.** Four parks within 25 m — Chaparral 8 m, Oso Grande 8 m, Frog 19 m,
   Stoneridge 23 m — and three school campuses within 90 m. *(A2 geometric measurement; B2 park
   polygons from OSM)*

And one absence: **it has never been sampled.** Not in EnviroStor, not in GeoTracker. That is the
finding — a gap, not a result.

Water is also the mechanism that the historical record itself points at. Arsenical dipping vats were
sited near running water precisely so spent solution could be flushed. If any arsenic signature
survives anywhere in this landscape, a drainage line is where sediment chemistry would concentrate
it. **That is a hypothesis to test, not a conclusion to confirm.**

---

## The result that would make this rigorous

State it before collecting anything, so the design cannot drift:

> **A negative result is a real and publishable result.** If sediment cores from depositional zones
> show arsenic at or below regional background, that materially weakens the arsenic hypothesis for
> this community, and saying so plainly is what makes every other finding in this project credible.

A study that can only come back positive is not a study.

---

## Phase 0 — establish background before anything else *(free, no permission, do first)*

**Without a background number, no measurement means anything.** California soils carry naturally
elevated arsenic in many areas; a raw ppm figure from Horno Creek is uninterpretable on its own.

| Task | Source | Channel |
|---|---|---|
| Regional soil arsenic background | USGS Geochemical Survey of Soils of the Conterminous US | https://mrdata.usgs.gov/ |
| California background arsenic | DTSC background metals guidance; Kearney Foundation soil survey | https://dtsc.ca.gov/ |
| Local geology — arsenic-bearing formations | USGS / CGS geologic maps of the Santa Ana Mountains | https://ngmdb.usgs.gov/ |

**Deliverable:** a defensible background range with a source_id, and a stated screening level.
**Gate:** do not proceed to Phase 3 sampling design without this.

---

## Phase 1 — free public water data *(free, no permission)*

Answer "has anyone sampled this watershed?" before asking anyone for anything.

| Task | What it would show | Channel |
|---|---|---|
| CEDEN surface water and sediment chemistry | any past sampling in the San Juan Creek watershed | https://ceden.waterboards.ca.gov/ |
| GeoTracker — expand to surface water | sites within the drainage corridor | https://geotracker.waterboards.ca.gov/ |
| SMARTS construction stormwater permits | who held erosion/sediment control duty per phase, 1997–2006 | https://smarts.waterboards.ca.gov/ |
| SWRCB CIWQS | NPDES, enforcement, complaints in the watershed | https://ciwqs.waterboards.ca.gov/ |
| San Diego RWQCB (Region 9) records | Ladera drains to San Juan Creek — **Region 9, not Santa Ana** | https://www.waterboards.ca.gov/sandiego/ |

**Note:** the region assignment is a real trap. South Orange County is San Diego Region 9. Querying
Santa Ana Region 8 will return nothing and look like an absence of records.

**Deliverable:** a sampling-history table for the watershed, or a documented statement that none
exists.

---

## Phase 2 — records, using the drafted requests *(free, needs the user to send)*

| Ask | Custodian | Draft |
|---|---|---|
| Channel as-builts, **sediment removal and maintenance history**, dredge spoil disposal | OC Public Works / Flood Control | fold into `M6-REQ-OC-BOARD-02` or a new creek-specific request |
| Recycled-water distribution, in-service dates, any water quality sampling | SMWD | `M6-REQ-SMWD-PRA-06` *(already drafted)* |
| Erosion and sediment control plans, SWPPPs for the grading years | OC Development Services | fold into `M6-REQ-OC-PERMIT-01` follow-up |

**The highest-value single item here is sediment removal history.** If the County has dredged the
channel, that tells us (a) where sediment accumulates, which is exactly where to core, and (b)
whether the historical record has already been physically removed — which would be a genuine and
important negative.

---

## Phase 3 — desk work we can do right now with imagery already held *(free, no permission, executable today)*

This is the part that needs no one's approval, and it is the highest-leverage unexecuted work in the
whole project.

**3a. Depositional-zone mapping.** Using the 0.3 m January 2004 orthoimagery (100% AOI coverage,
already held) plus the 1929–1990 aerial series, map where the channel **widens, meanders, flattens
in gradient, or is impounded**. Those are where fine sediment — and anything bound to it — would
settle. This produces a *sampling map* rather than guesswork.

**3b. Channel change detection, 1929 → 2004.** Overlay the mapped channel on each historical frame
at the identical AOI. Where has the alignment been moved, culverted, straightened or filled? A
reach that was buried in 1999 may preserve a sealed pre-development sediment layer; a reach that was
excavated has lost its record. **This directly determines where evidence can still exist.**

**3c. Grading-to-drainage adjacency, by month.** We hold 102 monthly Landsat frames and per-year
disturbed-area maps. Quantify, for each month, how much disturbed ground lay within a fixed buffer
of the drainage. This is a *land-surface* measurement, not a transport model, and it must be
labelled as such.

**3d. Upstream catchment definition.** Delineate what actually drains into Horno Creek above the
community, using a DEM. If the 1907–1912 dipping locations are hydrologically **outside** the
catchment, that is a strong argument against creek transport from those sites — a falsification
test, and one that could close the hypothesis cheaply.

> **Constraint carried from the Mission 7 rules:** 3a–3d describe landscape form and land-surface
> condition. None of them may be presented as showing that anything moved, and no plume, dispersion
> or exposure product may be produced from them.

---

## Phase 4 — sampling design *(gated: needs consent + funding; do not execute)*

Only after Phases 0–3. Design principles, so that if it ever happens it is worth doing:

- **Depositional zones**, chosen from the Phase 3a map, not convenience.
- **Depth-resolved cores**, not surface grabs. A pre-1913 layer, if it survives, is at depth. A
  surface sample answers a different question.
- **Matched comparison drainages** in Zone C communities selected on objective criteria — development
  age, geology, climate, landscaping intensity — and **never on cancer counts**.
- **Full analyte suite**, not arsenic alone: arsenic, lead, DDT/DDE, toxaphene, PAHs. Lead-arsenate
  co-occurrence is diagnostic; arsenic alone is not.
- **Speciation** where total arsenic exceeds background: inorganic vs organic changes the toxicological
  meaning entirely.
- **Chain of custody and an accredited lab**, or the results are worthless for any downstream purpose.
- **Blind the lab** to which samples are Ladera and which are comparison.

**Access consent required from:** LARMAC and sub-associations (common areas, parks), County (channel
and O'Neill Regional Park), CUSD (school grounds). None obtained.

---

## Phase 5 — interpretation limits, fixed in advance

1. Arsenic in sediment shows **arsenic in sediment**. It does not show human contact, dose, or
   uptake.
2. Elevated relative to background shows **elevation**, not source. Attribution requires isotopic or
   co-contaminant fingerprinting, and even then it is an inference.
3. Nothing measured in 2026 establishes what any person contacted in 1999.
4. **The health question is not answered by this pathway at any point.** Sediment chemistry cannot
   establish causation of any illness, and this plan may not be represented as attempting to.

---

## Where this fits in the larger question — the part the physicians need

The project's own literature review (`research/literature/evidence_review.md`) establishes facts
that any physician colleague will already know, and that any reviewer will raise immediately:

- Ewing sarcoma is defined by a somatic **EWSR1-FLI1** fusion binding GGAA microsatellites;
  germline microsatellite architecture drives susceptibility.
- The ancestry gradient is the most striking epidemiologic fact and is **largely biological** —
  incidence is 6–8× lower in African ancestry, 2–3× lower in East/Southeast Asian ancestry.
- **No environmental, lifestyle, radiation or familial cause is established.** The etiologically
  relevant exposure window, if one exists, is unknown.
- The strongest Ewing-specific positive signals are **parental farming** studies (paternal OR 2.3,
  maternal 3.9) — and farming is a *proxy* for pesticide exposure, never a measurement of it.

Two consequences follow, and they are the most useful things in this document:

**First, the denominator problem is the single greatest threat to any cluster claim here.** Because
risk is strongly ancestry-patterned through germline biology, a cluster in a predominantly
non-Hispanic-white master-planned community has an **elevated baseline expectation**. Using an
all-population incidence rate as the denominator would bias a standardised incidence ratio upward
and produce an apparent excess that is an artefact of the comparison, not a signal. **Any analysis
that does not ancestry-adjust the denominator will be dismissed by the first qualified reviewer who
reads it.** Getting this right is worth more than any amount of additional exposure data.

**Second, exposure assessment cannot substitute for the case data.** However thorough the
environmental reconstruction becomes, the question "is there an excess here?" is answered only by
registry-confirmed counts with an appropriate denominator — gate **G01**, California Cancer
Registry. That remains the highest-value unopened gate in the entire project, and it needs a named
institutional requester, which is precisely what physician involvement could provide.

The honest framing for collaborating clinicians is therefore not *"help us tie arsenic to these
cancers."* It is:

> *"There is a documented state-mandated arsenical program in this landscape, a continuous drainage
> that has never been sampled, and reported cases. We have built a rigorous exposure-side
> reconstruction. What we cannot do without you is (a) get registry-confirmed case data with an
> ancestry-appropriate denominator, and (b) design a sampling programme that could falsify our own
> hypothesis. Will you help us test it properly?"*

That version is fundable, defensible, and survives peer review. The first version does not, and a
finding presented as a conclusion reached in advance will be discounted the moment it reaches
anyone with the standing to act on it.

---

---

## Phase 3d, executed 2026-07-30 — a preliminary falsification result

Ran the catchment-proximity test described in 3d against the documented dip-ranch geography
(T6S R7W Sections 24/25, Bell Canyon / north-east Coto de Caza — the corrected Joplin patent
location). Straight-line distance from that vicinity to each named channel in the study area:

| Channel | Distance from documented dip-ranch vicinity |
|---|---|
| **Cañada Chiquita** | **4.80 km** — nearest |
| Trabuco Creek Channel | 5.56 km |
| Acjachema Storm Drain | 7.37 km |
| Oso Creek Channel | 8.56 km |
| **Horno Creek Channel** | **10.08 km** — farthest |

**Preliminary reading, with the limitation stated first: this is straight-line distance, not
hydrological connectivity.** Two points 4 km apart can sit in different watersheds separated by a
ridge, and two points 10 km apart can share a channel. This test does not settle the question. It
orders the candidates.

Subject to that, three things follow:

1. **Horno Creek is the *least* likely reach to carry a signature from the documented dip ranch.**
   It is the farthest of the five, and Bell Canyon drains toward the Trabuco system, which passes
   Ladera Ranch on its **western** boundary and joins San Juan Creek **downstream** of Horno Creek's
   own confluence. On that geometry, water from the documented dip site would bypass the community
   entirely rather than flow through it.
2. **Cañada Chiquita is the better candidate** for any transport pathway from the documented site,
   and it runs along the **eastern** edge of the study area. If the transport hypothesis is to be
   tested at all, that is where to test it first — a change of priority this analysis did not
   anticipate.
3. **This does not close the arsenic question.** It constrains one specific pathway. The 1907–1912
   quarantine covered the whole county, dipping was compulsory, and the O'Neill Ranch — the land
   Ladera Ranch is built on — would have needed its own facilities. **A vat sited on the O'Neill
   Ranch within the Horno or Chiquita catchment remains entirely possible and is unaddressed by this
   test.** The prior imagery audit found no vat resolvable on adequate frames, which is an absence of
   evidence at the resolution examined, not evidence of absence.

**What this changes in practice:** stop treating "arsenic washed down from the Bell Canyon dip ranch
into Ladera" as the leading pathway. Either find a facility inside the local catchment, or the
transport hypothesis needs a different mechanism than this creek.

**Required to confirm or overturn:** a DEM-based watershed delineation (USGS 3DEP 1 m or 10 m,
free at https://apps.nationalmap.gov/downloader/) establishing the true drainage divide between the
Trabuco and San Juan sub-basins and which sub-basin the Section 24/25 ground actually sits in. Until
that is run, the table above is ordering, not proof.

*Provenance: A2 / interpreted. Channel geometry A+ (OC Flood_Channels). Dip-ranch location A2
(patent record, corrected). Distance calculation deterministic; hydrological inference NOT yet
verified.*

---

## Immediate next actions

| Priority | Action | Needs |
|---|---|---|
| 1 | **DEM watershed delineation** — confirm or overturn the 3d result above | nothing; USGS 3DEP is free |
| 1 | **Phase 3a–3c** — depositional mapping, channel change detection, grading adjacency | nothing; executable now |
| 2 | **Phase 0** — background arsenic, screening level | nothing; free public data |
| 3 | **Phase 1** — CEDEN / Region 9 sampling history | nothing; free public data |
| 4 | Add sediment-removal history to the OC records request | user sends |
| 5 | G01 registry approach via a physician collaborator | institutional standing |
