# LEHRP task runner. Most targets need only Python stdlib + Node.
LHDRS_PYTHON ?= python3

.PHONY: bootstrap dev build process-gis process-pur lhdrs-fetch lhdrs-mission4-fetch lhdrs-noaa-fetch lhdrs-terrain-fetch lhdrs-school-fetch lhdrs-imagery-fetch lhdrs-mission4-ingest lhdrs-mission4-ocr lhdrs-build lhdrs-mission4 lhdrs-mission5-acquire lhdrs-mission5 lhdrs-rebuild-temporal lhdrs-rebuild-construction lhdrs-rebuild-occupancy lhdrs-calculate-proximity lhdrs-build-snapshots lhdrs-export-graph lhdrs-mission4-publish lhdrs-mission4-docs lhdrs-mission4-verify lhdrs-mission5-publish lhdrs-mission5-docs lhdrs-mission5-verify lhdrs-publish test analyze build-reports clean

bootstrap:            ## Install web deps (Python pipeline deps are optional)
	cd apps/web && npm install

dev:                  ## Run the web app (file-based; no DB required)
	cd apps/web && npm run dev

build:                ## Production build of the web app
	@# NOTE: `npm run build` and `npm run dev` share apps/web/.next. Running the production
	@# build while the dev server is live clobbers the dev server's webpack chunks
	@# ("Cannot find module './631.js'"). Stop dev first, or rm -rf apps/web/.next after.
	cd apps/web && npm run build

process-pur:          ## Analyze a downloaded DPR PUR annual archive (Orange County)
	@test -n "$(ARCHIVE)" || (echo "Usage: make process-pur ARCHIVE=/path/to/pur2023.zip" && exit 1)
	python3 pipelines/python/process_pur.py $(ARCHIVE)

process-gis:          ## Regenerate GeoJSON map layers from the research CSVs
	python3 pipelines/python/build_geojson.py

lhdrs-fetch:          ## Archive LHDRS public sources and refresh official GIS inputs
	python3 scripts/lhdrs_fetch_sources.py

lhdrs-mission4-fetch: ## Archive Mission 4 official tract-map documents
	python3 scripts/lhdrs_mission4_fetch.py

lhdrs-noaa-fetch:     ## Archive NOAA station metadata and selected Global Hourly files
	python3 scripts/lhdrs_fetch_noaa.py

lhdrs-terrain-fetch:  ## Archive County terrain, watershed, stream, and flood-channel inputs
	python3 scripts/lhdrs_fetch_terrain.py

lhdrs-school-fetch:   ## Archive DSA project records for original Ladera public-school campuses
	python3 scripts/lhdrs_fetch_schools.py

lhdrs-imagery-fetch:  ## Archive County imagery catalog metadata and development-era frames
	python3 scripts/lhdrs_fetch_imagery.py

lhdrs-mission4-ocr:   ## Render and OCR all archived tract-map title sheets
	$(LHDRS_PYTHON) scripts/lhdrs_ocr_tract_maps.py

lhdrs-mission4-ingest: ## Refresh all public Mission 4 evidence archives
	$(LHDRS_PYTHON) scripts/lhdrs_mission4_fetch.py
	$(LHDRS_PYTHON) scripts/lhdrs_fetch_noaa.py
	$(LHDRS_PYTHON) scripts/lhdrs_fetch_terrain.py
	$(LHDRS_PYTHON) scripts/lhdrs_fetch_schools.py
	$(LHDRS_PYTHON) scripts/lhdrs_fetch_imagery.py

lhdrs-build:          ## Build annual atlas layers and publication copies
	python3 pipelines/python/build_lhdrs.py

