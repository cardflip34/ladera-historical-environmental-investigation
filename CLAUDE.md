# LEHRP — Ladera Environmental Health Research Platform

> Working project name. Designed so the name can change without refactoring.

## IDENTITY

This is a **hypothesis-neutral environmental health research platform** investigating
reported pediatric cancers (primarily Ewing sarcoma) in Ladera Ranch, South Orange
County, California. It is an **independent research and data-organization project**. It
does **NOT** provide medical advice and does **NOT** establish causation.

## NON-NEGOTIABLE RULES

1. **HYPOTHESIS-NEUTRAL.** Never assume pesticides caused any illness. Investigate all
   hypotheses with equal rigor: pesticides/landscaping chemicals, former agricultural
   land use, imported soil/fill, drinking water, recycled irrigation water, construction
   activity, air pollution, oil & gas proximity, industrial contaminants, parental
   occupational exposure, household products, genetic/ancestry susceptibility, population
   age structure, diagnostic/referral patterns, and statistical coincidence.

2. **SOURCE GRADING.** Every record carries exactly one grade. Never silently promote a
   lower grade to a higher one.
   - **A1** — Official machine-readable government dataset; peer-reviewed primary research;
     official registry publication; official agency report.
   - **A2** — Official government webpage; regulatory filing; official meeting document;
     official GIS service.
   - **B1** — University / research-institution report; systematic review; nonprofit
     technical report with transparent methodology.
   - **B2** — Reputable news outlet quoting **named** sources or documents; public
     statements from identifiable stakeholders.
   - **C** — Advocacy materials; law-firm summaries; community petitions; social-media
     statements; unverified case counts; anonymous claims.
   - **D** — Speculation; unsourced reposts; unsupported online claims.

3. **PRIVACY & ETHICS — absolutely forbidden.**
   - Identifying or inferring individual children.
   - Publishing exact residential addresses or residential coordinates.
   - Inferring the schools, parks, or routines of specific children from social media,
     photos, or uniforms.
   - Scraping private profiles or deanonymizing families.
   - Medical speculation about named individuals.
   - Fabricating data, silently filling missing values, or inventing patient information.
   - Health data is stored at an **aggregated** level only.

4. **LANGUAGE DISCIPLINE.** Always distinguish: Verified fact · Credible report ·
   Official statement · Scientific finding · Public allegation · Unverified case report ·
   Model-based estimate · Inference · Hypothesis · Missing evidence.

5. **PROVENANCE.** No map object, database row, chemical assertion, case report, chart, or
   finding may exist without a `source_id` linking to the source registry. Every inferred
   record additionally records: inference method, input sources, assumptions, confidence,
   date created.

6. **CONFIDENCE DISPLAY.** Never display "likely", "industry standard", or inferred data
   as an actual application. Always show the confidence badge.

7. **NO SENSATIONALISM.** No "cancer hotspot" graphics without valid statistical support.
   No photos of sick children. No skulls, warning symbols, or fear-based graphics. No
   advocacy slogans presented as scientific conclusions.

8. **ONLINE-FIRST, NO EARLY BLOCKERS.** Never stop or declare the project blocked because
   private records are unavailable. Log gaps in `FUTURE_EVIDENCE_GATES.md` and continue
   with public sources. Draft records requests only at the final stage, based on exact
   gaps found.

## STUDY ZONES

- **Zone A (Core):** Ladera Ranch — all villages, HOAs, parks, schools, trails, common
  areas, slopes, drainage corridors, commercial centers.
- **Zone B (5-mile exposure ring):** Las Flores, Rancho Mission Viejo, Mission Viejo, Coto
  de Caza, Rancho Santa Margarita, San Juan Capistrano, Laguna Niguel, adjacent
  unincorporated OC.
- **Zone C (South OC comparison):** Talega, Aliso Viejo, Foothill Ranch and similar
  master-planned communities — matched by **objective criteria** (development age,
  demographics, landscaping intensity, climate, housing), **never by cancer counts**.

## TIME SCOPE

Primary: **Jan 2005 – present.** Extended: **Jan 2000 – present.** Land-use history: as far
back as reliable public records allow. Every dataset records: source publication date,
observation/coverage period, retrieval date, temporal precision, known update schedule,
and whether the record is current/historical/inferred/archived.

## TECH STACK

- Next.js (App Router) + TypeScript + React
- Tailwind CSS + lightweight in-repo UI components
- Prisma ORM (PostGIS-ready; file-based GeoJSON/CSV/Parquet/JSON fallback works without a DB)
- MapLibre GL JS + OpenStreetMap basemap (no paid Mapbox)
- Python + GeoPandas + Shapely + PyProj + Pandas + DuckDB for pipelines
- Docker Compose for PostGIS (optional, later)

## DESIGN

Light background, dark navy typography, restrained blue accents. Clean GIS interface, high
readability. Confidence badges: Verified Official · Primary Scientific · Official Public
Record · Credible Secondary · Public Allegation · Model Estimate · Unknown.

## DISCLAIMER (include on every page)

> This platform is an independent research and data-organization project. It does not
> provide medical advice and does not establish that any pesticide, property, organization,
> employer, school, water provider, government agency, or other party caused any illness.
> Publicly reported health events may not have been independently medically verified.
> Geographic and temporal overlap does not establish exposure or causation. Formal
> conclusions require authorized epidemiological analysis, verified medical information,
> exposure assessment, toxicological review, and independent scientific evaluation.

## APPROVED LANGUAGE

- "The reported pattern warrants investigation."
- "The available evidence does not yet establish causation."
- "This source supports further examination of…"
- "This association may be explained by…"
- "The current data are insufficient to determine…"
- "A formal individual-level epidemiological analysis would be required…"

## FORBIDDEN LANGUAGE

- "There has to be a correlation."
- Any causal claim without explicit statistical support and appropriate caveats.
