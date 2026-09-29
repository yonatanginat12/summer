# -*- coding: utf-8 -*-
"""Amendments to the two covers Carmela asked to change.

Same pipeline as the original renders — four.py's helpers, same paper, same
grain — with four changes to טופס 17 (shorter table, titles higher, red line
centred on the handwriting, title smaller, ח redrawn) and the author's name
corrected on both.

The original called playwright to raster the handwriting; playwright's browser
isn't installed here, so that one step goes through Chrome's CLI instead. Same
viewport, same scale factor, same downsample.
"""
import pathlib, base64, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage

_src = pathlib.Path("four.py").read_text(encoding="utf-8")
exec(compile(_src[:_src.index("# ============================================================ 1.")],
             "helpers", "exec"), globals())

HANDF = base64.b64encode(pathlib.Path("fonts/GveretLevin.woff2").read_bytes()).decode()
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
AUTHOR = "כרמלה מרינגר-גינת"

# The font draws ח with a loop over its left shoulder that reads as a mark on
# the letter rather than as the letter. This is the same stroke without it:
# down the right side, over the top, down the left — plain cursive ח.
HET_SVG = ('<svg class="het" viewBox="0 0 100 104" preserveAspectRatio="xMidYMid meet">'
           '<path d="M88 96 L84 34 C82 14 64 6 44 10 C28 13 18 26 16 44 L10 96" '
           'fill="none" stroke="#000" stroke-width="12" '
           'stroke-linecap="round" stroke-linejoin="round"/></svg>')

def chrome_shot(html, png, w_css, h_css, scale):
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={w_css},{h_css}",
                    f"--force-device-scale-factor={scale}",
                    "--default-background-color=00000000",
                    "--virtual-time-budget=6000",
                    f"--screenshot={png}", f"file://{pathlib.Path(html).resolve()}"],
                   check=True, capture_output=True)

def handwriting(lines, name, fix_het=True):
    """Monoline handwriting mask — the same skeletonise-and-redraw as the original."""
    rows = ""
    for txt, t, s, r in lines:
        if fix_het and "ח" in txt:
            a, _, b = txt.partition("ח")
            inner = (f'<span>{a}</span>{HET_SVG}<span>{b}</span>')
            rows += (f'<div class="l row" style="top:{t:.2f}mm;font-size:{s}mm;'
                     f'transform:rotate({r}deg)">{inner}</div>')
        else:
            rows += (f'<div class="l" style="top:{t:.2f}mm;font-size:{s}mm;'
                     f'transform:rotate({r}deg)">{txt}</div>')
    html = f"""<!DOCTYPE html><html lang="he" dir="rtl"><head><meta charset="utf-8"><style>
@font-face{{font-family:H;src:url(data:font/woff2;base64,{HANDF}) format('woff2');font-display:block}}
*{{margin:0;padding:0}} html,body{{background:transparent;width:135mm;height:210mm}}
.b{{position:relative;width:135mm;height:210mm;overflow:hidden}}
.l{{position:absolute;text-align:center;left:0;right:0;font-family:H;color:#000;
   line-height:1;white-space:nowrap}}
.row{{display:flex;direction:rtl;justify-content:center;align-items:baseline}}
.het{{width:.60em;height:.78em;display:inline-block;vertical-align:baseline;
      margin:0 .012em;transform:translateY(.055em)}}
</style></head><body><div class="b">{rows}</div></body></html>"""
    src = f"_{name}.html"; png = f"_{name}.png"
    pathlib.Path(src).write_text(html, encoding="utf-8")
    chrome_shot(src, png, 510, 794, 3.1259)
    a = np.array(Image.open(png).split()[-1].resize((W, H)), np.float32) / 255

    def disk(r):
        k = np.arange(-r, r + 1)
        return (k[:, None] ** 2 + k[None, :] ** 2) <= r * r
    b_ = a > 0.5
    d = ndimage.distance_transform_edt(b_).astype(np.float32)
    ds = ndimage.gaussian_filter(d, 1.2)
    sk = b_ & (ds > ndimage.maximum_filter(ds, size=3) - 0.75) & (d > 1.5)
    sk = ndimage.binary_closing(sk, structure=disk(3))
    return ndimage.gaussian_filter(ndimage.binary_dilation(sk, structure=disk(3)).astype(np.float32), 0.6)

def seg(m, x0, y0, x1, y1, w=2.0):
    yy, xx = np.mgrid[0:H, 0:W]
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    t = np.clip(((xx - x0) * dx + (yy - y0) * dy) / max(L2, 1e-6), 0, 1)
    dist = np.hypot(xx - (x0 + t * dx), yy - (y0 + t * dy))
    m += np.clip(1 - (dist - w / 2) / 1.2, 0, 1)
    np.clip(m, 0, 1, out=m)
    return m

def rect(m, x0, y0, x1, y1, w=2.0):
    for a in ((x0, y0, x1, y0), (x0, y1, x1, y1), (x0, y0, x0, y1), (x1, y0, x1, y1)):
        seg(m, *a, w)
    return m

