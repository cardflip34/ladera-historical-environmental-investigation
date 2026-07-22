#!/usr/bin/env python3
"""Composite 'plates' (captioned contact sheets) that combine ALL relevant imagery into the master
California Report without exploding the page count. Each plate = a titled grid of images with per-cell
captions. Output: research/plates/plate_*.jpg. Hypothesis-neutral captions; provenance in each caption."""
import os
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS=None
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,"research/plates"); os.makedirs(OUT,exist_ok=True)
INK=(22,35,58); PAPER=(247,245,240); LINE=(200,193,178); CAPBG=(238,233,222)
def F(sz,b=True):
    p="/System/Library/Fonts/Supplemental/Arial Bold.ttf" if b else "/System/Library/Fonts/Supplemental/Arial.ttf"
    try: return ImageFont.truetype(p,sz)
    except: return ImageFont.load_default()
def wrap(dr,txt,w,font):
    out=[]; line=""
    for word in txt.split():
        if dr.textlength(line+" "+word,font=font)>w and line: out.append(line); line=word
        else: line=(line+" "+word).strip()
    if line: out.append(line)
    return out

def plate(fn, title, cells, cols, cellw=520, cellh=360, capline=3):
    """cells = list of (path, caption). Missing files skipped."""
    items=[(os.path.join(ROOT,p),c) for p,c in cells if os.path.exists(os.path.join(ROOT,p))]
    n=len(items); rows=(n+cols-1)//cols
    pad=16; capf=F(15,False); capH=capline*20+10
    gw=cols*cellw+(cols+1)*pad; gh=rows*(cellh+capH)+(rows+1)*pad
    TOP=76
    im=Image.new("RGB",(gw,gh+TOP),PAPER); dr=ImageDraw.Draw(im)
    dr.rectangle([0,0,gw,TOP],fill=INK); dr.text((24,22),title,font=F(34),fill=(255,255,255))
    for i,(path,cap) in enumerate(items):
        r,c=divmod(i,cols)
        x=pad+c*(cellw+pad); y=TOP+pad+r*(cellh+capH+pad)
        try: pic=Image.open(path).convert("RGB")
        except: continue
        # fit within cell box, letterbox on white
        sc=min(cellw/pic.width,cellh/pic.height); nw,nh=int(pic.width*sc),int(pic.height*sc)
        pic=pic.resize((nw,nh))
        box=Image.new("RGB",(cellw,cellh),(252,251,248))
        box.paste(pic,((cellw-nw)//2,(cellh-nh)//2))
        im.paste(box,(x,y)); dr.rectangle([x,y,x+cellw,y+cellh],outline=LINE,width=2)
        dr.rectangle([x,y+cellh,x+cellw,y+cellh+capH],fill=CAPBG,outline=LINE,width=1)
        for j,ln in enumerate(wrap(dr,cap,cellw-16,capf)[:capline]):
            dr.text((x+8,y+cellh+6+j*20),ln,font=capf,fill=(60,55,45))
    im.save(os.path.join(OUT,fn),quality=84)
    print("wrote",fn,f"({n} images, {im.size[0]}x{im.size[1]})")

E="evidence/images/"; H="research/historical_imagery/"; C="research/coto_de_caza/"; I="research/irvine/imagery/"

plate("plate_1_dipping_program.jpg","Plate 1 — The dipping program and the vat",[
 (E+"illustrative/USDA_ARS_cattle_fever_tick_dipping_vat_PD.jpg","Cattle swimming a fever-tick dipping vat. USDA Agricultural Research Service (public domain); present-day border quarantine — same national program & vat design, illustrative."),
 (E+"usda_bai_circ174_1911_cover.jpg","Cover — 'Eradicating Cattle Ticks in California', USDA BAI Circular 174 (1911) [A1]."),
 (E+"usda_bai_circ174_1911_p295_fig7_swim_vat_plans.png","Government swim-vat construction plan, Circular 174 fig. 7 [A1]."),
 (E+"usda_bai_circ207_1912_fig1_concrete_dipping_vat_plan.png","Concrete dipping-vat plan, Circular 207 fig. 1 (1912) [A1]."),
 (E+"usda_bai_circ207_1912_fig2_brick_dipping_vat_plan.png","Brick dipping-vat plan, Circular 207 fig. 2 [A1]."),
 (E+"usda_bai_circ174_1911_PLATE_XV_cage_vat_for_dipping_cattle.png","Cage vat for dipping cattle, Circular 174 Plate XV [A1]."),
 (E+"usda_bai_circ174_1911_p299_fig10_small_wade_tank_plans.png","Small wade-tank plan, Circular 174 fig. 10 [A1]."),
 (E+"usda_bai_circ174_1911_p293_VAT_POISON_WARNING_sign_text.png","The warning posted at every vat: POISONOUS to man and all animals, Circular 174 p.293 [A1]."),
],cols=2,cellw=560,cellh=380)

plate("plate_2_ranch_photographs.jpg","Plate 2 — The ranch this land was, 1886–1972",[
 (E+"usc_chs2358_UC139843_cattle_grazing_near_small_stream_santa_margarita_ranch_sd_county_1900.jpg","Cattle grazing at a stream, O'Neill Santa Margarita ranch, c.1900 — cattle gather at water; so did ticks and working grounds [A2, USC CHS]."),
 (E+"usc_chs2360_UC139844_herd_of_cattle_grazing_santa_margarita_ranch_sd_county_1900.jpg","Herd grazing, Santa Margarita ranch, c.1900 [A2, USC CHS]."),
 (E+"usc_chs2359_UC139832_lone_mounted_cowboy_santa_margarita_ranch_sd_county_1900.jpg","Vaquero on the O'Neill range, c.1900 [A2, USC CHS]."),
 (E+"OCPL_OCStories_CattleAtRanchoMissionViejo_1972_CHAA112_id1785.jpg","Cattle on Rancho Mission Viejo, 1972 — the operation persisted to development [A2, OCPL]."),
 (E+"OCPL_OCStories_MissionViejoRanch_roundup_1972_id1279.jpg","Roundup, Mission Viejo ranch, 1972 [A2, OCPL]."),
 (E+"OCPL_OCStories_MissionViejoRanch_CattleCorralEntrance_CHAA018_id1691.jpg","Corral entrance — the working-node type where a dip vat would stand [A2, OCPL]."),
 (E+"OCPL_OCStories_MissionViejoRanch_branding_AliceChandler_ranchhand_1971_id1676.jpg","Branding with ranch hand (Chandler), 1971 [A2, OCPL]."),
 (E+"OCPL_OCStories_MissionViejoRanchWell_AliceChandler_dowsed_1971_id1690.jpg","A hand-dowsed ranch well, 1971 — stock water on the range [A2, OCPL]."),
 (E+"usc_chs2085_UC123008_santa_marguerita_ranch_vineyard_and_winery_1886.jpg","Ranch vineyard & winery, 1886 [A2, USC CHS]."),
 (E+"OCPL_OCArchives_TrabucoAdobeRuins_ONeillPark_dateUnknown_id1508.jpg","Trabuco adobe ruins, O'Neill Park [A2, OC Archives]."),
 (E+"SantaAnaPL_11478028_TrabucoMesaAdobe_Wview_1936.jpg","Trabuco Mesa adobe, 1936 [A2, Santa Ana PL]."),
 (E+"HABS_CA-48_SantaMargaritaRanchHouse_01_general_view_from_south.jpg","Santa Margarita ranch house (HABS CA-48) — the O'Neill headquarters [A2]."),
],cols=3,cellw=440,cellh=320)

plate("plate_3_ladera_aerials.jpg","Plate 3 — Ladera Ranch footprint: historical aerials, 1929–2022",[
 (H+"oc_aerials/ann_1929.jpg","1929 — open cattle rangeland, 12 yrs after dipping ended [A2, OC Survey]."),
 (H+"oc_aerials/ann_1937.jpg","1937–38 at 1.15 ft/px — the sharpest pre-development frame [A2]."),
 (H+"oc_aerials/ann_2022.jpg","2022 — built out [A2, OC Survey]."),
 (H+"11_timeseries_1929-2022_with_water.jpg","1929·1937·1946·2022 with all 41 surveyed water bodies [A2]."),
 (H+"oc_aerials/z1_ranch_1937.jpg","'Node A' structure, 1937 — woodland + clearing, no building geometry (demoted) [A2]."),
 (H+"oc_aerials/z1_ranch_2022_modern.jpg","Same ground, 2022 — preserved greenbelt [A2]."),
 ("research/ladera/imagery/ladera_dip_bestguess_thennow.jpg","Best-guess siting (graded inference), 1937–38 vs 2022 [A2]."),
 ("research/ladera/imagery/ladera_candidates_under_neighborhood.jpg","Which candidates are greenbelt vs under houses today [A2]."),
 ("research/ladera/imagery/ladera_nodeA_zoom_thennow.jpg","Node A close-up, 1937 → 2022 greenbelt [A2]."),
],cols=3,cellw=440,cellh=330)

plate("plate_4_coto_joplin_aerials.jpg","Plate 4 — Bell Canyon / Coto de Caza / the Joplin dip ranch: aerials",[
 (C+"imagery/coto_1929_watersheds_wide.jpg","1929 South County Watersheds flight over the Coto valley [A2]."),
 (C+"imagery/coto_1938_wide.jpg","1938 — the Coto/Trabuco valley as open rangeland [A2]."),
 (C+"imagery/trabuco_mouth_1938_zoom.jpg","Trabuco canyon-mouth node, 1938 — structures + orchard [A2]."),
 (C+"joplin_patent_section_overlay.jpg","Joplin's 1909 patent (T6S R7W Sec 24/25) on today's imagery — NE Coto [A2, BLM]."),
 (C+"imagery/joplin_patent_triptych.jpg","The patent ground 1938 → 1953 → today [A2]."),
 (C+"imagery/joplin_z3_bellcanyon_east_1938.jpg","The Bell Canyon ranchstead, 1938 — buildings, orchard, fields [A2]."),
 (C+"imagery/joplin_z3_bellcanyon_east_modern.jpg","Same ranchstead ground today — still open canyon [A2]."),
 (C+"imagery/bellcanyon_starrranch_1938.jpg","Bell Canyon / Starr Ranch area, 1938 [A2]."),
 (C+"joplin_dip_site_then_and_now.jpg","The documented Joplin dip site: then and now [A2]."),
],cols=3,cellw=440,cellh=330)

plate("plate_5_other_areas_aerials.jpg","Plate 5 — Other study areas: Irvine, Newport Coast, Upper Newport Bay",[
 (I+"bommer_1931_equalized.jpg","Irvine Ranch 1931 — ranch complex near Bommer Canyon [A2]."),
 (I+"irvine_1938_sweep_montage.jpg","Southern Irvine Ranch core, 1938 systematic sweep [A2]."),
 (I+"irvine_core_overlay.jpg","The ~4-mi Irvine ranch core, 1938 vs 2022 [A2]."),
 (I+"pondcluster_beforeafter_overlay.jpg","NE farmstead / pond cluster, then & now [A2]."),
 ("research/newport_coast/newport_coast_1931_pregrading.jpg","Newport Coast, 1931 — pre-grading rangeland [A2]."),
 ("research/newport_coast/newport_coast_1938_pregrading.jpg","Newport Coast, 1938 — pre-grading [A2]."),
 ("research/eastbluff/imagery/eastbluff_mesa_1931_zoomA.jpg","Eastbluff mesa, 1931 [A2]."),
 ("research/newport_bay_areas/imagery/bigcanyon_overlay.jpg","Big Canyon, then & now [A2]."),
 ("research/newport_bay_areas/imagery/santaanaheights_overlay.jpg","Santa Ana Heights, then & now [A2]."),
],cols=3,cellw=440,cellh=330)
print("plates done")
