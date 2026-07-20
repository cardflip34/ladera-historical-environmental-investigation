# Pesticide Data Coverage — What Public Data Can and Cannot Show

**Prepared:** 2026-07-18. Governs interpretation of every pesticide record in the platform.

## Bottom line

California's Pesticide Use Reporting (PUR) is the most complete such system in the US, but
its coverage of **urban/landscape** application in a community like Ladera Ranch is partial
and non-uniform. **Absence of a PUR record is not evidence of non-application.**

## What is and is not reported (governing distinction: FAC §11408)

| Category | Reportable to PUR? | Granularity |
|---|---|---|
| Production agriculture | Yes — mandatory | COMTRS (~1 sq mi) + date |
| Restricted materials (any use) | Yes — mandatory; permit + NOI | COMTRS + date; advance notice (feeds SprayDays) |
| Rights-of-way, parks, golf, cemeteries, greenbelts | Yes (non-production ag) | COMTRS + date |
| **Landscape/ornamental maintenance by a licensed PCB/MGPCB for hire (e.g., HOA common areas)** | **Yes — the pest-control business must report** | COMTRS + date |
| Structural pest control (Branch 2/3, termite) | Yes, **but county monthly SUMMARY only** — no address, no COMTRS, no per-application count (since 10/1/2016) | County-month only |
| **Homeowner / consumer self-application** | **NO — exempt** | — |
| Institutional/industrial; public-agency vector control | Excluded from "agricultural use" definition | — |

## CORRECTED BY EMPIRICAL TEST (2026-07-18)

> The regulatory table above describes what is *reportable*. Actual 2023 Orange County PUR
> data shows what is *reported*, and the difference is decisive. See
> **`pur_analysis.md`** for the full analysis (A1, official dataset, 79,473 records).
>
> - **94.6% of Orange County pesticide records carry no location at all.**
> - **Landscape maintenance: 15,383 records but only 22 (0.1%) are geolocated.** Landscape
>   use *is* reported as a category, but effectively at county level — not COMTRS.
> - Only agricultural/nursery site types are reliably located (≈100%).
> - Ladera Ranch sits in unsectioned (former land-grant) PLSS territory, so the COMTRS
>   scheme may not be able to express its location at all.
>
> **Therefore: PUR is structurally incapable of placing a pesticide application inside
> Ladera Ranch.** The posted LARMAC/O'Connell notices are the only public location-specific
> evidence, which raises the priority of gates G04/G05.
>
> PUR *does* independently confirm glufosinate as a major Orange County landscape herbicide
> (442 records, 10,531.9 lbs; 336 records in landscape maintenance) — corroborating the
> documented application pattern as ordinary regional practice, not as evidence of causation.

## Implication for Ladera Ranch

- **Common-area (LARMAC/O'Connell) applications are reported to PUR as a category, but are
  not geolocatable** (see the correction above). The earlier expectation of ~1-sq-mi section
  granularity for landscape work is **not borne out by the data**.
- **Individual homeowners' yards are entirely invisible** to PUR (home-use exemption).
- **Termite/structural work is present only as county-wide monthly totals** — cannot be tied
  to Ladera Ranch or an address.
- **Net:** PUR is a *floor*, not a census, of urban pesticide exposure.

## Most concrete primary evidence obtained

The single strongest primary source is a **Notice of Pesticide Application posted publicly
on laderalife.com (Dec 5–8, 2023, series continues into 2025)**, on **O'Connell Landscape
Maintenance** letterhead, documenting **"Lifeline Herbicide" (UPL), EPA Reg. No. 70506-310,
active ingredient glufosinate-ammonium**, "target weed control," applied to Front-Yard SBA
common areas across Ladera Ranch villages. LARMAC's landscape page confirms it contracts
O'Connell for pest management including weeds. This is recorded as `APP-001` with
evidence class `documented_within_reporting_unit` (the notice covers common-area zones, not
individual parcels).

## Access paths (pipeline feasibility)

- **PUR bulk (primary pipeline):** `files.cdpr.ca.gov/pub/outgoing/pur_archives/pur{YEAR}.zip`
  (1974–2023), fixed-schema DBF/CSV joinable on `prodno`/`chem_code`; filter `county_cd=30`
  (Orange); join `comtrs` to DPR PLSS shapefiles to map sections overlapping ZIP 92694.
  Fully automatable.
- **CalPIP** interactive query (calpip.cdpr.ca.gov) for ad-hoc county/ZIP/chemical + CSV
  export; no documented API.
- **EPA PPLS/PPIS** for product/label + active-ingredient tables (JSON/XML, no key).
- **EPA CompTox CTX APIs** for toxicology (free key by email).
- **USGS PNSP** county-level estimates — **agricultural use only** (misses urban/turf/
  structural/residential); use only as an agricultural cross-check.

## Non-automatable / gaps (→ evidence gates)

- OC restricted-materials permits & NOIs — not in any public DB (CalAgPermits login-gated);
  obtain via CPRA.
- Healthy Schools Act school-level pesticide use — not publicly queryable (annual PDF or by
  request); Capistrano USD serves Ladera Ranch schools.
- LARMAC's full chemical-usage history & O'Connell contract — largely resident-login or
  by-request; residents allege records were refused.
- **SprayDays is not useful here** — restricted-materials/production-ag only, advance-notice
  only, no history; glufosinate is general-use and landscape is excluded.

## Regulatory-fact vs advocacy-claim (glufosinate)

Advocacy framing ties glufosinate to the cases as an "EU-banned" chemical. Precise record:
EU **non-renewal (2018) was on reproductive-toxicity grounds (Repr. 1B), not a cancer ban**;
no regulator classifies glufosinate as a carcinogen (EPA "Not Likely"; IARC not classified;
not on Prop 65; not a CA restricted material). Its documented hazards are neuro-,
developmental-, and reproductive-toxicity. The leap to causation of a specific cancer cluster
is unestablished and under official review.
