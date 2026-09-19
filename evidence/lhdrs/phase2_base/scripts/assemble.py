#!/usr/bin/env python3
"""Phase 2 BASE assembly. usage: assemble.py <voice_prefix n|uk|el> <outname>"""
import subprocess, sys, re, os, json
V=sys.argv[1] if len(sys.argv)>1 else "n"; OUTN=sys.argv[2] if len(sys.argv)>2 else "Ladera_Phase2_BASE"
HERE=os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
NAR="../p2src"; DOC="../doc"; S="seg"
VO="video_full.mp4" if "--full" in sys.argv else "video_only.mp4"
def dur(f):
    o=subprocess.run(["ffmpeg","-i",f],capture_output=True,text=True).stderr; m=re.search(r"Duration: (\d+):(\d+):([\d.]+)",o)
    return int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3))
FULL="--full" in sys.argv
SEGS=([("OPENMAP",f"{S}/open.mp4")] if "--open" in sys.argv else [])+[("USER",f"{S}/user.mp4")]+([("INTRO",f"{S}/intro.mp4"),("THREAT",f"{S}/threat.mp4")] if FULL else [])+[("FL",f"{S}/fl.mp4"),("REEL",f"{S}/reel.mp4"),("EXPL",f"{DOC}/fA.mp4"),("B",f"{DOC}/fB.mp4"),("C",f"{DOC}/fC.mp4"),("TS",f"{S}/tire.mp4"),("PD",f"{S}/pond.mp4"),("TR",f"{S}/trail.mp4"),("D",f"{DOC}/fD_ext.mp4")]+([("P3",f"{S}/p3.mp4")] if FULL else [])+[("CLOSE",f"{S}/close.mp4")]
ST={}; T=0.0
with open("list_full.txt" if FULL else "list.txt","w") as L:
    for k,f in SEGS: L.write(f"file '{f}'\n"); ST[k]=round(T,3); T+=dur(f)
if not os.path.exists(VO) or "--rebuild" in sys.argv:
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",("list_full.txt" if FULL else "list.txt"),"-c","copy",VO],check=True)
TOT=dur(VO); print("total",TOT); json.dump({"starts":ST,"total":TOT},open("starts_full.json" if FULL else "starts.json","w"),indent=1)
for k,f in SEGS: print(f"{k:6s} {ST[k]:8.2f}  ({dur(f):.2f}s)")
ms=lambda s:int(s*1000)
NB=({"OPEN":"INTRO","THREAT":"THREAT"} if FULL else {})|{"1":"REEL","1b":"REEL","FL":"FL","2":"EXPL","3":"B","4":"C","TS":"TS","PD":"PD","TR":"TR","5":"D"}|({"P3":"P3"} if FULL else {})|{"6":"CLOSE"}
def mix(out,narr=True):
    inputs=["-i",f"{S}/user_audio.m4a","-i",f"{S}/reel_audio.m4a"]
    fc=f"[0:a]adelay={ms(ST['USER'])}|{ms(ST['USER'])}[ua];[1:a]volume={0.55 if narr else 0.7},adelay={ms(ST['REEL'])}|{ms(ST['REEL'])}[ra];"
    labels="[ua][ra]"; n=2
    if narr:
        for b,seg in NB.items():
            f=f"{NAR}/{V}_{b}.mp3"
            if not os.path.exists(f): f=f"{NAR}/n_{b}.mp3"
            off=57.6 if b=="1b" else 0.8; st=ST[seg]+off
            inputs+=["-i",f]; fc+=f"[{n}:a]adelay={ms(st)}|{ms(st)}[n{n}];"; labels+=f"[n{n}]"; n+=1
            print(f"  block {b:3s} <- {os.path.basename(f):12s} @ {st:7.2f}s")
    fc+=f"{labels}amix=inputs={n}:normalize=0,volume={1.3 if narr else 1.0},alimiter=limit=0.95,apad=whole_dur={TOT},afade=t=out:st={TOT-2.5}:d=2.5[aout]"
    subprocess.run(["ffmpeg","-y","-loglevel","error"]+inputs+["-filter_complex",fc,"-map","[aout]","-t",str(TOT),"-c:a","aac","-b:a","192k",out+".m4a"],check=True)
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",VO,"-i",out+".m4a","-map","0:v","-map","1:a","-c:v","copy","-c:a","copy","-shortest","-movflags","+faststart",out+".mp4"],check=True)
    print("wrote",out+".mp4",round(dur(out+".mp4"),2),"s")
mix(OUTN,True)
if "--nonarr" in sys.argv: mix(OUTN+"_NoNarration",False)
