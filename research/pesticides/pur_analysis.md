# PUR Empirical Analysis — Orange County 2023

**Data:** California DPR Pesticide Use Report annual archive `pur2023.zip` (248 MB),
downloaded 2026-07-18 from `files.cdpr.ca.gov/pub/outgoing/pur_archives/`. Orange County
extract: `pur2023/pur_data/udc23_30.txt`. Reproduce with
`python3 pipelines/python/process_pur.py <archive>`. Source grade **A1** (official
machine-readable government dataset). **79,473** Orange County application records.

This analysis **empirically tests** — rather than assumes — how much of Orange County's
reported pesticide use can actually be placed on a map.

## Headline finding: 94.6% of Orange County pesticide records have no location

| | Records | Share |
|---|---|---|
| With township/range/section | 4,256 | **5.4%** |
| **Without any location** | **75,217** | **94.6%** |
| Distinct located sections (whole county) | 58 | — |

## Location precision *by site type* — the decisive table

| Site type | Records | Located | % located |
|---|---|---|---|
| Structural pest control | 55,442 | 0 | **0.0%** |
| **Landscape maintenance** | **15,383** | **22** | **0.1%** |
| Nursery – outdoor plants in containers | 2,990 | 2,982 | 99.7% |
| Golf course turf | 1,375 | 0 | 0.0% |
| Rights of way | 1,130 | 48 | 4.2% |
| Regulatory pest control | 583 | 0 | 0.0% |
| Public health | 435 | 0 | 0.0% |
| Pepper, fruiting (agriculture) | 183 | 183 | 100.0% |

**This corrects an earlier working assumption.** Preliminary research held that licensed
landscape-maintenance applications to HOA common areas are reportable to PUR "with full
location detail (COMTRS)." The data show that landscape maintenance **is** reported as a
category — 15,383 records, 110,664 lbs — but **99.9% of those records carry no
township/range/section at all.** Only *agricultural and nursery* site types are reliably
geolocated. Urban/landscape categories are, in practice, county-level.

## Ladera Ranch may not be representable in PUR's location system at all

A BLM PLSS (CadNSDI) lookup places Ladera Ranch in **Township 7 South, Range 7 West** and
**Township 7 South, Range 8 West**, San Bernardino Meridian (`PLSSID CA270070S0070W0` /
`CA270070S0080W0`). Queried at the community centroid and at all four corners of the study
boundary, the **section (first-division) number returns "00" — i.e., no PLSS section**.

*Inference (moderate confidence, flagged for verification):* this is consistent with the
community sitting on former **Mexican land-grant (Rancho Mission Viejo)** land, which was
never subdivided into standard PLSS sections. If correct, the COMTRS scheme PUR uses to
record location **cannot express a Ladera Ranch address**. This should be confirmed against
DPR's own PLSSNET layer (`calpip.cdpr.ca.gov/plssFiles.cfm`), which may differ from BLM's.

Located PUR records do exist in T07S R07W for sections 21 and 36, but those sections lie in
the *sectioned* portion of the township and **cannot be assumed to cover Ladera Ranch.**

**Combined conclusion:** between the 99.9%-unlocated landscape category and the unsectioned
footprint, **PUR is structurally incapable of placing a pesticide application inside Ladera
Ranch.** The publicly posted LARMAC/O'Connell notices are therefore not merely the *best*
location-specific evidence — they are effectively the *only* public source of it. This
materially raises the priority of obtaining the HOA/vendor application logs (gates G04/G05).

## Glufosinate is real, and is a major Orange County landscape herbicide

The active ingredient named in Ladera Ranch common-area notices is independently confirmed
in the state's own dataset:

| Metric | Value |
|---|---|
| Glufosinate records, Orange County 2023 | **442** |
| Total pounds applied | **10,531.9 lbs** |
| Records in *landscape maintenance* | **336** (10,177.1 lbs — 97% of its total poundage) |
| Other top sites | Nursery outdoor containers (58), Rights of way (38) |
| Located records | 59 of 442 (13.3%), in only 4 sections |

So glufosinate use in Orange County is **overwhelmingly a landscape-maintenance herbicide**,
which corroborates the documented Ladera Ranch application pattern as ordinary regional
practice — *not* as evidence of anything unusual, and *not* as evidence of causation.

## What is actually applied to Orange County landscapes

Top active ingredients in the **landscape maintenance** category (15,383 records):

| Records | Pounds | Active ingredient |
|---|---|---|
| 942 | 22,048.8 | Glyphosate, isopropylamine salt |
| 834 | 1.8 | Diphacinone (rodenticide) |
| 599 | 1,098.4 | Imidacloprid |
| 558 | 799.9 | Bifenthrin |
| 520 | 95.9 | Dicamba |
| 485 | 53.5 | Carfentrazone-ethyl |
| 479 | 1,315.4 | 2,4-D, 2-ethylhexyl ester |
| 419 | 8,002.8 | Glyphosate, potassium salt |
| 362 | 1,329.4 | Triclopyr, butoxyethyl ester |
| **336** | **10,177.1** | **Glufosinate-ammonium** |
| 331 | 32.0 | Strychnine |
| 316 | 596.0 | Trinexapac-ethyl |

Glyphosate (both salts combined: 1,361 records, ~30,052 lbs) is the dominant landscape
herbicide; glufosinate is second by poundage.

## Watched ingredients — county-wide presence (2023)

Present: glufosinate (442), glyphosate (2,380), 2,4-D (788), triclopyr (461), dithiopyr
(309), isoxaben (182), pendimethalin (148), trifluralin (52), oryzalin (14), imidacloprid
(3,390), bifenthrin (4,163), permethrin (943), malathion (20), carbaryl (10), diuron (6),
MSMA (6). **Not present:** cypermethrin.

Note that imidacloprid, bifenthrin, and permethrin are dominated by *structural* pest control
(2,650 / 3,473 / 877 records respectively) — i.e., building treatment, not landscape.

## Limitations

- Single year (2023). Multi-year trend requires downloading additional annual archives.
- **Homeowner/consumer self-application is entirely exempt** from PUR and appears nowhere.
- Structural pest control is a county monthly summary by regulation — the 0% located figure
  reflects the reporting rule, not missing data.
- **Absence of a record is not evidence of non-application.**
- The unsectioned-footprint inference needs confirmation against DPR's PLSSNET layer.

## Outputs

- `research/pesticides/pur_orange_county_2023.csv` — 382 chemicals × records × pounds
- `research/pesticides/pur_orange_county_2023_sites.csv` — 45 site types
