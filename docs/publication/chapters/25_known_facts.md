# Known Facts

Claims this investigation regards as established: documented in a primary or official source, verified against that source, and reproducible by a reader who follows the citation. Each carries its limiting or contradictory evidence, because an established fact with no stated limits is usually an overstated one.

**30 claims in this category.**


## EM-001 — Ladera Ranch sits on land that was part of the Rancho Mission Viejo cattle operation prior to development

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** USGS 7.5' quadrangles 1948-1968 label the area MISSION VIEJO OR LA PAZ; OC Survey aerials 1929-1946 show open rangeland with stock trails and grazing patterns

**Limiting or contradictory evidence.** None identified

**Citation.** USGS San Juan Capistrano 7.5' quadrangle, 1948 and 1968 editions; OC Survey Historic_Imagery_v2 frames OID 346/310/293


## EM-002 — The Ladera Ranch footprint was undeveloped open rangeland in every available pre-1950 aerial photograph

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** Six pre-1950 frames examined (1929/1931/1937-38/1938/1946-47); systematic 4x3 tile survey of Zone A at full resolution; no structures resolvable inside Zone A except one node on Trabuco Creek

**Limiting or contradictory evidence.** 1946-47 frame has a coverage gap over the NW quarter of the footprint

**Citation.** OC Survey Historic_Imagery_v2, frames OID 346/351/310/340/286/293; research/historical_imagery/README.md


## EM-003 — No cattle dip vat or corral complex has been identified anywhere inside the Ladera Ranch footprint

**Confidence:** Low  ·  **Status:** Verified - confidence downgraded

**Supporting evidence.** Systematic tile survey of Zone A on the 1937-38 frame at 1.15 ft/px, a resolution at which a corral would be unmistakable; also examined 1929, 1946-47, 1948/1968/1974 topographic and orthophoto sheets

**Limiting or contradictory evidence.** SUBSTANTIALLY REVISED 2026-07-19, see correction C-004. USDA Circular 174 documents that California vats were frequently SMALL: a cage vat cost $55-65 in materials and 'is installed near the corrals and requires only a short chute'; for cage vats 'draining pens are not essential and are rarely used'. A wade tank cost 'less than $10 for materials' and measures roughly 15 ft long by 4 ft deep. Structures of that class need not produce a large corral complex and may not be resolvable at 1.15 ft/px. The earlier claim that 'a corral complex would be unmistakable' was overconfident. PLUS the original limits: imagery begins 1929, twelve years after the programme; vats were commonly backfilled; USGS symbology had no vat symbol.

**Citation.** research/historical_imagery/README.md sections 3 and 5


## EM-004 — Orange County publishes scanned aerial photography of the study area back to 1929

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** Raster catalog query returned 36 frames intersecting the footprint spanning 1929-1997; six pre-date 1950; frames retrieved and georeferencing verified against modern landmarks

**Limiting or contradictory evidence.** None

**Citation.** https://ocgis.com/arcpub/rest/services/Historic_Imagery/Historic_Imagery_v2/ImageServer


## EM-005 — The 1968 USGS field survey mapped 41 surface-water bodies of 350 sq m or larger within the study footprint, 16 of them inside Zone A

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** Cyan hydrography ink extracted from the georeferenced 1968 sheet by colour threshold; 41 features passed area and elongation filters

**Limiting or contradictory evidence.** Derived by colour thresholding, so inherits cartographic generalisation and scan artefacts; positions are centroids not digitised outlines; features under 350 sq m excluded by design

**Citation.** USGS San Juan Capistrano 7.5' quadrangle, 1968 edition; pipelines/python/extract_topo_water.py


## EM-006 — Every one of the 41 ranch-era water bodies now has a modern building within 500 metres; median distance to the nearest building is 66 metres

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** Measured against 10618 OSM building footprints; 24/41 within 100 m, 34/41 within 200 m, 40/41 within 300 m, 41/41 within 500 m

**Limiting or contradictory evidence.** OSM completeness is not guaranteed uniform, though under-mapping would bias distances upward not downward, so the finding is conservative

**Citation.** pipelines/python/premise_homes_on_water.py; research/historical_imagery/premise_homes_on_water.json


