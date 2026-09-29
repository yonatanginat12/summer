# -*- coding: utf-8 -*-
"""Gveret Levin's ח, with the mark taken off it.

Skeletonising the glyph shows what it is made of: a left leg, a roof and a
right leg — a normal ח — plus two short spurs at the top-left shoulder, which
are what read as something scribbled on the letter. So no redrawing: thin the
glyph to its centreline, prune the two spurs, and give the remaining strokes
the pen weight back. Every curve is still the typeface's own.
"""
import pathlib, base64, subprocess, json, re
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.morphology import skeletonize

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONT = "fonts/GveretLevin.woff2"
F = 400
PAD = 140

def _face():
    b = base64.b64encode(pathlib.Path(FONT).read_bytes()).decode()
    return f"@font-face{{font-family:H;src:url(data:font/woff2;base64,{b}) format('woff2');font-display:block}}"

def metrics():
    html = f"""<meta charset=utf-8><style>{_face()}
    body{{margin:0}} span{{font-family:H;font-size:{F}px;line-height:1}}</style>
    <span id=a>ח</span>
    <script>var a=document.getElementById('a').getBoundingClientRect();
    document.title=JSON.stringify({{het:[a.width,a.height]}});</script>"""
    pathlib.Path("_met.html").write_text(html, encoding="utf-8")
    dom = subprocess.run([CHROME, "--headless", "--disable-gpu", "--dump-dom",
                          "--virtual-time-budget=4000",
                          f"file://{pathlib.Path('_met.html').resolve()}"],
                         capture_output=True, text=True).stdout
    return json.loads(re.search(r"<title>(.*?)</title>", dom, re.S).group(1))

def glyph_mask(ch, box):
    w, h = int(round(box[0])) + 2 * PAD, int(round(box[1])) + 2 * PAD
    html = f"""<meta charset=utf-8><style>{_face()}
    html,body{{margin:0;background:transparent;width:{w}px;height:{h}px;overflow:hidden}}
    span{{font-family:H;font-size:{F}px;line-height:1;display:block;
          position:absolute;left:{PAD}px;top:{PAD}px}}</style><span>{ch}</span>"""
    pathlib.Path("_g.html").write_text(html, encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={w},{h}", "--default-background-color=00000000",
                    "--virtual-time-budget=4000", "--screenshot=_g.png",
                    f"file://{pathlib.Path('_g.html').resolve()}"],
                   check=True, capture_output=True)
    return np.array(Image.open("_g.png").split()[-1], np.float32) / 255, (w, h)

def neighbours(sk):
    k = np.ones((3, 3), np.uint8)
    return ndimage.convolve(sk.astype(np.uint8), k, mode="constant") - sk.astype(np.uint8)

def prune_spurs(sk, keep=2):
    """Walk in from every loose end; drop all but the `keep` longest branches."""
    branches = []
    for _ in range(12):
        nb = neighbours(sk)
        ends = np.argwhere(sk & (nb == 1))
        if len(ends) <= keep:
            break
        paths = []
        for (y, x) in ends:
            path, cy, cx, prev = [(y, x)], y, x, None
            while True:
                nb_local = [(cy + dy, cx + dx)
                            for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                            if (dy or dx) and sk[cy + dy, cx + dx]]
                nxt = [p for p in nb_local if p != prev and p not in path[-3:]]
                if len(nxt) != 1:
                    break
                prev = (cy, cx); cy, cx = nxt[0]; path.append((cy, cx))
                if len(path) > 4000:
                    break
            paths.append(path)
        paths.sort(key=len)
        if len(paths) <= keep:
            break
        victim = paths[0]                      # shortest loose branch
        branches.append(len(victim))
        for (y, x) in victim[:-1]:             # leave the junction pixel
            sk[y, x] = False
    return sk, branches

if __name__ == "__main__":
    m = metrics()
    mask, box = glyph_mask("ח", m["het"])
    b = mask > 0.5
    radius = float(np.percentile(ndimage.distance_transform_edt(b)[b], 90))
    sk = skeletonize(b)
    sk, removed = prune_spurs(sk.copy(), keep=2)
    print(f"pruned {len(removed)} spurs, lengths {removed}px; pen radius {radius:.1f}px")

    def disk(r):
        k = np.arange(-r, r + 1)
        return (k[:, None] ** 2 + k[None, :] ** 2) <= r * r
    ink = ndimage.binary_dilation(sk, structure=disk(int(round(radius))))
    ink = ndimage.gaussian_filter(ink.astype(np.float32), 0.8)

    img = np.zeros(ink.shape + (4,), np.uint8)
    img[..., 3] = (np.clip(ink, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(img, "RGBA").save("_het_glyph.png")
    json.dump({"img_w_em": box[0] / F, "img_h_em": box[1] / F,
               "left_em": -PAD / F, "top_em": -PAD / F,
               "adv_em": m["het"][0] / F}, open("_het_glyph.json", "w"))
    print("wrote _het_glyph.png", box)
