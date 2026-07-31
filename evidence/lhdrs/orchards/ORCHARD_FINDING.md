# Orchard delineation — a second arsenic source, mapped, and where it is not

**Run 2026-07-31.** 35 blocks detected across 1929/1938/1947 at ~0.37 m/px.

## What was done

Built a detector for the specific signature of a planted orchard: **periodic row texture** at a
plausible spacing, concentrated at **one orientation**. Row spacing detected is **5.3–8.0 m,
median 6.8 m** — consistent with period citrus and walnut planting.

## Two corrections made to my own detector before trusting it

**First version flagged 36,600 of 37,000 cells** — essentially the entire frame. Cause: it tested
only whether power existed in the row-spacing band, and film grain is broadband, so every cell
passed. Fixed by adding a **directionality test**: an orchard concentrates power at one orientation,
grain is isotropic.

**Second version still flagged 13,904 cells.** So I calibrated instead of guessing — scored 8
**visually confirmed** orchard sites and 8 confirmed rangeland sites from the vat-hunt contact
sheet:

| | score |
|---|---|
| confirmed orchards, in-band spacing | 0.66 – 0.75 |
| confirmed rangeland | max 0.22 |

Threshold set at 0.30, band tightened to 4.5–8.5 m. That favours **precision over recall** — the
map will miss marginal or immature blocks, and should be read as a minimum.

Result: **874 cells, 35 blocks** — 49 ha (1929), 111 ha (1938), 8 ha (1947).

## The finding, and it cuts against the concern

**The orchards are almost entirely OUTSIDE the community, and concentrated to the west and south.**

Of 35 blocks, 7 fall inside the study area — all in the **far south-west corner**, and all remote
from anything that matters:

| Block | Area | To nearest school | To the drainage |
|---|---|---|---|
| 33.53656, −117.66825 | 17.5 ha | 2,760 m | 2,033 m |
| 33.53283, −117.66904 | 9.7 ha | 2,979 m | 2,005 m |
| 33.52869, −117.66803 | 2.3 ha | 3,122 m | 1,703 m |
| four smaller blocks | 0.9–2.3 ha | 2,793–3,207 m | 1,439–1,676 m |

**Nearest orchard block to any school is 2.8 km. Nearest to the drainage is 1.4 km.**

So the orchard pathway, which looked like a promising second source when the vat hunt surfaced it,
**does not co-locate with the community, the schools, or the creek**. On this evidence it is a
weaker explanation for anything in Ladera Ranch than it first appeared — not because orchards
weren't sprayed, but because they weren't *here*.

That is a real result and it should be reported as plainly as a positive would be.

## What this does not settle

- **Precision-biased**: immature or sparse plantings score below threshold. This is a floor.
- Detection covers **1929–1947 only**. An orchard cleared before 1929 leaves no row texture.
- The 2004 basemap shows the blocks now sit under built development and open slope — soil could
  have been graded, cut, filled or exported since.
- **Lead arsenate use on these specific blocks is not documented.** It was the standard orchard
  insecticide of the era as general practice. Only measurement can speak to these parcels.

## Why it still matters for sampling design

Lead–arsenate co-occurrence remains the **diagnostic that separates the two candidate sources**:

- orchard ground → arsenic **with** lead
- cattle-dip ground → arsenic **without** lead

The sampling plan already specifies lead in the analyte suite. This map now says where the orchard
confounder actually is, so a result from the community core cannot be dismissed as "probably an old
orchard" — because on this evidence, the nearest one is nearly 3 km away.