## EM-007 — Modern housing was NOT preferentially sited on the ranch-era water bodies

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** Zone-A-restricted null: water sites average 9.0 buildings within 100 m vs 9.3 for 6000 random points in the same area. Enrichment 0.97x, permutation p = 0.51

**Limiting or contradictory evidence.** A bbox-wide null gave 0.79x, inflated by dense Mission Viejo inside the extent; the Zone-A-restricted null is the fair comparison and is reported as primary

**Citation.** research/historical_imagery/premise_null_zonea.json


## EM-008 — Modern slope beneath buildings cannot be used to infer original landform siting

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** Buildings sit at median 1.7 degrees vs 6.7 degrees for available land, but Ladera Ranch was mass-graded, so pad flatness was manufactured by the grading under investigation. The comparison is circular.

**Limiting or contradictory evidence.** None - this is a methodological exclusion, deliberately recorded so the figure is not later mistaken for a finding

**Citation.** research/historical_imagery/README.md section 6; USGS 3DEP DEM


## EM-009 — A single structure existed at 33.55505 -117.65492 on Trabuco Creek in the pre-development period

**Confidence:** Medium  ·  **Status:** Verified

**Supporting evidence.** Visible on the 1948 USGS sheet at a trail convergence on the valley floor at elevation 307, adjacent to water; setting is consistent with a ranch working area

**Limiting or contradictory evidence.** The map does not label it. A single building is equally consistent with a line camp, barn, or ranch house. It is NOT identified as a dip site.

**Citation.** USGS San Juan Capistrano 7.5' quadrangle 1948 edition; research/historical_imagery/07_zoom_1948_ranch_structure_elev307.jpg


## EM-010 — The watercourse containing the 1948 ranch structure is Trabuco Creek, not Canada Chiquita

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** The 1937-38 OC Survey aerial carries the county cartographer's own red ink label across the corridor, legible at 1.15 ft/px

**Limiting or contradictory evidence.** Earlier project documentation misidentified it as Canada Chiquita; corrected and logged as C-002

**Citation.** OC Survey Historic_Imagery_v2 frame OID 310; research/CORRECTIONS.md C-002


## EM-011 — Orange County was within the California cattle tick quarantine area and was classified by the USDA as heavily tick-infested

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** USDA Bureau of Animal Industry Circular 174 (1911), p.285, lists Orange County among counties found 'heavily infested' with cattle ticks, alongside San Luis Obispo, Santa Barbara, San Diego, Fresno and Ventura. The same page refers to losses 'south of the quarantine line in California'. Page read and verified directly, not via summary. Circular 174 is titled 'Eradicating Cattle Ticks in California' and is a US Government work.

**Limiting or contradictory evidence.** Reported at COUNTY level only. It does not place a dipping vat on any specific parcel, on Rancho Mission Viejo, or within the Ladera Ranch footprint. Orange County in 1911 covered roughly 800 square miles. This establishes the programme's geographic scope, not any site-specific activity.

**Citation.** MacKellar, W.M. and Hart, G.H. (1911) 'Eradicating Cattle Ticks in California', USDA Bureau of Animal Industry Circular No. 174, p.285. archive.org/details/CAT31283802


## EM-013 — DTSC found arsenic in soil at several school sites on former agricultural land near Ladera Ranch

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** EnviroStor records for Carl Hankey Elementary, Plant Depot School Site, and San Juan Elementary list arsenic among contaminants found

**Limiting or contradictory evidence.** Arsenic occurs naturally in California soils at background levels; presence alone does not establish an anthropogenic source or a link to cattle dipping. Former orchard land also carries lead arsenate residues from a completely different practice.

**Citation.** DTSC EnviroStor site records


## EM-019 — Cattle dipping demonstrably occurred in Orange County in 1908, at four named locations, county-ordered and supervised by public officials

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** Los Angeles Herald, 27 May 1908, p.10, datelined Santa Ana: reports Dr. Coleman, deputy state quarantine officer, consulting with Orange County cattle raisers, and states that 'several hundred head of stock have been treated by dipping at the ranch of J. C. Joplin in Trabuco canyon, six or seven hundred head are now being dipped at Capistrano and dipping is in progress at Yorba and at the Bixby ranch in Santa Ana canyon.' ARTICLE READ AND VERIFIED DIRECTLY at cdnc.ucr.edu. Corroborated by Los Angeles Herald 25 July 1908 (dipping ordered by county veterinarian Dr. W.S. McFarlane; Levengood claim for six cattle deaths) and Pacific Rural Press 15 Aug 1908.

