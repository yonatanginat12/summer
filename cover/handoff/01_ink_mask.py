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
  <!-- קווי הסרגל של הפנקס: 34 מ"מ + k*8.73. הכתיבה יושבת *על* הקווים,
       כמו יד אמיתית; קודם היא ריחפה וחצתה אותם בגבהים שרירותיים.
       הכותרת הוגדלה כי במבחן התמונה הממוזערת היא לא החזיקה. -->
  <div class="ln" style="top:40.1mm;right:24mm;font-size:31mm;transform:rotate(-0.9deg)">&#1504;&#1497;&#1510;&#1495;&#1493;&#1504;&#1493;&#1514;</div>
  <div class="ln" style="top:75.0mm;right:24mm;font-size:31mm;transform:rotate(-0.35deg)">&#1511;&#1496;&#1504;&#1497;&#1501;</div>
  <div class="ln" style="top:120.4mm;font-size:10.5mm;transform:rotate(-0.5deg)">&#1502;&#1505;&#1506; &#1489;&#1513;&#1500;&#1493;&#1513; &#1502;&#1506;&#1512;&#1499;&#1493;&#1514;</div>
  <div class="ln" style="top:170.5mm;font-size:13mm;transform:rotate(-0.7deg)">&#1499;&#1512;&#1502;&#1500;&#1492; &#1490;&#1497;&#1504;&#1514;</div>
  <svg style="position:absolute;top:110.5mm;right:24.5mm;width:80mm;height:9mm;overflow:visible"
       viewBox="0 0 800 90" xmlns="http://www.w3.org/2000/svg">
    <g fill="none" stroke="#000" stroke-linecap="round">
      <path d="M786 26 C600 16 320 34 96 22" stroke-width="7"/>
      <path d="M762 52 C600 44 360 58 150 47" stroke-width="4.2" opacity=".8"/>
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
