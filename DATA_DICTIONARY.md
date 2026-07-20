# DATA_DICTIONARY.md

Schema documentation for the platform's core entities. The canonical machine schema is
`packages/database/schema.prisma`; CSV registries under `research/` mirror these fields.
Every substantive record links to at least one `Source` via `sourceId`.

## Source
The provenance backbone. Nothing substantive exists without one.

| Field | Type | Notes |
|-------|------|-------|
| id | string | e.g. `SRC-OFF-001` |
| title | string | |
| publisher | string | |
| author | string? | |
| url | string? | |
| publicationDate | date? | |
| retrievalDate | date | when we accessed it |
| sourceType | enum | dataset / webpage / report / news / filing / meeting_doc / advocacy / social / literature / gis_service |
| geographicCoverage | string | e.g. "Orange County, CA" |
| timeCoverage | string | e.g. "2000–2024" |
| isOfficial | bool | |
| isPrimary | bool | primary vs secondary |
| isPeerReviewed | bool | |
| dataFormat | string | HTML/PDF/CSV/GeoJSON/API/… |
| localFilePath | string? | archived copy |
| checksum | string? | sha256 of archived copy |
| citationText | string | formatted citation |
| reliabilityGrade | enum | A1 / A2 / B1 / B2 / C / D |
| knownLimitations | string? | |
| notes | string? | |

## PublicHealthEvent
Aggregate-only. **Never** stores names, addresses, or residential coordinates.

| Field | Type | Notes |
|-------|------|-------|
| id | string | `PHE-001` |
| reportedDiagnosis | string | as stated by source |
| isEwingSarcoma | bool | |
| approximateAge | string? | age or range only |
| approximateYearOfDiagnosis | string? | year or range |
| communityAssociation | string | e.g. "associated with Ladera Ranch" |
| sourceId | string | FK → Source |
| sourceWording | string | short quote of how the source phrased it |
| namesIndividual | bool | whether the *source* names a person (name NOT stored) |
| hasCorroboration | bool | independent second source exists |
| medicalVerificationStatus | enum | not_independently_verified (default) / registry_confirmed / official_confirmed |
| duplicateResolutionStatus | enum | unique / possible_duplicate / merged |
| notes | string? | |

## LiteratureEntry
| id · citation · doi · pmid · abstract(summary) · studyDesign · population · sampleSize ·
exposure · outcome · effectEstimate · confidenceInterval · mainFinding · limitations ·
funding · conflicts · relevanceToProject(High/Med/Low) · evidenceDirection(Supports/Weakens/
Does-not-resolve/Methodological) · sourceId |

## PesticideProduct
| id · productName · manufacturer · epaRegistrationNumber · caRegistrationId · formulation ·
registrationStatus · firstRegistrationDate · cancellationDate · sourceId |

## ActiveIngredient
| id · commonName · casNumber · chemicalClass · soilHalfLife · waterHalfLife · vaporPressure
· solubility · koc · driftPotential · runoffPotential · cancerClassification ·
developmentalToxicityClassification · genotoxicityEvidence · endocrineActivityEvidence ·
restrictedMaterialCA · sourceId |
Numeric fate values are null unless a real value was retrieved; never guessed.

## ApplicationEvent
| id · date · time · temporalPrecision · productId · activeIngredientId · quantity · unit ·
applicationRate · area · cropOrSiteType · location · locationPrecision · applicator ·
permitNumber · method · targetPest · weatherNotes · **evidenceClass** · confidenceGrade ·
sourceId · notes |

`evidenceClass` (never display an inference as an application):
`documented_exact` · `documented_within_reporting_unit` · `documented_purchase` ·
`documented_approved_product` · `contractually_permitted` · `current_policy_product` ·
`historically_likely` · `industry_standard_inference` · `unverified_allegation`.

## ApplicationArea
| id · geometry · accuracy · reportingUnit · parcelId · siteName · siteType · bufferAssumptions
· sourceId |

## Site
| id · name · address · coordinates · operator · owner · maintenanceResponsibility ·
knownVendor · knownProduct · knownApplication · policyDocuments · sourceQuality ·
earliestEvidence · latestEvidence · unknownFields · sourceId |

## EnvironmentalSite
| id · name · siteType · status · contaminants · geometry · database · distanceToZoneA ·
sourceId |

## WaterSystem
| id · name · provider · source · treatmentType · serviceAreaGeometry · sourceId |

## Provenance for inferred records
Any inferred/estimated record additionally stores: `inferenceMethod`, `inputSourceIds[]`,
`assumptions`, `confidence`, `dateCreated`, `codeVersion`.
