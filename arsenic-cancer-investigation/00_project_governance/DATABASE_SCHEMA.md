# DATABASE SCHEMA (source + evidence records)

## MASTER_BIBLIOGRAPHY.csv / SOURCE_INTEGRITY_LOG.csv (one row per source)
source_id, title, authors, year, journal_or_publisher, doi, pmid, pmcid, url, access_date,
source_type(primary_research|review|systematic_review|monograph|govt_report|registry|preprint|
dissertation|conference|secondary), peer_reviewed(y/n), grade(A1|A2|B1|B2|C|D), retraction_flag,
expression_of_concern, predatory_flag, funding_conflicts, full_text_available, file_path, sha256,
notes, reviewer, verification_status(unverified|single|dual)

## STUDY_EVIDENCE_MATRIX.csv (one row per claim/study)
evidence_id, disease, exposure, arsenic_species, exposure_route, exposure_window, study_type,
population_or_model, sample_size, outcome, effect_estimate, ci, significance, dose_response,
mechanism, supports(y/n), contradicts(y/n), neutral(y/n), directness(direct|indirect|analogous),
relevance(high|med|low), risk_of_bias, key_limitations, replication_status, citation, doi, pmid,
url, access_date, full_text, notes, reviewer, verification_status

## CLAIMS_AUDIT.csv (one row per assertion)
claim_id, claim_text, domain, source_ids, classification(verified|partially|plausible_unverified|
unsupported|contradicted|needs_expert|needs_env_testing|needs_epi|needs_medical_records|needs_discovery),
evidence_level(a-g), notes, reviewer

Mechanism/biomarker/other-cancer matrices follow PROJECT spec fields; headers seeded in 18_evidence_matrices.
