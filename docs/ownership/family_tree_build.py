# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont

DPI=200; W=int(24*DPI); H=int(36*DPI); M=230
GROUND=(247,246,242); INK=(22,32,46); RULE=(201,196,184)
MUTE=(106,107,102); BLUE=(31,78,121); OX=(140,58,43); PAPER=(255,254,251)

B='/System/Library/Fonts/Supplemental/Baskerville.ttc'
G='/System/Library/Fonts/Supplemental/Georgia.ttf'
GB='/System/Library/Fonts/Supplemental/Georgia Bold.ttf'
GI='/System/Library/Fonts/Supplemental/Georgia Italic.ttf'
AV='/System/Library/Fonts/Avenir Next Condensed.ttc'
tt=ImageFont.truetype
F={'title':tt(B,200,index=1),'sub':tt(B,58),'kick':tt(AV,40),
   'gen':tt(AV,38),'name':tt(GB,44),'name_s':tt(GB,36),'dates':tt(G,32),
   'role':tt(GI,30),'note':tt(G,28),'small':tt(G,25),'tiny':tt(G,22),
   'sec':tt(B,88,index=1),'lead':tt(G,36),'lab':tt(AV,30),'lab2':tt(AV,25),
   'evt':tt(AV,27),'yr':tt(AV,30),'tlname':tt(GB,34),'tlname_s':tt(G,31)}

img=Image.new('RGB',(W,H),GROUND); d=ImageDraw.Draw(img,'RGBA')
def tw(t,fo): b=d.textbbox((0,0),t,font=fo); return b[2]-b[0]
def ctr(t,fo,cx,y,fill=INK): d.text((cx-tw(t,fo)/2,y),t,font=fo,fill=fill)
def wrap(t,fo,mw):
    out=[];cur=''
    for w_ in t.split():
        c=(cur+' '+w_).strip()
        if tw(c,fo)<=mw: cur=c
        else: out.append(cur); cur=w_
    if cur: out.append(cur)
    return out
def para(t,fo,x,y,mw,lh,fill=INK):
    for ln in wrap(t,fo,mw): d.text((x,y),ln,font=fo,fill=fill); y+=lh
    return y

# ── header
y=M
d.rectangle([M,y,W-M,y+7],fill=INK); y+=52
ctr('THE O’NEILL LINE',F['title'],W/2,y); y+=262
ctr('Five generations on one landholding, 1882 to the present, with every lifespan',F['sub'],W/2,y,MUTE); y+=86
ctr('set against the cattle-fever quarantine era',F['sub'],W/2,y,MUTE); y+=120
d.rectangle([M,y,W-M,y+3],fill=RULE); y+=34
ctr('LADERA ENVIRONMENTAL HEALTH RESEARCH PROJECT   ·   COMPILED 21 SEPTEMBER 2026   ·   DOCUMENT-ONLY: NO CLAIM OF KNOWLEDGE, INTENT OR CONDUCT',F['kick'],W/2,y,MUTE)

# ── card
def card(cx,cy,w,h,name,dates,role,notes=(),key=False,dim=False):
    x0,y0,x1,y1=cx-w/2,cy-h/2,cx+w/2,cy+h/2
    d.rounded_rectangle([x0+7,y0+8,x1+7,y1+8],14,fill=(0,0,0,16))
    d.rounded_rectangle([x0,y0,x1,y1],14,fill=PAPER,outline=(OX if key else RULE),width=(6 if key else 3))
    if key: d.rounded_rectangle([x0,y0,x1,y0+13],14,fill=OX)
    ty=y0+36
    nf=F['name'] if tw(name,F['name'])<=w-60 else F['name_s']
    for ln in wrap(name,nf,w-60): ctr(ln,nf,cx,ty,MUTE if dim else INK); ty+=52
    ctr(dates,F['dates'],cx,ty+2,MUTE); ty+=50
    if role:
        for ln in wrap(role,F['role'],w-70): ctr(ln,F['role'],cx,ty,BLUE); ty+=40
    for n in notes:
        for ln in wrap(n,F['small'],w-70): ctr(ln,F['small'],cx,ty,MUTE); ty+=33
    return (x0,y0,x1,y1)
