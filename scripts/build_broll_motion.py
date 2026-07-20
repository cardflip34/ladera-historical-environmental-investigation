#!/usr/bin/env python3
"""Generate vertical (1080x1920) B-roll motion clips for the Instagram cut.

Outputs five self-contained MP4s to docs/outreach/broll/motion/. No external footage — the
aerials are this project's own public-record data; the graphics are drawn from verified figures
in the report. Design tokens match the publication (navy ground, brass + cyan accents).
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio.v2 as imageio

Image.MAX_IMAGE_PIXELS = None
ROOT = "/Users/andystavros/Ladera-Ranch"
AER = os.path.join(ROOT, "research/historical_imagery/oc_aerials")
OUT = os.path.join(ROOT, "docs/outreach/broll/motion")
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1920
FPS = 30

BG      = (11, 15, 22)
PANEL   = (19, 26, 36)
INK     = (233, 230, 224)
DIM     = (150, 168, 184)
BRASS   = (200, 169, 81)
CYAN    = (79, 195, 232)
WATER   = (107, 169, 196)
GREEN   = (95, 179, 122)
RED     = (196, 117, 107)
WHITE   = (255, 255, 255)

FSUP = "/System/Library/Fonts/Supplemental/Arial.ttf"
FBLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def font(sz, bold=True):
    try:
        return ImageFont.truetype(FBLD if bold else FSUP, sz)
    except Exception:
        return ImageFont.load_default()


def ease(t):                       # smoothstep
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def frame(color=BG):
    return Image.new("RGB", (W, H), color)


def ctext(dr, cx, y, s, f, fill, ls=0, anchor="mm"):
    if ls == 0:
        dr.text((cx, y), s, font=f, fill=fill, anchor=anchor)
        return
    # manual letter-spacing, centered
    widths = [dr.textlength(ch, font=f) for ch in s]
    total = sum(widths) + ls * (len(s) - 1)
    x = cx - total / 2
    for ch, wd in zip(s, widths):
        dr.text((x, y), ch, font=f, fill=fill, anchor="lm")
        x += wd + ls


def vignette(im, strength=0.55):
    a = np.asarray(im).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    m = np.clip(1 - strength * np.clip(d - 0.6, 0, 1), 0, 1)[..., None]
    return Image.fromarray((a * m).astype(np.uint8))


def writer(name):
    return imageio.get_writer(os.path.join(OUT, name), fps=FPS, codec="libx264",
                              quality=8, macro_block_size=1, ffmpeg_log_level="error")


def load_vertical(path):
    """Center-crop a source image to 9:16 and return a large RGB array to Ken-Burns from."""
    im = Image.open(path).convert("RGB")
    iw, ih = im.size
    tar = W / H
    if iw / ih > tar:
        nw = int(ih * tar); im = im.crop(((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih))
    else:
        nh = int(iw / tar); im = im.crop((0, (ih - nh) // 2, iw, (ih - nh) // 2 + nh))
    return im.resize((int(W * 1.15), int(H * 1.15)), Image.LANCZOS)


def kenburns(base, z0, z1, t):
    """Return a 1080x1920 crop from an oversized base, scaling z0->z1 across t."""
    z = z0 + (z1 - z0) * t
    bw, bh = base.size
    cw, ch = int(W / z * (bw / (W * 1.15))), int(H / z * (bh / (H * 1.15)))
    cw, ch = min(cw, bw), min(ch, bh)
    x = (bw - cw) // 2; y = (bh - ch) // 2
    return base.crop((x, y, x + cw, y + ch)).resize((W, H), Image.LANCZOS)


def darken(im, f):
    return Image.blend(im, Image.new("RGB", im.size, (0, 0, 0)), f)


def lower_gradient(im, h=460):
    g = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    for i in range(h):
        gd.line([(0, i), (W, i)], fill=(6, 10, 16, int(215 * (i / h))))
    im = im.convert("RGBA"); im.paste(g, (0, H - h), g)
    return im.convert("RGB")


# ─────────────────────────────────────────────────────────────── CLIP 1
def clip_dissolve():
    a = load_vertical(os.path.join(AER, "1937.jpg"))
    b = load_vertical(os.path.join(AER, "2022_modern.jpg"))
    fA, fld, fB = 66, 54, 84                      # frames: hold A, crossfade, hold B  (~6.8s)
    total = fA + fld + fB
    fT, fS = font(120), font(40, False)
    w = writer("01_dissolve_1937_2022.mp4")
    for i in range(total):
        t = i / total
        za = kenburns(a, 1.0, 1.12, t)
        zb = kenburns(b, 1.12, 1.0, t)
        if i < fA:
            im = za; year = "1937"; col = INK
        elif i < fA + fld:
            k = ease((i - fA) / fld)
            im = Image.blend(za, zb, k); year = "1937" if k < .5 else "2022"; col = INK
        else:
            im = zb; year = "2022"; col = INK
        im = lower_gradient(darken(im, 0.18))
        dr = ImageDraw.Draw(im, "RGBA")
        # year, big, top-left
        a_in = ease(min(1, i / 12))
        dr.text((70, 150), year, font=fT, fill=col + (int(255 * a_in),))
        if i >= fA + fld:
            k = ease(min(1, (i - fA - fld) / 20))
            ctext(dr, W / 2, H - 230, "THE SAME GROUND", font(52), WHITE + (int(255 * k),))
            ctext(dr, W / 2, H - 165, "open cattle ranch  ·  now 8,000 homes", fS, DIM + (int(255 * k),))
        w.append_data(np.asarray(im))
    w.close(); print("  01_dissolve_1937_2022.mp4")


# ─────────────────────────────────────────────────────────────── CLIP 2
def clip_gap():
    total = 205                                    # ~6.8s
    fSub = font(44, False)
    fLab = font(34)
    w = writer("02_forty_year_gap.mp4")
    x0, x1 = 120, W - 120
    y_dip, y_rev = 820, 1120
    top, bot = 720, 1300
    def yx(yr):                                    # 1895..2005 across the bar
        return x0 + (x1 - x0) * (yr - 1895) / (2005 - 1895)
    for i in range(total):
        im = frame()
        dr = ImageDraw.Draw(im, "RGBA")
        ctext(dr, W / 2, 210, "WHAT THEY CHECKED", font(56), INK)
        ctext(dr, W / 2, 282, "vs. the years they were looking for", fSub, DIM)

        # 1) gap band FIRST, behind everything
        p3 = ease(max(0, min(1, (i - 115) / 55)))
        gx0, gx1 = yx(1912), yx(1952)
        if p3 > 0:
            band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(band).rectangle([gx0, top, gx1, bot], fill=BRASS + (int(34 * p3),))
            im = Image.alpha_composite(im.convert("RGBA"), band).convert("RGB")
            dr = ImageDraw.Draw(im, "RGBA")
            for gx in (gx0, gx1):
                dr.line([(gx, top), (gx, bot)], fill=BRASS + (int(210 * p3),), width=3)

        # 2) axis
        dr.line([(x0, bot), (x1, bot)], fill=PANEL, width=4)
        for yr in (1900, 1920, 1940, 1960, 1980, 2000):
            xx = yx(yr)
            dr.line([(xx, bot - 8), (xx, bot + 8)], fill=DIM, width=3)
            ctext(dr, xx, bot + 44, str(yr), fLab, DIM)

        # 3) bars on top
        p1 = ease(min(1, i / 45))
        dxs, dxe = yx(1907), yx(1912)
        dr.rounded_rectangle([dxs, y_dip, dxs + max(6, (dxe - dxs)) * p1, y_dip + 84], 8, fill=RED)
        if p1 > .6:
            a1 = int(255 * ease((p1 - .6) / .4))
            dr.text((dxs, y_dip - 44), "ARSENIC DIPPING", font=font(34), fill=RED + (a1,), anchor="lm")
            dr.text((dxe + 20, y_dip + 42), "ends 1912", font=fLab, fill=WHITE + (a1,), anchor="lm")
        p2 = ease(max(0, min(1, (i - 55) / 45)))
        rxs, rxe = yx(1952), yx(1999)
        dr.rounded_rectangle([rxs, y_rev, rxs + (rxe - rxs) * p2, y_rev + 84], 8, fill=WATER)
        if p2 > .6:
            a2 = int(255 * ease((p2 - .6) / .4))
            dr.text((rxs, y_rev - 44), "ENVIRONMENTAL REVIEW", font=font(34), fill=WATER + (a2,), anchor="lm")
            dr.text((rxs, y_rev + 42), "starts 1952", font=fLab, fill=WHITE + (a2,), anchor="lm")

        # 4) payoff
        if p3 > 0:
            ctext(dr, (gx0 + gx1) / 2, 1520, "40 YEARS", font(140), BRASS + (int(255 * p3),))
            ctext(dr, W / 2, 1650, "the window nobody looked at", fSub, INK + (int(255 * p3),))
        w.append_data(np.asarray(im))
    w.close(); print("  02_forty_year_gap.mp4")


# ─────────────────────────────────────────────────────────────── CLIP 3
def clip_dust():
    total = 210                                    # ~7s
    rng = np.random.default_rng(7)
    ground = 1200
    # particles seeded once
    P = 90
    px = rng.uniform(0, W, P); py = rng.uniform(ground - 10, ground + 10, P)
    pv = rng.uniform(0.4, 1.6, P); pph = rng.uniform(0, 2 * math.pi, P)
    fLab = font(46, False)
    w = writer("03_point_source_dust.mp4")
    for i in range(total):
        im = frame()
        dr = ImageDraw.Draw(im, "RGBA")
        ctext(dr, W / 2, 210, "HOW A SMALL SPOT SPREADS", font(52), INK)
        # ground line
        dr.line([(0, ground), (W, ground)], fill=PANEL, width=5)
        # phase 1 (0-.28): a single concentrated dot
        # phase 2 (.28-.55): grading spreads it into a wide thin band
        # phase 3 (.55-1): dust rises
        t = i / total
        spread = ease(max(0, min(1, (t - .28) / .27)))
        cx = W / 2
        band_w = 60 + spread * (W - 180)
        # the contamination band
        for s in range(60):
            xx = cx - band_w / 2 + band_w * s / 59
            h = (14 + 26 * (1 - spread)) * (0.5 + 0.5 * math.cos((s / 59 - .5) * math.pi))
            aa = int(200 * (1 - .45 * spread))
            dr.line([(xx, ground), (xx, ground - h)], fill=RED + (aa,), width=int(band_w / 60) + 2)
        if t < .30:
            k = ease(min(1, i / 18))
            ctext(dr, cx, ground - 150, "a dip vat", fLab, RED + (int(255 * k),))
            ctext(dr, cx, ground - 95, "the size of a garage", font(34, False), DIM + (int(255 * k),))
        # grading label
        if .26 < t < .60:
            k = ease(min(1, (t - .26) / .12)) * (1 - ease(max(0, (t - .52) / .08)))
            ctext(dr, cx, ground + 90, "GRADING  ·  cut and spread", font(40), BRASS + (int(255 * k),))
        # phase 3: dust
        if t > .5:
            df = ease((t - .5) / .5)
            for j in range(P):
                life = (i * pv[j] * 1.2) % 260
                yy = ground - life * (0.7 + spread) - 4
                if yy < 250: continue
                drift = math.sin(pph[j] + i * 0.05) * 30 * df
                xx = px[j] + drift
                fade = max(0, 1 - life / 260)
                r = 3 + 5 * (1 - fade)
                dr.ellipse([xx - r, yy - r, xx + r, yy + r],
                           fill=(200, 180, 150, int(120 * fade * df)))
            k = ease(min(1, (t - .55) / .25))
            ctext(dr, W / 2, 470, "spread thin, then airborne", font(44), INK + (int(255 * k),))
            ctext(dr, W / 2, 540, "breathed in. carried on the wind.", font(34, False),
                  DIM + (int(255 * k),))
        im = vignette(im, 0.4)
        w.append_data(np.asarray(im))
    w.close(); print("  03_point_source_dust.mp4")


# ─────────────────────────────────────────────────────────────── CLIP 4
def clip_map():
    total = 210                                    # ~7s
    cx, cy = W / 2, 1120
    ppm = 42.0                                     # px per mile (near sites to scale)
    r5 = 5 * ppm                                   # 5-mile ring = 210 px
    CAPR = 700                                     # far sites capped at this radius, with arrow
    sites = [                                       # name, miles, bearing(deg from N), appear-frame
        ("Capistrano", 3.4, 200, 45),
        ("Trabuco Cyn", 8.4, 40, 80),
        ("Santa Ana Cyn", 22.8, 8, 115),
        ("Yorba", 25.6, 335, 150),
    ]
    fT = font(46); fLab = font(34); fD = font(30, False)
    w = writer("04_dip_sites_map.mp4")
    for i in range(total):
        im = frame()
        dr = ImageDraw.Draw(im, "RGBA")
        ctext(dr, W / 2, 175, "WHERE DIPPING IS DOCUMENTED", fT, INK)
        ctext(dr, W / 2, 235, "Orange County, 1908", fD, DIM)
        # 5-mile ring (reference)
        ra = ease(min(1, i / 25))
        dr.ellipse([cx - r5, cy - r5, cx + r5, cy + r5], outline=CYAN + (int(130 * ra),), width=3)
        dr.text((cx + r5 * 0.7, cy - r5 * 0.7 - 8), "5-mi ring", font=fD,
                fill=CYAN + (int(170 * ra),), anchor="lm")
        # community center
        dr.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=CYAN, outline=WHITE, width=3)
        ctext(dr, cx, cy + 48, "LADERA RANCH", font(30), WHITE)
        for name, miles, brg, af in sites:
            k = ease(max(0, min(1, (i - af) / 22)))
            if k <= 0: continue
            ang = math.radians(brg)
            true_r = miles * ppm
            rr = min(true_r, CAPR)
            capped = true_r > CAPR
            sx = cx + rr * math.sin(ang); sy = cy - rr * math.cos(ang)
            dr.line([(cx, cy), (sx, sy)], fill=(90, 64, 60, int(150 * k)), width=2)
            dr.ellipse([sx - 12, sy - 12, sx + 12, sy + 12], fill=RED + (int(255 * k),),
                       outline=WHITE + (int(255 * k),), width=2)
            right = math.sin(ang) >= 0
            lx = sx + (34 if right else -34); an = "lm" if right else "rm"
            arrow = "  »" if capped else ""
            dr.text((lx, sy - 13), name, font=fLab, fill=INK + (int(255 * k),), anchor=an)
            dr.text((lx, sy + 15), f"{miles} mi{arrow}", font=fD,
                    fill=(DIM if not capped else BRASS) + (int(255 * k),), anchor=an)
        p = ease(max(0, min(1, (i - 165) / 40)))
        if p > 0:
            im = lower_gradient(im, 380)
            dr = ImageDraw.Draw(im, "RGBA")
            ctext(dr, W / 2, H - 250, "NONE OF THEM IS HERE", font(58), WHITE + (int(255 * p),))
            ctext(dr, W / 2, H - 172, "nearest is 3.4 miles away · none is this ranch",
                  fD, DIM + (int(255 * p),))
        w.append_data(np.asarray(im))
    w.close(); print("  04_dip_sites_map.mp4")


# ─────────────────────────────────────────────────────────────── CLIP 5
def clip_arsenic():
    total = 175                                    # ~5.8s
    cx = W / 2
    box = 460; bx, by = cx - box / 2, 430
    w = writer("05_arsenic_card.mp4")
    for i in range(total):
        im = frame()
        dr = ImageDraw.Draw(im, "RGBA")
        # periodic cell
        ap = ease(min(1, i / 22))
        col = tuple(int(BG[j] + (BRASS[j] - BG[j]) * 1) for j in range(3))
        dr.rounded_rectangle([bx, by, bx + box, by + box], 24,
                             outline=BRASS + (int(255 * ap),), width=6)
        dr.text((bx + 34, by + 26), "33", font=font(70), fill=DIM + (int(255 * ap),), anchor="lm")
        dr.text((bx + box - 34, by + 26), "74.92", font=font(40, False),
                fill=DIM + (int(255 * ap),), anchor="rm")
        if ap > .5:
            k = ease((ap - .5) / .5)
            ctext(dr, cx, by + box / 2 + 10, "As", font(240), INK + (int(255 * k),))
            ctext(dr, cx, by + box - 60, "ARSENIC", font(46), BRASS + (int(255 * k),), ls=8)
        # lines reveal
        def line(y, s, f, fill, start):
            k = ease(max(0, min(1, (i - start) / 20)))
            if k > 0:
                ctext(dr, cx, y, s, f, tuple(fill) + (int(255 * k),))
        line(1120, "An element.", font(64), INK, 55)
        line(1210, "It does not break down.", font(64), INK, 78)
        line(1380, "Pesticides fade over the years.", font(42, False), DIM, 110)
        line(1445, "Arsenic doesn't.", font(42, False), DIM, 125)
        line(1600, "Put in the ground in 1910 —", font(46), BRASS, 145)
        line(1665, "in mass, still there today.", font(46), BRASS, 152)
        w.append_data(np.asarray(im))
    w.close(); print("  05_arsenic_card.mp4")


if __name__ == "__main__":
    print("Rendering vertical B-roll (1080x1920)...")
    clip_dissolve()
    clip_gap()
    clip_dust()
    clip_map()
    clip_arsenic()
    print("Done ->", OUT)
