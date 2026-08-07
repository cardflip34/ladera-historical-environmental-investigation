#!/usr/bin/env python3
"""
Build the field-observation PDF for the concrete structure found near the 1948 node.

Usage:
    python3 scripts/lhdrs_build_field_observation_pdf.py [path/to/photo.jpg]

If a photo path is given it is embedded. If not, a marked placeholder is drawn and the document
still builds, so the write-up exists and the image can be added later by re-running with the path.

DISCIPLINE THIS DOCUMENT MUST HOLD
This is a FIELD OBSERVATION RECORD, not an identification. The structure has not been measured to
a standard, has not been sampled, and has not been assessed by anyone qualified. The document is
built to be handed to an agency or a specialist, which means the case against must be as visible
as the case for, and the dimensions must be labelled as reported-approximate throughout.
"""
from __future__ import annotations
import os, sys, datetime
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image as RLImage, PageBreak, KeepTogether)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "reports")
os.makedirs(OUT, exist_ok=True)
TODAY = datetime.date.today().isoformat()
PHOTO = sys.argv[1] if len(sys.argv) > 1 else None

INK = colors.HexColor("#171E2B"); MUT = colors.HexColor("#5F6672")
RED = colors.HexColor("#B03A2A"); AMB = colors.HexColor("#9A6A12")
GRN = colors.HexColor("#2F6B45"); RULE = colors.HexColor("#D8D5CE")
WARNBG = colors.HexColor("#FBEFEC"); PANEL = colors.HexColor("#F7F6F3")

ss = getSampleStyleSheet()
def S(name, **kw):
    base = dict(fontName="Helvetica", fontSize=10, leading=14, textColor=INK, alignment=TA_LEFT)
    base.update(kw); return ParagraphStyle(name, **base)

H1   = S("H1", fontName="Times-Bold", fontSize=21, leading=25, spaceAfter=4)
SUB  = S("SUB", fontSize=10.5, leading=14, textColor=MUT, spaceAfter=12)
H2   = S("H2", fontName="Times-Bold", fontSize=13.5, leading=17, spaceBefore=15, spaceAfter=6)
BODY = S("BODY", fontSize=10, leading=14.5, spaceAfter=7)
SMALL= S("SMALL", fontSize=8.6, leading=11.5, textColor=MUT)
CAP  = S("CAP", fontSize=8.6, leading=11.5, textColor=MUT, spaceBefore=4)
WARN = S("WARN", fontSize=10, leading=14, textColor=colors.HexColor("#7A2618"))
LI   = S("LI", fontSize=10, leading=14, leftIndent=13, bulletIndent=3, spaceAfter=3)

def rule(): return Table([[""]], colWidths=[6.9*inch], rowHeights=[0.8],
                         style=TableStyle([("BACKGROUND",(0,0),(-1,-1),RULE)]))

def box(flowables, bg=PANEL, bc=RULE, pad=9):
    return Table([[flowables]], colWidths=[6.9*inch], style=TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),bg), ("BOX",(0,0),(-1,-1),0.8,bc),
        ("LEFTPADDING",(0,0),(-1,-1),pad), ("RIGHTPADDING",(0,0),(-1,-1),pad),
        ("TOPPADDING",(0,0),(-1,-1),pad), ("BOTTOMPADDING",(0,0),(-1,-1),pad)]))

