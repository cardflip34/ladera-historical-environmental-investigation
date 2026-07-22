#!/usr/bin/env python3
"""B-roll boards for the California video cut. PIL only, 1920x1080. Measured/archival style,
no fear imagery. Text quotes are from graded sources (see sources.csv); clipping boards are styled
reproductions of REAL headlines/text (B2 press), clearly labeled as set-type reproductions."""
import os
from PIL import Image, ImageDraw, ImageFont
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,"media/broll/boards"); os.makedirs(OUT,exist_ok=True)
W,H=1920,1080
INK=(22,35,58); PAPER=(247,245,240); LINE=(221,215,202); ACC=(47,96,135); BRASS=(169,126,31)
def F(sz,name="Arial Bold"):
    try: return ImageFont.truetype(f"/System/Library/Fonts/Supplemental/{name}.ttf",sz)
    except: return ImageFont.load_default()
def board(title):
    im=Image.new("RGB",(W,H),PAPER); dr=ImageDraw.Draw(im)
    dr.rectangle([0,0,W,10],fill=BRASS); dr.rectangle([0,H-56,W,H],fill=INK)
    dr.text((40,H-40),"LEHRP · independent research · geographic overlap ≠ exposure ≠ causation · no soil tested; no contamination asserted",font=F(20,"Arial"),fill=(210,216,226),anchor="lm")
    if title: dr.text((60,50),title,font=F(54),fill=INK)
    return im,dr
def wrap(dr,txt,x,y,w,font,fill,lh):
    line="";
    for word in txt.split():
        if dr.textlength(line+" "+word,font=font)>w and line:
            dr.text((x,y),line,font=font,fill=fill); y+=lh; line=word
        else: line=(line+" "+word).strip()
    if line: dr.text((x,y),line,font=font,fill=fill); y+=lh
    return y

# B6 — FL/SE vs CA process comparison
im,dr=board("Two states. One program. One difference: the record.")
cols=[("THE SOUTHEAST / FLORIDA",(46,105,60),[
 "Government-run: state crews BUILT and OPERATED the vats",
 "Sites LOGGED — Florida can name 3,000+ former vat sites today",
 "NSW Australia: register + guidelines + notice to land buyers"]),
 ("CALIFORNIA",(150,60,42),[
 "Mandated the dipping — then left it to EACH RANCH",
 "Worked from a mailed federal circular; 'homemade dips are the ones most commonly used' (USDA, 1911)",
 "NO agency register · no follow-up in ANY later decade · DTSC ag guidance still excludes animal point sources"])]
for i,(h,c,items) in enumerate(cols):
    x=80+i*940; dr.rounded_rectangle([x,170,x+860,930],14,outline=c,width=5)
    dr.rectangle([x,170,x+860,250],fill=c); dr.text((x+430,210),h,font=F(40),anchor="mm",fill=(255,255,255))
    y=300
    for it in items:
        dr.ellipse([x+40,y+8,x+64,y+32],fill=c); y=wrap(dr,it,x+90,y,720,F(33,"Arial"),INK,44)+36
im.save(f"{OUT}/B6_fl_vs_ca_process.jpg",quality=92)

# B7 — timeline 1906→2026 (staggered label levels; labels clamped to margins)
im,dr=board("The decades of silence")
y0=560; dr.line([100,y0,W-100,y0],fill=INK,width=6)
# (year, label, level): level = vertical slot; negative above line, positive below
ev=[(1906,"quarantine begins",-1),(1907,"CA compels arsenical dipping",1),
    (1908,"Joplin dip · 6 cattle die",-2),(1912,"quarantine LIFTED — record ends",2),
    (1950,"aerial-photo era begins (Phase-I lookback limit)",-1),(1968,"Coto begins",1),
    (1999,"Ladera built (paper-only reviews)",-1),(2026,"still ZERO arsenic tests on dip ground",1)]
x0,x1=100,W-100; yr0,yr1=1906,2026
gx=lambda yr: x0+(yr-yr0)/(yr1-yr0)*(x1-x0)
dr.rectangle([int(gx(1912)),y0-6,int(gx(1999)),y0+6],fill=(200,80,60))
for yr,lab,lv in ev:
    x=gx(yr); hot=yr in (1912,2026)
    dr.ellipse([x-14,y0-14,x+14,y0+14],fill=BRASS if hot else ACC)
    ly=y0+lv*95+(20 if lv>0 else -20)
    dr.line([x,y0+(16 if lv>0 else -16),x,ly],fill=(160,160,150),width=2)
    tw=dr.textlength(lab,font=F(28,"Arial"))
    tx=min(max(x,120+tw/2),W-120-tw/2)
    dr.text((tx,ly+(26 if lv>0 else -26)),lab,font=F(28,"Arial"),fill=INK,anchor="mm")
    dr.text((tx,ly+(64 if lv>0 else -64)),str(yr),font=F(34),fill=BRASS if hot else ACC,anchor="mm")
