# Historical Photographs and Image Analysis

This chapter describes what photographic evidence exists, how it was analysed, and — at some
length — the analyses that failed. The failures are included because two of them nearly produced
published findings that were wrong.

---

## 12.1 The photographic record

| Epoch | Source | Resolution | What it shows |
|---|---|---|---|
| **1886** | USC / California Historical Society, CHS-2085 | — | Ranch house, vineyard and winery — **San Diego County** |
| **1900** | USC / CHS, CHS-2358/2359/2360 | — | Cattle at a stream, a mounted vaquero, a grazing herd — **San Diego County** |
| **1911** | USDA BAI Circular 174, Plate XV | — | A cage vat in operation: gross view, cage lowered with an attendant ducking the animal, cage raised |
| **1929** | OC Survey, frame OID 346 | 2.6 ft/px | Open rangeland, riparian corridor, dirt roads |
| 1931 | OC Survey, OID 351 | 2.5 ft/px | Partial coverage |
| **1937–38** | OC Survey, OID 310 | **1.15 ft/px** | Individual oaks, fence lines, wheel ruts, the cartographer's "Trabuco Creek" label |
| 1938 | OC Survey, OID 340 | 3.2 ft/px | Full footprint |
| 1946–47 | OC Survey, OID 286 / 293 | 2.2–4.3 ft/px | Still rangeland; NW coverage gap |
| 1974 | USGS orthophoto quad | — | Open rangeland, Mission Viejo building out to the west |
| 2022 | OC Survey | 1 ft/px | Built out |

::: classification limit
**The 1886 and 1900 photographs depict San Diego County** — Rancho Santa Margarita y Las Flores,
now largely Camp Pendleton. Shared ownership with Rancho Mission Viejo, partitioned in the
1940s, **but different land**. They are published to show the character and scale of the cattle
operation in the period the tick programme ran, and are captioned so they cannot be mistaken for
this study area.

No photograph of Rancho Mission Viejo ranch operations has been located. **This is a genuine
gap**, and the most likely place to close it is a family album rather than an archive.
:::

## 12.2 How the aerials were analysed

**Common extent.** Every frame was rendered to one bounding box — −117.680 to −117.616 longitude,
33.520 to 33.575 latitude — so any two epochs compare pixel for pixel without further
transformation.

**Georeferencing verified, not assumed.** Rectification is Orange County's own; the export
service echoes the extent it rendered, matching the request to ±25 m. That is a claim about the
service, so it was checked independently: the modern 2022 frame rendered through the same
pipeline places Zone A on the real subdivisions, with I-5 and Mission Viejo where they belong.

**Systematic, not impressionistic.** Zone A was divided into a **4 × 3 grid** and each tile
examined at full resolution for both 1929 and 1937–38 — twenty-four tiles. Each carries its own
corner coordinates and a 200-metre scale bar, so any reader can return to the same ground.

**Result: no vat, no corral, no pen, no chute complex in any tile.**

## 12.3 Three analyses that failed

### Automated structure detection — 4% accurate

A connected-component detector was run over the 1948 topographic sheet for solid-black,
compact, building-sized blobs. It returned **25 candidates** inside the footprint.

Visual verification showed **24 were artefacts** — letters from the "MISSION VIEJO" map label,
red section-line dots, and a benchmark "X" mark. One survived.

**None of the 24 is plotted anywhere in this publication.** Only manual review prevented them
from becoming findings.

@figure FIG-12

### Automated water detection — abandoned

Water was sought directly in the 1929 and 1937 frames on a defensible physical premise: on
panchromatic film, standing water is both **dark** and **smooth**, whereas vegetation is dark but
*textured* and hillslope shadow is dark but *elongated*.

It returned 111 candidates in the 1929 frame and 225 in 1937, roughly 100 inside Zone A. Review
showed it was detecting **hillslope shadow**.

The cause was specific: the scans have incompatible tone curves. The 1929 frame's 12th-percentile
brightness sits at DN ~109–128 (bright, low contrast); the 1937 frame's at DN ~23–43 (dark, high
contrast). No single threshold serves both.

**Superseded by** extracting cyan hydrography ink from the 1968 USGS sheet, where every feature
was drawn by a surveyor who visited the ground. Strictly better evidence, obtained by abandoning
the clever method for the boring one.

### The resolution argument — wrong twice

Covered in full under corrections C-003 and C-004. In summary: the project first argued a vat was
undetectable *in principle* because the earliest imagery was 1948, then — having found 1929
photography at 1.15 ft/px — argued the objection had "disappeared entirely" and a corral complex
"would be unmistakable."

USDA's own California circular describes cage vats installed beside existing corrals with **no
drainage pen**, and wade tanks costing **under ten dollars** and measuring about fifteen feet.
Neither need be visible.

**Both arguments were about photographs. Neither was checked against what was being photographed.**

## 12.4 What the imagery can and cannot establish

::: classification fact
**Can establish:** that the footprint was open rangeland throughout 1929–1974; that no *large
permanent* installation stood inside Zone A in any frame examined; the location of one structure
on Trabuco Creek; the position of drainages, roads, and field boundaries before development.
:::

::: classification limit
**Cannot establish:** the absence of a small cage vat or wade tank; the absence of any facility
demolished before 1929 — **seventeen years** after the quarantine ended, on the corrected
timeline; the function of the one structure found; anything at all about what is in the soil.
:::

## 12.5 The photograph that would change this

A single clear photograph of Rancho Mission Viejo cattle-working operations — showing a vat, or
showing a corral complex with no vat — would move this investigation further than any further
online searching.

Ranch photography from this period exists. Roundups were photographed; families kept albums;
the ranch was used as a filming location. None of it has surfaced in the collections searched.

If you have one, please see the invitation at the front of this report.
