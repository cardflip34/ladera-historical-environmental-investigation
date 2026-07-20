# Research Log

Every search performed, in order. Negative results are recorded with the same weight as
positive ones — a query that returns nothing is a finding, and an undocumented failed search
is an invitation to repeat it.

Format: date · cluster · source searched · query · result · follow-up

---

## 2026-07-18 — Session 1: Historical imagery

| # | Source | Query / action | Result |
|---|---|---|---|
| 1 | ocgis.com ArcGIS REST | Enumerate `/arcgis/rest/services` | **404.** Wrong path — the conventional ArcGIS root does not exist for this county. |
| 2 | ocgis.com ArcGIS REST | Enumerate `/arcpub/rest/services?f=json` | **HIT.** 41 folders returned, including `Historic_Imagery` and `Aerial_Imagery_Countywide`. This single path difference had blocked all prior attempts. |
| 3 | ArcGIS webappviewer | App ID `489ff1f4c63844ec9f5c96d604289f8b` → webmap `75daa7a29b7c4ea0b5c01596ac24904d` | **DEAD END.** Webmap resolves to rainfall/weather layers, not imagery. Logged. |
| 4 | Historic_Imagery_v2 ImageServer | Raster catalog `/query` intersecting footprint bbox | **HIT.** 36 frames, 1929–1997. Six pre-1950. |
| 5 | Historic_Imagery_v2 | `exportImage` with `esriMosaicLockRaster` per frame | **HIT.** Six pre-1950 frames retrieved; extent verified to ±25 m. |
| 6 | Eagle_Aerial_2025_OC_1FT_sid | `exportImage` at 6000×5200 | **FAIL.** Size limit exceeded. Fell back to `OC_Aerial_2022_1ft_WGS84` at 4000×3467 — succeeded. |
| 7 | USGS 3DEP ImageServer | `exportImage` DEM, F32, footprint bbox | **HIT.** 1400×1213, 4.2×5.0 m/px. |
| 8 | Overpass API (overpass-api.de) | `way["building"]` over footprint bbox | **FAIL.** HTTP 406 on POST. |
| 9 | Overpass (overpass.kumi.systems) | Same query via GET | **HIT.** 10,618 building ways. |
| 10 | 1968 USGS quad (local raster) | Colour-threshold cyan hydrography ink | **HIT.** 41 water bodies ≥350 m², 16 inside Zone A. |
| 11 | 1929/1937/1946 aerials | Automated dark+smooth blob detection for impounded water | **ABANDONED.** Returned ~100 Zone-A candidates in the 1937 frame; visual review showed it was keying on hillslope shadow, not water. Frames have wildly different tone curves. Superseded by method 10. Script retained at `pipelines/python/detect_water_1930s.py` with the failure documented in its docstring. |

**Session 1 corrections issued:** C-002 (creek misidentified as Cañada Chiquita; it is Trabuco
Creek), C-003 ("earliest available imagery is 1948" was wrong — 1929 exists).

---

## 2026-07-18 — Session 2: Archival research (in progress)

Six parallel research clusters launched:

| Cluster | Scope |
|---|---|
| A | Cattle tick eradication and arsenical dipping — USDA BAI, CA State Veterinarian, statutory basis, whether Orange County was ever included |
| B | Land grant and chain of title — Spanish grant through Rancho Mission Viejo Corporation and Ladera Ranch entitlement |
| C | Ranch operations and infrastructure — corrals, cow camps, water systems, oral histories, photograph collections |
| D | Environmental review audit — EIRs, Phase I/II ESAs, what historical land use was actually reconstructed |
| E | Historic maps and imagery — 1912 plats, 1942 AMS sheets, UCSB FrameFinder, **GLO survey field notes** |
| F | Historical newspapers — quarantine and dipping legal notices, ranch news, development coverage |

Results appended below as clusters report.
