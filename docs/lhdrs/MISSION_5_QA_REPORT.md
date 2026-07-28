# Mission 5 QA report

## Passed checks

- Dedicated Mission 5 verification: passed.
- LHDRS integrity suite: 30/30 passed.
- Full clean verifier: 7/7 stages passed, including clean install, TypeScript, Prisma validation, high-severity npm audit, and production build.
- Acquisition manifest: 30/30 retrieved; byte sizes and SHA-256 checksums verified.
- Text extraction: 25/25 succeeded; output checksums verified.
- County arithmetic: Phase I 1,129; UAC 386; Phase V 1,242; Phase VI 892 built-and-occupied units.
- Product arithmetic: Phase V 1,259 planned/permits and 1,242 2006 escrows; Phase VI 1,006 planned, 731 permits and 705 escrows in 2006, 892 escrows including custom lots by 2011.
- Evidence models: 243 observations, 243 claims, and equal convergence rows.
- Evidence graph: 1,229 nodes and 1,614 edges; every edge has evidence and registered source IDs.
- Atlas publication: 14 files with verified byte sizes and checksums.
- Proximity safeguard: zero published proximity results; every relevant new record remains ineligible.

## Static report checks

The HTML and Markdown atlas contain no absolute user paths or `file://` links. Referenced image assets exist and are checksummed. Direct in-app browser rendering of the local `file:` report was unavailable under the browser URL policy, so visual QA was limited to source-image inspection and static HTML/reference validation.

## Residual risk

The dominant residual risk is not software correctness; it is incomplete historical record access. Current geographic associations and aggregate County milestones could be misread as tract-level physical history if their limitations are discarded. Every relevant output therefore repeats its scope and keeps proximity disabled.
