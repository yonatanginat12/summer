# -*- coding: utf-8 -*-
"""שלב 1: הפקת מסכת אלפא של כתב היד בלבד, על רקע שקוף, ב-300dpi."""
import base64, glob, os, pathlib
from playwright.sync_api import sync_playwright


def chromium_exe():
    """נתיב לכרומיום מותקן מראש, אם playwright לא מוצא אותו בעצמו."""
    cand = os.environ.get("CHROMIUM_EXECUTABLE", "")
    if cand and os.path.exists(cand):
        return cand
    root = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "")
    for pat in ("chromium-*/chrome-linux/chrome", "chromium"):
        hits = sorted(glob.glob(os.path.join(root, pat))) if root else []
        if hits:
            return hits[-1]
    return None

FD = pathlib.Path("fonts")
HAND = base64.b64encode((FD / "GveretLevin.woff2").read_bytes()).decode()

# 141x216mm  @300dpi -> 1666x2553
HTML = f"""<!DOCTYPE html><html lang="he" dir="rtl"><head><meta charset="utf-8"><style>
@font-face{{font-family:Hand;src:url(data:font/woff2;base64,{HAND}) format('woff2');font-display:block}}
*{{margin:0;padding:0}} html,body{{background:transparent}}
.board{{position:relative;width:141mm;height:216mm;overflow:hidden}}
.ln{{position:absolute;right:22mm;text-align:right;font-family:Hand;color:#000;
     line-height:1;white-space:nowrap}}
</style></head><body><div class="board">
  <!-- כיול מול הרפרנסים: גובה אות הכותרת שם הוא פי 1.0-1.15 ממרווח
       השורות (8.73 מ"מ), ואצלי הוא היה פי 1.8. לכן הכותרת נראתה
       שולטת והשורות נראו דלילות. עברית קומפקטית מאנגלית, ולכן הפתרון
       הוא שורה אחת ולא שתיים: 16 מ"מ, גובה אות ~8.8 מ"מ, רוחב ~70%
       מהחיתוך — בדיוק היחסים של הרפרנסים.
       קווי הסרגל: 34 + k*8.73. כל קו בסיס יושב על אחד מהם. -->
  <div class="ln" style="top:44.0mm;right:22mm;font-size:17.5mm;transform:rotate(-0.55deg)">&#1504;&#1497;&#1510;&#1495;&#1493;&#1504;&#1493;&#1514; &#1511;&#1496;&#1504;&#1497;&#1501;</div>
  <div class="ln" style="top:70.3mm;font-size:8mm;transform:rotate(-0.4deg)">&#1502;&#1505;&#1506; &#1489;&#1513;&#1500;&#1493;&#1513; &#1502;&#1506;&#1512;&#1499;&#1493;&#1514;</div>
  <div class="ln" style="top:95.1mm;font-size:9.5mm;transform:rotate(-0.6deg)">&#1499;&#1512;&#1502;&#1500;&#1492; &#1490;&#1497;&#1504;&#1514;</div>
  <svg style="position:absolute;top:63.4mm;right:24.5mm;width:92mm;height:5mm;overflow:visible"
       viewBox="0 0 920 50" xmlns="http://www.w3.org/2000/svg">
    <g fill="none" stroke="#000" stroke-linecap="round">
      <path d="M906 20 C700 11 360 27 104 17" stroke-width="2.6"/>
      <path d="M880 38 C700 31 400 43 160 34" stroke-width="1.7" opacity=".8"/>
    </g>
  </svg>
</div></body></html>"""

pathlib.Path("inkmask.html").write_text(HTML, encoding="utf-8")

with sync_playwright() as p:
    exe = chromium_exe()
    b = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
    pg = b.new_page(viewport={"width": 600, "height": 900}, device_scale_factor=3.125)
    pg.goto(pathlib.Path("inkmask.html").resolve().as_uri())
    pg.wait_for_timeout(2500)
    pg.locator(".board").screenshot(path="inkmask.png", omit_background=True)
    b.close()

from PIL import Image
im = Image.open("inkmask.png")
print("mask", im.size, im.mode)

# ---------------------------------------------------------------------------
# מסכת התבליט: מה שנכתב על הדף שמעל ונחרט לתוך הדף הזה.
# פסאודו-כתב בכוונה — לא ממציאים טקסט אישי על כריכה של מישהו אחר.
import random
_r = random.Random(7)
_AL = "\u05d0\u05d1\u05d2\u05d3\u05d4\u05d5\u05d6\u05d7\u05d8\u05d9\u05db\u05dc\u05de\u05e0\u05e1\u05e2\u05e4\u05e6\u05e7\u05e8\u05e9\u05ea"
def _word():
    return "".join(_r.choice(_AL) for _ in range(_r.randint(2, 6)))
def _line(n):
    return " ".join(_word() for _ in range(n))
_rows = "".join(
    f'<div class="ln" style="top:{21.9 + i * 8.73:.2f}mm;right:{20 + _r.randint(0, 9)}mm;'
    f'font-size:6.6mm;transform:rotate({_r.uniform(-0.7, 0.5):.2f}deg)">{_line(_r.randint(3, 6))}</div>'
    for i in range(11, 22))

DEB = f"""<!DOCTYPE html><html lang="he" dir="rtl"><head><meta charset="utf-8"><style>
@font-face{{font-family:Hand;src:url(data:font/woff2;base64,{HAND}) format('woff2');font-display:block}}
*{{margin:0;padding:0}} html,body{{background:transparent}}
.board{{position:relative;width:141mm;height:216mm;overflow:hidden}}
.ln{{position:absolute;text-align:right;font-family:Hand;color:#000;
     line-height:1;white-space:nowrap}}
</style></head><body><div class="board">{_rows}</div></body></html>"""
pathlib.Path("debossmask.html").write_text(DEB, encoding="utf-8")

with sync_playwright() as p:
    exe = chromium_exe()
    b = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
    pg = b.new_page(viewport={"width": 600, "height": 900}, device_scale_factor=3.125)
    pg.goto(pathlib.Path("debossmask.html").resolve().as_uri())
    pg.wait_for_timeout(2000)
    pg.locator(".board").screenshot(path="debossmask.png", omit_background=True)
    b.close()
print("deboss", Image.open("debossmask.png").size)
