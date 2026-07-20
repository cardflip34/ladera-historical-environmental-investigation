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

## C-004 — The "a corral complex would be unmistakable" claim was overconfident (2026-07-19)

**What was wrong.** After correcting C-003 and obtaining 1.15 ft/px aerial photography, this
investigation stated that the resolution objection to finding a dipping vat had "disappeared
entirely" — that at that resolution "a two-metre vat is roughly six pixels across, and a corral
complex … would span hundreds of pixels. It would be unmistakable."

**What the primary source actually says.** USDA Bureau of Animal Industry Circular 174,
*Eradicating Cattle Ticks in California* (1911), documents that California vats were frequently
**small and cheap**:

- The **cage vat**: materials cost **$55–65**. It "is installed near the corrals and requires
  only a short chute leading from the corral to the cage." Critically: "Draining pens with such
  vats are **not essential and are rarely used**, as the animal drains while the cage is being
  raised." (p. 299)
- The **wade tank**: "can be constructed with an outlay of **less than $10** for materials, thus
  being cheaper than a good spray pump," and is "recommended only in the disinfection of very
  small herds." Figure 10 shows a vertical section roughly **15 feet long and 4 feet deep**.
  (p. 299)

**Why this matters.** The earlier argument assumed the American swim-vat model: a long concrete
trench with a sloped drip pen and substantial holding pens — a complex that would indeed be
obvious from the air. Circular 174 shows that was **not the only California pattern**. A wooden
cage vat or wade tank installed beside an existing corral, with no drip pen, is a fundamentally
different photographic target: small, low-contrast, and easily lost against ranch infrastructure
that was itself unremarkable.

**Effect on the findings.** The negative imagery result stands as an observation — no vat or
corral complex was identified — but its **evidential weight is substantially reduced**. Claim
EM-003's confidence is downgraded from Medium to **Low**.

The corrected position: the imagery search would likely have detected a **large swim-vat
installation** and did not. It provides **weak to no evidence** against a small cage vat or wade
tank, which the primary source indicates were common in California and which cost as little as
ten dollars in lumber.

**Pattern worth noting.** This is the second time this investigation has built an argument on an
assumption about the physical evidence without checking the primary source first — C-003 assumed
the imagery was inadequate; C-004 assumed the target would be large. Both assumptions were
convenient. Both were wrong in the direction that made the analysis simpler.

## C-005 — The 1842 grant date circulating online is wrong (2026-07-19)

**What is wrong, in the wider record.** Several web sources give **1842** as the grant date for
Rancho Mission Viejo / La Paz.

**The primary record.** Ogden Hoffman, *Reports of Land Cases Determined in the U.S. District
Court, Northern District of California* (1862), Appendix, claim no. 396:

> Juan Foster, claimant for Mission Vieja or La Paz, in Los Angeles county, **granted April 4th,
> 1845, by Pio Pico to Agustin Olvera**; claim filed October 16th, 1852, confirmed by the
> Commission October 31st, 1854, by the District Court February 21st, 1857, and appeal dismissed
> June 4th, 1857; containing 46,432.65 acres.

Read and verified directly from the full text, and corroborated by the volume's own index.

**Also corrected:** **Forster was the claimant, not the grantee.** The grantee was **Agustín
Olvera**. Forster acquired the rancho later and pressed the claim in his own name. Several
secondary accounts collapse this distinction.

## C-006 — Armor (1921) was briefly treated as a land-title source (2026-07-19)

**What was wrong.** An earlier version of chapter 7 reproduced Samuel Armor's ownership
succession — Forster → Crocker → Flood → O'Neill — with only a general caveat that it was a
biographical sketch rather than a deed abstract.

**What checking against the primary record showed.** Armor contains several substantive errors
in that very passage:

- He calls the three ranchos "Spanish grants." All three were **Mexican**.
- He states Mission Viejo "originally belonged to the Picos." Hoffman gives the grantee as
  **Agustín Olvera**.
- He describes Pío Pico as the last governor "under the Spanish regime." Pico was the last
  **Mexican** governor.
- In his rancho table he **conflates two different ranchos** — San Juan Cajón de Santa Ana
  (confirmed to Ontiveros, 31,501.99 acres) and Cañón de Santa Ana (Bernardo Yorba, 13,328.53
  acres).

**The Charles Crocker link is uncorroborated** and appears in no other source consulted. It is
now reported as *what Armor says*, not as established fact, and EM-027 is downgraded from
ESTABLISHED FACT to **INVESTIGATIVE LEAD, Low confidence**.

**Armor remains useful** — his acreage figures for Mission Viejo and Trabuco match Hoffman,
Lewis (1890) and the California Secretary of State exactly. He is reliable on some things and
not on others, which is precisely why source grading exists. He is graded **B1** and should not
carry a title claim alone.

**Pattern note.** This is the same failure mode as C-001, C-003 and C-004: a convenient source
was used without being checked against the primary record. Four of six corrections now share
that shape.
