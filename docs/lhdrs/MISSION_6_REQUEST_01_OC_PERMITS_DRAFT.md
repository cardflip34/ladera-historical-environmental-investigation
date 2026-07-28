# M6-REQ-OC-PERMIT-01 — Orange County permit / occupancy index request

**Status: DRAFT — NOT SUBMITTED.** No public-records request, inquiry, order, or paid transaction
has been submitted by any lane of this project. This letter cannot be sent until (1) the user
explicitly authorizes submission, and (2) the required local appendices below are generated from
repository data. Nothing in this file constitutes legal advice.

| Field | Value |
|---|---|
| Request ID | `M6-REQ-OC-PERMIT-01` (priority 1 of 11) |
| Custodian | County of Orange — OC Public Works / OC Development Services |
| Primary channel | NextRequest — https://orangecounty.nextrequest.com/ |
| Alternate channel | Permit Record Research counter, County Administration South, 601 N. Ross Street, Santa Ana, CA 92701 · (714) 667-8800 |
| Statute | California Public Records Act, Gov. Code § 7920.000 et seq. |
| Date scope | 1997-01-01 through 2011-12-31 |
| Gates addressed | `permit_occupancy_gate`, `address_lifecycle_gate` |

## Blocking prerequisites — ✅ GENERATED 2026-07-27

All six appendices are produced by `scripts/lhdrs_mission6_appendices.py` (reproducible) into
`data/development/mission6_appendices/`:

| # | Appendix | File | Status |
|---|---|---|---|
| A | Canonical tract list + aliases | `appendix_A_canonical_tracts.csv` | ✅ 123 canonical + 1 excluded/conflicted (TR 17588) |
| B | Address crosswalk, deduplicated | `appendix_B_address_crosswalk.csv` | ✅ 6,368 rows — ⚠️ **APN column empty, see below** |
| C | Project AOI polygon and map | `appendix_C_aoi.geojson` | ✅ 1 feature (existing repo AOI, not redrawn) |
| D | Street-to-tract crosswalk | `appendix_D_street_tract_crosswalk.csv` | ✅ 288 features, multi-date tracts preserved |
| E | Known identifiers | `appendix_E_known_identifiers.csv` | ✅ 182 |
| F | Party name variants | `appendix_F_party_name_variants.csv` | ✅ 91 |

**✅ RESOLVED 2026-07-28 — APNs acquired.** The earlier limitation (no APN data in the repository)
is closed. Mission 7 Phase A3 acquired the official OC Parcels FeatureServer layer and, after
clipping to the CDP polygon, yielded **6,055 unique valid APNs** inside Ladera Ranch. These are
published as **`appendix_B2_apn_list.csv`** (APN, site address where the County carries one, raw
YEAR_BUILT, bedrooms), provenance grade A+.

- 4,564 APNs carry a County site address; 1,491 are APN-only (no address in the County layer).
- The request should now cite Appendix B2 as the authoritative parcel list, which converts item 1
  from "please identify the parcels" into "here are the exact parcels."
- **YEAR_BUILT remains unusable as an occupancy source:** it is blank for 6,041 of 6,101 parcels
  inside the CDP (populated for 4, ~0.1%). This *strengthens* the case for item 1 — the County
  permit/CO index is the only route to parcel-level dates.

**Remaining blocker: user authorization to submit.** Nothing else stands in the way.

---

## Draft letter

> **Subject:** Public Records Act request — development permit and occupancy indexes, Ladera Ranch
> area, 1997–2011
>
> To the Custodian of Records, County of Orange:
>
> Under the California Public Records Act (Gov. Code § 7920.000 et seq.), I request access to and
> copies of the following **existing** records for the tract numbers, assessor parcel numbers, and
> situs addresses listed in the attached appendices, located in the Ladera Ranch area of
> unincorporated Orange County, for the period **January 1, 1997 through December 31, 2011**.
>
> This request is part of an independent historical land-development research project. It seeks
> only records that already exist; **it does not ask the County to create a new record, perform
> analysis, or answer questions.**
>
> **1. Permit and case system exports**
> Existing exports or reports from the building, grading, subdivision improvement, planning,
> map-check, and related development permit or case systems, including:
> - permit, application, case, and certificate identifiers;
> - tract number, APN, situs address, permit type, work description, applicant, owner, contractor,
>   and builder fields;
> - application, issuance, inspection, correction, final inspection, expiration, cancellation,
>   **certificate of occupancy**, certificate of use and occupancy, and closure dates and statuses;
> - inspection event history and final result fields.
>
> **2. System documentation needed to interpret the above**
> Legacy system names, migration dates, field definitions, code tables, record indexes, and
> tract/address/APN crosswalks.
>
> **3. Retention documentation**
> The applicable department-specific retention schedules and any disposition documentation for the
> above record classes.
>
> **Preferred format.** Native machine-readable export (CSV, XLSX, or database extract) **with field
> names and code tables**, plus linked PDF or image records where they exist. If a machine-readable
> export is not available, please advise what format is.
>
> **Requests regarding scope and process**
> - Please produce records on a **rolling basis** as they become available rather than holding the
>   entire production to the end.
> - Please provide a **fee estimate before performing any chargeable work**, and confirm whether any
>   portion can be produced electronically at no or reduced cost.
> - If responsive records were **migrated** from a prior system, please identify the legacy system
>   name(s), the identifiers used, any crosswalk between old and new identifiers, and the current
>   custodian responsible for the migrated data.
> - If responsive records were **destroyed or transferred**, please identify the applicable
>   retention schedule, the destruction authorization or transfer accession, and the date.
> - If any portion of a record is exempt, please produce all **reasonably segregable non-exempt
>   portions** and provide an index describing the withheld material and the exemption claimed.
> - If another County department or agency is the correct custodian for any part of this request,
>   please refer that portion and identify the receiving custodian.
>
> Please confirm receipt and provide a determination within the statutory period. I am happy to
> narrow or clarify any part of this request if that speeds production.
>
> Sincerely,
> [NAME] · [CONTACT] · [DATE]
>
> **Attachments:** Appendix A (tract list) · Appendix B (address/APN crosswalk) · Appendix C (AOI
> map) · Appendix D (street-to-tract crosswalk) · Appendix E (known identifiers) · Appendix F (party
> name variants)

---

## Evidentiary handling on response (do not skip)

Per the registry's principles, **every** acknowledgement, clarification, production, fee notice,
extension, no-record result, denial, referral, and closure must be archived as evidence with its
date and channel.

**Critical:** a "no records found" response is archived as **a result about the County's holdings**,
not as a factual finding that an event did not occur. A failed or incomplete request must never be
silently converted into a negative factual conclusion.

**Do not claim:** a road acceptance, map recordation, sales date, year-built value, school or
facility opening, or aerial observation **is not** a certificate of occupancy.
