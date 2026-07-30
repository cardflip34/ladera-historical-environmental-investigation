# M6-REQ-OC-AERIAL-03 — OC Survey historical aerial imagery request

**Status: DRAFT — NOT SUBMITTED.** Nothing in this file has been sent to any agency. It cannot be
sent until the user reviews it and chooses to submit. Nothing here constitutes legal advice.

| Field | Value |
|---|---|
| Request ID | `M6-REQ-OC-AERIAL-03` (priority 3 of 11) |
| Custodian | Orange County Survey / Geospatial Services (OC Public Works) |
| Primary channel | NextRequest — https://orangecounty.nextrequest.com/ |
| Reference | https://ocs.ocpublicworks.com/service-areas/oc-survey/products/historical-aerial-imagery |
| Statute | California Public Records Act, Gov. Code § 7920.000 et seq. |
| Date scope | **1997-01-01 through 2003-12-31** and **2005-01-01 through 2011-12-31** |
| Gate addressed | `aerial_interval_gate` |
| Prerequisite | Appendix C (AOI polygon + rendered map) — ✅ generated 2026-07-27 |

---

## Why this request is now much narrower than originally scoped

The registry drafted this on 2026-07-27 asking for imagery across **1999–2004 and 2006–2008**.
Mission 7 has since closed part of that window, so asking for all of it would waste the County's
time and weaken the request. What we now hold, and therefore do **not** need:

| Period | Source held | Resolution | Coverage |
|---|---|---|---|
| 1929, 1938, 1947 | OC Survey aerials (incl. a labelled 1947/1938 composite) | ~0.35 m | 100% of AOI |
| 1953, 1960, 1969, 1980, 1990 | OC Survey countywide series, LockRaster exports | varies | 100% of AOI |
| **2004-01-21** | **USGS High Resolution Orthoimagery, 20 tiles** | **0.3 m** | **100% of AOI** |
| 1997–2006, 102 months | Landsat 5/7 Collection 2 Level-2 | 30 m | 100% of AOI |

**The residual gap is therefore specific:** high-resolution (sub-metre or better) aerial coverage
of the AOI for **1997 through 2003** — the grading and build-out years — and for **2005 through
2011**. At 30 m, Landsat resolves grading extent and road alignment but **not** individual pads,
structures, equipment, stockpiles or haul routes. That is the evidentiary difference this request
exists to close.

The public Historical Aerial Imagery Explorer returned catalogue items 4 and 33 for this location
(catalogued 1995/1994 and 1998/1997) and did not expose a construction-period item after 1998 at
the queried point. **That does not establish that no such imagery exists** — only that the public
explorer did not surface it at that query point. This request asks the custodian to check the
catalogue itself.

---

## Draft letter

> **Subject:** Public Records Act request — historical aerial imagery and flight indexes, Ladera
> Ranch area, 1997–2003 and 2005–2011
>
> To the Custodian of Records, OC Survey / Geospatial Services:
>
> Under the California Public Records Act (Gov. Code § 7920.000 et seq.), I request access to and
> copies of the following **existing** records covering the project area shown in the attached
> Appendix C map and polygon, in the Ladera Ranch area of unincorporated Orange County.
>
> This is an independent historical land-development research project. It seeks only records that
> already exist; **it does not ask the County to create a new record, fly new imagery, perform
> analysis, or answer questions.**
>
> **1. Imagery catalogue and index records**
> For all aerial acquisitions whose footprints intersect the attached AOI, for the periods
> **1 January 1997 – 31 December 2003** and **1 January 2005 – 31 December 2011**:
> - aerial survey indexes, flight-line indexes and frame-centre indexes;
> - acquisition dates, contractor or mission identifiers, project or job numbers;
> - scale, ground sample distance / resolution, film or sensor type, and coordinate system;
> - coverage footprints, in GIS format if they exist in one.
>
> **2. The imagery itself**
> Orthophotos, source frames, mosaics, contact prints, or existing derivatives for those periods,
> in whatever form the County holds them.
>
> **3. Catalogue records for imagery not exposed publicly**
> Records for any acquisition covering this AOI that is **not** surfaced by the public Historical
> Aerial Imagery Explorer. I have searched the public explorer and it returned items catalogued
> 1995/1994 and 1998/1997 at this location and nothing from the construction period after 1998. I
> am asking whether the underlying catalogue holds more than the public interface exposes.
>
> **4. Retention documentation**
> The applicable retention schedule for these record classes, and any transfer, accession or
> destruction documentation for imagery of this area from these periods.
>
> **Preferred format.** GeoTIFF or the native raster format, with sidecar or embedded
> georeferencing metadata; CSV or GeoJSON for indexes and footprints. If imagery exists only as
> film, print, or unscanned material, please say so and identify the medium, the holding location,
> and whether scanning is available and at what cost.
>
> **Requests regarding scope and process**
> - Please provide a **fee estimate before performing any chargeable work**, and confirm whether
>   any portion can be produced electronically at no or reduced cost.
> - Please produce records on a **rolling basis** rather than holding everything to the end. The
>   index and footprint records in item 1 are the most useful to me first, because they will let me
>   narrow items 2 and 3 to only what actually exists and reduce the burden on your staff.
> - If responsive imagery was **migrated** from a prior system or catalogue, please identify the
>   legacy system, the identifiers used, and any crosswalk between old and new identifiers.
> - If responsive records were **destroyed or transferred**, please identify the applicable
>   retention schedule, the authorisation, and the date.
> - If another department or agency is the correct custodian for any part of this request, please
>   refer that portion and identify the receiving custodian.
>
> I am glad to narrow any part of this request if that speeds production — in particular, if the
> index records show only a small number of relevant acquisitions, I will happily reduce item 2 to
> those specific frames.
>
> Please confirm receipt and provide a determination within the statutory period.
>
> Sincerely,
> [NAME] · [CONTACT] · [DATE]
>
> **Attachment:** Appendix C — project AOI polygon and rendered map
> (`appendix_C_aoi_MAP.png` rendered sheet · `appendix_C_aoi.geojson` · `appendix_C_aoi.kml`)

---

## Do not claim from the response

- An aerial observation is **not** a certificate of occupancy. A roofed structure in a frame shows
  a roofed structure on that date and nothing about occupancy, permit final, or first sale.
- Absence of imagery for a period is **not** evidence that nothing happened in that period.
- Imagery resolves ground surface condition only. It does not show soil chemistry, and nothing in
  the response may be used to infer contamination, transport, or exposure.

## Definition of done

Response received and logged with a source_id in the registry; any imagery received registered with
acquisition date, resolution, CRS, footprint and checksum; `aerial_interval_gate` re-evaluated
against what actually arrived, and either closed or restated with the specific residual gap.
