# SEARCH LOG (reproducible)

Each entry: id · date · database/engine · exact string · filters · result count · action.
Note: 2026-07-23 searches used a general web engine as an index into primary databases; each hit
must be re-run in the native database (PubMed/Europe PMC/etc.) and captured with full fields before
use in a brief. Native-database re-runs are pending (see NEXT_30_PRIORITY_ACTIONS).

| id | date | engine | query | results | action |
|---|---|---|---|---|---|
| SL-2026-07-23-01 | 2026-07-23 | web index | arsenic Ewing sarcoma EWSR1 fusion inorganic arsenic exposure study | 8 shown | 0 direct As–Ewing studies; Ewing = FET::ETS fusions, "no established environmental risk factors" -> Finding 1 |
| SL-2026-07-23-02 | 2026-07-23 | web index | IARC arsenic group 1 carcinogen established cancer sites lung skin bladder genotoxicity mechanism | 17 shown | Group 1; sufficient human evidence = bladder/lung/skin (epithelial); genotoxic + DNA-repair-inhibition mechanisms -> Findings 2 & 3 |

## Native-database strings queued (WORKSTREAM 3 variants) — to run + log
arsenic AND "Ewing sarcoma"; "inorganic arsenic" AND Ewing; "arsenic trioxide" AND Ewing;
arsenite AND Ewing; arsenate AND Ewing; arsenic AND EWSR1; arsenic AND "EWS-FLI1";
arsenic AND "ETS translocation"; arsenic AND "fusion oncogene"; arsenic AND "pediatric bone cancer";
arsenic AND "small round blue cell tumor"; arsenic AND "mesenchymal stem cell" transformation;
arsenic AND "DNA double-strand breaks"; arsenic AND "nonhomologous end joining";
arsenic AND "homologous recombination"; arsenic AND chromothripsis; arsenic AND "genomic instability".
Databases: PubMed, PMC, Europe PMC, Crossref, OpenAlex, Semantic Scholar, Scholar, ProQuest,
NTP, IARC, ATSDR, EPA IRIS, OEHHA, ClinicalTrials.gov. Record filters, counts, exclusions each run.

## 2026-07-23 session 2 (mechanism, etiology, other cancers, biomarkers)
| id | query | results | action |
|---|---|---|---|
| SL-2026-07-23-03 | arsenic DNA double-strand breaks NHEJ HR repair inhibition | 6 | As2O3 lowers HR not NHEJ (PMID 37530740) -> Bridge A |
| SL-2026-07-23-04 | Ewing cell of origin MSC EWSR1-FLI1 fusion timing prenatal | 8 | embryonic MSC origin; fusion impairs repair (PMC2952797; Nat Commun 2025) |
| SL-2026-07-23-05 | Ewing environmental risk agricultural pesticide parental occupation | 7 | farm/pesticide case-control signal (PMID 12020108;1311140;15551353) |
| SL-2026-07-23-06 | arsenic chromosomal translocation gene fusion carcinogenesis | 8 | error-prone repair -> translocations; As2O3 treats APL (PMC5421966) |
| SL-2026-07-23-07 | arsenic osteosarcoma/bone/soft-tissue sarcoma | 9 | STS (angiosarcoma est.; vineyard STS); osteosarcoma no direct |
| SL-2026-07-23-08 | arsenic leukemia/lymphoma/kidney/liver | 10 | kidney/liver suggestive; leuk/lymph inconsistent (PMC9099091) |
| SL-2026-07-23-09 | deciduous teeth arsenic reconstruction biomarker | 6 | tooth-ring metal biomarker validated (s41370-021-00400-x) |
| SL-2026-07-23-10 | newborn blood spots / toenail / hair arsenic biomarker | 6 | toenail in-utero As (jes201438); banked DBS (Clin Chem 2026) |

## 2026-07-23 session 3 (epidemiology / spatial)
| id | query | results | action |
|---|---|---|---|
| SL-11 | CDC ATSDR cancer cluster guidelines 2022 criteria | 10 | 2022 guidelines; cluster def; 10-criteria; de-emphasize significance (S016) |
| SL-12 | Ewing incidence per million SEER age-specific | 9 | ~2.93-3/M <20; peak 10-15; M:F 3:1; 9x white (S017) |
| SL-13 | SaTScan spatial scan Poisson Bayesian SIR | 8 | SaTScan methods; multi-scale scans (S020) |
| SL-14 | cluster pitfalls Texas sharpshooter multiple comparisons | 8 | silent multiplicity; pre-specify boundaries; source-before-test (S018,S019) |

## 2026-07-23 session 4 (causal MOA / dip chemistry / fate)
| id | query | results | action |
|---|---|---|---|
| SL-15 | arsenic MOA AOP key characteristics IARC | 8 | dominant MOA cytotoxicity/regeneration, oft non-genotoxic (S021,S022) -> tempers plausibility |
| SL-16 | As2O3/arsenite/arsenate dip formulation CAS toxicity | 8 | arsenite from As2O3+NaOH; arsenite 10x arsenate; sulfhydryl MOA (S026) |
| SL-17 | former cattle-dip vat soil arsenic contamination Australia | 8 | up to ~3000 mg/kg As + DDT; persists decades; residential exceedances (S023,S024,S025) |

## 2026-07-23 session 5 (molecular signatures)
| id | query | results | action |
|---|---|---|---|
| SL-18 | arsenic mutational/methylation signature tumor WGS | 8 | As lung T>G signature (S027); 255-CpG methylation (S028) |
| SL-19 | Ewing genomic landscape low mutation burden STAG2 | 7 | 0.15 mut/Mb -> low signature power (S029) |
