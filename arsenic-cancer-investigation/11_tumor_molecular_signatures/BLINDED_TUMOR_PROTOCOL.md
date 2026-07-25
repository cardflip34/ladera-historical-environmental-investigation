# BLINDED TUMOR MOLECULAR & METALLOMIC PROTOCOL — E3 (DRAFT, gated)

**Status:** DRAFT for molecular-pathology + IRB review. **Not initiated by this engine.** FFPE blocks
are finite/destroyable → legal hold (Phase 3); human-subjects + specimen approvals at GATE B. Builds on
MOLECULAR_SIGNATURE_PROTOCOL.md (09). Levels: a fact · d plausible · g unknown.

## Objective
Test, **blinded**, whether Ewing tumors from the community differ from sporadic Ewing in (a) **tumor
arsenic burden**, (b) an **arsenic exposure/methylation signature**, and (c) **EWSR1 breakpoint
architecture** — while honestly bounding what each result can mean.

## Hard design constraint (state up front)
Ewing has **one of the lowest mutation burdens of any cancer (~0.15 mut/Mb)** → a **mutational-
signature** (e.g., arsenic T>G) approach is **underpowered**; treat as exploratory only. Prioritize
**element (metallomics)** and **epigenetic/structural** readouts, which do not depend on mutation count.

## Samples (blinded; codes broken only after analysis lock)
- **Arm 1 — community Ewing** (FFPE, with authorization/consent).
- **Arm 2 — sporadic Ewing** controls from outside the hypothesized area (matched age/sex where feasible).
- **Arm 3 — non-Ewing sarcoma** controls (specificity).
- Adequate n per power analysis acknowledging the low-burden constraint; document block adequacy/tumor
  content; minimize destructive use (finite blocks).

## Assays (FFPE-compatible; certified labs)
| Assay | Readout | Note |
|---|---|---|
| **Metallomics** — LA-ICP-MS / ICP-MS on tumor + adjacent normal | tumor **arsenic** (and lead) | element, not mutation; primary |
| **EPIC methylation array** | 255-CpG **arsenic exposure signature** (S028); tumor methylation class | epigenetic marks abundant in FFPE |
| **Targeted/long-read seq of EWSR1 breakpoint** | breakpoint position + **microhomology / repair fingerprint** | does the fusion junction bear an error-prone-repair signature? |
| **Low-pass WGS** | structural-variant burden / genomic instability | context |
| **(exploratory) WES/WGS** | T>G fraction, STAG2/TP53/CDKN2A status | low power — exploratory |

## Endpoints (pre-specified)
Primary: tumor arsenic (Arm 1 vs 2). Secondary: arsenic methylation signature presence; EWSR1
breakpoint microhomology vs sporadic. Exploratory: T>G mutational fraction; SV burden.

## Statistics
Pre-registered; blinded; multiplicity correction; power calc stating the low-mutation limitation;
report effect sizes + CIs, not just p-values.

## Interpretation limits (governance)
- Exposure/methylation signatures are **non-specific** and **not validated for causal attribution** in
  sarcoma. **A hit is hypothesis-strengthening, not proof;** **a null does not exonerate.**
- Tumor arsenic could reflect post-diagnosis or agonal factors — interpret with exposure timeline (E2).
- Molecular-pathological-epidemiology framing: integrate with soil (E1) + biomarker (E2), not alone.

## Ethics / custody
IRB; specimen consent; legal hold on blocks; chain of custody; results into private analytic layer
(11_/13_ GIS), aggregated for any public output.

## Sequence
Lower priority than E1/E2 (specimen-scarce, signatures non-specific). Run once blocks are secured and
after E1/E2 give an exposure read to interpret against.

*DRAFT — requires molecular-pathology + IRB review (GATE A/B) before any specimen work.*
