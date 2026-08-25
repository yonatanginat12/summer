# -*- coding: utf-8 -*-
"""עזר: תצוגה מוקטנת + חתכי 1:1, לבדיקה עינית אחרי כל שינוי."""
import sys, pathlib
from PIL import Image

PXMM = 300 / 25.4
OUT = pathlib.Path("previews")
OUT.mkdir(exist_ok=True)


def down(src, name, max_w=1100):
    im = Image.open(src)
    s = min(1.0, max_w / im.width)
    im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS).save(OUT / name)
    print(name, im.size, "->", (round(im.width * s), round(im.height * s)))


def crop_mm(src, name, x_mm, y_mm, w_mm, h_mm):
    im = Image.open(src)
    x, y = round(x_mm * PXMM), round(y_mm * PXMM)
    w, h = round(w_mm * PXMM), round(h_mm * PXMM)
    im.crop((x, y, min(x + w, im.width), min(y + h, im.height))).save(OUT / name)
    print(name, "1:1", (w, h), "at", (x, y))


if __name__ == "__main__":
    args = sys.argv[1:]
    src = args[0] if args else "final_trim.png"
    tag = pathlib.Path(src).stem
    down(src, f"{tag}_small.png")
