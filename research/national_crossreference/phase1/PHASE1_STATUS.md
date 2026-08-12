# Phase 1 status — exposure layer (blind to outcomes)
Started 2026-08-10. RULE: this layer completes before any outcome (cluster) data is joined.

## Done
- CA quarantine footprint at county level from held A1 documents: the 1906 line crossed at
  the northern limits of SLO/Fresno/Madera/San Bernardino = 13 southern counties; statewide
  release March 1912. -> quarantine_counties.csv
- State-level rows for the other 14 program states with source pointers.
- CA ranch-to-suburb conversion inventory started: 24 communities, ~550k homes on former
  ranch/range land within the 13 quarantined counties. -> ca_communities.csv (grade B2,
  each row to be verified against county records + historical imagery).

## Next
1. County detail for TX/OK/MO/etc from BAI annual reports (archive.org/HathiTrust fetch list).
2. Verify CA community rows: development years from county records; former-ranch documentation.
3. Dip-likelihood scoring pass (LEHRP targeting method) - Vail Ranch/Temecula flagged HIGH
   PRIORITY (largest So-Cal cattle operation converted wholesale to suburbs).
4. Texas community inventory (San Antonio, Austin, DFW, Houston fringes).
5. Florida answer-key prep: FDOH county vat lists -> machine-readable table.

## BAI annual-report findings (added 2026-08-11, grade A1)
FY1910 "Areas released from cattle quarantine" table (BAI Annual Report, archive.org
cat11088167_1910 @ char 191242):
  California 32,271 sq mi — THE LARGEST RELEASE IN THE NATION THAT YEAR
  Texas 10,675 · Arkansas 3,466 · Oklahoma 3,076 · South Carolina 2,673 · Virginia 1,695 ·
  Tennessee 1,442 · Mississippi 1,407 · Georgia 815 · TOTAL 57,520 sq mi
Context: active operations also in North Carolina, Alabama, Missouri. Bureau supervised
12.15M sheep-scabies dippings that FY (separate program, shows dipping-infrastructure scale).
Implication: California shed most of its quarantined area in FY1910 alone, completing
statewide release Mar 1912 — the fastest exit of any major program state. The vats built for
1906-1910 compliance had the shortest institutional memory anywhere in the program.
