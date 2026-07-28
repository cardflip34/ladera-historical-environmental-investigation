# Mission 5 data completeness

| Domain | Coverage | What is supported | What remains missing |
| --- | --- | --- | --- |
| Sources | 57 total; 30 new | Complete for acquired set | Agency/manual archives remain |
| Recorded tracts | 123/123 legal recording dates | Complete legal-map inventory | Planning, grading, building, occupancy lifecycle |
| Current tract/neighborhood crosswalk | 116/123 tracts; 6,446 address rows | Strong current geography | Historical assignment and validity periods |
| Neighborhoods | 130 official named phases | Complete current official directory | Phase opening/construction dates |
| Builders/products | 69 products; 27 County-controlled | Strong for Phase V/VI snapshots | Exact tract assignment and other primary tables |
| Occupancy | 20 annual CFD counts plus first-resident conflict | Strong nonspatial aggregate | Tract/address first and substantial occupancy |
| Construction | Three new bounded status/change records | Useful visual/report bounds | Permits, closeouts, active work polygons |
| Imagery | Full 2005, 2009, 2010 plus two partial earlier frames | Strong on capture-date visible state | Full annual coverage for missing years |
| Schools | Official openings and administrative projects | Strong campus milestones | Historical attendance boundaries and exact work footprints |
| Facilities | Official retrospective opening milestones | Moderate milestone coverage | Exact dates, construction windows, historical footprints |
| Commercial | Eight exact 2006-12-31 UAC status rows | Strong status snapshot | Opening dates, tenants, permits, footprints |
| Roads | 361 current roads; one 2008 widening status | Current geometry plus one historical observation | Opening, acceptance, maintenance, haul routes |

## Proximity gate

All construction, occupancy, and lifecycle additions remain `proximityEligible=false`. Construction, school, and neighborhood proximity result tables remain empty. This is a required evidence safeguard, not a failed calculation.
