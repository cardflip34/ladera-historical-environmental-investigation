# CANCER TAXONOMY TEMPLATE (Workstream 1) — schema only; DATA lives PRIVATELY in 04 (gitignored)

Physician/legal teams populate one record per diagnosis in 04_cancer_registry_private (never committed).
Public outputs use aggregation/masking only. Do not place identifiers here.

Fields per case:
standardized_disease_name; histologic_subtype; primary_tumor_location; age_at_diagnosis; sex;
year_of_diagnosis; year_began_residence_or_school; residence_exposure_window; school_exposure_window;
prenatal_parental_residence_window; known_genetic_predisposition; prior_therapeutic_radiation_or_chemo;
pathology_confirmation_status; molecular_findings; EWSR1_fusion_status; EWSR1_fusion_partner;
bone_or_extraskeletal; ever_lived_outside_area; other_major_exposures; data_provenance;
verification_status.

Rules: separate research branch per confirmed cancer; **do not combine biologically unrelated cancers**;
diagnoses verified against the California Cancer Registry (not social media). PHI never leaves 04.
