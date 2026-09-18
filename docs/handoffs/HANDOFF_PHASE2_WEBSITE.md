# HANDOFF: Phase 2 video → YouTube + californiasforgottenpast.org (website lane)

Owner: website lane. Prepared 2026-09-17 by the video lane. Everything you need is on Andy's Desktop.

## 1. Files (Andy's Desktop)
| File | Use |
|---|---|
| `Ladera_Phase2_FINAL_16x9_YouTube.mp4` | YouTube upload. 1920x1080, 24 fps, 11:41. The vertical film centered over a blurred, darkened fill, the same treatment as the Phase 1 YouTube upload (see how the Phase 1 embed looks on the site). |
| `Ladera_Phase2_FINAL.mp4` | Vertical 1080x1920 master (Instagram/TikTok). Do not upload this one to YouTube. |
| `Ladera_Phase2_COVER_16x9.jpg` | YouTube thumbnail. |
| `Ladera_Phase2_COVER_9x16.jpg` | Share card / vertical cover. |
| `Ladera_Phase2_BASE/README_FINAL_TIMELINE.txt` | Chapter times for the YouTube description. |
| `Ladera_Phase2_BASE/phase2_full_script.txt` | Narration script (for captions if YouTube auto-captions fail). |

If the 16x9 file is missing, make it from the vertical master with:
```bash
ffmpeg -i Ladera_Phase2_FINAL.mp4 -filter_complex "[0:v]split=2[a][b];[a]scale=1920:1080,boxblur=30:5,eq=brightness=-0.15[bg];[b]scale=-2:1080[fg];[bg][fg]overlay=(W-w)/2:0,format=yuv420p[v]" -map "[v]" -map 0:a -c:v libx264 -preset fast -crf 18 -r 24 -c:a copy -movflags +faststart Ladera_Phase2_FINAL_16x9_YouTube.mp4
```

## 2. YouTube upload (Andy's channel, same as Phase 1)
Title: `Phase 2: I Found the Concrete Vat Base. Ladera Ranch and California's Forgotten Arsenic Program`
Visibility: Public. Category: News & Politics. Not made for kids. Thumbnail: `Ladera_Phase2_COVER_16x9.jpg`.
Playlist: California's Forgotten Past (create if missing; add Phase 1 too).
Chapters (paste into the description exactly; YouTube needs 0:00 first):
```
0:00 Cover and Phase 1 recap
0:49 Since Phase 1
1:02 The map that sent me out there
1:56 Finding the concrete base
2:11 The site: rails and rim
2:31 Florida kept records
3:07 What a dipping station looked like (AI-assisted reconstruction)
4:17 The arithmetic: 8 lb per 500 gallons
5:22 Grading 1997 to 2007
5:46 Three ways soil moves
6:22 The tire swing
6:39 The pond by the golf course, 1929 to 2025
7:56 The public trail
8:14 Water, and where to test
8:59 The hardest part to say carefully
9:48 Closing
```
Description:
```
PHASE 2 of an independent investigation into California's state-mandated arsenic cattle-dipping program (1907 to 1912) and Ladera Ranch, the South Orange County community built on the former O'Neill Ranch. Phase 1 is on this channel.

In August 2026 I hiked into the ungraded open space beside Ladera Ranch and the Arroyo Trabuco golf course and found a twelve-foot concrete rectangle with iron pipe rails still leading up to it. Twelve feet is the floor length of a federal-specification dipping vat (USDA Bureau of Animal Industry Circular 183, 1911). It is unfenced, unmarked, and beside a public trail. Below it is a pond that appears in every aerial back to 1929.

This video shows the site, a reconstruction of a 1911-specification dipping station (AI-assisted imagery, labeled as such; not historical footage), the arithmetic from the federal formula (8 lb arsenic trioxide per 500 gallons, every animal every 14 days), Florida's record of the same program (11 of 12 tested vat sites failed the soil arsenic standard), the grading history of the community, and where soil should be sampled.

What this video does not do: it does not establish that anything caused anyone's illness. Ewing sarcoma has no established environmental cause. The identification of the concrete base as a vat is not confirmed until the soil is tested. Some soil sampling in Ladera Ranch is now under way; what it is testing for, and where, has not been shared, and I have not been contacted to help determine where to test.

The ask is one sentence. California: test the soil.

Full report, maps, sources and the Phase 1 film: https://californiasforgottenpast.org
Contact: via the website.

Independent research and data-organization project. Not medical advice. Establishes no causation. Figures are model estimates from documented herd sizes and the federal formula; every source is graded on the website.
```
Tags: Ladera Ranch, arsenic, cattle dipping vat, Texas fever tick, Orange County, Rancho Mission Viejo, Ewing sarcoma, soil testing, California history, environmental health, USDA Bureau of Animal Industry, Arroyo Trabuco.

