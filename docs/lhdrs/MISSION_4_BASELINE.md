# Mission 4 Baseline

Baseline captured: 2026-07-27T00:47:36Z

## Repository State

- Starting branch: `main`
- Mission branch: `codex/mission-4-reconstruction`
- Starting commit: `91d7dcee3e0ff6ff21938d562d93f31298266419`
- First-edition state: preserved as uncommitted work; no files were discarded, reset, or overwritten.
- Git status: 11 tracked files modified and the complete first-edition LHDRS source,
  evidence, generated-data, report, script, and test trees untracked at mission start.
- Git operational note: ordinary status refreshes read a large packed object and can take
  several minutes. `GIT_OPTIONAL_LOCKS=0 git status --short` returns the same state without
  the optional index rewrite and is the preferred Mission 4 status command.

## First-Edition Inventory

| Item | Baseline |
|---|---:|
| Registered LHDRS sources | 19 |
| Historical events | 34 |
| Annual chapters | 12 |
| County tract polygons | 123 |
| School records | 4 |
| Evidence-graph edges | 18 |
| Application routes | 22 |

The first-edition HTML and Markdown reports, County tract GeoJSON, and transparent
1997/1998 aerial are present and nonempty. First-edition report filenames are reserved and
must not be replaced by Mission 4 publication generation.

## Verification Baseline

| Check | Result |
|---|---|
| Existing data-integrity tests | 7/7 pass |
| LHDRS integrity tests | 12/12 pass |
| Prisma 5.16.1 schema validation | Pass |
| `npm audit --audit-level=high` | 0 vulnerabilities |
| Production build immediately before Mission 4 | Pass; 22 static routes generated with Next 15.5.21 |
| Mission-start production rerun | Operational stall before compiler output; no compilation error emitted |

## Pre-Existing Operational Issue

The Mission-start build rerun slept in synchronous filesystem reads while loading Next.js,
both with the normal runtime and the bundled Node runtime, including after deleting the
generated `.next` cache. The identical source had built successfully immediately before
Mission 4. This is logged as an environment/filesystem performance issue, not a product
regression. Mission 4 must rerun the production build after implementation and cannot claim
final build success until that run completes.

## Evidence Boundary

At baseline, historical construction proximity is blocked. The repository has legal
tract-recording geometries and community-level sales/occupancy milestones, but does not
yet have sufficiently dated active-construction and occupied/habitable polygons for the
same intervals. A missing comparison is not a zero-distance result.

