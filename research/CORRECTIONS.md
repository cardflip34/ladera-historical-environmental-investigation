# CORRECTIONS

Material corrections to the platform's data, recorded openly per `SOURCE_POLICY.md`. Nothing
is silently revised.

## C-001 — Study-area centroid was ~1.93 miles too far north (2026-07-18)

**What was wrong.** The platform inherited a working centroid of **33.5747, −117.6353** from
the original project brief. The authoritative Ladera Ranch CDP centroid is
**33°32′48″N 117°38′25″W = 33.5467, −117.6403**.

**How it was caught.** Rendering the report map figure showed the Zone A polygon sitting
*north* of the OpenStreetMap "Ladera Ranch" place label — a visual contradiction that a table
of numbers would not have surfaced.

**Magnitude.** 1.93 miles north–south, 0.29 miles east–west.

**What it affected.**
- Zone A boundary and the Zone B 5-mile ring (both regenerated).
- All distance-to-community figures for environmental sites and oil/gas wells (recomputed by
  haversine from the corrected centroid).
- Default map centre in the web app, `.env.example`, and the print-map figure.

**What it did NOT affect.**
- Demographics and person-years (CDP-based, not centroid-based).
- SIR scenarios and Poisson intervals.
- PUR analysis and the location-precision finding.
- The PLSS result: re-queried at the corrected point, Ladera Ranch is still
  **T7S R7W, section 00 (unsectioned)** — the finding stands.

### Corrected distances — environmental sites

| Site | Was | Now |
|---|---|---|
| Blue Diamond Materials Plant | 3.1 | **1.3** |
| Carl Hankey Elementary (former orchard/row crops) | 1.2 | **1.8** |
| Meggitt (OC) Inc. / former Endevco | 4.2 | **2.3** |
| Plant Depot School Site (arsenic, nitrate) | 4.8 | **2.9** |
| Ambuehl Elementary (DDT, toxaphene) | 5.0 | **3.0** |
| San Juan Elementary (arsenic, chlordane, DDT) | 5.1 | **3.2** |
| SOLAG Disposal Site | 5.2 | **3.5** |
| Prima Deshecha Landfill | 3.5 | **4.3** |
| Alicia Towne Plaza | 4.3 | **5.1** |
| Polo Cleaners | 3.6 | **5.6** |
| El Toro High School | 5.7 | **6.8** |
| El Toro MCAS (former) | 9.0 | **10.3** |

The former-agricultural school sites carrying legacy organochlorine/arsenical residues are
therefore **closer** than previously recorded (~3 miles rather than ~5).

### Corrected distances — oil & gas wells (CalGEM)

| Well | Status | Was | Now |
|---|---|---|---|
| Citizens National Trust B-1 / Exxon Mobil | Plugged, dry hole | 2.0 | **0.25** |
| O'Neill #1 / Union Oil | Plugged, dry hole | 2.7 | **0.77** |
| Shumaker #1 / Conoco | Plugged, dry hole | 3.7 | **2.98** |
| Norswing & Halvorson #1 | Idle | 6.0 | **4.22** |
| O'Neill Estate B-1 / Exxon Mobil | Plugged, dry hole | 3.7 | **5.27** |
| South Fullerton Oil Co. #1 | Idle | 5.1 | **5.59** |

**Consequence.** **Two plugged/abandoned wells lie within ~1 mile of the community centroid**
(one at ~0.25 mi, effectively within the footprint), rather than the ~2–2.7 miles previously
recorded. Three lie within 5 km; all six within 10 km.

**How to interpret this — carefully.** A 2026 peer-reviewed California study (Clark et al.,
LIT-001) reported a *suggestive, non-significant* association between residential proximity to
**abandoned** oil/gas wells within 10 km and childhood Ewing sarcoma (OR 1.27, 95% CI
0.96–1.66), stronger in Hispanic children. The corrected geometry places this community well
inside that exposure contrast, which **raises the priority of characterising these wells** —
it does **not** establish exposure or causation. These are mid-20th-century plugged
exploratory dry holes, generally lower leakage risk than production wells, and the community's
drinking water is imported rather than local groundwater. Proximity is a screening signal, not
a dose.

**Follow-up added:** verify well integrity/plugging records and any methane or soil-gas
monitoring near the two nearest wells (added to the evidence-gate list).

## C-002 — Creek misidentified in the historical-imagery analysis (2026-07-18)

**What was wrong.** The drainage corridor containing the 1948 ranch structure at
**33.55505, −117.65492** was described as **Cañada Chiquita**. It is **Trabuco Creek**.

**How it was caught.** The 1937–38 OC Survey aerial carries the county cartographer's own red
ink label across the corridor, legible at 1.15 ft/px. Cañada Chiquita lies further east.

**What it affected.** The layer label on the interactive map and the prose in
`research/historical_imagery/README.md`. **Coordinates, distances and the structure's
identification as a ranch-activity node are unaffected** — only the name of the watercourse
was wrong.

## C-003 — "Earliest available imagery is 1948" was wrong (2026-07-18)

**What was wrong.** The first historical-imagery pass concluded that the earliest imagery
covering the footprint was the **1948** USGS topographic sheet, and built an argument on that:
that the record post-dates the 1907–1917 dipping period by **31 years**, making a vat
undetectable in principle.

**What is actually available.** Orange County publishes scanned aerial photography back to
**1929** through a public ArcGIS image service. Thirty-six frames intersect the footprint;
six pre-date 1950. The best, 1937–38, resolves at **1.15 ft/px**.

**Why it was missed.** The service sits under `https://ocgis.com/arcpub/rest/services/`, not
the conventional `/arcgis/` path, which returns 404. An earlier lead — webmap ID
`75daa7a29b7c4ea0b5c01596ac24904d` — resolved to rainfall layers and was a dead end.

**What it changes.** The gap to the dipping period narrows from 31 years to **12**, and the
resolution objection disappears entirely: at 1.15 ft/px a corral complex would be
unmistakable. **The conclusion nevertheless stands — no dip vat or corral was found** — but it
now rests on adequate imagery rather than on the imagery being inadequate. That is a
materially different, and stronger, basis for the same negative finding.