def genlab(y,t,s):
    d.rectangle([M,y,M+178,y+42],fill=INK); d.text((M+16,y+5),t,font=F['gen'],fill=GROUND)
    d.text((M+202,y+6),s,font=F['lab'],fill=MUTE)
def bus(py,ychild,parent_x,kids,drop=110):
    d.line([(parent_x,py),(parent_x,py+drop)],fill=RULE,width=5)
    d.line([(min(kids+[parent_x]),py+drop),(max(kids+[parent_x]),py+drop)],fill=RULE,width=5)
    for k in kids: d.line([(k,py+drop),(k,ychild)],fill=RULE,width=5)
def marr(b1,b2,label=None):
    yy=(b1[1]+b1[3])/2
    d.line([(b1[2],yy),(b2[0],yy)],fill=MUTE,width=6)
    mx=(b1[2]+b2[0])/2; d.ellipse([mx-10,yy-10,mx+10,yy+10],fill=MUTE)
    if label: d.text((mx-tw(label,F['lab2'])/2,yy-52),label,font=F['lab2'],fill=MUTE)
    return mx,yy

R1,R2,R3,R4,R5=1200,1930,2660,3390,4060
genlab(R1-320,'GEN I','THE FOUNDER  ·  THE 1882 PURCHASE')
a=card(1150,R1,940,330,'Richard O’Neill Sr.','17 March 1824 – 7 May 1910',
  'Resident manager from 1882; half owner 1906/07',
  ['Born County Cork. Ran this land as a working cattle','operation for twenty-eight years. Alive and a half owner','when Orange County was quarantined in March 1910.'])
b=card(2320,R1,800,330,'Alice O’Neill','1823 – 1916','Wife',
  ['Given as “Mary” in one source.','Outlived her husband by six years.'],dim=True)
c=card(3700,R1,1000,330,'James C. Flood, then James L. Flood','1826–1889  ·  1857–1926',
  'Equal partner from 1882 — not family',
  ['The Flood half was conveyed to the O’Neills','in 1906/07 on a handshake made in 1882.'],dim=True)
marr(a,b)
d.line([(b[2],R1),(c[0],R1)],fill=RULE,width=4)
d.text(((b[2]+c[0])/2-tw('PARTNERSHIP',F['lab2'])/2,R1-52),'PARTNERSHIP',font=F['lab2'],fill=MUTE)

genlab(R2-340,'GEN II','THE DIPPING ERA  ·  1907–1926')
j =card(800 ,R2,900,360,'Jerome O’Neill','1861 – 1926','Owner and operator, 1907–1926',
  ['THE MAN IN CHARGE DURING THE COMPULSORY','DIPPING PROGRAMME. Disabled by polio.','Died 1926, two days from James L. Flood.'],key=True)
r2=card(1960,R2,900,360,'Richard O’Neill Jr.','28 Jan 1863 – 28 Dec 1943','Trust beneficiary 1926; took the Orange County land',
  ['Aged forty-five in 1908. An adult on this ranch','through the whole quarantine — and he lived','seventeen years past his brother.'],key=True)
dz=card(3000,R2,900,360,'Marguerite “Daisy” Moore O’Neill','1879 – 1981','No corporate office — she decided anyway',
  ['Refused the bank’s 1944 sale and kept the ranch.','Lived one hundred and two years.'],key=True)
ma=card(4060,R2,860,360,'Mary Agatha O’Neill Baumgartner','dates not documented','Sister; co-beneficiary of the Jerome O’Neill Trust',[],dim=True)
mx2,_=marr(r2,dz,'m. 1916')
bus(R1+165,R2-180,(a[2]+b[0])/2,[800,1960,4060])

genlab(R3-330,'GEN III','THE DEVELOPMENT DECISION  ·  1963')
al=card(1450,R3,1150,380,'Alice Marguerite O’Neill Moiso Avery','28 Jan 1917 – 22 July 2014',
  'Co-owner and matriarch. No officer title documented',
  ['m. James Robert Moiso 1938, div. c.1944–45  ·  m. Waldo A. Avery III 1951',
   '1963: with her brother, opened 11,000 acres to development.',
   'Recorded six interviews with the company historian,',
   'December 1993 – August 1994. UC Irvine, MS-R173, Box 106.'],key=True)
