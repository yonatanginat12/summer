# -*- coding: utf-8 -*-
"""טופס 17 in three other hands.

Everything except the handwriting is identical to the chosen version: same
paper, same rules, same red line, same Raanana labels, same grain. Only the
face that writes the title and signs the form changes.

Each hand is fitted rather than set at a nominal size — the script renders a
line, measures its actual ink, and rescales so every version's title occupies
the same width and sits on the same baseline as the chosen one. Otherwise a
narrow face like Amatic would read as a different layout rather than a
different hand.
"""
import pathlib, base64, subprocess, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage

_src = pathlib.Path("four.py").read_text(encoding="utf-8")
exec(compile(_src[:_src.index("# ============================================================ 1.")],
             "helpers", "exec"), globals())

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
AUTHOR = "כרמלה מרינגר-גינת"
HEB_RANGE = "U+0590-05FF,U+200C-2010,U+20AA,U+25CC,U+FB1D-FB4F"
LAT_RANGE = "U+0000-00FF,U+2000-206F"

HANDS = {
    "gveret":   ("Gveret Levin",        "fonts/GveretLevin.woff2",         None),
    "playpen":  ("Playpen Sans Hebrew", "fonts/PlaypenSansHebrew.woff2",   "fonts/PlaypenSansHebrew-latin.woff2"),
    "amatic":   ("Amatic SC",           "fonts/AmaticSC.woff2",            "fonts/AmaticSC-latin.woff2"),
    "solitreo": ("Solitreo",            "fonts/Solitreo.woff2",            "fonts/Solitreo-latin.woff2"),
    "scribble": ("Rubik Scribble",      "fonts/RubikScribble.woff2",       "fonts/RubikScribble-latin.woff2"),
    "hatch":    ("Rubik Marker Hatch",  "fonts/RubikMarkerHatch.woff2",    "fonts/RubikMarkerHatch-latin.woff2"),
    "corsiva":  ("Corsiva Hebrew",      None,                              None),
}

def _b64(p): return base64.b64encode(pathlib.Path(p).read_bytes()).decode()

def face_css(key):
    name, heb, lat = HANDS[key]
    if heb is None:                       # a system-installed face
        return '@font-face{font-family:H;src:local("' + name + '")}'
    css = (f"@font-face{{font-family:H;src:url(data:font/woff2;base64,{_b64(heb)}) format('woff2');"
           f"font-display:block;unicode-range:{HEB_RANGE}}}")
    if lat:
        css += (f"@font-face{{font-family:H;src:url(data:font/woff2;base64,{_b64(lat)}) format('woff2');"
                f"font-display:block;unicode-range:{LAT_RANGE}}}")
    return css


HET_GAP = 0.15   # the pruned ח sets tight against the צ; open it up
HET_SHIFT = 0.0  # how much of that room goes on the ו side rather than the צ side

def het_html(gap_em=0.0):
    """Gveret's ח carries two short spurs on its shoulder that read as a mark
    scribbled on the letter. het.py thins the glyph to its centreline, prunes
    those two branches and restores the pen weight — same glyph, same metrics,
    same box, just without the mark."""
    m = json.load(open("_het_glyph.json"))
    g = base64.b64encode(pathlib.Path("_het_glyph.png").read_bytes()).decode()
    return (f'<span style="display:inline-block;width:{m["adv_em"]+gap_em:.4f}em;height:1em;'
            f'position:relative;vertical-align:top">'
            f'<img src="data:image/png;base64,{g}" style="position:absolute;'
            f'left:{m["left_em"] + HET_SHIFT:.4f}em;top:{m["top_em"]:.4f}em;'
            f'width:{m["img_w_em"]:.4f}em;height:{m["img_h_em"]:.4f}em"></span>')

def _shot(html, png):
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--window-size=510,794", "--force-device-scale-factor=3.1259",
                    "--default-background-color=00000000", "--virtual-time-budget=6000",
                    f"--screenshot={png}", f"file://{pathlib.Path(html).resolve()}"],
                   check=True, capture_output=True)

def _monoline(alpha):
    """The same skeletonise-and-redraw the original used, so every hand gets one pen."""
    def disk(r):
        k = np.arange(-r, r + 1)
        return (k[:, None] ** 2 + k[None, :] ** 2) <= r * r
    b = alpha > 0.5
    d = ndimage.distance_transform_edt(b).astype(np.float32)
    ds = ndimage.gaussian_filter(d, 1.2)
    sk = b & (ds > ndimage.maximum_filter(ds, size=3) - 0.75) & (d > 1.0)
    sk = ndimage.binary_closing(sk, structure=disk(3))
    return ndimage.gaussian_filter(ndimage.binary_dilation(sk, structure=disk(3)).astype(np.float32), 0.6)