After upload, record the 11-character video id (the part after `watch?v=`). You need it for step 3.

## 3. Website: add the Phase 2 video (repo `~/Ladera-Ranch`, static site on Vercel, page `docs/california/report.html`)
The Phase 1 embed is a click-to-load facade: `docs/california/report.html` line ~142, `<div class="videobox" id="ytfacade" data-yt="QDGB_R92jns" ...>` with caption `<p class="vb-cap">Watch: a short documentary…</p>`, loaded by the script at the bottom of the file (`getElementById("ytfacade")`).
1. Duplicate the videobox block directly below the Phase 1 one. Set `data-yt` to the new id. Give it `id="ytfacade2"`. Poster image: add `docs/california/assets/phase2_cover_16x9.jpg` (copy of `Ladera_Phase2_COVER_16x9.jpg`) and reference it the same way the Phase 1 poster is referenced.
2. Captions: Phase 1 box → `Phase 1 (July 2026): the record. A short documentary on the investigation, by Andy Stavros.`  Phase 2 box → `Phase 2 (September 2026): the site. A concrete dip-vat base found in the open space beside Ladera Ranch, and where to test.`
3. Change the loader script so it handles both boxes: replace `var f=document.getElementById("ytfacade"); if(!f) return;` + the two listeners with a loop over `document.querySelectorAll(".videobox[data-yt]")`, attaching the same `load` closure to each. Keep the `window.va("event",{name:"Video play"})` call; add the box id to the event name so analytics can tell them apart (`"Video play: "+f.id`).
4. Add an "Update, September 2026" paragraph under the Phase 2 box (3 to 4 sentences, no coordinates, no photos of the exact spot beyond what the video shows): base found, unfenced, beside a trail; identification unconfirmed until soil is tested; some sampling under way, Andy not consulted on locations; the ask is unchanged. Link the Phase 2 evidence page if one exists; otherwise link the video.
5. `index.html` and `share-card.jpg`: add the Phase 2 line to the masthead description ("Phase 1: the record. Phase 2: the site.") and regenerate the share card if it carries text. Update `sitemap.xml` lastmod.
6. Do NOT publish coordinates of the concrete base or the pond anywhere on the site (project rule: stage coordinate disclosure; the state and the landowner get them first).
7. Commit with the repo's commit style and the `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` trailer; push to `main` triggers the Vercel deploy. `PUSH_INSTRUCTIONS.md` covers the remote.

## 4. Remove the password protection
There is no password code in the repo, so the gate is Vercel's Deployment Protection. In the Vercel dashboard: Project `californiasforgottenpast` (or whatever the project is named) → Settings → Deployment Protection → set Vercel Authentication and Password Protection to Disabled for Production (and Preview if Andy wants the previews open too) → Save. Then open the site in a private window to confirm no prompt. If a `middleware` or Basic-Auth header was added at the Vercel edge instead, remove it from the project's Functions/Edge config. Andy has to do the dashboard click himself if the lane has no Vercel login; tell him the exact path above.

## 5. Order of operations
YouTube upload (unlisted first, check it plays, then Public) → site edit with the new id → deploy → verify both embeds play on phone and desktop → remove password protection → tell Andy it is live so he can post Instagram (captions are in `Desktop/Ladera_Phase2_BASE/SOCIAL_POSTS_Phase1_Phase2.md`).

## 6. Content notes the lane must not change
The film's on-screen language was audited claim by claim (`evidence/lhdrs/phase2_base/NARRATION_AUDIT.md` in the Documents repo). Do not add "confirmed", "contaminated", "poisoned" or any causal wording on the site around the video. The pond and vat coordinates stay off the site.