**Limiting or contradictory evidence.** Names RANCHES AND DISTRICTS, NOT vat coordinates. None of the four named locations is Rancho Mission Viejo, and none falls inside Zone A. Measured distances from the Ladera Ranch centroid: Capistrano 3.4 mi (inside Zone B), Trabuco Canyon 8.4 mi (OUTSIDE Zone B), Yorba 25.6 mi, Santa Ana Canyon 22.8 mi. SUPERSEDED 2026-07-20: this field previously stated 'NO DIP CHEMISTRY IS NAMED for any Orange County location'. THAT IS NO LONGER TRUE - see EM-035 and EM-036. The California State Veterinarian's 1908 report names the arsenical dip, gives its formula, and describes an Orange County dipping incident using it. Do not cite the superseded wording.

**Citation.** Los Angeles Herald, Vol.35 No.238, 27 May 1908, p.10, 'Hope to Save Cattle from the Texas Tick'. cdnc.ucr.edu/?a=d&d=LAH19080527.2.83.22.7.3


## EM-020 — The Orange County cattle tick quarantine ran from approximately February 1908 to March 1912

**Confidence:** Medium  ·  **Status:** Verified

**Supporting evidence.** San Francisco Call, 8 Mar 1912: 'A proclamation lifting the quarantine against the Texas fever [tick] in Orange county... was issued today by State Veterinarian Keane and signed by Governor Johnson.' Los Angeles Herald 7 Feb 1909 cites a Gillett proclamation of 1 Feb 1908. Further proclamations referenced 31 Mar 1910. Tick presence in Orange County reported as early as Nov 1898.

**Limiting or contradictory evidence.** REFINES AND NARROWS the '1907-1917' window this project had assumed. That figure was a general California/national approximation; the Orange-County-specific record indicates roughly 1908-1912. The proclamations themselves have NOT been read - these are newspaper reports OF proclamations, graded B2. The primary instruments are held by the California State Library and could not be retrieved (DE-010). A narrower window means a longer gap to the 1929 imagery: 17 years, not 12.

**Citation.** San Francisco Call, 8 Mar 1912; Los Angeles Herald, 7 Feb 1909. Via cdnc.ucr.edu


## EM-022 — The Phase I environmental historical review of aerial photography for this land began in 1952

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** EIR 589 Appendix I states across all nine Planning Areas: 'Photographs dating from 1952 to 1999 were reviewed at Continental Aerial Photo' (two areas read 1953); topographic maps 1948-1988. The Oso Grande School Phase I - the one document inside the Ladera Ranch footprint - reviewed five aerials: 1952, 1968, 1977, 1989, 1994. Verified by direct text extraction across all 218 and 67 pages respectively; regex sweep for pre-1952 years returned only 1920, 1942 and 1948, all map references. Documents archived in evidence/documents/.

**Limiting or contradictory evidence.** Describes documents OBTAINED AND READ. The Ladera Ranch entitlement EIR was NOT located, and its hazardous-materials appendix (Michael Brandman Associates, May 1995, Appendix H) is not online. This is NOT a criticism of the consultants: ASTM 1527 requires review to first developed use or 1940 using REASONABLY ASCERTAINABLE sources, and Continental Aerial Photo's holdings began in 1952. The 1929-1947 county imagery this project used is a modern digitisation that was not reasonably ascertainable in 2002.

**Citation.** EIR 589 Appendix I (SCH 2003021141), Phase I ESA PA 1-9, 2003 rev. 2004; Oso Grande School Phase I ESA, Feb 2002 (EnviroStor 30020004)


## EM-023 — No environmental review document obtained contains any reference to cattle dipping, dip vats, or arsenical dip

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** Full-text search across EIR 589 Appendix I (582,000 chars), the 2016 Ranch Plan PEIR (4.4 million chars), and the Oso Grande Phase I and Addendum. 'dip vat' 0, 'cattle dip' 0, 'sheep dip' 0. The single 'dipping' hit in EIR 589 App I (p.181) concerns metal-finishing at an industrial facility; the single 'arsenic' hit (p.119) concerns groundwater at a mine-tailings reservoir. Oso Grande: 'dip' 0, 'arsenic' 0, 'livestock' 0.