dk=card(3200,R3,1100,380,'Richard Jerome “Dick” O’Neill','3 May 1923 – 4 April 2009',
  'Director and general partner, Mission Viejo Co., 1963; later Chairman',
  ['m. Donna Newman 1951 (d. 2002); no children.','Chairman, OC Democratic Central Committee;','State Chair, California Democratic Party.'])
bus(R2+180,R3-190,mx2,[1450,3200])

genlab(R4-320,'GEN IV','THE ENTITLEMENT YEARS  ·  1995 AND 2004')
tm=card(1150,R4,1150,380,'Anthony R. “Tony” Moiso','born c. 1939–40',
  'President, Rancho Mission Viejo 1972–2022; Chairman from 2022',
  ['President and CEO, The Santa Margarita Company, 1983/84–c.1996.',
   'Founded Rancho Mission Viejo, LLC, 1996.',
   'Named grantee as trustee on LL 95-007, recorded 5 Oct 1995 —',
   'twelve days before EIR 555 was certified.'],key=True)
jm=card(2520,R4,820,340,'J. Jerome Moiso','1941 – 2024','Mission Viejo Co. board; continuing owner',[])
da=card(3560,R4,820,340,'Douglas Avery','dates not documented','Mission Viejo Co. board; continuing owner',[],dim=True)
bus(R3+190,R4-190,1450,[1150,2520,3560])

genlab(R5-300,'GEN V','SUCCESSION  ·  2022 AND 2026')
fd=card(900,R5,900,330,'Four daughters','all married','Deliberately not named here',
  ['No public officer role is documented for any of them.','They are private individuals.'],dim=True)
jl=card(2200,R5,1150,330,'Jeremy T. Laster','dates not documented',
  'Son-in-law. Joined 2001; President Oct 2022; CEO for 2026',
  ['Registered agent for fifty-eight entities in the group.',
   'The chief executive is family by marriage, not an outside hire.'],key=True)
bus(R4+190,R5-165,1150,[900])
marr(fd,jl)

# purpose box, right of gen V
nx0,ny0,nx1,ny1=3000,R5-300,W-M,R5+230
d.rounded_rectangle([nx0,ny0,nx1,ny1],14,fill=(255,255,255,205),outline=RULE,width=3)
d.text((nx0+40,ny0+34),'WHAT THIS CHART IS FOR',font=F['lab'],fill=OX)
yy=ny0+96
yy=para('A family tree usually records descent. This one is an instrument. It tests whether the people who lived '
        'through the 1907–1915 cattle-fever quarantine on this land could plausibly have passed what they knew '
        'to the people who later decided how it would be developed.',F['note'],nx0+40,yy,nx1-nx0-80,44)
yy+=20
para('The lifespan chart below answers that and nothing more. Overlap is not transmission.',F['note'],nx0+40,yy,nx1-nx0-80,44,MUTE)

# ───────────── TIMELINE
ty=4330
d.rectangle([M,ty,W-M,ty+6],fill=INK); ty+=44
d.text((M,ty),'THE OVERLAP',font=F['sec'],fill=INK); ty+=118
para('Each bar is one life. The shaded column is the Orange County cattle-fever quarantine era. Read down its left '
     'edge to see who was already alive; read right to see how far each of those lives carried forward.',
     F['lead'],M,ty,W-2*M,48,MUTE)

X0=M+820; X1=W-M-150; Y0=4680; Y1=5590
YR0,YR1=1820,2030
def px(yr): return X0+(yr-YR0)/(YR1-YR0)*(X1-X0)
d.rectangle([px(1907),Y0-86,px(1915),Y1+30],fill=(140,58,43,40))
for e in (1907,1915): d.line([(px(e),Y0-86),(px(e),Y1+30)],fill=OX,width=4)
d.text((px(1907)+16,Y0-132),'QUARANTINE / DIPPING ERA  1907–1915',font=F['lab'],fill=OX)
for yr in range(1820,2031,20):
    d.line([(px(yr),Y0-50),(px(yr),Y1+6)],fill=(201,196,184,110),width=2)
    ctr(str(yr),F['yr'],px(yr),Y1+22,MUTE)

