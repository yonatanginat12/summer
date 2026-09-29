# -*- coding: utf-8 -*-
"""Print-ready sheets: one cover per page, either at trim or with 3mm bleed.

Trim is 135x210mm. For bleed the artwork is enlarged to cover 141x216mm and
cropped equally on all four sides, so anything that runs off the edge — the
circle in b3 — keeps running through the bleed instead of stopping at the cut.
"""
import sys, covers2, proofcss

TRIM_W, TRIM_H = 135.0, 210.0
BLEED = 3.0

ORDER = ["a1", "a2", "a3", "b1", "b2", "b3", "c1", "c2", "c3"]

def sheet(bleed=False):
    if bleed:
        pw, ph = TRIM_W + 2*BLEED, TRIM_H + 2*BLEED
        scale = max(pw/TRIM_W, ph/TRIM_H)          # cover the whole bleed box
        cw, ch = TRIM_W*scale, TRIM_H*scale
        off_x, off_y = (pw - cw)/2, (ph - ch)/2
        page_rule = f"@page{{size:{pw}mm {ph}mm;margin:0}}"
        box = (f"width:{cw}mm;height:{ch}mm;margin-left:{off_x}mm;margin-top:{off_y}mm")
    else:
        pw, ph = TRIM_W, TRIM_H
        page_rule = f"@page{{size:{pw}mm {ph}mm;margin:0}}"
        box = f"width:{pw}mm;height:{ph}mm"

    pages = "".join(
        f'<div class="page"><div class="cv {"form" if k.startswith("a") else ""}">'
        f'{covers2.COVERS[k]()}</div></div>' for k in ORDER)

    return f"""<meta charset="utf-8"><title>ניצחונות קטנים — עטיפות</title>
<style>
{proofcss.FONTS}
{page_rule}
html,body{{margin:0;padding:0;background:#fff}}
.page{{width:{pw}mm;height:{ph}mm;overflow:hidden;page-break-after:always;
  break-after:page;position:relative}}
.page:last-child{{page-break-after:auto;break-after:auto}}
.page .cv{{{box};box-shadow:none;aspect-ratio:auto}}
{proofcss.COVERCSS}
.cv{{box-shadow:none}}
</style>{pages}"""

if __name__ == "__main__":
    bleed = "--bleed" in sys.argv
    out = "covers-bleed.html" if bleed else "covers-trim.html"
    open(out, "w", encoding="utf-8").write(sheet(bleed))
    print("wrote", out)
