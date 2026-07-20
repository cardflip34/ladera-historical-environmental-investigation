# Dead End Log

Approaches that failed, and why. Recorded so they are not repeated — by a future
contributor, or by a future session of this work.

A dead end is not a wasted search. Several of the entries below are substantive negative
findings that constrain what can be claimed.

---

## DE-001 — ArcGIS conventional service root (2026-07-18)

**Tried:** `https://ocgis.com/arcgis/rest/services` and variants.
**Result:** 404 on every attempt across multiple sessions.
**Why it failed:** Orange County publishes at `/arcpub/`, not `/arcgis/`. There is no
redirect and no discoverable hint.
**Cost:** Blocked the discovery of 1929–1947 aerial photography through an entire prior
session, and produced a *published conclusion that was wrong* — that the earliest imagery
was 1948 and a dip vat was therefore undetectable in principle. See correction C-003.
**Lesson:** when an agency's GIS portal is known to exist but the REST root 404s, enumerate
alternative path prefixes before concluding the service is absent.

## DE-002 — ArcGIS webmap 75daa7a29b7c4ea0b5c01596ac24904d (2026-07-18)

**Tried:** Extracting the historical-imagery webmap ID from the OC webappviewer config, then
resolving its operational layers.
**Result:** The webmap resolves to rainfall and weather layers. Not imagery.
**Why it failed:** The app config pointed at a different or stale webmap than the viewer
actually renders.
**Lesson:** verify a webmap's layer list before building on its ID.

## DE-003 — Automated water detection on 1929–1947 aerial frames (2026-07-18)

**Tried:** Detecting impounded water as regions that are simultaneously dark and
low-variance (water is dark *and* smooth on panchromatic film, unlike vegetation which is
dark and textured, or shadow which is dark and elongated).
**Result:** ~111 candidates in the 1929 frame and ~225 in the 1937 frame, of which ~100 fell
inside Zone A. Visual review showed the detector was keying on **hillslope shadow**, not
water.
**Why it failed:** the scanned frames have wildly different tone curves — the 1929 frame's
12th-percentile brightness is DN ~109–128 (bright, low contrast), the 1937 frame's is DN
~23–43 (dark, high contrast). A single percentile threshold cannot serve both, and the
terrain is steep enough that shadow dominates the dark tail.
**Superseded by:** extracting cyan hydrography ink from the 1968 USGS sheet, where every
feature was drawn by a surveyor who visited the ground. Strictly better evidence.
**Script retained** at `pipelines/python/detect_water_1930s.py` with the failure documented
in its docstring, so the approach is not naively retried.

## DE-004 — Overpass API primary endpoint (2026-07-18)

**Tried:** POST to `overpass-api.de/api/interpreter`.
**Result:** HTTP 406 Not Acceptable.
**Workaround:** GET with `--data-urlencode` against `overpass.kumi.systems` succeeded.

## DE-005 — Eagle_Aerial_2025 export at full resolution (2026-07-18)

**Tried:** `exportImage` at 6000×5200 against the 2025 imagery service.
**Result:** `"The requested image exceeds the size limit."`
**Workaround:** `OC_Aerial_2022_1ft_WGS84` at 4000×3467. Modern imagery is used only for
comparison and georeferencing verification, so the older vintage costs nothing.

## DE-006 — Referenced repository path (2026-07-18)

**Tried:** locating `workspace/ladera-historical-environmental-investigation`.
**Result:** does not exist anywhere on the filesystem.
**Resolution:** the directive's path is a placeholder. All work continues in the existing
repository at `/Users/andystavros/Ladera-Ranch`, which already holds the source registry,
GIS layers, imagery archive, and prior reports. No new project created.

---

## Standing access barriers

These are not failures of method — they are materials that exist and are known, but are not
reachable without an in-person visit, a paid reproduction order, or a formal request. They
are tracked here and in `FUTURE_EVIDENCE_GATES.md` rather than treated as blockers.

| Barrier | Holding | Route |
|---|---|---|
| Rancho Mission Viejo company records | Private corporate archive | Direct request; no public access route |
| Sherman Library & Gardens ranch collections | Corona del Mar, CA | In-person appointment |
| First American Title historical photograph archive | Santa Ana, CA | In-person / reproduction request |
| National Archives RG 17 (Bureau of Animal Industry) field records | NARA | Reproduction request; most not digitised |
| Orange County Archives original plats and assessor records | Santa Ana, CA | In-person |
| LA Times / OC Register full archives | Commercial | Paywalled |