PEOPLE=[('Richard O’Neill Sr.','1824 – 1910',1824,1910,'bought in 1882; half owner 1906/07',True),
 ('Alice O’Neill','1823 – 1916',1823,1916,'',False),
 ('Jerome O’Neill','1861 – 1926',1861,1926,'owner and operator through the entire quarantine',True),
 ('Richard O’Neill Jr.','1863 – 1943',1863,1943,'forty-five in 1908  ·  lived seventeen years past Jerome',True),
 ('Marguerite “Daisy” O’Neill','1879 – 1981',1879,1981,'married in 1916  ·  ran the ranch from 1943  ·  102 years',True),
 ('Alice O’Neill Avery','1917 – 2014',1917,2014,'recorded on tape 1993–94  ·  97 years',True),
 ('Richard J. “Dick” O’Neill','1923 – 2009',1923,2009,'',False),
 ('Anthony R. Moiso','born c. 1939–40',1940,2026,'living',True),
 ('J. Jerome Moiso','1941 – 2024',1941,2024,'',False)]
rh=(Y1-Y0)/len(PEOPLE)
for i,(nm,dt,s,e,note,key) in enumerate(PEOPLE):
    cy=Y0+rh*i+rh/2
    d.text((M,cy-44),nm,font=F['tlname'] if key else F['tlname_s'],fill=INK if key else MUTE)
    d.text((M,cy+6),dt,font=F['small'],fill=MUTE)
    bh=32 if key else 24; col=INK if key else (152,154,150)
    d.rounded_rectangle([px(s),cy-bh/2,px(e),cy+bh/2],bh/2,fill=col)
    if e>=2026: d.polygon([(px(e),cy-bh),(px(e)+48,cy),(px(e),cy+bh)],fill=col)
    if note: d.text((px(e)+(66 if e>=2026 else 22),cy-15),note,font=F['small'],fill=MUTE)

EV=[(1882,'1882 — the purchase',0),(1910,'1910 — county quarantine',3),
    (1912,'1912 — partial release keeps T6S R7W',4),
    (1915,'1915 — Orange County still named',5),(1926,'1926 — Jerome and J. L. Flood die',2),
    (1963,'1963 — 11,000 acres opened',2),(1995,'1995 — EIR 555 certified',3),(2004,'2004 — Ranch Plan approved',4)]
ey=Y1+62
for yr,lab,slot in EV:
    d.line([(px(yr),Y0-86),(px(yr),ey+12)],fill=(31,78,121,85),width=3)
    d.ellipse([px(yr)-9,ey+4,px(yr)+9,ey+22],fill=BLUE)
    d.text((px(yr)+16,ey+40+slot*40),lab,font=F['evt'],fill=BLUE)
d.line([(px(1908),Y0-86),(px(1908),ey+12)],fill=(140,58,43,200),width=5)
d.ellipse([px(1908)-13,ey+0,px(1908)+13,ey+26],fill=OX)
d.text((px(1908)+20,ey+38),'1 SEPTEMBER 1908 — THE PRESS REPORTS CATTLE ON THE',font=F['lab2'],fill=OX)
d.text((px(1908)+20,ey+74),'THREE O’NEILL RANCHES GOING THROUGH THE TICK DIP',font=F['lab2'],fill=OX)

# ───────────── reading
ry=ey+280
d.rectangle([M,ry,W-M,ry+6],fill=INK); ry+=42
d.text((M,ry),'WHAT THE OVERLAP SHOWS — AND WHAT IT DOES NOT',font=F['sec'],fill=INK); ry+=118
CW=(W-2*M-180)/3
def col(x,head,tone,body):
    d.text((x,ry),head,font=F['lab'],fill=tone)
    yy=ry+52
    for p in body: yy=para(p,F['note'],x,yy,CW,44)+14
    return yy