# ══════════════════════════════════════════════════ טופס 17, amended
def form17_v2(out="b2_form17_v2.png"):
    BG = np.array([0.9333, 0.9255, 0.8941], np.float32)
    IK = np.array([0.1451, 0.1608, 0.2078], np.float32)
    RD = np.array([0.7059, 0.1725, 0.1373], np.float32)
    img = np.ones((H, W, 3), np.float32) * BG
    form = np.zeros((H, W), np.float32)
    L, R_, T, B = W * 0.085, W * 0.915, H * 0.075, H * 0.90
    rect(form, L, T, R_, B, 3.0)
    seg(form, L, T + H * 0.062, R_, T + H * 0.062, 3.0)

    TABLE = [0.135, 0.187, 0.239, 0.291]          # was 0.135 → 0.345
    RULES = [0.430, 0.510, 0.590, 0.670, 0.750, 0.830]
    for y in TABLE + RULES:
        seg(form, L, H * y, R_, H * y, 1.6)
    for x in (0.34, 0.63):
        seg(form, W * x, H * TABLE[0], W * x, H * TABLE[-1], 1.6)
    seg(form, W * 0.40, H * 0.750, W * 0.40, H * 0.885, 1.6)
    img = img * (1 - (form * 0.55)[..., None]) + IK[None, None, :] * (form * 0.55)[..., None]

    lab = np.zeros((H, W), np.float32)
    for txt, xp, yp in (("שם המבוטחת", 88, 12.2), ("מספר זהות", 60, 12.2), ("תאריך", 30, 12.2),
                        ("סעיף", 88, 17.4), ("קוד", 60, 17.4), ("מוסד", 30, 17.4),
                        ("אבחנה", 88, 22.6), ("הפניה", 60, 22.6), ("תוקף", 30, 22.6),
                        ("פירוט", 88, 31.5), ("חתימת הרופא", 88, 77.5), ("תאריך", 36, 77.5)):
        lab = np.clip(lab + typeset_at(txt, xp, yp, 2.9, 0.5, RAANANA, anchor="r"), 0, 1)
    img = img * (1 - (lab * 0.62)[..., None]) + IK[None, None, :] * (lab * 0.62)[..., None]

    hdr = typeset_at("טופס 17", 88, 10.2, 7.2, 1.6, RAANANA, anchor="r")
    img = img * (1 - hdr[..., None]) + IK[None, None, :] * hdr[..., None]

    hw = handwriting([("ניצחונות", 78.0, 22.0, -2.6), ("קטנים", 104.0, 22.0, -1.8)], "v2t")
    img = img * (1 - hw[..., None]) + IK[None, None, :] * hw[..., None]
    sig = handwriting([(AUTHOR, 163.0, 9.4, -1.2)], "v2s", fix_het=False)
    img = img * (1 - sig[..., None]) + IK[None, None, :] * sig[..., None]

    sub = typeset_at("מסע בשלוש מערכות", 50, 35.4, 5.4, 1.2, RAANANA, anchor="c")
    img = img * (1 - sub[..., None]) + RD[None, None, :] * sub[..., None]
    finish(img, out)

# ══════════════════════════════════════════════════ אנסו
def enso_v2(out="c3_enso_v2.png", ghost_layer=True):
    BG = np.array([0.9098, 0.8863, 0.8353], np.float32)
    INK = np.array([0.1059, 0.1608, 0.3608], np.float32)
    ACC = np.array([0.7451, 0.2588, 0.1922], np.float32)
    img = np.ones((H, W, 3), np.float32) * BG
    if ghost_layer:
        gh = ghost(0.10, centre=0.5, span=0.46, zoom=1.15)
        img = img * (1 - gh[..., None] * 0.55) + INK[None, None, :] * (gh * 0.55)[..., None]

    cx, cy, R = W * 0.5, H * 0.455, W * 0.335
    th = np.linspace(np.deg2rad(-64), np.deg2rad(268), 2600)
    wob = ndimage.gaussian_filter1d(rng(2).standard_normal(2600), 90) * R * 0.035
    p = np.stack([cx + (R + wob) * np.cos(th), cy + (R + wob) * np.sin(th) * 1.06], 1).astype(np.float32)
    u = np.linspace(0, 1, len(p))
    prof = 22.0 * (0.20 + 0.95 * np.sin(np.pi * np.clip(u * 0.97 + 0.03, 0, 1)) ** 0.55)
    prof *= 1 + 0.30 * ndimage.gaussian_filter1d(rng(12).standard_normal(len(p)), 130)
    m = brush(p, 0, 0, dry=0.44, seed=6, prof=prof)
    img = img * (1 - m[..., None]) + INK[None, None, :] * m[..., None]
    yy, xx = np.mgrid[0:H, 0:W]
    d0 = np.hypot(xx - p[0][0], yy - p[0][1])
    dot = np.clip(1 - (d0 - 16) / 3.0, 0, 1)
    img = img * (1 - dot[..., None]) + ACC[None, None, :] * dot[..., None]

    t, widths = typeset([("ניצחונות", 40.0, 15.0, 2.6, RAANANA),
                         ("קטנים", 50.0, 15.0, 2.6, RAANANA),
                         ("מסע בשלוש מערכות", 58.0, 6.6, 1.0, CORSIVA),
                         (AUTHOR, 88.0, 6.4, 1.7, RAANANA)])
    print("   author line width: %.1f%% of trim" % (widths[-1] * 100))
    img = img * (1 - t[..., None]) + INK[None, None, :] * t[..., None]
    finish(img, out)

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("both", "form"): form17_v2()
    if which in ("both", "enso"): enso_v2()
    if which in ("both", "enso", "enso3"):
        enso_v2("c3_enso_v3.png", ghost_layer=False)   # no handwriting under the circle
