# Lane command: publish Phase 2 (paste this whole block into the website-lane session)

You are the website lane for californiasforgottenpast.org (repo: ~/Ladera-Ranch, static site on Vercel, main page docs/california/report.html). Do the following in order and report each step's result.

## 1. Files (all on Andy's Desktop)
- Ladera_Phase2_FINAL_16x9_YouTube.mp4  (1920x1080, 11:48; YouTube upload)
- Ladera_Phase2_FINAL.mp4  (1080x1920 vertical master; Instagram; do not upload to YouTube)
- Ladera_Phase2_COVER_9x16.jpg  (chosen cover: ARSENIC. / Is California's soil poisoned? / I found it.)  → make the YouTube thumbnail: 1280x720 crop of its upper 60 %, centred, or request a 16:9 export from the video lane
- Ladera_Phase1_FINAL_16x9_YouTube.mp4 and Ladera_Phase1_COVER_16x9.jpg  (Phase 1 re-cut with the matching cover; replace the Phase 1 YouTube video's thumbnail with this cover, and if Andy wants, upload the re-cut as a new video)
- Ladera_Phase2_BASE/README_FINAL_TIMELINE.txt (chapters), Ladera_Phase2_BASE/phase2_full_script.txt (script for captions)

## 2. YouTube (Andy's channel, same as Phase 1). Andy or you must drag the file into YouTube Studio; the video lane cannot upload.
Title: Phase 2: I Found the Concrete Vat Base. Ladera Ranch and California's Forgotten Arsenic Program
Visibility: Unlisted first, check playback, then Public. Category: News & Politics. Not made for kids. Playlist: California's Forgotten Past (add Phase 1 too).
Chapters (paste at the top of the description):
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
6:39 The pond by the golf course
7:48 The pond, the slope and the creek
8:06 The public trail
8:24 Water, and where to test
9:09 The hardest part to say carefully
9:58 Closing
Description:
PHASE 2 of an independent investigation into California's state-mandated arsenic cattle-dipping program (1907 to 1912) and Ladera Ranch, the South Orange County community built on the former O'Neill Ranch. Phase 1 is on this channel.

In August 2026 I hiked into the ungraded open space beside Ladera Ranch and the Arroyo Trabuco golf course and found a twelve-foot concrete rectangle with iron pipe rails still leading up to it. Twelve feet is the floor length of a federal-specification dipping vat (USDA Bureau of Animal Industry Circular 183, 1911). It is unfenced, unmarked, and beside a public trail. Below it, at the foot of the slope, is a pond built with the golf course around 2004; on the creek beside it, about 260 yards upstream, the 1968 federal survey mapped a cattle watering pond.

This video shows the site, a reconstruction of a 1911-specification dipping station (AI-assisted imagery, labeled as such; not historical footage), the arithmetic from the federal formula (8 lb arsenic trioxide per 500 gallons, every cow every 14 days), Florida's record of the same program (11 of 12 tested vat sites failed the soil arsenic standard), the grading history of the community, and where soil should be sampled.

What this video does not do: it does not establish that anything caused anyone's illness. Ewing sarcoma has no established environmental cause. The identification of the concrete base as a vat is not confirmed until the soil is tested. Some soil sampling in Ladera Ranch is now under way; what it is testing for, and where, has not been shared, and I have not been contacted to help determine where to test.

The ask is one sentence. California: test the soil.

Full report, maps, sources and the Phase 1 film: https://californiasforgottenpast.org

Independent research and data-organization project. Not medical advice. Establishes no causation. Figures are model estimates from documented herd sizes and the federal formula; every source is graded on the website.
Tags: Ladera Ranch, arsenic, cattle dipping vat, Texas fever tick, Orange County, Rancho Mission Viejo, Ewing sarcoma, soil testing, California history, environmental health, USDA Bureau of Animal Industry, Arroyo Trabuco
Record the 11-character video id from the watch URL.

## 3. Website edits (docs/california/report.html)
The Phase 1 embed is a click-to-load facade at ~line 142: <div class="videobox" id="ytfacade" data-yt="QDGB_R92jns" ...> with caption <p class="vb-cap">…</p>, loaded by the script at the bottom of the file (getElementById("ytfacade")).
a. Duplicate the videobox block directly below it with id="ytfacade2" and data-yt set to the new id. Poster: add docs/california/assets/phase2_cover_16x9.jpg (copy of Ladera_Phase2_COVER_16x9.jpg, or a 16:9 crop of the 9x16 cover) and reference it the way the Phase 1 poster is referenced. Replace the Phase 1 poster with docs/california/assets/phase1_cover_16x9.jpg (copy of Ladera_Phase1_COVER_16x9.jpg) so the two match.
b. Captions: Phase 1 → "Phase 1 (July 2026): the record. A short documentary on the investigation, by Andy Stavros."  Phase 2 → "Phase 2 (September 2026): the site. A concrete dip-vat base found in the open space beside Ladera Ranch, and where to test."
c. Loader script: replace the single getElementById("ytfacade") with a loop over document.querySelectorAll(".videobox[data-yt]"), attaching the same load closure to each; keep the window.va("event") call and add the box id to the event name ("Video play: "+f.id).
d. Under the Phase 2 box add an "Update, September 2026" paragraph (3 to 4 sentences): base found, unfenced, beside a trail; identification unconfirmed until soil is tested; the pond is a golf-course-era feature at the foot of the slope, with the 1968 survey water body on the creek about 260 yards upstream; some sampling under way, Andy not consulted on locations; the ask is unchanged. No coordinates. No photos beyond what the video shows.
e. index.html masthead: add "Phase 1: the record. Phase 2: the site." Regenerate share-card.jpg if it carries text. Bump sitemap.xml lastmod.
f. Never publish coordinates of the concrete base or the pond. Do not add "confirmed", "contaminated" or "poisoned" as statements of fact anywhere on the site.
g. Commit with the repo's style and the trailer "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"; push main (Vercel deploys). PUSH_INSTRUCTIONS.md covers the remote.

## 4. Remove password protection
No password code exists in the repo; it is Vercel Deployment Protection. Vercel dashboard → the site's project → Settings → Deployment Protection → set Vercel Authentication and Password Protection to Disabled for Production → Save. Verify in a private window. If you have no Vercel login, give Andy that exact path.

## 5. Verify and report
Both embeds play on phone and desktop; no prompt on the public URL; report the Phase 2 video id and the deploy URL back to Andy so he can post Instagram (captions in Desktop/Ladera_Phase2_BASE/SOCIAL_POSTS_Phase1_Phase2.md).
