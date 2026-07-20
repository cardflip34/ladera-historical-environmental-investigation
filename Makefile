# LEHRP task runner. Most targets need only Python stdlib + Node.
.PHONY: bootstrap dev build process-gis process-pur test analyze build-reports clean

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

test:                 ## Run data-integrity tests
	python3 tests/test_data_integrity.py

analyze:              ## Run the hypothetical incidence-scenario analysis
	python3 notebooks/incidence_scenario_analysis.py

build-reports:        ## (Re)generate GIS + run tests + print report locations
	$(MAKE) process-gis
	$(MAKE) test
	@echo "Reports: reports/preliminary_findings.md, reports/evidence_gate_package.md"

clean:
	rm -rf apps/web/.next apps/web/node_modules
