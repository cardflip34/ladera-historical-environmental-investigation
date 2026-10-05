# -*- coding: utf-8 -*-
import json, re
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, Image as RLImage, PageBreak, KeepTogether)
from PIL import Image as PILImage

INK=colors.HexColor('#171e2b'); NAVY=colors.HexColor('#20304d'); MUT=colors.HexColor('#5d6675')
LINE=colors.HexColor('#d9dee6'); RED=colors.HexColor('#a23b2c')
TIERC={'V':colors.HexColor('#a23b2c'),'A':colors.HexColor('#2f8a52'),'B':colors.HexColor('#b07d10'),
       'C':colors.HexColor('#2d5d8f'),'D':colors.HexColor('#6b7280')}

T=json.load(open('/Users/andystavros/Ladera-Ranch/docs/sampling/targets_data.json'))
R=json.load(open('/private/tmp/claude-501/-Users-andystavros-Ladera-Ranch/11a645e3-0e32-4153-b26f-2484e88c6e14/scratchpad/plan_rows.json'))
ROW={r['n']:r for r in R}
BY={t['n']:t for t in T}

S=lambda n,**k: ParagraphStyle(n, fontName=k.pop('f','Helvetica'), textColor=k.pop('c',INK), **k)
h1=S('h1',f='Helvetica-Bold',fontSize=21,leading=24,spaceAfter=4)
sub=S('sub',fontSize=10.5,leading=14,c=MUT,spaceAfter=2)
h2=S('h2',f='Helvetica-Bold',fontSize=13.5,leading=16,c=NAVY,spaceBefore=14,spaceAfter=6)
h3=S('h3',f='Helvetica-Bold',fontSize=10.5,leading=13,c=NAVY,spaceBefore=8,spaceAfter=3)
body=S('body',fontSize=9.2,leading=12.6,spaceAfter=5)
small=S('small',fontSize=7.9,leading=10.4,c=MUT)
cellh=S('cellh',f='Helvetica-Bold',fontSize=8.0,leading=10.2)
cell=S('cell',fontSize=8.0,leading=10.2)
cellm=S('cellm',fontSize=7.6,leading=9.8,c=MUT)
idst=S('idst',f='Helvetica-Bold',fontSize=13,leading=15,c=colors.white,alignment=1)

PW,PH=letter; M=0.55*inch
def page(c,doc):
    c.saveState()
    c.setFillColor(NAVY); c.rect(0,PH-0.34*inch,PW,0.34*inch,fill=1,stroke=0)
    c.setFillColor(colors.white); c.setFont('Helvetica-Bold',7.6)
    c.drawString(M,PH-0.225*inch,'LADERA ENVIRONMENTAL HEALTH RESEARCH PROJECT   ·   SOIL TESTING PLAN   ·   NOT FOR PUBLICATION')
    c.setFillColor(MUT); c.setFont('Helvetica',7.2)
    c.drawRightString(PW-M,PH-0.225*inch,'4 October 2026')
    c.setStrokeColor(LINE); c.setLineWidth(0.6); c.line(M,M-6,PW-M,M-6)
    c.setFillColor(MUT); c.setFont('Helvetica',7)
    c.drawString(M,M-16,'Hypothesis-neutral. Nothing in this plan asserts that any contaminant is present in any soil.')
    c.drawRightString(PW-M,M-16,'Page %d'%doc.page)
    c.restoreState()

doc=BaseDocTemplate('/Users/andystavros/Desktop/Ladera_Soil_Testing_Plan.pdf',pagesize=letter,
    leftMargin=M,rightMargin=M,topMargin=M+0.16*inch,bottomMargin=M+0.18*inch,
    title='Ladera Ranch soil testing plan', author='LEHRP')
doc.addPageTemplates([PageTemplate(id='n',frames=[Frame(M,M+0.18*inch,PW-2*M,PH-2*M-0.34*inch,id='f')],onPage=page)])
E=[]
AW=PW-2*M

E.append(Paragraph('Where to Test the Soil, and Why',h1))
E.append(Paragraph('Twenty-three historically derived stations across Ladera Ranch and the Arroyo Trabuco corridor, '
  'plus the concrete structure located by drone on 3 October 2026. Each station is here because a documentary '
  'layer put something at that spot — not because anything has been measured there.',sub))