dr.text((W//2,975),"1912 → 1999: no register · no follow-up · vat locations structurally invisible to every later review",font=F(32,"Arial"),fill=(150,60,42),anchor="mm")
im.save(f"{OUT}/B7_timeline.jpg",quality=92)

# B5 — the two arsenics
im,dr=board("Two arsenic signatures — California only ever tested one")
c1,c2=(90,110,60),(150,60,42)
for i,(h,c,l1,l2,l3) in enumerate([
 ("LEAD-ARSENATE",c1,"Orchard / crop pesticide","Arsenic WITH lead (As + Pb)","This is what school/orchard tests target"),
 ("ARSENIC TRIOXIDE ('white arsenic')",c2,"THE CATTLE-DIP POISON (8 lb / 500 gal)","Arsenic with little or NO lead","NEVER the target of any California test")]):
    x=80+i*940; dr.rounded_rectangle([x,190,x+860,820],14,outline=c,width=5)
    dr.text((x+430,250),h,font=F(38),fill=c,anchor="mm")
    dr.text((x+430,380),l1,font=F(34,"Arial"),fill=INK,anchor="mm")
    dr.text((x+430,500),l2,font=F(44),fill=c,anchor="mm")
    dr.text((x+430,680),l3,font=F(30,"Arial"),fill=INK,anchor="mm")
dr.text((W//2,900),"A lab can tell them apart. Speciation + the lead ratio = the discriminator.",font=F(34),fill=ACC,anchor="mm")
im.save(f"{OUT}/B5_two_arsenics.jpg",quality=92)

# B1/B2/B10/B11 — clipping-style boards (typeset reproductions, labeled)
CLIPS=[("B1_clip_1908_dip","LOS ANGELES HERALD — MAY 27, 1908","HOPE TO SAVE CATTLE FROM THE TEXAS TICK",
 "“Several hundred head of stock have been treated by dipping at the ranch of J. C. Joplin in Trabuco canyon… six or seven hundred head at Capistrano… dipping in progress at Yorba and at the Bixby ranch in Santa Ana canyon.”"),
 ("B2_clip_1908_killed","SAN JOSE MERCURY — JUNE 26, 1908","KILLED TICKS AND CATTLE",
 "“Six head of cattle belonging to E. J. Levengood died following their dipping for Texas fever tick… the arsenic preparation recommended by the Government.”"),
 ("B10_clip_1912_quarantine","SAN FRANCISCO CALL — MARCH 8, 1912","QUARANTINE AGAINST FEVER TICK IS RAISED",
 "“In California, the county of Orange is released from quarantine.” — federal order, as printed 15 Mar 1912"),
 ("B11_clip_1933_obit","LA HABRA STAR — JUNE 23, 1933","COUNTY PIONEER LAID TO REST",
 "“Funeral services for Josiah C. Joplin, 89, Orange county pioneer…” — the Bell Canyon homesteader of the 1908 dip record")]
for fn,src,head,body in CLIPS:
    im,dr=board(None)
    dr.rectangle([160,80,W-160,H-140],fill=(252,250,244),outline=LINE,width=3)
    dr.text((W//2,150),src,font=F(28,"Arial"),fill=(120,110,90),anchor="mm")
    dr.line([460,190,W-460,190],fill=(120,110,90),width=2)
    dr.text((W//2,290),head,font=F(64,"Times New Roman Bold" if os.path.exists("/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf") else "Arial Bold"),fill=(30,28,24),anchor="mm")
    wrap(dr,body,320,420,W-640,F(40,"Times New Roman" if os.path.exists("/System/Library/Fonts/Supplemental/Times New Roman.ttf") else "Arial"),(45,42,36),58)
    dr.text((W//2,H-110),"set-type reproduction of the original text · source grade B2 · original scan: cdnc.ucr.edu",font=F(22,"Arial"),fill=(140,130,110),anchor="mm")
    im.save(f"{OUT}/{fn}.jpg",quality=92)

# B12/B13 — school boards
SCH=[("B12_schools_ladera","LADERA RANCH — every public school, and what the record shows",[
 ("Oso Grande Elementary (2005)","Phase 1 + Addendum only (2003) — PAPER REVIEW, no soil sampled, arsenic never an analyte"),
 ("Ladera Ranch Elementary (2003)","no EnviroStor school-investigation entry located"),
 ("Ladera Ranch Middle School (2003)","no EnviroStor school-investigation entry located"),
 ("Chaparral Elementary (2001)","no EnviroStor school-investigation entry located"),
 ("+ 5 private/preschool operators, 1 former campus","see verified roster — none with an entry")]),
 ("B13_schools_coto","COTO / TRABUCO AREA — no school inside the gates; the surrounding five",[
 ("Wagon Wheel Elementary (1997) — west of the Joplin patent ground","no EnviroStor school-investigation entry located"),
 ("Trabuco Elementary (Trabuco Canyon)","no EnviroStor school-investigation entry located"),
 ("Robinson Elementary (1994, Robinson Ranch)","no EnviroStor school-investigation entry located"),
 ("Portola Hills Elementary (1992)","no EnviroStor school-investigation entry located"),
 ("Dove Canyon Montessori","no EnviroStor school-investigation entry located")])]
for fn,t,rows in SCH:
    im,dr=board(t)
    y=220
    for name,status in rows:
        dr.rounded_rectangle([80,y,W-80,y+130],10,fill=(252,250,244),outline=LINE,width=2)
        dr.text((120,y+38),name,font=F(38),fill=INK,anchor="lm")
        dr.text((120,y+92),status,font=F(28,"Arial"),fill=(150,60,42) if "PAPER" in status else (100,96,88),anchor="lm")
        y+=150
    dr.text((80,y+30),"absence of an entry ≠ clearance — it means the question was never opened",font=F(30,"Arial"),fill=ACC)
    im.save(f"{OUT}/{fn}.jpg",quality=92)
print("boards written to",OUT, len(os.listdir(OUT)))
