# Regional Wind Context

Generated from archived NOAA Integrated Surface Database station metadata and Global
Hourly files. The study uses El Toro MCAS as the closer partial record and John Wayne
Airport as the continuous 1997-2010 regional record.

| Output | Rows |
|---|---:|
| Candidate station-history records within 70 km | 40 |
| Selected annual station summaries | 17 |
| Selected monthly station summaries | 204 |
| Same-year El Toro / John Wayne comparisons | 1 |

## Processing

- One routine report is selected per UTC hour, preferring `FM-12` or `FM-15` and then
  the observation nearest the top of the hour.
- Wind speed uses the NOAA `WND` field in tenths of metres per second after rejecting
  missing values and suspect or erroneous quality codes 2, 3, 6, and 7.
- Direction sectors describe where wind was reported as coming from. Easterly is
  45-134 degrees and westerly is 225-314 degrees.
- Calm means reported sustained speed equals 0.0 m/s. Strong-wind counts use 10 m/s.
- El Toro files are available for 1997, 1999, and 2000 only. The 1999-2000 files contain
  daily/monthly precipitation summaries but no valid `WND` observations, so only 1997
  supports wind statistics. The gap is not interpolated.
- John Wayne observations use file ID `72297793184` in 1997-1999 and 2004-2010 and
  the same station's `72297799999` identity in 2000-2003. Summary-only companion files
  are archived but excluded from wind statistics.

## Interpretation Boundary

Airport observations are regional historical context. Ladera Ranch terrain, elevation,
and local flow can differ. These summaries do not downscale wind, reconstruct parcel-level
conditions, or model movement between places.