def raw_line(text, size_mm, rot, key, tag, top_mm=70, fix_het=False):
    if fix_het and "ח" in text:
        a, _, b = text.partition("ח")
        text = a + het_html(HET_GAP) + b
    html = f"""<!DOCTYPE html><html lang="he" dir="rtl"><head><meta charset="utf-8"><style>
{face_css(key)}
*{{margin:0;padding:0}} html,body{{background:transparent;width:135mm;height:210mm}}
.b{{position:relative;width:135mm;height:210mm;overflow:hidden}}
.l{{position:absolute;top:{top_mm}mm;left:0;right:0;text-align:center;font-family:H;color:#000;
   line-height:1;white-space:nowrap;font-size:{size_mm}mm;transform:rotate({rot}deg)}}
</style></head><body><div class="b"><div class="l">{text}</div></div></body></html>"""
    src, png = f"_h{tag}.html", f"_h{tag}.png"
    pathlib.Path(src).write_text(html, encoding="utf-8")
    _shot(src, png)
    a = np.array(Image.open(png).split()[-1].resize((W, H)), np.float32) / 255
    return _monoline(a)

def ink_box(m, thr=0.35):
    ys, xs = np.where(m > thr)
    if len(xs) == 0: return None
    return xs.min(), ys.min(), xs.max(), ys.max()

def fitted_line(text, rot, key, tag, target_w, target_cx, target_top, start=22.0, fix_het=False):
    """Render, measure, rescale to the reference width, then place by its ink."""
    m = raw_line(text, start, rot, key, tag, fix_het=fix_het)
    x0, y0, x1, y1 = ink_box(m)
    size = start * target_w / (x1 - x0)
    m = raw_line(text, round(size, 2), rot, key, tag, fix_het=fix_het)
    x0, y0, x1, y1 = ink_box(m)
    dx = target_cx - (x0 + x1) / 2.0
    dy = target_top - y0
    m = ndimage.shift(m, (dy, dx), order=1, mode="constant", cval=0.0)
    return np.clip(m, 0, 1), size

def seg(m, x0, y0, x1, y1, w=2.0):
    yy, xx = np.mgrid[0:H, 0:W]
    dx, dy = x1 - x0, y1 - y0
    t = np.clip(((xx - x0) * dx + (yy - y0) * dy) / max(dx * dx + dy * dy, 1e-6), 0, 1)
    dist = np.hypot(xx - (x0 + t * dx), yy - (y0 + t * dy))
    m += np.clip(1 - (dist - w / 2) / 1.2, 0, 1)
    np.clip(m, 0, 1, out=m)
    return m

def rect(m, x0, y0, x1, y1, w=2.0):
    for a in ((x0, y0, x1, y0), (x0, y1, x1, y1), (x0, y0, x0, y1), (x1, y0, x1, y1)):
        seg(m, *a, w)
    return m

# reference ink geometry, measured off the chosen Gveret version
REF = {"l1":  (791, 745, 956),    # ink width px, centre x, top y
       "l2":  (529, 789, 1248),
       "sig": (821, 773, 1913)}

def form17(key, out):
    label = HANDS[key][0]
    BG = np.array([0.9333, 0.9255, 0.8941], np.float32)
    IK = np.array([0.1451, 0.1608, 0.2078], np.float32)
    RD = np.array([0.7059, 0.1725, 0.1373], np.float32)
    img = np.ones((H, W, 3), np.float32) * BG
    form = np.zeros((H, W), np.float32)
    L, R_, T, B = W * 0.085, W * 0.915, H * 0.075, H * 0.90
    rect(form, L, T, R_, B, 3.0)
    seg(form, L, T + H * 0.062, R_, T + H * 0.062, 3.0)
    TABLE = [0.135, 0.187, 0.239, 0.291]
    for y in TABLE + [0.430, 0.510, 0.590, 0.670, 0.750, 0.830]:
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

    hw = np.zeros((H, W), np.float32)
    for text, rot, tag, ref in (("ניצחונות", -2.6, "1", "l1"),
                                ("קטנים",   -1.8, "2", "l2")):
        m, size = fitted_line(text, rot, key, tag, *REF[ref],
                              fix_het=(key == "gveret" and text == "ניצחונות"))
        hw = np.clip(hw + m, 0, 1)
        print(f"    {label:20} {text:9} {size:5.1f}mm")
    img = img * (1 - hw[..., None]) + IK[None, None, :] * hw[..., None]

    sig, ssize = fitted_line(AUTHOR, -1.2, key, "s", *REF["sig"], start=9.4)
    print(f"    {label:20} signature {ssize:5.1f}mm")
    img = img * (1 - sig[..., None]) + IK[None, None, :] * sig[..., None]

    sub = typeset_at("מסע בשלוש מערכות", 50, 35.4, 5.4, 1.2, RAANANA, anchor="c")
    img = img * (1 - sub[..., None]) + RD[None, None, :] * sub[..., None]
    finish(img, out)

if __name__ == "__main__":
    keys = sys.argv[1:] or ["playpen", "amatic", "solitreo"]
    for k in keys:
        form17(k, f"form17_{k}.png")
