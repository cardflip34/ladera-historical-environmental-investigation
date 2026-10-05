# National map: where the dipping happened

`natmap.py` draws the base (Albers Equal Area, ESRI:102003 via pyproj), `chrome.py`
adds the title, legend and key.

## The fifteen states, sourced

Fourteen come from one sentence in **USDA Bureau of Animal Industry, *Operations of
the Bureau of Animal Industry*, fiscal year 1907** (archive.org `CAT10681481`):

> "During the fiscal year 1907 the work of eradicating cattle ticks has been pursued
> to a greater or less extent in the States of Virginia, North Carolina, South
> Carolina, Georgia, Alabama, Tennessee, Kentucky, Arkansas, Texas, Missouri,
> California, Louisiana, and the Territory of Oklahoma."

Mississippi is named elsewhere in the same report ("Nine men have been engaged in it
in North Carolina, South Carolina, Georgia, Tennessee, Mississippi, Louisiana, and
Texas"). **Florida is the fifteenth** and is evidenced separately by the Florida DEP
records response already held by this project: a state register of **3,281 vats**.

## The point data

`vats_clean.json` — **328 records, 1,918 vats**, 1911–1936, across nine states, from
the public ArcGIS feature service *Dynamited Dipping Vats in the War for the Southern
Range* (William & Mary, item `c53b58e30ca8401982c7feec35dd6d4a`). Fields: state, year,
county/parish, town, lat/lon, number of vats destroyed, vat names, proximate date,
notes, source.

**These are vats that were destroyed and recorded.** They mark where vats stood; they
are not an inventory of vats. State whitespace is inconsistent in the source
(`Oklahoma` vs `Oklahoma `) and is stripped on load.

## What the map must not be read as

Absence of a dot is absence of a record, not absence of a vat. The great majority of
vats were never catalogued anywhere. California — where vats were built by individual
ranchers from a mailed federal circular rather than by government crews — has **no
register at all**, which is the whole premise of this project.

## Not attempted

Plotting "all ranch locations" nationally is not possible: the programme ran for ~37
years across a third of the country and the vats numbered in the hundreds of
thousands. A county-level plausibility surface would need the annual BAI quarantine
county lists (Service and Regulatory Announcements) and 1910/1920 Census of
Agriculture cattle counts by county, neither of which was retrieved here.