E.append(Spacer(1,7))

leg=[[Paragraph('<b>V</b>',ParagraphStyle('x',parent=idst)),Paragraph('<b>THE CONCRETE STRUCTURE</b>  —  located 3 Oct 2026. Highest priority. Exact coordinate pending.',cell)],
     [Paragraph('<b>A</b>',ParagraphStyle('x',parent=idst)),Paragraph('<b>UNGRADED OPEN SPACE</b>  —  native grade, never mass graded. The only ground where an original soil profile can still exist.',cell)],
     [Paragraph('<b>B</b>',ParagraphStyle('x',parent=idst)),Paragraph('<b>FILL OVER A SOURCE POINT</b>  —  a historic water point now buried under placed fill. Tests the fill, and what is under it.',cell)],
     [Paragraph('<b>C</b>',ParagraphStyle('x',parent=idst)),Paragraph('<b>RANCH-ERA REFERENCE</b>  —  open rangeland outside the community. Establishes the local ranch-era value.',cell)],
     [Paragraph('<b>D</b>',ParagraphStyle('x',parent=idst)),Paragraph('<b>PRE-1990 DEVELOPMENT</b>  —  built before the Ladera grading era. Lowest priority.',cell)]]
lt=Table(leg,colWidths=[0.42*inch,AW-0.42*inch],rowHeights=[0.26*inch]*5)
st=[('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(1,0),(1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),2),('TOPPADDING',(0,0),(-1,-1),2)]
for i,k in enumerate(['V','A','B','C','D']): st.append(('BACKGROUND',(0,i),(0,i),TIERC[k]))
lt.setStyle(TableStyle(st)); E.append(lt)
E.append(Spacer(1,9))

E.append(Spacer(1,10))
E.append(Paragraph('How to use this document',h3))
E.append(Paragraph('The map overleaf carries every station as a numbered marker, coloured by tier. '
  'The key that follows gives, for each number: <b>what is there now</b>, the <b>recommended station coordinate</b> and its grading history, '
  '<b>why that spot was selected</b>, and <b>what to collect</b>. The stations were derived from the 1968 USGS surface-water survey, the 1948 '
  'topographic sheet and seven decades of aerial imagery, then reconciled against the 1999–2003 grading history so that no station asks '
  'anyone to sample ground that no longer exists.',body))
E.append(Paragraph('<b>The recommended coordinate is not always the historic point.</b> Where the historic point is unreachable, under a building, '
  'or on private ground, the station is offset to the nearest defensible surface and the offset distance is recorded in the project files.',body))
E.append(PageBreak())
im=PILImage.open('map.jpg'); iw,ih=im.size
mw=AW; mh=mw*ih/iw
avail=PH-2*M-0.34*inch-0.62*inch
if mh>avail: mh=avail; mw=mh*iw/ih
E.append(RLImage('map.jpg',width=mw,height=mh))
E.append(Spacer(1,4))
E.append(Paragraph('Base imagery: OC Survey 2025 countywide aerial, 1 ft. Markers show the <b>recommended accessible station</b> for each target. '
  'The red box is the search area for the concrete structure (V); its own coordinate is not yet resolved.',small))
E.append(PageBreak())

def why_of(n):
    t=BY[n]; ws=t.get('why',[]) or []
    outs=[]
    for w in ws:
        w=w.strip()
        w=w[0].upper()+w[1:]
        outs.append(w)
    if not outs: outs=['Mapped 1968 stock-water point — daily cattle congregation.']
    return outs

def block(n):
    t=BY[n]; r=ROW[n]; tier=r['tier']
    rec=t.get('rec') or {}
    lo,la=(rec.get('lon') or t['lon']),(rec.get('lat') or t['lat'])
    idcell=Paragraph(f'<b>{n}</b>',idst)
    head=Paragraph(f"<b>{t.get('today','')}</b>",cellh)
    coord=Paragraph(f"<font face='Helvetica-Bold'>{la:.5f}, {lo:.5f}</font><br/>{t.get('grading','')}",cellm)
    whyp=Paragraph('<br/>'.join('• '+w for w in why_of(n)),cell)
    act=Paragraph(r['action'],cell)
    tb=Table([[idcell,head,whyp],['',coord,act]],colWidths=[0.40*inch,2.55*inch,AW-0.40*inch-2.55*inch])
    tb.setStyle(TableStyle([
        ('SPAN',(0,0),(0,1)),('BACKGROUND',(0,0),(0,1),TIERC[tier]),
        ('VALIGN',(0,0),(0,1),'MIDDLE'),('VALIGN',(1,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(1,0),(-1,-1),7),('RIGHTPADDING',(1,0),(-1,-1),7),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LINEBELOW',(0,1),(-1,1),0.6,LINE)]))
    return tb

E.append(Paragraph('The Key — every station, and why it is on the list',h2))
E.append(Paragraph('Read each entry as: <b>what is there now</b>, the <b>recommended station coordinate</b> and its grading history, '
  'the <b>reason it was selected</b>, and <b>what to collect</b>.',body))

E.append(Paragraph('V · The concrete structure',h3))
vt=Table([[Paragraph('<b>V</b>',idst),
  Paragraph("<b>Concrete rectangle, approx. 3 × 12 ft, with iron pipe rails leading up to it.</b> Ungraded open space on the western flank of the "
            "Arroyo Trabuco corridor, south of the Hillcrest commercial block in Mission Viejo. Located by drone 3 October 2026; "
            "first found on foot August 2026.",cell),
  Paragraph("• The floor dimension matches the vat bottom in USDA Bureau of Animal Industry Circular 183 (1911): "
            "<i>“Length at top of vat, 26 feet; bottom, 12 feet.”</i><br/>"
            "• It is the single most specific thing this investigation has to point a spade at.<br/>"
            "• <b>Identification is unestablished.</b> A matching dimension is a correspondence, not a vat.",cell)],
  ['',Paragraph("<b>Search area 33.5516–33.5566 N, −117.6618 to −117.6566 W.</b> The structure's own coordinate is not yet resolved — "
            "the drone files supplied had their EXIF stripped.",cellm),
     Paragraph("<b>Under hazardous-materials protocol.</b> The structure floor; the apron or drip-pen side if one is found; the pen footprint; "
               "and a downslope transect toward the drainage. Three depths at each: 0–5, 15–30 and 45–60 cm. "
               "<b>Do not dig or probe before sampling is designed</b> — the soil is the evidence.",cell)]],
  colWidths=[0.40*inch,2.55*inch,AW-0.40*inch-2.55*inch])
vt.setStyle(TableStyle([('SPAN',(0,0),(0,1)),('BACKGROUND',(0,0),(0,1),TIERC['V']),
    ('VALIGN',(0,0),(0,1),'MIDDLE'),('VALIGN',(1,0),(-1,-1),'TOP'),
    ('LEFTPADDING',(1,0),(-1,-1),7),('RIGHTPADDING',(1,0),(-1,-1),7),
    ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),5),
    ('LINEBELOW',(0,1),(-1,1),0.6,LINE)]))
E.append(vt)

NAMES={'A':'Tier A · Ungraded open space — native grade survives here',
       'B':'Tier B · Fill over a historic water point',
       'C':'Tier C · Ranch-era reference, outside the community',
       'D':'Tier D · Pre-1990 development — lowest priority'}
for tier in ['A','B','C','D']:
    ns=sorted([r['n'] for r in R if r['tier']==tier])
    E.append(Paragraph(NAMES[tier]+f'  ({len(ns)} stations)',h3))
    for n in ns: E.append(block(n))

E.append(PageBreak())
E.append(Paragraph('What to ask the laboratory for',h2))
E.append(Paragraph('A generic “heavy metals” scan reports total arsenic. That is necessary and not sufficient. '
  'Separating a dipping-vat signature from California background, from orchard lead-arsenate, and from imported fill '
  'requires arsenic and lead on the same sample — and, on anything that exceeds background, speciation and a bioavailability '
  'measure. <b>These have to be requested before the samples are run, or the archive has to be re-pulled.</b>',body))
lab=[[Paragraph('<b>Analysis</b>',cellh),Paragraph('<b>Method</b>',cellh),Paragraph('<b>Why</b>',cellh)],
 [Paragraph('Arsenic, total',cell),Paragraph('EPA 3050B or 3051A digestion, then <b>EPA 6020B ICP-MS</b>',cell),
  Paragraph('The headline number. <b>Ask for ICP-MS, not ICP-OES</b> — the lower reporting limit matters when background is the comparison.',cell)],
 [Paragraph('Lead, total',cell),Paragraph('Same digestion and run',cell),
  Paragraph('<b>On every sample, reported alongside arsenic.</b> Lead-arsenate orchard spray carries both; a dipping vat carries arsenic without the lead. This single addition is what makes the result interpretable.',cell)],
 [Paragraph('Arsenic speciation',cell),Paragraph('HPLC-ICP-MS',cell),
  Paragraph('On exceedances only. Arsenic trioxide weathers to inorganic arsenate; a strongly organic signature would point to a different source such as MSMA herbicide.',cell)],
 [Paragraph('Bioaccessibility',cell),Paragraph('EPA 1340 gastric-phase extraction',cell),
  Paragraph('On exceedances only. Converts a soil number into a meaningful exposure statement, and is the honest answer to “does this matter?”',cell)],
 [Paragraph('Organochlorines',cell),Paragraph('EPA 8081B',cell),
  Paragraph('Optional. Tests the later pesticide era rather than the dipping era.',cell)]]
lt2=Table(lab,colWidths=[1.1*inch,1.85*inch,AW-2.95*inch])
lt2.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eef1f5')),
  ('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),0.5,LINE),
  ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
  ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
E.append(lt2)

E.append(Paragraph('Depths, replicates and controls',h2))
for t_ in ['<b>Depths.</b> 0–5 cm for the contact horizon, <b>15–30 cm</b> because a surface-only grab answers a pesticide-application question well and a legacy question badly, and 45–60 cm at the tier A stations where native grade survives.',
  '<b>Sediment.</b> Grab the top 5 cm of fine sediment at a slack-water bar, basin bottom or outfall apron, and note whether the deposit is active or relict.',
  '<b>Replicates.</b> One field duplicate per ten samples, minimum one per day. One equipment rinsate blank per day if non-disposable tools are used.',
  '<b>Background.</b> A minimum of three stations on ungraded ground, at least 300 m from any 1968 water point, any historic orchard footprint and any concrete feature. <b>Without these the arsenic numbers cannot be read.</b>',
  '<b>Field record.</b> GPS to better than 3 m with the accuracy value recorded, a photograph looking north from each station, slope position, and apparent fill versus native ground.',
  '<b>Chain of custody.</b> Signed from field to lab, with the analyte list and any hold requests <b>written on the form itself, not agreed verbally</b>. Retain residual material 90 days.']:
    E.append(Paragraph(t_,body))

E.append(Paragraph('What this plan does not claim',h2))
E.append(Paragraph('It does not claim that arsenic, pesticides or any other contaminant is present in Ladera Ranch soil, runoff, recycled water or '
  'irrigation water. <b>Nothing here is a measurement.</b> It does not identify the concrete structure as a cattle-dipping vat. It does not assert any '
  'connection between the reported pediatric cancers and any environmental factor. The station coordinates are computed from imagery and public layers; '
  'they have not been surveyed, and ownership and access must be confirmed before anyone sets foot on them. '
  '<b>Where testing has not occurred, that absence is itself part of the record.</b>',body))
E.append(Spacer(1,6))
E.append(Paragraph('Sources: 1968 USGS 7.5′ San Juan Capistrano surface-water survey, digitised (A1). 1948 USGS topographic sheet (A1). '
  'OC Survey historic aerial imagery 1929–1998 and 2025 countywide 1 ft (A2). USDA Bureau of Animal Industry Circular 183, 1911 (A1). '
  'California State Veterinarian biennial reports and Governor’s quarantine proclamations (A1). Field observations, August and October 2026 '
  '(field observation, identification unestablished).',small))
doc.build(E)
print('PDF written')
