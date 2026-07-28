# LEHRP — Ladera Environmental Health Research Platform

An independent, **hypothesis-neutral** environmental-health research and data-organization
platform investigating publicly reported pediatric cancers (primarily Ewing sarcoma) in
Ladera Ranch and surrounding South Orange County, California.

> **This platform does not provide medical advice and does not establish causation.**
> Publicly reported health events may not have been independently medically verified.
> Geographic and temporal overlap does not establish exposure or causation. See
> [CLAIMS_AND_LIMITATIONS.md](CLAIMS_AND_LIMITATIONS.md) and
> [ETHICS_AND_PRIVACY.md](ETHICS_AND_PRIVACY.md).

## What this is

A research repository plus a local web application that:

1. Catalogs publicly reported cancer cases **without** treating them as medically verified.
2. Catalogs discoverable pesticide, chemical, landscaping, agricultural, school, park,
   water, land-use, demographic, and environmental data — every item source-graded.
3. Produces a time-aware GIS map of Ladera Ranch and surrounding South OC.
4. Tracks the quality, provenance, and limitations of every record.
5. Produces preliminary descriptive analyses **without** unsupported causal claims.
6. Identifies exact remaining evidence gaps for a possible later, authorized phase.

## Governance (read these first)

| Doc | Purpose |
|-----|---------|
| [CLAUDE.md](CLAUDE.md) | Project constitution: rules, zones, scope, stack, language discipline |
| [LHDRS_MASTER_PRD.md](LHDRS_MASTER_PRD.md) | Historical-development reconstruction specification |
| [docs/LHDRS_REPOSITORY_AUDIT.md](docs/LHDRS_REPOSITORY_AUDIT.md) | Inventory, gap analysis, duplicate report, and recommendations for the LHDRS workstream |
| [docs/lhdrs/RECURSIVE_GAP_REVIEW.md](docs/lhdrs/RECURSIVE_GAP_REVIEW.md) | First-edition stop condition, evidence gates, and next research order |
| [reports/LHDRS_Historical_Development_Atlas.html](reports/LHDRS_Historical_Development_Atlas.html) | Generated print-ready historical-development atlas |
| [reports/LHDRS_Historical_Development_Atlas_Second_Edition.html](reports/LHDRS_Historical_Development_Atlas_Second_Edition.html) | Preserved second-edition atlas with 1997-2010 annual chapters and evidence-qualified gaps |
| [docs/lhdrs/MISSION_4_IMPLEMENTATION_SUMMARY.md](docs/lhdrs/MISSION_4_IMPLEMENTATION_SUMMARY.md) | Mission 4 reconstruction scope, outputs, blockers, and verification summary |
| [reports/LHDRS_Historical_Evidence_Atlas_Mission_5.html](reports/LHDRS_Historical_Evidence_Atlas_Mission_5.html) | Mission 5 public-evidence atlas with County product/absorption tables and official 2005/2009/2010 imagery |
| [docs/lhdrs/MISSION_5_IMPLEMENTATION_SUMMARY.md](docs/lhdrs/MISSION_5_IMPLEMENTATION_SUMMARY.md) | Mission 5 sources, reconstruction outputs, safeguards, and remaining manual-record blockers |
| [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) | Research questions, hypothesis set, study design |
| [METHODOLOGY.md](METHODOLOGY.md) | SIR/Poisson/scenario/screening methods and bias register |
| [SOURCE_POLICY.md](SOURCE_POLICY.md) | Source grading (A1–D) and conflict handling |
| [CLAIMS_AND_LIMITATIONS.md](CLAIMS_AND_LIMITATIONS.md) | Claim levels and global limitations |
| [ETHICS_AND_PRIVACY.md](ETHICS_AND_PRIVACY.md) | Privacy prohibitions and aggregation rules |
| [DATA_DICTIONARY.md](DATA_DICTIONARY.md) | Entity schemas |
| [FUTURE_EVIDENCE_GATES.md](FUTURE_EVIDENCE_GATES.md) | Final-stage private-record gates |
| [PROJECT_STATE.md](PROJECT_STATE.md) | Live status, phase tracking, resume commands |

## Layout

```
/apps/web          Next.js web application
/packages          database (Prisma), shared types, ui, gis helpers
/research          source-graded registries (CSV/MD/JSON) by topic
/data              raw / interim / processed / geospatial / exports
/pipelines         Python & TypeScript ingestion/transform scripts
/notebooks         reproducible analysis (incidence scenarios, etc.)
/reports           preliminary findings & evidence-gate package
/tests             schema/privacy/provenance/geometry tests
```

## Quick start

```bash
# Web app (file-based; no database required)
cd apps/web && npm install && npm run dev

# Optional PostGIS backend
docker compose up -d

# Python pipelines
cd pipelines/python && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Rebuild and verify the second-edition LHDRS outputs with the repository's GIS-capable
Python environment:

```bash
make lhdrs-mission4 LHDRS_PYTHON=/path/to/python
make lhdrs-mission4-publish LHDRS_PYTHON=/path/to/python
make lhdrs-mission4-docs LHDRS_PYTHON=/path/to/python
make lhdrs-mission4-verify LHDRS_PYTHON=/path/to/python
```

Rebuild the Mission 5 evidence integration from the archived public records:

```bash
make lhdrs-mission5 LHDRS_PYTHON=/path/to/python
make lhdrs-mission5-publish LHDRS_PYTHON=/path/to/python
make lhdrs-mission5-docs LHDRS_PYTHON=/path/to/python
make lhdrs-mission5-verify LHDRS_PYTHON=/path/to/python
```

## Status

Active build. See [PROJECT_STATE.md](PROJECT_STATE.md) for the current phase, what is
complete, and exact resume commands.
