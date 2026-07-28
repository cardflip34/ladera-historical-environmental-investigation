#!/usr/bin/env python3
"""
Mission 7 - assemble the Landsat time-lapse into a video.

Reads timelapse_manifest.json and uses ONLY the frames in videoSequence, so the smoke-contaminated
2003-10-25 frame is excluded automatically rather than by hand.

Every frame carries its own date, a timeline bar showing true position in time (frame spacing is
uneven because cloudy months are absent), and the standing caveats. Nothing is added in post, so the
video cannot circulate without its own limitations.

Outputs:
  ladera_timelapse_1997_2006.mp4   1080x1080, ~7 fps
  ladera_timelapse_1997_2006.gif   smaller, for messaging apps
"""
from __future__ import annotations
import json, os, glob, datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio.v2 as imageio

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "evidence/lhdrs/mission7")
FR = os.path.join(OUT, "timelapse_frames")
man = json.load(open(os.path.join(OUT, "timelapse_manifest.json")))
seq = man["videoSequence"]
excluded = [f["date"] for f in man["frames"] if f.get("qaFlag") != "ok"]
print(f"{len(seq)} frames in sequence; {len(excluded)} excluded ({', '.join(excluded) or 'none'})")

SIZE = 1080
MAP = 820                      # map area
FD = "/System/Library/Fonts/Supplemental/"


def F(s, b=False):
    p = FD + ("Arial Bold" if b else "Arial") + ".ttf"
    return ImageFont.truetype(p, s) if os.path.exists(p) else ImageFont.load_default()


NAVY = (16, 22, 34); PAPER = (246, 245, 242); MUT = (150, 156, 168); ACC = (214, 138, 70)


def to_dec(d):
    y, m = int(d[:4]), int(d[5:7])
    return y + (m - 0.5) / 12.0


T0, T1 = 1997.0, 2007.0


def compose(path, date, idx, total):
    src = Image.open(path).convert("RGB")
    src = src.crop((0, 0, src.width, src.height - 34))          # drop the small label bar
    src = src.resize((MAP, MAP), Image.LANCZOS)
    im = Image.new("RGB", (SIZE, SIZE), NAVY)
    im.paste(src, ((SIZE - MAP) // 2, 96))
    d = ImageDraw.Draw(im)

    d.text((36, 26), "Ladera Ranch", font=F(40, True), fill=(255, 255, 255))
    d.text((36, 74), "Landsat true colour, 6 km square", font=F(17), fill=MUT)
    # big date, right aligned
    d.text((SIZE - 36, 30), date[:7], font=F(48, True), fill=ACC, anchor="ra")
    d.text((SIZE - 36, 84), date, font=F(16), fill=MUT, anchor="ra")

    # timeline bar - true position in time, not frame index
    bx0, bx1, by = 36, SIZE - 36, 96 + MAP + 30
    d.line([bx0, by, bx1, by], fill=(60, 68, 84), width=3)
    for yr in range(1997, 2008):
        x = bx0 + (bx1 - bx0) * (yr - T0) / (T1 - T0)
        d.line([x, by - 7, x, by + 7], fill=(90, 100, 118), width=2)
        if yr % 2 == 1:
            d.text((x, by + 12), str(yr), font=F(14), fill=MUT, anchor="ma")
    # tick for every frame actually present, so gaps are visible
    for s in seq:
        x = bx0 + (bx1 - bx0) * (to_dec(s) - T0) / (T1 - T0)
        d.line([x, by - 3, x, by + 3], fill=(120, 132, 152), width=1)
    px = bx0 + (bx1 - bx0) * (to_dec(date) - T0) / (T1 - T0)
    d.ellipse([px - 8, by - 8, px + 8, by + 8], fill=ACC)

    d.text((36, SIZE - 62), "30 m pixels: grading and roads visible, individual houses are not.",
           font=F(15), fill=(176, 182, 194))
    d.text((36, SIZE - 40), "Ground conditions only. Not a contamination, dust or exposure product.",
           font=F(15), fill=(176, 182, 194))
    d.text((SIZE - 36, SIZE - 51), "Landsat 5/7 · USGS/NASA · A+", font=F(14), fill=MUT, anchor="ra")
    return np.asarray(im)


# ---- title card
def card(lines, sub=None, hold=1):
    im = Image.new("RGB", (SIZE, SIZE), NAVY)
    d = ImageDraw.Draw(im)
    y = 360
    for t, s, b in lines:
        d.text((SIZE // 2, y), t, font=F(s, b), fill=(255, 255, 255), anchor="ma")
        y += int(s * 1.5)
    if sub:
        y += 20
        for t in sub:
            d.text((SIZE // 2, y), t, font=F(17), fill=MUT, anchor="ma")
            y += 30
    return [np.asarray(im)] * hold


frames = []
frames += card([("Ladera Ranch", 62, True), ("1997 to 2006", 34, False)],
               ["Monthly satellite record of construction",
                f"{len(seq)} cloud-free Landsat frames"], hold=14)

for i, dt in enumerate(seq):
    g = glob.glob(os.path.join(FR, f"*_{dt}.png"))
    if not g:
        continue
    frames.append(compose(g[0], dt, i, len(seq)))

frames += card([("Ground disturbance peaked", 34, False), ("in 2002", 58, True)],
               ["Built from free USGS/NASA Landsat imagery",
                "Individual houses are not resolvable at 30 m",
                "This shows ground conditions only"], hold=16)

print(f"composed {len(frames)} frames")
mp4 = os.path.join(OUT, "ladera_timelapse_1997_2006.mp4")
imageio.mimsave(mp4, frames, fps=7, quality=9, macro_block_size=1)
print("wrote", mp4, f"{os.path.getsize(mp4)/1e6:.1f} MB")

gif = os.path.join(OUT, "ladera_timelapse_1997_2006.gif")
small = [np.asarray(Image.fromarray(f).resize((540, 540), Image.LANCZOS)) for f in frames]
imageio.mimsave(gif, small, duration=0.14, loop=0)
print("wrote", gif, f"{os.path.getsize(gif)/1e6:.1f} MB")