**Limiting or contradictory evidence.** Statement about DOCUMENTS OBTAINED, not about all documents that exist. The Ladera Ranch entitlement EIR and its 1995 hazardous-materials appendix were not located. Absence from the searchable record examined here is NOT evidence that the question was never considered.

**Citation.** Full-text extraction, documents archived in evidence/documents/


## EM-024 — The one assessed site inside the Ladera Ranch footprint was cleared with no soil sampling

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** Oso Grande School, 10 acres, EnviroStor 30020004, inside the footprint at 33.5436/-117.6377. EnviroStor records past use 'AGRICULTURAL - LIVESTOCK'. No soil sampling performed. Pesticides addressed qualitatively: 'pesticides and/or herbicides are not suspected within the near-surface soils beneath the site. Any pesticides and/or herbicides at the site were likely mixed and/or placed at lower depths during the development of the site.' DTSC required a PEA 8 Sep 2003, then on 7 Oct 2003 accepted the Addendum and concluded 'further environmental investigation of the site is not required', based on a site visit and geotechnical borings reviewed for methane and organics. Final status: NO CONTAMINANTS FOUND / NO ACTION REQUIRED.

**Limiting or contradictory evidence.** This is a legitimate outcome under the applicable process, and a Phase I ESA is non-sampling by definition under ASTM 1527 - so absence of sampling is a property of the instrument, not a finding about the soil. 'No contaminants found' means none were looked for in soil. Tract-level grading and geotechnical reports, and any developer-commissioned sampling for the residential areas, are not in the public repositories searched and may exist.

**Citation.** Oso Grande School Phase I ESA (Feb 2002) and Addendum (Oct 2003); DTSC letters 8 Sep and 7 Oct 2003; DTSC EnviroStor site 30020004


## EM-026 — Rancho Mission Vieja or La Paz was granted 4 April 1845 by Governor Pio Pico to Agustin Olvera, contained 46,432.65 acres, and was patented 6 August 1866

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** PRIMARY SOURCE: Ogden Hoffman, Reports of Land Cases Determined in the U.S. District Court, Northern District of California (1862), Appendix claim no.396, verbatim: 'Juan Foster, claimant for Mission Vieja or La Paz, in Los Angeles county, granted April 4th, 1845, by Pio Pico to Agustin Olvera; claim filed October 16th, 1852, confirmed by the Commission October 31st, 1854, by the District Court February 21st, 1857, and appeal dismissed June 4th, 1857; containing 46,432.65 acres.' READ AND VERIFIED DIRECTLY from full text, corroborated by the volume's own index. Acreage independently matched by Lewis (1890) p.825, Armor (1921) p.36, and the California Secretary of State US Surveyor General grant-map list, which also gives the patent date 6 Aug 1866.

**Limiting or contradictory evidence.** FORSTER WAS THE CLAIMANT, NOT THE GRANTEE - the grantee was Agustin Olvera; several secondary accounts collapse this. County given as Los Angeles; Orange County was not created until 1889. Acreage is the CONFIRMED figure and need not match the original Mexican grant description. A grant date of 1842 circulating online is contradicted by this record - see C-005. Whether the Ladera Ranch footprint fell within Mission Viejo, within Trabuco (a separate grant, 22,184.47 acres), or across the boundary is NOT resolved.

**Citation.** Hoffman, Ogden (1862), Reports of Land Cases, Appendix p.55 claim 396. archive.org/details/reportsoflandcas01hoff


## EM-029 — Rancho Santa Margarita y Las Flores was a separate grant, made in 1841 by Governor Alvarado to Pio and Andres Pico, in San Diego County

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** Hoffman (1862), Appendix claim no.700: 'Pio Pico et al., claimants for Santa Margarita and Las Flores, in San Diego county, granted May 10th, 1841, by Juan B. Alvarado to Pio Pico and Andres Pico; claim filed March 2d, 1853, and confirmed by the Commission April 24th, 1855.' Forster acquired it by PURCHASE from Pio Pico c.1863-64, not by grant.

