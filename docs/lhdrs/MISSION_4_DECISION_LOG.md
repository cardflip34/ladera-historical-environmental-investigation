# Mission 4 Decision Log

## M4-D001: Preserve the first edition by filename and data boundary

Mission 4 adds observation, interval, proximity, and second-edition outputs. Existing
first-edition reports and canonical rows remain available. Corrections are versioned or
superseding records, not silent replacements.

## M4-D002: Separate observations, claims, and lifecycle states

An observation records what a source directly states or an analyst directly interprets.
A claim combines one or more observations. A lifecycle state is a dated system conclusion.
The three concepts receive separate identifiers, provenance, confidence, and review state.

## M4-D003: Tract recording is not construction or occupancy

County tract-map geometry and recording dates remain high-quality legal subdivision
evidence. They do not establish grading, roads, utilities, vertical construction,
habitability, sale, or occupancy without separate evidence.

## M4-D004: Use intervals rather than invented dates

Where evidence establishes only a before/after relationship, Mission 4 records earliest
and latest bounds. It does not apply a standard construction duration or convert a sequence
into an exact date.

## M4-D005: Gate every published proximity comparison

A result requires a subject geometry and construction geometry with overlapping valid
time, explicit provenance, nonempty valid geometry, and stated confidence. Metric
calculations will use NAD83 / California zone 6 (`EPSG:26946`) or a documented equivalent,
never longitude/latitude. Failed gates produce an explicit blocked-comparison record.

## M4-D006: Descriptive historical scope only

Construction proximity, wind, terrain, and drainage are descriptive historical variables.
Mission 4 will not model contamination, transport, individual exposure, health risk, or
disease causation.

## M4-D007: Preserve source geometry and raw OCR

Invalid County polygons are reported as received and repaired only in memory for metric
operations. Title-sheet OCR keeps raw candidates and explicit corrections. A normalized
parent number may use the intersecting-tract graph as a review constraint, but no OCR
normalization is hidden and high-risk corrections receive visual review.

## M4-D008: Title-sheet parties are not automatically builders

Recorded maps identify owners, beneficiaries, managers, and other interest holders. Those
names are indexed as documentary parties. A party becomes a tract builder only when the
title sheet or separate evidence establishes that role.

## M4-D009: Airport winds are regional context only

John Wayne and El Toro Global Hourly observations describe regional station conditions.
They do not establish parcel-level wind, transport, or exposure conditions in Ladera Ranch.

## M4-D010: Current terrain is not a historical surface

The County DEM is dated 2018 and is used as present-day terrain context. Its elevation
values are converted from an inferred US survey-foot vertical unit with medium confidence;
neither the dataset nor the conversion is presented as a 1997-2010 ground surface.

## M4-D011: DSA milestones are administrative milestones

DSA received, approval, and closeout dates describe project administration. They are not
silently converted into physical construction start, completion, opening, or occupancy dates.

## M4-D012: Empty geometry means unsupported, not absent

Empty construction, habitability, occupancy, and school-boundary layers record that no
qualified public geometry was established. They do not claim that development or attendance
areas did not exist.

## M4-D013: A blocked gate is a complete analytical result

The proximity workflow is complete when every candidate comparison has been tested against
the evidence gates. With no qualifying dated subject and target polygons, the defensible
output is zero calculated comparisons plus explicit blocked records.

## M4-D014: Verify the web build in an exact clean mirror

Repeated dependency reads from the Documents volume stalled without a compiler error. The
verifier therefore copies the exact application source and lockfile to a temporary local
workspace, symlinks the repository data and schema, performs `npm ci`, and runs TypeScript,
Prisma, audit, and production-build checks there.

## M4-D015: The current CDP is a display extent

The current Census-designated-place boundary is useful for reproducible clipping and atlas
display. It is not substituted for a historical entitlement, village, tract, or occupancy
boundary.
