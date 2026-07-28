# Mission 5 source and method

## Source hierarchy

1. Contemporary official County tables control builder, permit, escrow, absorption, and asset-status claims within their stated CFD scope.
2. Official orthorectified imagery controls only capture-date visible-state observations.
3. Official current directories and GIS control only current names and geography.
4. Contemporary journalism and trade publications support reported events within their wording.
5. Secondary real-estate directories are candidate crosswalks. Conflicts with official contemporary records remain visible and are resolved in favor of the official record.

## Acquisition

Each retrieved item records its original URL, local path, publication date where known, retrieval date, byte count, archive status, source class, reliability grade, and SHA-256 checksum. The acquisition manifest and summary are under `evidence/lhdrs/mission5/`.

## Text and table review

Embedded text was extracted from 25 PDF/HTML records. OCR was not used. County tables were checked against rendered pages because text extraction can scramble columns. Source locators identify the relevant report page or table.

## Current tract/neighborhood crosswalk

The process normalizes the 2019 official street directory, filters current County address points by street and address constraints, then assigns each point to the smallest covering recorded-tract polygon. The relationship is valid at the 2026-07-27 retrieval date. It is not historical tract parentage.

## Imagery

Official CDFW/USDA NAIP service exports cover the current Ladera CDP and surrounding area. Raster catalog filenames establish exact tile dates. Full-resolution and southern-region comparisons support seven written observations. No visual region was digitized for proximity analysis.

## Confidence

- `high`: direct official record or official imagery within a tightly bounded claim.
- `medium`: contemporary reporting, visual synthesis requiring interpretation, or a current spatial crosswalk with historical limits.
- `low`: unconfirmed secondary candidate.

Unknown fields remain blank or explicitly `unknown`. Zero is used only where a source reports zero.
