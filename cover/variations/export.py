# -*- coding: utf-8 -*-
"""Two exports of the nine covers:

  covers-pages.pdf  — A4, one cover per page, filling the page, with its name
  exports/<key>.png — 1620x2520 px, i.e. 135x210mm at ~305dpi
"""
import os, subprocess, sys, covers2, proofcss

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ROOT   = os.path.abspath("..")
SCRATCH = os.path.abspath(".build")

ORDER = ["a1", "a2", "a3", "b1", "b2", "b3", "c1", "c2", "c3"]
NAMES = {
    "a1": ("טופס 17", "הטופס המלא"),
    "a2": ("טופס 17", "הכותרת מודפסת"),
    "a3": ("טופס 17", "בלי משבצות"),
    "b1": ("האנסו", "המעגל מוגבה"),
    "b2": ("האנסו", "הכותרת מעל"),
    "b3": ("האנסו", "גדול מהדף"),
    "c1": ("שלוש מערכות", "טור"),
    "c2": ("שלוש מערכות", "שורה"),
    "c3": ("שלוש מערכות", "מרכז אחד"),
}

def chrome(*args):
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", *args],
                   check=True, capture_output=True)

# ---------------------------------------------------------------- PDF, one per page
def pages_pdf():
    body = ""
    for k in ORDER:
        concept, name = NAMES[k]
        cls = "form" if k.startswith("a") else ""
        body += (f'<div class="page"><div class="cv {cls}">{covers2.COVERS[k]()}</div>'
                 f'<p class="slug" dir="rtl"><b>{concept}</b> · {name}'
                 f'<span>{k}</span></p></div>')

    html = f"""<meta charset="utf-8"><title>ניצחונות קטנים — תשע עטיפות</title>
<style>
{proofcss.FONTS}
@page{{size:A4;margin:0}}
html,body{{margin:0;padding:0;background:#fff}}
.page{{width:210mm;height:297mm;display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:6mm;page-break-after:always;break-after:page;overflow:hidden}}
.page:last-child{{page-break-after:auto;break-after:auto}}
.page .cv{{height:252mm;width:162mm;box-shadow:none}}
.slug{{margin:0;font-family:FRL,serif;font-size:10pt;color:#5A6070;letter-spacing:.04em;
  display:flex;gap:10mm;align-items:baseline}}
.slug b{{font-weight:500;color:#232A45}}
.slug span{{font-family:"Arial Hebrew",sans-serif;font-size:8pt;color:#9A9EA8;
  letter-spacing:.14em;text-transform:uppercase}}
{proofcss.COVERCSS}
.cv{{box-shadow:none}}
</style>{body}"""

    src = os.path.join(SCRATCH, "covers-pages.html")
    open(src, "w", encoding="utf-8").write(html)
    out = os.path.join(ROOT, "covers-pages.pdf")
    chrome("--no-pdf-header-footer", "--virtual-time-budget=8000",
           f"--print-to-pdf={out}", f"file://{src}")
    return out

# ---------------------------------------------------------------- PNG, 305dpi
def pngs(scale=3):
    outdir = os.path.join(ROOT, "exports")
    os.makedirs(outdir, exist_ok=True)
    made = []
    for k in ORDER:
        cls = "form" if k.startswith("a") else ""
        html = f"""<meta charset="utf-8"><style>
{proofcss.FONTS}
html,body{{margin:0;padding:0;background:#fff;overflow:hidden}}
{proofcss.COVERCSS}
.cv{{width:540px;height:840px;box-shadow:none;aspect-ratio:auto}}
</style><div class="cv {cls}">{covers2.COVERS[k]()}</div>"""
        src = os.path.join(SCRATCH, f"{k}.html")
        open(src, "w", encoding="utf-8").write(html)
        out = os.path.join(outdir, f"{k}.png")
        chrome("--window-size=540,840", f"--force-device-scale-factor={scale}",
               "--virtual-time-budget=6000", f"--screenshot={out}", f"file://{src}")
        made.append(out)
    return made

if __name__ == "__main__":
    os.makedirs(SCRATCH, exist_ok=True)
    print("pdf:", pages_pdf())
    for p in pngs():
        print("png:", os.path.relpath(p, ROOT))
