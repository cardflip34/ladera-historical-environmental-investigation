# Irvine / Newport Coast — historical aerial imagery (working notes)

> Documentary land-use reconnaissance. **No contamination or dip vat is identified or claimed.**
> Working file — not part of the publication.

## The pipeline (now proven and reusable)

The OC Survey public ArcGIS server serves historical aerials over the whole county via a mosaic
ImageServer — reachable directly (no Cloudflare block), so the imagery phase the Newport Coast recon
called "hands-on / physical" is actually doable online:

- Server: `https://www.ocgis.com/arcpub/rest/services/Historic_Imagery/Historic_Imagery/ImageServer`
  (SR = EPSG:2230, CA State Plane VI, ftUS).
- Aerials covering the former Irvine Ranch include **"Irvine Ranch 1931"** and **"Orange County
  1938 / 1947 / 1952 / 1953 / 1960"**, plus later years. The **1931 Irvine Ranch** frame is the
  oldest and sits only ~19 years after the ~1912 end of dipping.
- Reproduce: `python3 scripts/pull_oc_historical_aerial.py <lon> <lat> <half_ft> "Irvine Ranch 1931" out.jpg`

Note: a search-surfaced "Orange_USDA_1943" ImageServer on a Texas state server is **Orange County,
TEXAS** (UTM 15N, ~30°N) — a false lead, rejected, not used.

## First look — 1931 Irvine Ranch, Bommer / San Joaquin Hills area

Files: `research/irvine/imagery/bommer_1931_equalized.jpg` (wide, ~1 mi),
`bommer_1931_structures_zoom.jpg` (ranch complex). Centered near the Bommer Canyon area of the former
Irvine Ranch (area-level only; no exact coordinate published).

**What is visible (INVESTIGATIVE LEAD · Confidence: Medium for "a ranch complex," Low for specifics):**
- A **ranch building complex** at a canyon/drainage confluence: several rectangular buildings
  (bright barn/shed roofs), planted **shade trees** (typical of a ranch headquarters/homestead),
  and **converging dirt roads/tracks**.
- Surrounding **dry-farmed field patterns** and **riparian vegetation** along the creeks.
- Some **rectilinear features** adjacent to the buildings that *could* be corrals/stock pens — but
  this is **not confirmed** at this resolution.

**What is NOT identifiable (critical — the C-004 discipline):**
- **No dip vat can be identified.** A dip vat is a narrow (~30–60 ft) trough; it would be at or below
  the resolution limit and indistinguishable from other linear features in this scan. Its presence is
  neither shown nor excluded.
- The complex's exact identity (the documented "Bommer Canyon Cattle Camp" vs. another Irvine Ranch
  line camp/HQ) is **not yet confirmed** — the centering used the Bommer Canyon coordinate, but the
  building cluster's identity needs cross-checking against ranch maps (Sherman Library) and higher-res
  frames.

**Counter-evidence / limits:** the mosaic is a faded scan (heavy histogram stretch applied — stretching
also amplifies artifacts); a ranch HQ having buildings, trees, roads, and water is *expected* on any
cattle ranch and is **not** evidence of dipping; feature identification here is provisional and must be
confirmed with (a) the higher-resolution original frames (UCSB FrameFinder / OC Survey detail scans),
(b) ranch maps naming the facilities, and (c) ground/records work.

## Systematic 1938 sweep of the Irvine Ranch cattle core (done)

`irvine_1938_sweep_montage.jpg` — a 3×2 grid (~2.5 mi/cell) over the southern ranch core
(Bonita / Bommer-Shady / Quail Hill / Newport Coast / San Joaquin Hills / Laguna coast).

**What the sweep shows (land use, ~15 ft/px overview):** the core splits cleanly into **cultivated
farmland** in the north/northeast (geometric field patterns, tree-lined lanes — the orchard/row-crop
zone where DTSC later found lead-arsenate arsenic) and **natural grazed canyon-ridge** toward the
coast (cells D/E/F — the pre-grading Newport Coast/San Joaquin Hills terrain).

**Structure clusters that resolve (INVESTIGATIVE LEAD · Confidence: Low for specifics):**
1. **Bommer Canyon ranch-HQ complex** (already imaged) — the documented cattle-handling node.
2. **A NE farmstead** (Quail Hill / Sand Canyon vicinity, `irvine_1938_pondcluster_zoom.jpg`) — 5–8
   buildings at a hill base with a eucalyptus windrow lane, surrounded by **cultivated fields**. Reads
   as a **farming** node (orchard/crop), not a cattle-dip site.

**No dip vat is identifiable anywhere in the sweep** — at this resolution a ~30–60 ft trough is below
the noise floor. The land-use split is itself informative: it matches the recon's key counter-evidence
(arsenic tracks the *orchard/row-crop* ground, not the grazing core). Confirming any candidate needs
higher-resolution original frames (UCSB FrameFinder / OC detail scans) + ranch maps + ground/records
work. **No contamination or vat is claimed.**

## Newport Coast before/after grading (done)

`newport_coast_beforeafter_grading.jpg` — the *same frame* in 1938 (natural canyon-ridge grazing land,
ranch roads) and 2022 (terraced master-planned development). A documentary record of the land-use
transformation and the scale of terracing; it implies nothing about contamination.

## Correction — the imaged 1931 complex is developed, not the preserved camp

The 1931 building complex imaged near (−117.804, 33.634) and first labeled "Bommer Canyon ranch-HQ"
is, per the 1931-over-2022 overlay (`bommer_hq_overlay.jpg`), **now under residential + golf-course
development** — so it is **NOT** the City-preserved (undeveloped) Bommer Canyon Cattle Camp. It is a
**developed Irvine Ranch building node of unconfirmed identity** ~0.7 mi NW of the preserved camp
(~33.627, −117.795, which was *not* precisely imaged here). *Discipline:* the earlier "Bommer HQ"
label over-reached; treat the complex's identity as **open** pending the ranch maps (Sherman/UCI).
This does not change the substance (a documented ranch complex now under homes) — only the name.

## Land-use overlays built (1938/1931 over 2022)

Reusable: `scripts/build_historical_overlay.py`. All at identical extent (EPSG:2230); land-use history
only, neighborhood scale, no addresses/individuals, no contamination implied.
- `pondcluster_beforeafter_overlay.jpg` / `pondcluster_water_highlight.jpg` — the NE farmstead + creek
  now under homes + commercial; the water-highlight traces the 1938 drainage in blue.
- `bommer_hq_overlay.jpg` — the (developed) 1931 ranch complex now under homes + golf.
- `../ladera/imagery/ladera_overlay.jpg` — the 1938 Ladera drainage is now the community's central
  greenbelt spine, with homes on the graded ridges either side.
- `irvine_core_overlay.jpg` — the whole ~4-mi ranch core: now dense villages + reservoirs + preserved
  open space.

## Next imagery steps (Phase 1/3, now executable)

1. Pull 1931 + 1938 + 1952 over each candidate cattle-handling node (Bommer Canyon, and other Irvine
   Ranch camps once named) and **compare across years** for stable structures.
2. Georeference and difference against modern imagery to reconstruct the pre-grading surface (Newport
   Coast Phase 3) — for Newport Coast slopes specifically, pull 1931/1938 to see the pre-development
   landform before the ~60M cy of grading.
3. Cross-reference any building cluster with **Irvine Ranch maps** (Sherman Library pull-list) to name
   the facility before asserting anything about it.