**Limiting or contradictory evidence.** Different grantees, governor, date and county from Mission Viejo. Lewis (1890) records that only 3,616 acres of the Santa Margarita holding lay inside Orange County. Do not confuse with two other California ranchos also named Santa Margarita, in Marin and San Luis Obispo counties. The 1879 patent date reported for this rancho is UNVERIFIED.

**Citation.** Hoffman (1862), Appendix p.95 claim 700


## EM-030 — The county zoning instrument for Ladera Ranch is titled 'Ladera Planned Community', dated 17 October 1995, entitling 2,390 gross acres and 8,100 maximum dwelling units

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** Ladera Planned Community Program Text, 136 pages, published by OC Public Works. Cover page RENDERED AND READ DIRECTLY: 'LADERA PLANNED COMMUNITY / PROGRAM TEXT / OCTOBER 17, 1995 / REVISED JULY 30, 2003 / PLANNED COMMUNITY STATISTICAL SUMMARY AMENDED BY ORANGE COUNTY PLANNING COMMISSION'. Statistical table gives 2,390 gross acres and 8,100 max dwelling units. Document archived at evidence/documents/.

**Limiting or contradictory evidence.** The adopting ORDINANCE NUMBER and Board of Supervisors action date were NOT found - the PDF is a scanned image with no text layer and no adoption page in the sections examined. Rancho Mission Viejo's own website states the plan was approved in 1997, conflicting with the 1995 cover date; a plausible reconciliation is 1995 zoning adoption vs a later development agreement, but that is INFERENCE, not established. Acreage conflicts across sources: 2,390 zoned vs ~4,000 commonly cited vs 3,165 Census CDP area.

**Citation.** Ladera Planned Community Program Text, 17 Oct 1995 rev. 30 Jul 2003. OC Public Works, pwds.oc.gov/sites/ocpwocds/files/import/data/files/23433.pdf


## EM-032 — The western edge of the Ladera Ranch study area is sectioned PLSS land in T7S R8W; only the central and eastern portions are unsectioned grant land

**Confidence:** High  ·  **Status:** Verified - corrects prior finding

**Supporting evidence.** Queried directly against the BLM CadNSDI PLSS service, section layer. West-east transect at lat 33.5467: -117.678 returns T7S R8W section 23; -117.672 and east return section 00. North-south transect at lon -117.675 returns T7S R8W sections 36, 25, 24, 24, 13, 12. Queries run independently by this investigation, not taken from a summary.

**Limiting or contradictory evidence.** The community CENTROID does fall in section 00, so the earlier finding was correct about that point and wrong only in being generalised to the whole footprint. The 1948 ranch structure at 33.55505/-117.65492 also falls in section 00.

**Citation.** BLM National PLSS CadNSDI MapServer, layer 2 (PLSS Section), queried 2026-07-20; see correction C-007


## EM-033 — The survey underlying the 1866 US patent for Rancho Mission Vieja or La Paz was approved 18 December 1858

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** US Land Commission case file 250 SD, page 85 - Surveyor General's certificate of advertisement, rendered at 500 dpi and READ DIRECTLY: 'I, J. W. MANDEVILLE, United States Surveyor General, for the State of California, do hereby certify that the Rancho "Mission Viejo" or "La Paz" confirmed to Juan Forster, has been surveyed by this office, and that the survey and plat was approved by the U. S. Surveyor General, on the 18th day of December, 1858.' Records advertisement in the San Bernardino Herald (27 Sep - 16 Oct 1861) and Los Angeles Star (29 Sep - 2 Oct 1861), with a later certification of true copy dated 1866. Sequence: survey 1858, advertised 1861, certified copy 1866, patent 6 Aug 1866.

**Limiting or contradictory evidence.** A separate survey by J. C. Hays dated 19 December 1867 is indexed in Orange County GIS (LA Book 3/67-68). Being AFTER the 1866 patent it cannot be the survey the patent rested on. What it actually is - a resurvey, a county copy, something else - is UNRESOLVED. Some handwritten dates on the certificate are difficult to read with certainty; the 1858 survey approval date is clear, the signature date less so.

**Citation.** Bancroft Library, US Land Commission case file 250 SD p.85; archived at evidence/documents/


