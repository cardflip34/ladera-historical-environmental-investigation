import json, re, sys
from full_script import BLOCKS, ORDER
starts=json.load(open("../p2/starts_full.json"))["starts"]
NB={"OPEN":"INTRO","THREAT":"THREAT","FL":"FL","1":"REEL","1b":"REEL","2":"EXPL","3":"B","4":"C","TS":"TS","PD":"PD","TR":"TR","5":"D","P3":"P3","6":"CLOSE"}
words=json.load(open("uk_words.json")); norm=lambda x:re.sub(r"[^a-z0-9]","",x.lower().replace("ladaira","ladera"))
cues=[]
for k in ORDER:
    off=starts[NB[k]]+(57.6 if k=="1b" else 0.8); toks=re.findall(r"\S+",BLOCKS[k]); ws=words[k]; j=0; items=[]
    for a,b,w in ws:
        tw=norm(w); acc=""; got=[]
        while j<len(toks) and len(acc)<len(tw): acc+=norm(toks[j]); got.append(toks[j]); j+=1
        if acc!=tw: got=[w.replace("Ladaira","Ladera")]
        items.append((a,b," ".join(got)))
    chunk=[]; t0=None
    for a,b,tok in items:
        if t0 is None: t0=a
        chunk.append(tok); text=" ".join(chunk)
        if tok[-1] in ".:;?!" or len(chunk)>=9 or (tok[-1]=="," and len(chunk)>=5) or len(text)>44: cues.append((off+t0,off+b,text)); chunk=[]; t0=None
    if chunk: cues.append((off+t0,off+items[-1][1]," ".join(chunk)))
fixed=[]
for i,(a,b,t) in enumerate(cues):
    b=max(b,a+0.9)
    if i+1<len(cues): b=min(b,cues[i+1][0]-0.05)
    fixed.append((a,b,t))
ts=lambda s:f"{int(s//3600)}:{int(s%3600//60):02d}:{s%60:05.2f}"
ass=["[Script Info]","ScriptType: v4.00+","PlayResX: 1080","PlayResY: 1920","WrapStyle: 0","","[V4+ Styles]","Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding","Style: Cap,Arial,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H88000000,-1,0,0,0,100,100,0,0,3,4,0,8,50,50,230,1","","[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for a,b,t in fixed: ass.append(f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{t}")
open("captions_full.ass","w").write("\n".join(ass)+"\n")
ts2=lambda s:f"{int(s//3600):02d}:{int(s%3600//60):02d}:{int(s%60):02d},{int(round((s%1)*1000)):03d}"
open("captions_full.srt","w").write("\n".join(f"{i+1}\n{ts2(a)} --> {ts2(b)}\n{t}\n" for i,(a,b,t) in enumerate(fixed)))
print("cues",len(fixed),"first",fixed[0])