def tbl(data, widths, head=True):
    st = [("GRID",(0,0),(-1,-1),0.5,RULE),
          ("VALIGN",(0,0),(-1,-1),"TOP"),
          ("FONTSIZE",(0,0),(-1,-1),9),
          ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
          ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]
    if head:
        st += [("BACKGROUND",(0,0),(-1,0),colors.HexColor("#EEECE7")),
               ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold")]
    return Table(data, colWidths=widths, style=TableStyle(st))

story = []

# ------------------------------------------------------------------ header
story += [Paragraph("Field observation — concrete structure near the 1948 node", H1),
          Paragraph(f"Ladera Ranch vicinity, Orange County, California &nbsp;·&nbsp; "
                    f"recorded {TODAY} &nbsp;·&nbsp; LHDRS field record", SUB)]

story += [box([Paragraph("<b>THIS IS NOT AN IDENTIFICATION.</b>", WARN),
   Paragraph("The structure below has not been measured to a standard, has not been sampled, and "
     "has not been examined by anyone qualified to identify it. Dimensions are as reported by the "
     "observer and are approximate. This document exists to record what was seen, set out what "
     "would confirm or exclude a cattle-dipping vat, and be handed to someone able to decide.",
     SMALL)], bg=WARNBG, bc=RED)]

# ------------------------------------------------------------------ safety
story += [Spacer(1, 10),
  box([Paragraph("<b>SAFETY — READ BEFORE RETURNING TO THE SITE</b>", WARN),
   Paragraph("If this <i>is</i> a dipping vat, the sediment inside it is the single most "
     "concentrated place arsenic would be found anywhere in this landscape — this project's own "
     "modelling puts that compartment in the thousands of mg/kg against a California background "
     "of 1–11 mg/kg. <b>Do not dig in it. Do not handle or remove the sediment. Do not let "
     "children or animals into it.</b> Photograph and measure from outside. Arsenic does not "
     "degrade; a century has not reduced it.", SMALL)], bg=WARNBG, bc=RED)]

# ------------------------------------------------------------------ photo
story += [Paragraph("The structure as found", H2)]
if PHOTO and os.path.exists(PHOTO):
    from PIL import Image as PILImage
    iw, ih = PILImage.open(PHOTO).size
    w = 5.4*inch; h = w*ih/iw
    if h > 6.2*inch:
        h = 6.2*inch; w = h*iw/ih
    story += [RLImage(PHOTO, width=w, height=h)]
    src = os.path.basename(PHOTO)
else:
    story += [box([Paragraph("<b>[ PHOTOGRAPH TO BE INSERTED ]</b>", S("P", fontSize=11,
                    textColor=MUT, alignment=1)),
                   Spacer(1, 44),
                   Paragraph("Re-run this script with the image path to embed it:", SMALL),
                   Paragraph("<font face='Courier' size='8'>python3 scripts/"
                     "lhdrs_build_field_observation_pdf.py ~/Desktop/vat_photo.jpg</font>", SMALL),
                   Spacer(1, 40)])]
    src = "not yet attached"
story += [Paragraph(f"Observer photograph, source: {src}. Looking along the axis of the structure. "
                    "A rusted metal pipe frame lies across the near end; the concrete channel runs "
                    "away from the camera into heavy dry brush. Depth is obscured by accumulated "
                    "sediment and vegetation.", CAP)]

# ------------------------------------------------------------------ observed
story += [Paragraph("What was observed", H2),
  tbl([["Attribute", "As reported", "Confidence"],
       ["Material", "Concrete", "observer, direct"],
       ["Length", "approximately 15–20 ft", "estimated, not measured"],
       ["Width", "approximately 3–4 ft", "estimated, not measured"],
       ["Depth", "NOT MEASURED — obscured by infill", "unknown"],
       ["Form", "Discrete linear channel with ends; not a continuous ditch run", "observer, direct"],
       ["Associated", "Rusted metal pipe frame / rail at one end", "observer, direct"],
       ["Setting", "Heavy dry brush, drainage corridor, near the 1948 mapped structure",
        "observer, direct"],
       ["Coordinates", "NOT RECORDED — no GPS in the image metadata", "missing"],
       ["Image", "640 x 480 px, no EXIF GPS or timestamp retained", "low resolution"]],
      [1.25*inch, 3.55*inch, 2.1*inch])]

# ------------------------------------------------------------------ spec
story += [Paragraph("The federal specification for a concrete dipping vat", H2),
  Paragraph("USDA Bureau of Animal Industry Circulars 183 (1911) and 207 (1912) give construction "
    "specifications for <b>concrete</b> cattle-dipping vats. Circular 174 (1911) states cement is "
    "<i>preferable</i> to lumber because it &ldquo;has not the disadvantage of leaking, which is "
    "common in wooden vats.&rdquo; <b>Concrete construction is therefore consistent with, and in "
    "fact the recommended form of, a period dipping vat.</b>", BODY),
  tbl([["Dimension", "Circular 183 / 207 concrete vat", "Structure as reported"],
       ["Length", "26 ft at top, tapering to 12 ft at bottom", "~15–20 ft"],
       ["Width", "3.0 ft at top, tapering to 1.5 ft at bottom", "~3–4 ft"],
       ["Depth", "6.5 ft", "not measured"],
       ["Capacity", "1,470 gal at 5 ft 3 in fill", "unknown"],
       ["Chute", "30 in wide, 20 ft long, leading in", "not observed"],
       ["Drip pen", "~36 in wide, 20–40 ft, sloped back toward vat", "not observed"]],
      [1.05*inch, 3.15*inch, 2.7*inch])]

# ------------------------------------------------------------------ for
story += [Paragraph("Why it could be a vat — the case for", H2)]
for t in [
 "<b>Concrete is the specified material.</b> Not merely compatible — Circular 174 recommends it "
 "over timber specifically because timber vats leaked.",
 "<b>Reported length falls inside the spec envelope.</b> The documented vat is 12 ft at the floor "
 "widening to 26 ft at the rim. A reported 15–20 ft is what an observer would measure on a "
 "<i>tapered</i> vat part-filled with sediment, reading the length at whatever level the infill "
 "now sits — not at the true floor or rim.",
 "<b>Reported width brackets the spec top width.</b> 3–4 ft observed against 3.0 ft specified.",
 "<b>It is a discrete structure with ends.</b> A concrete-lined drainage channel runs continuously "
 "across a slope; it does not begin and end in 15–20 ft. A vat does.",
 "<b>A metal frame is present.</b> Vats were fitted with rails, splash boards on hinged posts, and "
 "chute fencing. A rusted pipe frame at one end is consistent with that, though not diagnostic.",
 "<b>The setting fits the siting logic.</b> Vats were placed near water and stock-handling ground. "
 "The structure sits in a drainage corridor near the only mapped 1948 structure in the study area.",
]:
    story += [Paragraph(t, LI, bulletText="•")]

# ------------------------------------------------------------------ against
story += [Paragraph("Why it might not be — the case against", H2),
  Paragraph("Stated at equal length, because a document that only argues one way is worth nothing "
    "to the agency or specialist who has to act on it.", SMALL), Spacer(1, 5)]
for t in [
 "<b>Depth is unmeasured, and depth is the whole question.</b> A dipping vat is <b>6.5 ft deep</b> "
 "with steep sides — cattle swim through it. If this structure proves to be 1–2 ft deep it is a "
 "trough, a flume or a lined ditch, and nothing else about it matters.",
 "<b>Concrete-lined drainage is extremely common here.</b> Brow ditches, V-ditches and terrace "
 "drains with pipe railings are standard on California graded slopes and in flood-control "
 "corridors. Many are 3–4 ft wide.",
 "<b>No taper has been confirmed.</b> A vat narrows markedly from rim to floor. A ditch has "
 "parallel walls. This has not been checked.",
 "<b>Neither end feature has been observed.</b> A vat is asymmetric — a steep entry slide at "
 "roughly 25° at one end, a cleated exit ramp at the other. Their absence would be strong evidence "
 "against.",
 "<b>No drip pen or chute has been seen.</b> These are large, concrete, and adjacent. Their "
 "absence is not conclusive — they may be buried or demolished — but their presence would be near "
 "decisive.",
 "<b>The systematic aerial search found no vat in this area.</b> 37,228 cells across the 1929, "
 "1938 and 1947 frames returned nothing vat-like inside the study frame. That is weak evidence of "
 "absence, but it is on the record and must be weighed.",
 "<b>Age is unestablished.</b> Nothing observed dates the concrete. It could postdate the dipping "
 "era by decades.",
]:
    story += [Paragraph(t, LI, bulletText="•")]

story += [PageBreak()]

# ------------------------------------------------------------------ resolve
story += [Paragraph("What would resolve it — in priority order", H2),
  tbl([["#", "Measurement", "Why it decides", "Vat if…"],
       ["1", "Depth to hard concrete floor, probed through sediment at several points",
        "The single most discriminating number. Vats are deep because cattle swim.", "5–6.5 ft"],
       ["2", "Width at rim and again as low as reachable",
        "A vat tapers; a ditch has parallel walls. Requires no digging.",
        "narrows ~3 ft → ~1.5 ft"],
       ["3", "Photograph both ends separately",
        "A vat is asymmetric: steep slide in, cleated ramp out. A ditch is uniform.",
        "slide one end, ramp the other"],
       ["4", "Look for an adjacent flat concrete apron",
        "The drip pen slopes back toward the vat and is unmistakable once seen.",
        "apron 36 in × 20–40 ft"],
       ["5", "Total length rim to rim, plus GPS coordinates and a scale object in frame",
        "Makes the record usable by anyone else and locatable again.", "12–26 ft"],
      ], [0.3*inch, 1.9*inch, 3.0*inch, 1.7*inch])]

story += [Spacer(1, 8),
  box([Paragraph("<b>Capacity check, once depth is known</b>", BODY),
   Paragraph("Using the reported 15–20 ft × 3–4 ft footprint and the prismatoid volume the "
     "circulars themselves specify: a depth of 2 ft yields about 916 gal; 3 ft about 1,375 gal; "
     "4 ft about 1,833 gal; 5.25 ft about 2,405 gal; 6.5 ft about 2,978 gal. The documented "
     "capacities are <b>1,470 gal</b> (Circular 183/207 concrete vat) and <b>2,088 gal</b> "
     "(Circular 174 swim vat). Depths at or above roughly 4 ft put the structure in the "
     "documented range; depths under 3 ft place it outside.", SMALL)])]

# ------------------------------------------------------------------ next
story += [Paragraph("If it holds up", H2),
  Paragraph("A suspected historic arsenical site is a regulatory matter with an established "
    "pathway. It should not be handled privately or by a contractor.", BODY)]
for t in [
 "<b>California DTSC</b> — the agency for suspected historic contamination. EnviroStor is their "
 "public system and shows no record for this area, which is itself a documented gap.",
 "<b>OC Public Works / Flood Control</b> — if the structure sits in or beside a county drainage "
 "easement, they hold the as-builts and the maintenance history.",
 "<b>Property owner consent</b> — LARMAC, the County, or Rancho Mission Viejo depending on parcel. "
 "This project's gate G10 already anticipates exactly this and requires consent plus an "
 "accredited laboratory.",
 "<b>Analyte suite:</b> arsenic <i>and lead</i>, plus DDT/DDE, toxaphene and PAHs. The lead ratio "
 "is what separates cattle-dip ground from orchard ground — dip ground carries arsenic without "
 "lead.",
]:
    story += [Paragraph(t, LI, bulletText="•")]

story += [Spacer(1, 14), rule(), Spacer(1, 6),
  Paragraph("<b>Statement class:</b> field observation, unverified. <b>Provenance:</b> observer "
    "photograph and verbal dimensions, uncorroborated. Specifications quoted are A1 — USDA Bureau "
    "of Animal Industry Circulars 174 (1911), 183 (1911) and 207 (1912), held locally with full "
    "text and SHA-256 checksums.", SMALL),
  Paragraph("<b>This document does not assert that a dipping vat has been found, that arsenic is "
    "present at this or any location, that anyone has been exposed, or that any illness has any "
    "environmental cause.</b> It records an observation and the measurements that would settle "
    "what it is. A single accredited laboratory result would outweigh everything in it.", SMALL),
  Paragraph(f"LHDRS — Ladera Historical & Environmental Investigation · generated {TODAY}", SMALL)]

path = os.path.join(OUT, "FIELD_OBSERVATION_concrete_structure.pdf")
SimpleDocTemplate(path, pagesize=LETTER,
                  leftMargin=0.8*inch, rightMargin=0.8*inch,
                  topMargin=0.75*inch, bottomMargin=0.7*inch,
                  title="Field observation - concrete structure near the 1948 node",
                  author="LHDRS").build(story)
print("wrote", path, f"{os.path.getsize(path)/1024:.0f} KB")
if not (PHOTO and os.path.exists(PHOTO)):
    print("\nNOTE: no photo embedded - placeholder drawn.")
    print("Save the image, then re-run:")
    print("  python3 scripts/lhdrs_build_field_observation_pdf.py ~/Desktop/vat_photo.jpg")
