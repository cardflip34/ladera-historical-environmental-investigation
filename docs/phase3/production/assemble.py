#!/usr/bin/env python3
"""Concatenate Phase 3 segments, lay narration under them, add music bed with ducking."""
import os,sys,json,subprocess,re
HERE=os.path.dirname(os.path.abspath(__file__))
SEG=HERE+"/seg"; NAR=HERE+"/nar"; OUT=HERE+"/out"; os.makedirs(OUT,exist_ok=True)
SEGS=[("01_open","OPEN"),("02_p1","P1TITLE"),("03_whatisvat","S2"),("04_sweep","S3"),
 ("05_trw","S4"),("06_quest","S5"),("07_kino","S6"),("08_ladera02","S7"),("09_cond22","S8"),
 ("10_p1map","S9"),("11_p2","P2TITLE"),("12_farm","S10"),("13_grading","S11"),("14_cols","S12"),
 ("15_targets","S13"),("16_control","S14"),("17_methods","S15"),("18_p3","P3TITLE"),
 ("19_twosys","S16"),("20_route","S17"),("21_blend","S18"),("22_tested","S19"),
 ("23_audit","S20"),("24_pest","S21"),("25_network","S22"),("26_layers","S23"),("27_end","END")]
def dur(p):
    o=subprocess.run(["ffmpeg","-i",p],capture_output=True,text=True).stderr
    m=re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)',o)
    return int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3)) if m else 0.0
def main():
    missing=[s for s,_ in SEGS if not os.path.exists(f"{SEG}/{s}.mp4")]
    if missing: print("MISSING:",missing); return 1
    # 1) concat video
    with open(OUT+"/list.txt","w") as f:
        for s,_ in SEGS: f.write("file '%s/%s.mp4'\n"%(SEG,s))
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",OUT+"/list.txt",
                    "-c","copy",OUT+"/video.mp4"],check=True)
    vd=dur(OUT+"/video.mp4"); print("video %.1fs = %d:%02d"%(vd,vd//60,vd%60))
    # 2) narration track: place each block at its segment start + lead-in
    starts={}; t=0.0
    for s,k in SEGS:
        starts[k]=t; t+=dur(f"{SEG}/{s}.mp4")
    LEAD=0.45
    ins=[]; filt=[]
    for i,(s,k) in enumerate(SEGS):
        ins += ["-i", f"{NAR}/{k}.mp3"]
        filt.append("[%d:a]adelay=%d|%d[a%d]"%(i+1,int((starts[k]+LEAD)*1000),int((starts[k]+LEAD)*1000),i))
    mix="".join("[a%d]"%i for i in range(len(SEGS)))
    filt.append("%samix=inputs=%d:normalize=0:dropout_transition=0[nar]"%(mix,len(SEGS)))
    cmd=["ffmpeg","-y","-loglevel","error","-i",OUT+"/video.mp4"]+ins+[
         "-filter_complex",";".join(filt),"-map","0:v","-map","[nar]",
         "-c:v","copy","-c:a","aac","-b:a","192k","-shortest",OUT+"/voice.mp4"]
    subprocess.run(cmd,check=True)
    print("narration laid ->",OUT+"/voice.mp4", "%.1fs"%dur(OUT+"/voice.mp4"))
    json.dump(starts,open(OUT+"/starts.json","w"),indent=1)
if __name__=="__main__": sys.exit(main() or 0)
