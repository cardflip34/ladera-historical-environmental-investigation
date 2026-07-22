# 72 · The Arsenic Model — a Mass Balance in Pounds

> **CLASSIFICATION: MODEL ESTIMATE · Confidence: Low.** Every number in this chapter is a
> mass-balance thought experiment built from the published USDA dip formula and from soil-arsenic
> concentrations *measured in Australia and the US Southeast* — **not in California**. No California
> dip-site soil has ever been tested. These figures state what is *plausible*, not what *is*. They
> **could be wrong by an order of magnitude (~10×) in either direction.** Nothing here asserts that
> any California soil is contaminated. Grades: [A1/A2] for inputs; the model output is MODEL
> ESTIMATE throughout.

---

## 72.1 Inputs (all sourced)

- **USDA California formula:** 8 lb white arsenic (As₂O₃) per 500 gal; up to 9–10 lb for range
  cattle [A1, S-USDA-C174 p.291].
- **Arsenic fraction of As₂O₃:** 75.7% by mass (from molar masses).
- **Vat size:** swim vats held ~3,000–4,000 gal; solution topped up as arsenic was carried off [A1].
- **Measured soil arsenic near vats elsewhere (empirical anchor):** ~500–3,000 mg/kg near the bath
  (NSW to 1,200–3,000 mg/kg) [A2, S-NSW-DIP].
- **California background arsenic:** ~11–12 mg/kg upper bound (DTSC HHRA Note 11; SF Bay RWQCB
  ambient 11 mg/kg) [A2].
- **Health screening levels:** EPA residential RSL **0.68 mg/kg**; California DTSC residential
  **0.11 mg/kg** (both cancer-based) [A2].

## 72.2 Results — MODEL ESTIMATE

Computed by `scripts/arsenic_mass_balance.py` (assumptions stated inline; reproducible).

| Quantity | MODEL ESTIMATE |
|---|---|
| Elemental arsenic **per 8-lb charge** | **6.1 lb** (dip-fluid strength ~1,450 mg As/L) |
| Arsenic **standing in one full vat** at a time | 3,000 gal → **36 lb**; 4,000 gal → **48 lb** |
| **Lifetime throughput per vat** (poured through, replenished over 3–10 yr) | **~145–1,200 lb** As; central ~470 lb |
| Arsenic **in the ground per heavily-used vat** (vat + apron + drain zone at 500–3,000 mg/kg) | **~100–500 lb** As (low 32 / high 857) |
| **Statewide ceiling** (total white arsenic ever purchased by the program) | **~33,000–165,000 lb (15–75 t)** As |
| Statewide **near-vat concentrated** fraction | **~6,600–66,000 lb (3–30 t)**; central ~10 t |
| **Implied number of vats** | **~50–150** (short, small program; Florida had 3,000+) |

The statewide figure is bounded by an independent cross-check: a throughput analysis (USGS
*Arsenic Historical Statistics* DS140 + the USDA cattle-drag-out method) caps total white arsenic
ever used by the whole California program at ~15–75 t elemental As across ~6–8 seasons. No more
arsenic can sit in California soil than was ever purchased and poured. Two independent methods
agree on ~3–30 t concentrated near vats, central ~10 t; the remainder dispersed thinly across
rangeland via cattle drag-out or was discarded as spent fluid. The earlier ~20–100 t statewide
figure assumed 200–1,000 vats and is superseded — it was inconsistent with the ceiling.

## 72.3 Toxicology yardsticks

The per-site numbers are the ones that matter for screening any single location. A dip site at the
empirical anchor of 500–3,000 mg/kg would sit far above every yardstick:

| Yardstick | Value | A dip site (500–3,000 mg/kg) is… |
|---|---|---|
| EPA residential screening level (RSL) | **0.68 mg/kg** | ~700–4,400× |
| California DTSC residential | 0.11 mg/kg | far above |
| California regional background | **~11–12 mg/kg** | **~40–270× background** |

Because California background arsenic already sits near a 1×10⁻⁴ cancer risk, the state regulates
arsenic *against background* — which is precisely why a point source rising 40–270× above
background is the thing a soil test would reveal [A2]. Arsenic is an IARC Group 1 human carcinogen
(skin, lung, bladder) and does not degrade; the real-world concern is chronic, not acute, with
children the sensitive receptor via incidental soil ingestion, and the inhalation pathway largest
during mass grading/earthmoving.

## 72.4 What the model does not claim

Mass grading neither creates nor destroys arsenic: it can **dilute** a hot spot (lowering mg/kg
while spreading the mass) or **relocate** it intact. None of this is knowable for any specific
site without (a) locating the vat and (b) testing the soil — the two things never done in
California. The material toxicity of the chemical in the bag (one 8-lb charge ≈ tens of thousands
of theoretical adult lethal doses) is **context only** — it is not an exposure or harm estimate;
soil is dilute, arsenic sorbs to Fe/Al oxides, and is only partly bioavailable. This entire chapter
is a MODEL ESTIMATE and is not a measurement.

---

*Source registry:* S-USDA-C174 [A1]; S-NSW-DIP [A2]; DTSC HHRA Note 11, EPA RSL [A2]; USGS DS140
[A1]. Model output: MODEL ESTIMATE, Confidence Low, reproducible via
`scripts/arsenic_mass_balance.py`. Full grading in chapter 73.
