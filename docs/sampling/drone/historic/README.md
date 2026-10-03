# Historic imagery sweep of the Oct 3 search area

`fetch.py` pulls every OC Survey historic frame that intersects the search area
(-117.6625 to -117.6560, 33.5510 to 33.5572; 603 x 688 m) at 20 cm/px, plus the
2022 three-inch and 2025 one-foot modern frames.

**Sixteen historic frames intersect. Fourteen are usable:**
1929, 1938 (two scans: OC 600-scale and OC countywide), 1953, 1959, 1960, 1970,
1977, 1980, 1986, 1990, 1998, plus 2022 and 2025.

Blank over this AOI despite intersecting the wider envelope: Irvine Ranch 1931,
San Joaquin Trans Corr 1988, CCSTWS Dec 1991, and OC 1200-scale 1947.

## Findings

**The 3 x 12 ft concrete floor was NOT resolved in any historic frame.** At
20 cm/px resampled from mid-century film, a 1 x 3.7 m slab in brush is at or
below the detection limit. This is a limit of the imagery, not evidence of
absence.

What the frames do resolve is the *working area* around such a structure:

- **Candidate A, 33.55311 -117.66109.** Access track terminating at a bright
  cleared pad on the spur where the cultivated field meets the creek woodland,
  with a straight linear feature ~20 m long and a curved enclosure ~16 m across.
  Present 1938-1960, vegetated by 1980, **now at or under the edge of the
  commercial development.**
- **Candidate B, 33.55449 -117.65717.** A small bright structure with internal
  detail on a cleared bench beside the creek, sharpest in 1960, under dense oak
  canopy today.

Neither is confirmed as the user's structure. Both are ranch-activity nodes of
the right character in the right place, recorded as candidates only.

## Caveats

Each historic frame is independently georeferenced by the county; expect a few
metres of misregistration between eras. The 1929 frame in particular does not
register tightly against the later ones.

The search area itself is derived from a landmark in the 3 October drone photos,
not from the structure's own coordinate, which remains unknown. Everything here
is a search of an area, not a targeting of a point.

Output figure and frames are **not committed**: locational data.
