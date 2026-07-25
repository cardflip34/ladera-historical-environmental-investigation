# TUMOR MOLECULAR SIGNATURES (Workstream 9) — feasibility + blinded protocol (design only)

**Date:** 2026-07-23 · single-reviewer · **design for expert review; do not initiate testing** (GATE B).
Levels: a fact · b strong · c suggestive · d plausible · g unknown.

## Is there an arsenic signature, and can it be tested on Ewing?
- **Candidate mutational signature (b):** WGS of an arsenic-related lung tumor showed a **distinctive
  mutational spectrum** distinguishing arsenic-related from unrelated lung tumors of the same
  histology, with a **high proportion of T>G transversions** (oxidative-damage pattern). PMID 24128716.
- **Epigenetic exposure signature (b):** a **255-CpG DNA-methylation** signature predicts urinary
  arsenic, arsenical skin lesions, and mortality; ~**1177 CpGs** associate with urinary arsenic.
  PMID 42051231; PMC6143427.
- **The hard constraint (a):** **Ewing sarcoma has one of the lowest mutation burdens of any cancer,
  ~0.15 mutations/Mb** (recurrent STAG2 ~21%, CDKN2A del ~14%, TP53 ~6%). PMID 25010205; 25223734.
  → **Very few somatic mutations exist to carry a mutational signature.** A T>G-signature approach is
  **underpowered in Ewing**; absence of the signature would be weakly informative, presence hard to
  reach significance.

## Honest feasibility read
- **Mutational-signature test:** low power in Ewing (sparse mutations). Report as exploratory only.
- **More feasible reads:** (1) **direct tumor arsenic (metallomics/LA-ICP-MS on FFPE)** — measures the
  element, not a mutation count; (2) **DNA-methylation** profiling vs the arsenic CpG signature —
  epigenetic marks are abundant and FFPE-compatible on arrays; (3) **structural-variant / breakpoint
  microhomology** analysis at the EWSR1 junction (does the fusion breakpoint bear an error-prone-repair
  fingerprint?). None of these has been done for arsenic in Ewing → all are gaps.

## Blinded protocol (for GATE-B review; not initiated)
1. **Samples:** archived Ewing FFPE (community cases, with consent/legal authorization) + matched
   **sporadic Ewing controls** from outside the hypothesized area + non-Ewing sarcoma controls.
   **Blinded** to case/control status through analysis.
2. **Assays:** methylation array (EPIC), targeted/long-read sequencing of the EWSR1 breakpoint region,
   low-pass WGS for structural variants, and **tumor metallomics (arsenic)**; run lead alongside.
3. **Endpoints (pre-specified):** (a) tumor arsenic vs controls; (b) presence of the 255-CpG arsenic
   methylation signature; (c) EWSR1 breakpoint microhomology/repair fingerprint; (exploratory) T>G
   mutational fraction.
4. **Statistics:** pre-registered; correct for multiplicity; power calc acknowledging low-mutation
   constraint; blinded code-break only after lock.
5. **Interpretation limits (state up front):** an arsenic exposure/methylation signature is **not
   proof of causation** of *this* tumor; signatures are non-specific and validated mainly outside
   sarcoma. A null does not exonerate; a hit is hypothesis-strengthening, not dispositive.

## Chain of custody / ethics
FFPE blocks are finite and destroyable → legal hold (Phase 3). Human-subjects + specimen approvals at
GATE B. No specimen handling by this engine.

## Sources
Arsenic lung mutational signature PMID 24128716; arsenic methylation signature PMID 42051231 / PMC6143427;
Ewing genomic landscape / low burden PMID 25010205; 25223734.
