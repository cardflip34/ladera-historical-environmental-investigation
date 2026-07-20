# Reservoirs, Water Infrastructure, and Ranch Facilities

## 15.1 Why water is the organizing question

Cattle concentrate at water. It is the most reliable spatial regularity in range livestock
management, and everything else follows from it: stock trails converge on water, holding
grounds sit near water, and working facilities — corrals, chutes, and historically dipping
vats — were sited where the animals already gathered, because moving cattle is expensive and
moving water is harder.

This gives the investigation a search strategy that does not depend on finding a vat directly.
**Locate the historical water, and you have located the small number of places where a working
facility could plausibly have stood.** Water is mapped; vats are not.

---

## 15.2 The 1968 surface-water layer

The 41 water bodies in this layer were not detected by an algorithm looking at photographs.
They were extracted from the **1968 USGS 7.5-minute San Juan Capistrano quadrangle** by
isolating the printed cyan hydrography ink.

The distinction matters. Every polygon recovered this way was **drawn by a surveyor who visited
the ground**. This is cartographic testimony, not image interpretation.

**Method.** Blue-dominant pixels were isolated by threshold (blue exceeding red by 26 levels
and green by 8, with brightness and paper-white exclusions), morphologically cleaned, and
labelled into connected components. Features smaller than 350 m² were dropped as stream
hairlines and print noise; shapes with elongation greater than 7 were dropped as drawn stream
lines rather than impoundments.

**Result: 41 water bodies of 350 m² or larger, 16 of them inside Zone A.** The largest is
24,745 m² at 33.54394, −117.66132.

@figure FIG-07


::: classification fact
**EM-005 · ESTABLISHED FACT · Confidence: High**
The 1968 USGS field survey mapped 41 surface-water bodies of ≥350 m² within the study
footprint, 16 of them inside Zone A.
*Supporting:* Cyan hydrography extracted from the georeferenced 1968 sheet; 41 features passed
area and elongation filters.
*Counter-evidence:* Derived by colour thresholding, so it inherits any generalisation in the
original cartography and any scan artefacts. Positions are **centroids, not digitised
outlines**. Features under 350 m² were excluded by design and are therefore absent from the
layer regardless of whether they existed.
*Citation:* USGS San Juan Capistrano 7.5′ quadrangle, 1968 edition [S-MAP-04];
`pipelines/python/extract_topo_water.py`.
:::

### The method that was tried first, and abandoned

Before the ink-extraction approach, water was sought directly in the 1929 and 1937 aerial
photographs on a defensible physical premise: on panchromatic film, standing water is both
**dark** and **smooth**, whereas riparian vegetation is dark but strongly *textured* and
hillslope shadow is dark but *elongated and attached to terrain*. Requiring low brightness and
low local variance together should separate ponds from both.

It did not work. The detector returned 111 candidates in the 1929 frame and 225 in the 1937
frame, roughly 100 of them inside Zone A. Visual review showed it was keying on **hillslope
shadow**.

The failure had a specific cause worth recording: the scanned frames have incompatible tone
curves. The 1929 frame's 12th-percentile brightness sits around DN 109–128 — it is a bright,
low-contrast scan. The 1937 frame's sits around DN 23–43 — dark and high-contrast. No single
percentile threshold serves both, and the terrain is steep enough that shadow dominates the
dark tail in the contrastier frame.

The script is retained with the failure documented in its docstring, so the approach is not
naively retried. **None of its candidates appear anywhere in this publication.**

---

## 15.3 Testing the central spatial hypothesis

An observation prompted this test. Looking at present-day property listings against the
historical maps, the homes in Ladera Ranch and Rancho Mission Viejo appear to sit exactly where
the old ranch water sources were. If true, and if working facilities followed water, that would
place modern housing on the most likely locations of historical cattle-handling activity.

It is a genuinely good hypothesis. It was tested directly.

**Method.** For each of the 41 water bodies mapped in 1968, count modern building footprints
within 100 metres, and record the distance to the nearest one. Compare against a null: the same
measurement taken at random points drawn from the same area. Building footprints from
OpenStreetMap, n = 10,618.

### The descriptive result — the observation holds

| Nearest modern building to a 1968 water body | Sites |
|---|---|
| within 100 m | 24 / 41 (59%) |
| within 200 m | 34 / 41 (83%) |
| within 300 m | 40 / 41 (98%) |
| **within 500 m** | **41 / 41 (100%)** |

**Median distance from a ranch-era water body to the nearest house today: 66 metres.**

Every single one of the water sources this land's cattle operation depended on now has a house
within 500 metres of it. As a description of the present landscape, the observation is exactly
right.

::: classification fact
**EM-006 · ESTABLISHED FACT · Confidence: High**
Every one of the 41 ranch-era water bodies now has a modern building within 500 m; the median
distance to the nearest building is 66 m.
*Supporting:* Measured against 10,618 OSM building footprints.
*Counter-evidence:* OpenStreetMap completeness is not guaranteed uniform. However, under-mapping
would bias measured distances *upward*, not downward — so the finding is conservative.
*Citation:* `pipelines/python/premise_homes_on_water.py` [S-GIS-02].
:::

### The causal result — the explanation does not hold