## EM-035 — Arsenical dip was the standard California cattle dipping solution from 1907, and its formula is documented

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** California State Veterinarian, Fifth Biennial Report (1908), read directly: 'The arsenical dip was first used in California during 1907, and such good results were obtained that it has been our most effective remedy ever since.' The formula given: Arsenic 8 pounds, Carbonate of soda 24 pounds, Soap 24 pounds, Pine tar 1 gallon, Water 500 gallons. The report adds: 'This solution, being poisonous in nature, is carefully used in order that cattle dipped in same are not poisoned themselves.'

**Limiting or contradictory evidence.** Statewide practice, not a site-specific finding. It establishes WHAT was used in California from 1907 onward. It does not establish that any vat existed on Rancho Mission Viejo or within the Ladera Ranch footprint.

**Citation.** California State Veterinarian, Fifth Biennial Report (1908), p.10; archived at evidence/documents/


## EM-036 — Orange County cattle were dipped in the arsenical solution, in a swim vat, in the 1907-1908 period

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** California State Veterinarian, Fifth Biennial Report (1908), read directly: 'One notable case occurred in Orange County, where a number of cattle were dipped in this solution preparatory to moving them on to a tick free pasture. Subsequently several head of these cattle died from what was claimed to be arsenical poisoning, due to the cattle drinking the dip while swimming through the vat.' 'This solution' refers to the arsenical dip whose formula is given on the same page. 'SWIMMING THROUGH THE VAT' indicates a SWIM VAT - the large permanent design, not a cage vat or wade tank.

**Limiting or contradictory evidence.** The State Veterinarian DISPUTED the arsenical-poisoning claim: 'Upon autopsy not the slightest indication of arsenical poisoning could be found.' He attributed the deaths to exhaustion, the cattle having been 'driven a distance of some 30 to 35 miles' on the day they were dipped. This is an OFFICIAL COUNTER-NARRATIVE to the newspaper account of the Levengood claim and the two should be read together. CRITICALLY: the vat is placed in 'Orange County' with NO location given. It is not attributed to Rancho Mission Viejo and not placed within the Ladera Ranch footprint.

**Citation.** California State Veterinarian, Fifth Biennial Report (1908), pp.10-11; archived at evidence/documents/


## EM-037 — Cattle were driven 30 to 35 miles in a single day to reach dipping facilities in Orange County

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** California State Veterinarian, Fifth Biennial Report (1908): the cattle in the Orange County incident 'were driven a distance of some 30 to 35 miles' on the day they were dipped.

**Limiting or contradictory evidence.** A single documented instance, not a general practice statement. It CUTS BOTH WAYS for this investigation: it shows cattle could be dipped very far from their home range, which REDUCES the necessity of an on-ranch vat - but equally shows cattle from a wide catchment converged on whichever facilities existed.

**Citation.** California State Veterinarian, Fifth Biennial Report (1908), p.10


## EM-038 — The Orange County quarantine was not fully lifted in March 1912; a small area in the extreme southwestern part of the county remained quarantined

**Confidence:** High  ·  **Status:** Verified - map examined; boundary indicative, not determinative

**Supporting evidence.** California State Veterinarian, Sixth Biennial Report (1912), read directly: 'March 7, 1912, by proclamation, your Excellency removed from quarantine all of Orange County EXCEPT A SMALL AREA IN THE EXTREME SOUTHWESTERN PART of said county. This leaves at the end of June 30, 1912, only San Diego County, that part of San Luis Obispo County lying west of...' THE MAP HAS NOW BEEN EXAMINED (p.11, rendered at 500 dpi and read directly). It shows San Diego County hatched almost entirely, and Orange County essentially clear EXCEPT a small solid wedge at its extreme southern coastal corner where it adjoins San Diego County - the San Clemente / San Onofre area.

**Limiting or contradictory evidence.** The residual area is NOT delimited in the proclamation text. The map is STATE-SCALE: county outlines are generalised and the drafting cannot resolve a four-square-mile community. Reading the wedge as the San Clemente/San Onofre coastal corner is an INTERPRETATION OF A SMALL-SCALE MAP, not a boundary determination. On that reading Ladera Ranch, roughly 8-10 miles north, falls OUTSIDE the residual area - but the map cannot prove it, and the underlying 7 March 1912 proclamation has NOT been obtained. Note also that the adjoining San Diego County land was Rancho Santa Margarita y Las Flores, under the same O'Neill/Flood ownership as Rancho Mission Viejo.

