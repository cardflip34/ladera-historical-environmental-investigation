# SEARCH PROTOCOL

1. For each research question, run the exact string in each listed database; log id/date/db/string/
   filters/count/exclusions in SEARCH_LOG.md.
2. Databases (WORKSTREAM order): PubMed, PMC, Europe PMC, Crossref, OpenAlex, Semantic Scholar,
   Google Scholar, Scopus/WoS (if access), ProQuest, univ. repositories; agencies IARC, NTP, ATSDR,
   EPA/IRIS, NIEHS, NCI, WHO, OEHHA, DTSC, USGS, USDA, CDPH, California Cancer Registry, ClinicalTrials.gov.
3. Secondary articles are used only to locate primary sources; never cited as the evidence.
4. Every retained hit -> full source record (DATABASE_SCHEMA) + sha256 of the PDF/HTML where possible.
5. Flag retractions/EoC/preprints/predatory venues. Capture negative + contradictory results equally.
6. Absence of results is recorded as a finding, with the exact strings that returned nothing.
7. Dual-review the consequential items before they enter any physician/attorney brief.