| | Buildings within 100 m |
|---|---|
| 1968 water sites in Zone A (n = 16) | 9.0 |
| Random points in Zone A (n = 6,000) | 9.3 |
| **Enrichment** | **0.97× (permutation p = 0.51)** |

The old water sites are **no more built over than any other ground in Zone A**. Developers did
not seek out the water and the cattle-working areas. If anything the point estimate falls
marginally below chance, and it is statistically indistinguishable from it.

::: classification fact
**EM-007 · ESTABLISHED FACT · Confidence: High**
Modern housing was **not** preferentially sited on the ranch-era water bodies.
*Supporting:* Zone-A-restricted null: 9.0 buildings within 100 m of water sites vs 9.3 for
6,000 random points. Enrichment 0.97×, permutation p = 0.51.
*Counter-evidence:* An initial bbox-wide null gave 0.79×, but that null was inflated by dense
Mission Viejo development falling inside the bounding box. The Zone-A-restricted null is the
fair comparison and is reported as primary. Both are published.
*Citation:* `research/historical_imagery/premise_null_zonea.json` [S-GIS-02].
:::

### Why both results are true at once

Development here was **near-total**. Once nearly every part of the footprint is close to
housing, proximity to housing stops carrying information. The water sites are all near houses
because *everything* is near houses.

The pattern was real. The explanation for it was not.

@figure FIG-01


### What this changes, and what it does not

It removes a mechanism: "the developers built on the cattle-working grounds" is not supported,
and should not be asserted.

**It does not reduce the exposure question — arguably the opposite.** If ranch-era ground
contamination exists anywhere within this footprint, near-total development means it now sits
under or beside housing **regardless of whether anyone selected those locations**. Targeting was
never required for coincidence; comprehensive development achieves the same outcome by a
different route.

What falls away is an explanation. The underlying concern is untouched.

---

## 15.4 A measurement that looks compelling and must not be used

Buildings in this footprint sit on a median slope of **1.7°**, against **6.7°** for available
land across the same extent. On its face that is a strong signal: houses are on flat ground,
flat ground is valley bottom, valley bottoms are where water and cattle were.

**This reasoning is circular and the measurement cannot be used.**

Ladera Ranch was **mass-graded**. The building pads were cut flat. The flatness measured under a
house today was manufactured by the grading — which is itself one of the activities under
investigation. The modern digital elevation model describes engineered pads, not original
landform, and cannot speak to where anyone chose to build relative to natural terrain.

::: classification limit
**EM-008 · ESTABLISHED FACT (methodological exclusion) · Confidence: High**
Modern slope beneath buildings cannot be used to infer original landform siting.
*Supporting:* Buildings at median 1.7° vs 6.7° for available land — but Ladera Ranch was
mass-graded, so pad flatness was manufactured by the grading under investigation.
*Counter-evidence:* None. This is a deliberate methodological exclusion, recorded so the figure
is not later mistaken for a finding.
*What would be required instead:* Reconstruction of pre-1980 elevations from the 1948 and 1968
topographic contours, which would give original landform independent of the grading.
*Citation:* USGS 3DEP DEM [S-GIS-01]; this investigation.
:::

This is recorded rather than omitted because the figure is genuinely persuasive and someone
will eventually rediscover it. It should be met with this note.

---

## 15.5 Water infrastructure named in the record

The 1968 sheet labels several features by name:

| Feature | Type | Source | Status |
|---|---|---|---|
| Terminal Reservoir | Reservoir | 1968 USGS quad, labelled | Located on sheet |
| Water Tank | Tank | 1968 USGS quad, labelled | Located on sheet |
| "WT 521" | Water tank w/ elevation | 1968 USGS quad, labelled | Located on sheet |
| Gaging Station | Stream gage | 1968 USGS quad, labelled | Located on sheet |
| Landing Strip | Airstrip | 1968 USGS quad, labelled | Located on sheet |
| Impoundment chain | ~8 stock ponds | 1968 USGS quad, drawn | Trabuco corridor |

::: classification open
**OPEN QUESTION — named ranch facilities not yet located.**
The historical record refers to a set of named ranch working facilities associated with this
operation — headquarters, cow camps, line camps, named corrals. **None has yet been located
with coordinates by this investigation**, and none appears in the imagery examined. Whether any
stood within the study footprint, as opposed to elsewhere on a ranch that covered well over a
hundred thousand acres, is unresolved.
*Next step:* General Land Office survey **field notes** for the relevant townships. Surveyors
routinely recorded springs, corrals, houses, and improvements in their notes that never appeared
on the published plat. This is the highest-value untapped cartographic source identified.
:::

---

## 15.6 Where this leaves the search

The water layer did its job. It converted a vague question — *where might a working facility
have been?* — into a bounded set of 41 specific locations, 16 of them inside the community.

It did not find a vat, and the spatial test it enabled removed one attractive hypothesis about
how development related to that history.

What it produces is a **sampling frame**. If soil investigation is ever undertaken here, these
41 locations plus the Trabuco ranch node are where an investigator with limited resources should
look first — not because contamination is expected at them, but because they are the places
where the historical activity of interest would have concentrated if it occurred at all. That
recommendation is developed in the environmental investigation chapter.
