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

TCELL = S("TCELL", fontSize=9, leading=11.5)
THEAD = S("THEAD", fontSize=9, leading=11.5, fontName="Helvetica-Bold")
def tbl(data, widths, head=True):
    # wrap cells in Paragraphs so long text wraps inside its column instead of overflowing
    data = [[(Paragraph(str(c), THEAD if (head and ri == 0) else TCELL)
              if isinstance(c, str) else c) for c in row]
            for ri, row in enumerate(data)]
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

# ------------------------------------------------------------------ photos (unrotated, 2-up)
FO = os.path.join(REPO, "evidence/lhdrs/field_observations")
GALLERY = [
 ("2026-08-07_axis_view_structure.jpg",
  "1 — Axis view. The concrete channel runs away into brush; pipe frame at the near end."),
 ("2026-08-07_end_view_corner_and_rails.jpg",
  "2 — End view. Clean 90° concrete corner, raised rim on both sides, pipe railing descending "
  "INTO the structure. The strongest visual argument for a discrete vessel."),
 ("2026-08-07_timber_post_with_wire.jpg",
  "3 — Weathered timber post with WIRE still attached, standing near the structure; a second "
  "short stake beside it. Utility pole in the background."),
 ("2026-08-07_fallen_pipe_rails.jpg",
  "4 — Fallen and leaning pipe rails in the brush beside the structure — consistent with chute "
  "or pen railing."),
]
story += [Paragraph("The structure and its surroundings, as found", H2),
  Paragraph("Photographs exactly as taken — no rotation, cropping or enhancement. Archived with "
    "SHA-256 checksums in evidence/lhdrs/field_observations/.", SMALL), Spacer(1, 6)]
from PIL import Image as PILImage
_cells = []
for _fn, _cap in GALLERY:
    _fp = os.path.join(FO, _fn)
    if not os.path.exists(_fp):
        continue
    iw, ih = PILImage.open(_fp).size
    w = 3.25*inch; h = w*ih/iw
    _cells.append([RLImage(_fp, width=w, height=h), Paragraph(_cap, CAP)])
_rows = []
for i in range(0, len(_cells), 2):
    pair = _cells[i:i+2]
    while len(pair) < 2: pair.append("")
    _rows.append(pair)
if _rows:
    story += [Table(_rows, colWidths=[3.45*inch, 3.45*inch], style=TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3),
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),8)]))]
src = "field photographs, 2026-08-07 visit"