*Updated as clusters report.*

## DE-007 — BLM General Land Office Records could not be searched (2026-07-19)

**Tried:** locating an early-20th-century plat and survey field notes for the townships covering
the study area.
**Result:** legacy GLO endpoints return HTTP 401; the current site redirects to **Login.gov**
authentication. No account was created.
**Consequence:** GLO remains the **most likely repository** for both a 1912-era plat and the
survey field notes identified as the highest-value untapped cartographic source. This is an
**unsearched archive, not a demonstrated absence**, and every statement in the publication about
the 1912 plat is worded accordingly.
**Route:** requires a signed-in human at glorecords.blm.gov.

## DE-008 — No 1912 plat of Rancho Santa Margarita y Las Flores located (2026-07-19)

**Searched:** Library of Congress maps and JSON API, David Rumsey Luna API, Calisphere, Online
Archive of California, archive.org.
**Found instead:** the **1867** Strobel survey plat (Bancroft Library, Land Case Map E-1362A,
89,742 acres), which was acquired.
**Note:** 1912 postdates the 1879 patent, so any 1912 document would more likely be a partition
or subdivision map than a Surveyor General plat. Combined with DE-007, the question stays open.

## DE-009 — USC full-resolution masters unavailable anonymously (2026-07-19)

**Tried:** `/cdm/ref/collection/`, `/digital/iiif/`, `/iiif/2/`, and legacy `/archive/` routes
for CHS-2085, 2358, 2359, 2360. All return 404 or 403.
**Available:** 1200 px derivatives, which are sufficient for publication.
**Route for masters (~5,280×4,200):** email specol@lib.usc.edu.
**Caution recorded:** USC image URLs are **time-expiring CloudFront signed URLs** and are not
stable citation targets. Cite the DOIs.

## DE-010 — California Governor's cattle fever quarantine proclamation, 15 April 1907 (2026-07-19)

**Located:** California State Library, executive-order collection, `5910-5913.pdf`.
**Result:** HTTP **403 from CloudFront** ("Request blocked") to automated access.
**Why it matters:** this is likely the founding state instrument of the quarantine and would
date the programme precisely. Worth retrying from an ordinary browser.

## DE-011 — No Orange County newspaper covering the quarantine period is digitised (2026-07-19)

**Searched:** California Digital Newspaper Collection and Chronicling America, for Orange County
cattle quarantine legal notices and dipping orders, c. 1900–1925.

**Result:** CDNC holds only **four** Orange County titles — Huntington Beach News, La Habra Star,
Santa Ana Journal, Tustin News — and **none covers 1900–1909**. Chronicling America holds **zero**
Orange County California titles, verified against a control (15 titles for Los Angeles County,
1 for San Diego).

**Consequence:** every Orange County finding in this investigation came from **out-of-county
papers reporting inward** — the *Los Angeles Herald* and *Pacific Rural Press*. Searches inside
the four OC titles held returned no Orange County dipping item at all; the apparent hits were
national wire briefs (e.g. a 1935 "Cattle Dipped" item datelined Laredo, Texas).

**This is a digitisation gap, not an absence of records.** The proclamations demonstrably
existed — three are referenced by date in located articles (Gillett, 1 Feb 1908; Gillett/Keane,
31 Mar 1910; Keane/Johnson, 7 Mar 1912). A *Pacific Rural Press* item of 1903 names the **Santa
Ana Blade** and **Anaheim Gazette** as the papers of record. Neither is digitised anywhere
searched. A county quarantine proclamation would have been published as a paid legal notice in
exactly those titles.

**Route:** microfilm at Orange County Archives, Santa Ana Public Library, or CSU Fullerton.
Target windows: Feb 1908, May–Aug 1908, Mar–Apr 1910, Mar 1912.

**Technical note for anyone repeating this:** CDNC blocks automated access via Cloudflare
Turnstile — HTTP 403 to both scripted fetches and command-line tools. It works normally in a
real browser.