lhdrs-mission4:       ## Rebuild all Mission 4 data and context (needs GIS dependencies)
	$(LHDRS_PYTHON) pipelines/python/build_mission4.py
	$(LHDRS_PYTHON) pipelines/python/build_wind_context.py
	$(LHDRS_PYTHON) pipelines/python/build_terrain_context.py
	$(LHDRS_PYTHON) pipelines/python/build_school_reconstruction.py
	$(LHDRS_PYTHON) pipelines/python/build_imagery_audit.py
	$(LHDRS_PYTHON) pipelines/python/build_reconstruction.py
	$(LHDRS_PYTHON) pipelines/python/build_context_publication.py
	$(LHDRS_PYTHON) pipelines/python/build_evidence_graph.py

lhdrs-mission5-acquire: ## Refresh Mission 5 public evidence archives (network required)
	$(LHDRS_PYTHON) scripts/lhdrs_mission5_acquire.py

lhdrs-mission5:       ## Rebuild Mission 5 chronology, crosswalk, evidence, and graph outputs
	$(LHDRS_PYTHON) pipelines/python/build_mission5.py
	$(LHDRS_PYTHON) pipelines/python/build_evidence_graph.py

lhdrs-rebuild-temporal: ## Rebuild temporal states and bounded chronology matrices
	$(LHDRS_PYTHON) pipelines/python/build_reconstruction.py

lhdrs-rebuild-construction: ## Rebuild imagery interpretations and construction gate inputs
	$(LHDRS_PYTHON) pipelines/python/build_imagery_audit.py
	$(LHDRS_PYTHON) pipelines/python/build_reconstruction.py

lhdrs-rebuild-occupancy: ## Rebuild occupancy events, matrices, and status layers
	$(LHDRS_PYTHON) pipelines/python/build_reconstruction.py

lhdrs-calculate-proximity: ## Apply evidence gates and calculate only eligible comparisons
	$(LHDRS_PYTHON) pipelines/python/build_reconstruction.py

lhdrs-build-snapshots: ## Rebuild annual and phase state manifests
	$(LHDRS_PYTHON) pipelines/python/build_reconstruction.py

lhdrs-export-graph:    ## Rebuild graph, queries, and Evidence Inspector index
	$(LHDRS_PYTHON) pipelines/python/build_evidence_graph.py

lhdrs-mission4-publish: ## Generate the separate second-edition atlas and export package
	$(LHDRS_PYTHON) scripts/generate_lhdrs_second_edition.py

lhdrs-mission4-docs:  ## Generate QA, completeness, conflict, gap, and request reports
	$(LHDRS_PYTHON) scripts/generate_mission4_documentation.py

lhdrs-mission4-verify: ## Run complete Mission 4 data, schema, audit, TypeScript, and build checks
	LHDRS_PYTHON=$(LHDRS_PYTHON) $(LHDRS_PYTHON) scripts/verify_lhdrs_mission4.py

lhdrs-mission5-publish: ## Generate the Mission 5 atlas and checksummed export package
	$(LHDRS_PYTHON) scripts/generate_lhdrs_mission5_atlas.py

lhdrs-mission5-docs: ## Generate Mission 5 execution, method, completeness, gap, and QA reports
	$(LHDRS_PYTHON) scripts/generate_mission5_documentation.py

lhdrs-mission5-verify: ## Verify Mission 5 sources, evidence, graph, safeguards, and publication files
	$(LHDRS_PYTHON) scripts/verify_lhdrs_mission5.py

lhdrs-publish:        ## Generate the LHDRS Markdown and print-ready HTML atlas
	python3 scripts/generate_lhdrs_publication.py

test:                 ## Run data-integrity tests
	python3 tests/test_data_integrity.py
	python3 tests/test_lhdrs_integrity.py

analyze:              ## Run the hypothetical incidence-scenario analysis
	python3 notebooks/incidence_scenario_analysis.py

build-reports:        ## (Re)generate GIS + run tests + print report locations
	$(MAKE) process-gis
	$(MAKE) lhdrs-build
	$(MAKE) lhdrs-publish
	$(MAKE) test
	@echo "Reports: reports/preliminary_findings.md, reports/evidence_gate_package.md, reports/LHDRS_Historical_Development_Atlas.html"

clean:
	rm -rf apps/web/.next apps/web/node_modules
