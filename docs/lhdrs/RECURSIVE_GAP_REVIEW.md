# LHDRS Recursive Gap Review

Review date: 2026-07-26

## First-Edition Stop Condition

The first LHDRS edition has exhausted the repository, indexed County planning pages,
County public GIS services, CEQAnet, official school records, the community association
retrospective, and bounded searches for the highest-priority missing records. Additional
general web searching is unlikely to resolve the remaining critical questions. The next
improvements require one or more of: an unindexed public record, a records request, manual
map registration and digitization, or a new dated imagery acquisition.

This is a research stop condition, not a claim that the historical record is complete.

## Evidence Gates

| Output | Current state | Evidence required to reopen | Prohibited substitute |
|---|---|---|---|
| Exact entitlement action | EIR 555 certification dated; broader action unresolved | Original 1995-10-17 Board minutes, resolution, ordinance, and findings | Treating EIR certification or a developer retrospective as the complete entitlement action |
| Planning-area and village GIS | Map archived; polygons not digitized | Registered County planned-community map and documented village crosswalk | Current CDP boundary or hand-drawn approximate villages |
| Annual grading and construction | Community-scale activity known; annual extents absent | Grading permits, inspection closeouts, dated aerial interpretation, or equivalent project records | Tract recording dates, sales dates, or current parcel footprints |
| Annual occupied neighborhoods | Community occupancy milestones known; dated polygons absent | Certificates of occupancy, assessor improvement years, or tract-level sales/occupancy releases | Treating all recorded or sold tracts as occupied |
| Historical construction proximity | Blocked | Dated occupied-neighborhood and active-construction polygons for the same year | Community centroids, zero distance, current boundaries, or legal tract-recording dates |
| Village/builders sequence | Nine villages registered; most milestone cells unresolved | Final-map title sheets, builder filings, brochures, and village-map crosswalk | Assigning a village from name similarity alone |
| Annual imagery sequence | County 1997/1998 frame archived; 1999-2006 sequence absent | NAIP, USGS, County flight-index, library, or licensed frames with acquisition metadata | Undated web imagery or present-day basemaps |
| Roads and utilities in service | Requirements and Phase 1 proposal documented | Acceptance resolutions, notices of completion, as-builts, and board records | Permit thresholds or CEQA proposal dates |

## Confirmed Corrections

- An official County staff record dates Board certification of Final EIR 555 to
  1995-10-17. The developer's separate 1997 approval statement remains visible as a
  lower-confidence conflicting claim.
- Planning Areas 7 and 8 were structurally realigned after CSV validation detected a
  shifted field. Automated header-width testing now covers every canonical CSV.
- The historical aerial is displayed as a transparent PNG. Its diagonal flight boundary
  is real coverage metadata; the earlier opaque black no-data wedge was a display
  artifact and is recorded in `dead_ends.csv`.

## Next Research Order

1. Request the 1995 Board packet and all adopted instruments for Final EIR 555 and the
   Ladera Planned Community.
2. Register and digitize the County planning-area map, then build a defensible village
   crosswalk before assigning tract polygons.
3. Obtain grading-permit and certificate-of-occupancy indexes for 1997-2008. These two
   inputs unlock the highest-value annual and proximity outputs.
4. Search County, USGS, USDA/NAIP, and library flight indexes for 1999-2006 frames, with
   capture dates and coverage footprints preserved.
5. Retrieve road, utility, school-construction, park, and commercial acceptance records
   only after the core occupied-versus-construction geometry gate is met.

## Rebuild and Review

After new evidence is added, run:

```bash
make lhdrs-build
make lhdrs-publish
make test
make build
```

Then repeat source-conflict review, annual-layer visual inspection, mobile and desktop
atlas checks, and this gap review. Do not silently replace the prior edition; archive the
new source and update its checksum and retrieval status first.