**Citation.** California State Veterinarian, Sixth Biennial Report (1912); archived at evidence/documents/


## EM-039 — Orange County was one of only three counties under strict quarantine in California in 1908

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** California State Veterinarian, Fifth Biennial Report (1908): 'To sum up: San Diego, Imperial and Orange counties are at present the only strictly quarantined counties left in the state.'

**Limiting or contradictory evidence.** A statement about regulatory status at one date, at county level. It indicates the tick problem in Orange County was among the most severe in California, but places no facility anywhere.

**Citation.** California State Veterinarian, Fifth Biennial Report (1908)


## EM-042 — The oldest depiction of this land is a USGS map field-surveyed in 1899; no photographic image predates the 1929 aerial

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** USGS Corona 30-minute quadrangle, field-surveyed 1899, published 1902 at 1:125,000, covers the full footprint (georeferencing verified by inverse polyconic projection). No aerial predates 1929: the 1927-28 Fairchild flights over Orange County all stopped at the coast/metro west of SR-133, verified against the flight index reports; the study area is bare basemap on each.

**Limiting or contradictory evidence.** The 1899 map is 1:125,000 - too coarse to show a single building or a vat - and it PRE-DATES the 1907-1912 dipping period, so it cannot show a vat regardless. It is a baseline of the landscape before dipping, not evidence of any facility. The imagery record for this land is now exhausted at both ends: nothing older than the 1899 map or the 1929 photo.

**Citation.** USGS Historical Topographic Map Collection, Corona quadrangle 1902 (1899 survey) [S-USGS-CORONA]; UCSB FrameFinder flight indices


## EM-044 — The Ladera Ranch environmental-review gap is the general case: 11 residential communities on former ranchos in dipping-quarantine counties all share it, two never reviewed at all

**Confidence:** Medium  ·  **Status:** Verified - screening layer

**Supporting evidence.** An automated per-community documentary scrub with adversarial verification ran the Ladera methodology across 11 residential targets in 5 counties (Orange, LA, San Diego, Ventura, San Bernardino, Riverside). Every one has an environmental-review historical floor post-dating the ~1912 dipping end-date by 15-34 years; Rancho Bernardo and the Rancho Santa Fe/Del Mar/Solana Beach area were built pre-CEQA with no historical-aerial review ever performed. Records in docs/statewide_program/results/.

**Limiting or contradictory evidence.** A SCREENING LAYER, not per-community verified investigation. Primary-archive confirmation (CDNC, Library of Congress) was bounded by tooling access limits (403/404) during the run. Several gap figures rest on regional Phase I aerial-floor norms where a community's own review document was not retrieved. NO contamination is found or implied for any community; no vat is located anywhere; no soil is tested anywhere. Newhall/Santa Clarita is a partial counter-example where arsenic soil testing of farmed parcels WAS required (2013 RWQCB).

**Citation.** Statewide screening program (statewide_sweep.workflow.js), 11 deep-dive records, this investigation [S-STATEWIDE]


## EM-045 — The arsenical chemistry of the California cattle dip, its toxicity, and its capacity to contaminate feed and water were documented explicitly by the U.S. Department of Agriculture in 1911, including a required poison-warning sign posted on every vat.

**Confidence:** High  ·  **Status:** Verified

**Supporting evidence.** USDA BAI, Eradicating Cattle Ticks in California (reprinted from the 26th Annual Report, 1909; issued 1911): p.291 prints the dip formula (8 lb white arsenic per 500 gal, up to 9-10 lb for range cattle); p.293 reproduces the mandatory vat sign - 'The fluid in this vat is POISONOUS to man and all animals. Do not allow it to contaminate any feed or water supply.' Read directly.

**Limiting or contradictory evidence.** The document's knowledge is county-level; it names no ranch and maps no individual vat. It establishes that the HAZARD was known, not that any specific site was recorded or located.

**Citation.** USDA BAI, Eradicating Cattle Ticks in California (1911), pp.291, 293

