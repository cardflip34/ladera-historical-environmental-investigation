# Mission 7 / Phase 3 — mass-grading progression from Landsat, 1997-2006

**Run:** 2026-07-28 · `scripts/lhdrs_m7_grading_landsat.py` (reproducible) ·
provenance **A+** (USGS/NASA Landsat C2 L2) · statementClass **interpreted** (NDVI threshold)

## Result

| Year | Scene | Sat | Bare/disturbed | Median NDVI |
|---|---|---|---|---|
| 1997 | 04-24 | L5 | 4.2% | 0.398 |
| 1998 | 04-27 | L5 | 1.2% | 0.622 |
| 1999 | 03-13 | L5 | **10.3%** | 0.447 |
| 2000 | 05-18 | L5 | 26.1% | 0.383 |
| 2001 | 05-05 | L5 | 30.4% | 0.432 |
| 2002 | 03-20 | L7 | **41.3%** (peak) | 0.245 |
| 2003 | 05-11 | L5 | 31.1% | 0.305 |
| 2004 | 05-13 | L5 | 26.7% | 0.286 |
| 2005 | 04-05 | L5 | 14.5% | 0.422 |
| 2006 | 02-12 | L5 | 23.3% | 0.280 |

All ten years achieved >=97% valid pixels after cloud/shadow masking. Chart:
`evidence/lhdrs/mission7/grading_progression_chart.png`.

## What it shows

A clear rise-and-fall consistent with a single large grading and construction campaign: near-zero
disturbance through 1998, first material increase in **1999**, sustained escalation to a **2002
peak**, then decline as ground was built on and landscaped.

**This is consistent with the independently documented development chronology** (entitlement ~1997,
mass grading from 1999, first homes 1999, build-out through ~2006). That agreement is a useful
validation signal for the method. It is **not** proof of either the method or the chronology, and
neither dataset should be cited as confirming the other.

## Limitations that constrain any use of this

1. **30 m pixels ~ one pixel per residential lot.** Rooftops are not resolvable. **No parcel-level
   claim may be derived from this product.** It answers "how much of the area was disturbed," never
   "was this parcel built."
2. **Bare soil has multiple causes.** Grading, senescence, fire and fallow ground read alike.
   Scenes were selected in the green season (Jan-May) to reduce this, not remove it.
3. **1998 is a climate artifact risk.** Median NDVI 0.622 is the highest in the series; 1998 was a
   strong El Nino year in Southern California. The 1997 -> 1998 *drop* in bare ground is more likely
   wet-year greening than land-use change. Do not read it as "less disturbance."
4. **2006 is seasonally inconsistent** (February vs March-May elsewhere). Its 23.3% is not directly
   comparable to adjacent years and the apparent uptick may be seasonal.
5. **2002 used Landsat 7**, pre-dating the 2003-05-31 SLC failure, so it is unaffected by striping.
   Landsat 5 was preferred for 2003+ specifically to avoid SLC gaps.
6. **statementClass = interpreted.** An NDVI threshold is an interpretation applied to documented
   imagery. It must never be promoted to `documented`, and both confidence chips render on every
   artifact.

## Explicitly out of scope

This measures **ground disturbance only**. It is not a contamination, dust, or exposure product; no
arsenic, air-movement, or health inference may be drawn from it. Those remain gated per the Mission 7
constraints and require real measured environmental data.

## What this unblocks, and what it does not

- **Unblocks:** neighborhood-scale grading chronology for the 1999-2004 window that had zero
  high-resolution coverage. Phase 3 of the reconstruction can proceed at this scale, free, now.
- **Does not unblock:** Phase 4 parcel-level build-out, which still requires the County permit/CO
  index (`M6-REQ-OC-PERMIT-01`) or high-resolution aerials. Landsat cannot substitute.