y1=col(M,'THE CHAIN OF LIVING MEMORY WAS NOT BROKEN',OX,[
 'This project previously recorded that the memory chain broke in 1926, when Jerome O’Neill and James L. Flood died within two days of each other, and stayed broken through thirty-seven years of bank trusteeship.',
 'That is true of the COMPANY. It is not true of the FAMILY.',
 'Richard O’Neill Jr. was forty-five in 1908 and lived to 1943. His wife Daisy lived to 1981. Their daughter Alice lived to 2014. Tony Moiso overlapped Daisy by about forty years and Alice by seventy-five.',
 'Four lives. Three handoffs. No gap anywhere in the line.'])
y2=col(M+CW+90,'BUT OVERLAP IS NOT TRANSMISSION',INK,[
 'People who share a house do not necessarily share what they know. A state dipping order was routine compliance, not a family story. It sat alongside thistles, drought, rustlers and fire.',
 'The company’s own printed history of 1992, describing exactly Jerome O’Neill’s years, says only that “Nature sent him a host of problems — everything from thistles to ticks.” That one word is the whole of it. No dipping, no vats, no arsenic, no quarantine.',
 'Nothing in this project establishes that anyone in this family ever discussed dipping with anyone else in it.'])
y3=col(M+2*(CW+90),'AND THERE IS A TAPE',BLUE,[
 'Alice O’Neill Avery sat for six recorded interviews with the company’s own historian between December 1993 and August 1994. She was born in 1917, two years after the last proclamation naming Orange County, into a household that had lived through all of it.',
 'Those recordings are in the Jim Sleeper papers, MS-R173, Special Collections and Archives, UC Irvine Libraries, Box 106. The finding aid states: “The collection is open for research.”',
 'That is the most direct surviving route to an answer, and no one on this project has listened to them.'])

fy=max(y1,y2,y3)+40
d.rectangle([M,fy,W-M,fy+3],fill=RULE); fy+=28
d.text((M,fy),'SOURCES AND GRADES',font=F['lab'],fill=MUTE); fy+=44
fy=para('Life dates and titles: obituaries, the National Register nomination for the Santa Margarita Ranch House (1971), the Santa Margarita Company’s own printed history (© 1992), Orange County Clerk-Recorder '
 'index entries, California Secretary of State registry records retrieved via mirrors, and Rancho Mission Viejo’s published leadership pages. Quarantine dates: Governor’s proclamations and California State Veterinarian '
 'biennial reports held by this project. The 1 September 1908 report: Los Angeles Herald, page 6, Library of Congress LCCN sn85042462. Conflicts recorded in the full ownership audit rather than smoothed over here: '
 'Richard O’Neill Sr.’s birthplace and his wife’s name; the year of the half-interest conveyance; the year the ranch was divided; Anthony R. Moiso’s exact year of birth.',
 F['tiny'],M,fy,W-2*M,32,MUTE)
fy+=24
d.rounded_rectangle([M,fy,W-M,fy+128],10,fill=(255,255,255,210),outline=RULE,width=3)
para('This chart is part of an independent research and data-organization project. It does not provide medical advice and does not establish that any pesticide, property, organization, employer, school, water provider, '
 'government agency or other party caused any illness. It does not establish that a cattle-dipping vat exists or ever existed on this land, that any person named here knew of one, or that anyone failed in any duty. '
 'Geographic and temporal overlap does not establish exposure or causation.',F['tiny'],M+32,fy+24,W-2*M-64,32,MUTE)
d.rectangle([M,H-M-6,W-M,H-M],fill=INK)
print('content ends at',fy+128,'of',H-M)
img.save('/Users/andystavros/Desktop/ONeill_Family_Tree_24x36.png',dpi=(DPI,DPI))
img.convert('RGB').save('/Users/andystavros/Desktop/ONeill_Family_Tree_24x36.pdf','PDF',resolution=DPI)
img.resize((W//4,H//4),Image.LANCZOS).save('/Users/andystavros/Desktop/ONeill_Family_Tree_preview.png')
print('saved',img.size)