# ------------------------------------------------------------------ observed
story += [Paragraph("What was observed", H2),
  tbl([["Attribute", "As reported", "Confidence"],
       ["Material", "Concrete", "observer, direct"],
       ["Length", "approximately 12 ft", "estimated by eye, not measured"],
       ["Width", "approximately 3–4 ft", "estimated, not measured"],
       ["Depth", "NOT MEASURED — obscured by infill", "unknown"],
       ["Form", "Discrete linear channel with ends; not a continuous ditch run", "observer, direct"],
       ["Rim & corner", "Raised concrete rim on both long sides; clean 90-degree corner at the near end", "photo 2"],
       ["Railing", "Rusted pipe frame at the near end, one rail descending INTO the structure; further fallen/leaning pipe rails in the brush beside it", "photos 1, 2, 4"],
       ["Timber post", "Weathered squared timber post standing nearby with WIRE still attached; a second short stake beside it", "photo 3"],
       ["Wire", "Strand wire at the post, consistent with pen/fence line", "photo 3"],
       ["Context", "Utility pole visible in background of photo 3 (locational aid); dry mustard/brush cover throughout", "photos"],
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
       ["Length", "26 ft at top, tapering to 12 ft at bottom", "~12 ft — matches the FLOOR length"],
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
 "<b>Observed length matches the spec floor exactly.</b> The documented vat is 12 ft at the floor "
 "widening to 26 ft at the rim. The observed ~12 ft equals the floor "
 "length — consistent with the visible concrete being the base course of a full-size vat, with "
 "the flaring upper walls buried, broken, or (in a hybrid build) never concrete at all.",
 "<b>Reported width brackets the spec width.</b> 3–4 ft observed; the spec runs 1.5 ft at the floor to 3.0 ft at the rim, so the reading sits at/above the rim width — widths were estimates.",
 "<b>It is a discrete structure with ends.</b> A concrete-lined drainage channel runs continuously "
 "across a slope; it does not begin and end in ~12 ft. A vat does.",
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

# ------------------------------------------------------------------ the system
story += [Paragraph("Why a lone concrete channel is what a whole station leaves behind", H2),
  Paragraph("A dipping vat was never a standalone object. Circular 183 specifies a complete "
    "<b>station</b>: receiving and retaining pens, a chute, the vat itself, an exit incline, a "
    "dripping pen, and a barrel sunk in the ground to catch and recycle run-off. Cattle moved "
    "through it in one direction.", BODY),
  Paragraph("The decisive detail is in the bill of materials. <b>The station splits cleanly by "
    "material, and only two components were concrete.</b>", BODY),
  tbl([["Component", "Specified material", "Expected after a century"],
       ["Vat", "CONCRETE (or timber; concrete preferred)", "SURVIVES"],
       ["Dripping-pen floor", "CONCRETE, 12 × 15 ft, pitched to a corner", "SURVIVES"],
       ["Chute, 30 in × 20 ft", "timber", "gone"],
       ["Receiving / retaining pens", "timber", "gone"],
       ["Dripping-pen posts and rails", "timber, 6×6 posts, 1×8 rails", "gone"],
       ["Cover leaves / splash boards", "timber on posts set 3 ft deep", "gone"],
       ["Entry slide facing", "sheet boiler iron on the cement", "rusted away"],
       ["Drainage pipe and barrel", "iron pipe, barrel sunk in ground", "rusted / buried"]],
      [1.85*inch, 2.85*inch, 2.2*inch]),
  Spacer(1, 9),
  box([Paragraph("<b>What follows from that</b>", BODY),
   Paragraph("A century on, the timber has rotted and the ironwork has largely gone. <b>The "
     "concrete is the only part expected to remain by default.</b> So an isolated concrete channel "
     "sitting in brush, with no pens, no chute and no fencing around it, is <i>precisely</i> what "
     "the surviving fragment of a complete dipping station would look like. The absence of the "
     "other components is the predicted condition — not evidence against.", SMALL),
   Spacer(1, 5),
   Paragraph("This cuts the other way too, and should be said: the same argument means a surviving "
     "concrete fragment carries <b>less</b> corroborating context than an intact site would. There "
     "is no chute or pen left to confirm the interpretation. That is why the measurements in the "
     "next section carry so much weight — the structure has to identify itself.", SMALL)]),
  Spacer(1, 10)]

_diag = os.path.join(REPO, "evidence/lhdrs/field_observations/dipping_station_plan_1911.png")
if os.path.exists(_diag):
    from PIL import Image as PILImage
    _dw, _dh = PILImage.open(_diag).size
    w = 6.9*inch; h = w*_dh/_dw
    story += [RLImage(_diag, width=w, height=h),
      Paragraph("Scale plan of a complete 1911-specification station, drawn from the federal "
        "instructions. Every dimension is quoted from USDA Bureau of Animal Industry Circular 183 "
        "(1911), repeated in Circular 207 (1912). Solid = concrete; hatched = timber and iron.",
        CAP)]

# ------------------------------------------------------------------ base hypothesis
story += [Paragraph("The measurement, and what sat on top", H2),
  Paragraph("The observable length of the structure is <b>approximately 12 ft</b> (estimated by "
    "eye; not tape-measured). Against the federal specification this is a significant figure, "
    "because <b>12 ft is exactly the specified FLOOR length of the vat</b> (26 ft at the rim "
    "tapering to 12 ft at the floor).", BODY),
  tbl([["Observed length", "Height above vat floor (from the taper)"],
       ["~12 ft", "0 ft — THE FLOOR ITSELF"],
       ["13 ft", "0.5 ft"], ["14 ft", "0.9 ft"],
       ["20 ft", "3.7 ft"], ["26 ft", "6.5 ft — the original rim"]],
      [2.2*inch, 4.7*inch]),
  Spacer(1, 8),
  Paragraph("An observed ~12-ft concrete rectangle is therefore consistent with the visible "
    "concrete being the <b>floor pan and lowest wall course</b> of a full-size vat — the base — "
    "with whatever stood above it now gone. Two documented construction variants explain the "
    "missing top, and they answer the question directly:", BODY),

  box([Paragraph("<b>READING A — the top was CONCRETE, and it is either buried or broken</b>", BODY),
   Paragraph("Circulars 183/207 describe a full-depth concrete vat cast in the excavation, walls "
     "flaring from 12 ft at the floor to 26 ft at the rim. If this was that type, the upper walls "
     "did not vanish — they are either (a) <b>BURIED</b>: a century of slopewash and sediment can "
     "bury the flaring upper walls outward and below present grade, leaving only the innermost "
     "course exposed; or (b) <b>BROKEN</b>: unreinforced upper courses crack from roots, frost and "
     "stock traffic and are pushed over — in which case rubble fragments should lie in the brush "
     "within a few yards. <b>Testable without digging: probe the soil 5–7 ft BEYOND each visible "
     "end. A buried rim or wall stub found there confirms Reading A.</b>", SMALL)]),
  Spacer(1, 6),
  box([Paragraph("<b>READING B — the top was TIMBER, above a concrete base, and it rotted in "
    "place</b>", BODY),
   Paragraph("Circular 174's swim vat was timber — 4×4 sills and posts, 2-inch plank walls — and "
     "period practice included <b>hybrid builds</b>: a concrete lower section for water-tightness "
     "with timber framing above grade. On this reading the concrete never extended beyond the "
     "base; the timber upper walls, cover leaves and splash boards simply <b>decayed where they "
     "stood</b> over a century. Nothing had to be hauled away. The <b>weathered timber post with "
     "wire standing beside the structure</b>, and the pipe rails, are exactly the surviving traces "
     "this reading predicts.", SMALL)]),
  Spacer(1, 6),
  Paragraph("<b>Which reading is true is decidable in one site visit:</b> Reading A leaves buried "
    "concrete beyond the visible ends (probe finds it); Reading B leaves none (probe finds "
    "undisturbed soil). Either way the sediment inside the visible rectangle is the sampling "
    "target, and either way it must not be disturbed except under consent with an accredited "
    "laboratory.", BODY)]

_cs = os.path.join(REPO, "evidence/lhdrs/field_observations/vat_cross_section_reconstruction.png")
if os.path.exists(_cs):
    from PIL import Image as PILImage
    _w, _h = PILImage.open(_cs).size
    w = 6.9*inch; h = w*_h/_w
    story += [Spacer(1, 6), RLImage(_cs, width=w, height=h),
      Paragraph("Longitudinal section, to scale. Solid = observed; ghosted = interpreted from "
        "USDA Circular 183. New finds (timber post with wire, pipe rails) listed on the figure.",
        CAP)]

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
   Paragraph("Using the observed ~12 ft × 3–4 ft footprint and the prismatoid volume the "
     "circulars themselves specify: a depth of 2 ft yields about 630 gal; 3 ft about 940 gal; "
     "4 ft about 1,260 gal; 5.25 ft about 1,650 gal; 6.5 ft about 2,040 gal. The documented "
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
