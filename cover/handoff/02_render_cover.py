# -*- coding: utf-8 -*-
"""
ניצחונות קטנים — כריכה קדמית, סימולציית נייר וכתיבה.

הרעיון: לא לצייר נייר, אלא לבנות משטח פיזי.
1. שדה גובה של גלי נייר (cockle)  -> ממנו נגזרות תאורה, צל והזחה
2. סיבי נייר בשתי תדירויות
3. קווי הסרגל והדיו מוזחים באותו שדה, ולכן שייכים לאותו משטח
4. דיו כדורי: צפיפות משתנה, דילוגים, הכהיה בשוליים, נזילה לסיבים
5. תאורה כיוונית מנורמלים, ואז גרעיניות צילום
"""
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

W, H = 1666, 2553          # 141x216 mm @300dpi (כולל 3 מ"מ בליד)
PXMM = 300 / 25.4
rng = np.random.default_rng(20260825)


def noise(shape, cell_px, octaves=1, persistence=0.5):
    """רעש חלק ע"י הגדלה ביקובית של רשת אקראית."""
    out = np.zeros(shape, np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        c = max(2, int(cell_px / (2 ** o)))
        gh, gw = max(2, shape[0] // c + 2), max(2, shape[1] // c + 2)
        g = rng.random((gh, gw)).astype(np.float32)
        up = np.array(Image.fromarray((g * 255).astype(np.uint8))
                      .resize((shape[1], shape[0]), Image.BICUBIC), np.float32) / 255
        out += amp * up
        tot += amp
        amp *= persistence
    return out / tot


def norm(a):
    return (a - a.min()) / (np.ptp(a) + 1e-9)


# ---------------------------------------------------------------- 1. משטח הנייר
# גלי נייר: אורך גל 25-70 מ"מ, אמפליטודה זעירה
cockle = (noise((H, W), int(58 * PXMM), 3, .55) - .5) * 2.0
cockle += (noise((H, W), int(23 * PXMM), 2, .5) - .5) * 0.9
# הדף מודבק בראשו ולכן מתגלגל מעט כלפי מטה
yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
cockle += (yy ** 1.6) * 0.55
cockle = ndimage.gaussian_filter(cockle, 9) * 0.34

# ------------------------------------------------------------------- 2. סיבים
fiber_fine = noise((H, W), 3, 2, .5)
fiber_long = ndimage.gaussian_filter(noise((H, W), 5, 1), (0.6, 7.5))   # סיבים אופקיים
fiber = norm(0.62 * fiber_fine + 0.38 * norm(fiber_long))
speck = (noise((H, W), 2, 1) > 0.986).astype(np.float32)                # נקודות עיסה
speck = ndimage.gaussian_filter(speck, 0.7)

# ---------------------------------------------------------- 3. הזחה לפי המשטח
gy, gx = np.gradient(ndimage.gaussian_filter(cockle, 18))
DISP = 5.2 * PXMM / 11.81                      # עד ~5 פיקסלים
Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
map_y = np.clip(Y + gy * DISP * 260, 0, H - 1)
map_x = np.clip(X + gx * DISP * 260, 0, W - 1)


def warp(a):
    return ndimage.map_coordinates(a, [map_y, map_x], order=1, mode="nearest")


# ------------------------------------------------------------ 4. צבע נייר בסיס
# צהוב פנקס אמיתי: פחות רווי ממה שנדמה, ונוטה לירקרק
base = np.zeros((H, W, 3), np.float32)
base[..., 0] = 0.949
base[..., 1] = 0.906
base[..., 2] = 0.639
# שונות צבע מקומית מהעיסה
tint = (noise((H, W), int(9 * PXMM), 2, .5) - .5)
base[..., 0] += tint * 0.030
base[..., 1] += tint * 0.026
base[..., 2] += tint * 0.045
base *= (0.965 + 0.055 * fiber)[..., None]
base -= (speck * 0.05)[..., None]

# ------------------------------------------------------------- 5. קווי הסרגל
rules = np.zeros((H, W), np.float32)
y0, step = 34 * PXMM, 8.8 * PXMM
lw = 0.62                                   # רוחב קו במ"מ *לא* עגול -> אנטי-אליאסינג
row = np.arange(H, dtype=np.float32)[:, None]
col = np.arange(W, dtype=np.float32)[None, :]
k = 0
while y0 + k * step < H + step:
    yc = y0 + k * step
    # עיוות הדפסה: כל קו נוטה ומתעגל מעט אחרת
    bow = np.sin(col / W * np.pi + (k % 5) * 0.9) * (1.1 + (k % 3) * 0.5)
    tilt = (col / W - 0.5) * ((k % 7) - 3) * 0.55
    d = np.abs(row - (yc + bow + tilt))
    rules = np.maximum(rules, np.clip(1 - (d - lw * PXMM / 2) / 1.1, 0, 1))
    k += 1
# צפיפות דיו לא אחידה לאורך הקו (הדפסת אופסט)
rules *= (0.62 + 0.38 * noise((H, W), int(6 * PXMM), 2, .5))
rules = warp(rules)

# ---------------------------------------------------------- 6. שוליים אדומים
red = np.zeros((H, W), np.float32)
for xc, wgt in ((121.4 * PXMM, 1.0), (122.8 * PXMM, 0.62)):
    bow = np.sin(row / H * np.pi * 1.3) * 2.2
    d = np.abs(col - (xc + bow))
    red = np.maximum(red, wgt * np.clip(1 - (d - 0.34 * PXMM) / 1.1, 0, 1))
red *= (0.6 + 0.4 * noise((H, W), int(7 * PXMM), 2, .5))
red = warp(red)

paper = base.copy()
paper -= (rules * 0.44)[..., None] * np.array([0.40, 0.28, -0.03], np.float32)
paper -= (red * 0.72)[..., None] * np.array([0.09, 0.42, 0.20], np.float32)

# ------------------------------------------------------- 7. רושם מהדף הקודם
ghost = np.array(Image.open("inkmask.png").split()[-1], np.float32) / 255
ghost = ndimage.shift(ndimage.gaussian_filter(ghost, 7.5), (31 * PXMM, -13 * PXMM))
paper -= (ghost * 0.013)[..., None] * np.array([0.55, 0.5, 0.28], np.float32)

# ------------------------------------------------------------------- 8. הדיו
a = np.array(Image.open("inkmask.png").split()[-1], np.float32) / 255

# 8א. רעידת יד ברמת הסיב
wob = ndimage.gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), 11) * 55
wob2 = ndimage.gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), 11) * 55
a = ndimage.map_coordinates(a, [np.clip(Y + wob, 0, H - 1),
                                np.clip(X + wob2, 0, W - 1)], order=1, mode="constant")

# 8ב. שדה כיוון המשיכה: הגרדיאנט של שדה המרחק חוצה את המשיכה,
#     ולכן הניצב לו רץ לאורכה — גם בתוך אות עבה.
inside = a > 0.5
sdf = (ndimage.distance_transform_edt(inside)
       - ndimage.distance_transform_edt(~inside)).astype(np.float32)
sdf = ndimage.gaussian_filter(sdf, 3)
gy2, gx2 = np.gradient(sdf)
mg = np.hypot(gx2, gy2) + 1e-6
tx, ty = (-gy2 / mg).astype(np.float32), (gx2 / mg).astype(np.float32)


def sample(f, py, px):
    return ndimage.map_coordinates(f, [np.clip(py, 0, H - 1), np.clip(px, 0, W - 1)],
                                   order=1, mode="nearest")


def lic(field, steps=8, step=1.6):
    """מריחה לאורך כיוון המשיכה — כך נוצרות פסי דיו ולא נקודות."""
    acc = field.copy()
    cnt = 1.0
    for sign in (1.0, -1.0):
        px, py = X.copy(), Y.copy()
        for _ in range(steps):
            dx, dy = sample(tx, py, px), sample(ty, py, px)
            px = px + sign * dx * step
            py = py + sign * dy * step
            acc = acc + sample(field, py, px)
            cnt += 1.0
    return acc / cnt


striae = norm(lic(noise((H, W), 2, 2, .5)))

# 8ג. צפיפות כדור העט — משתנה לאורך המשיכה, לא באופן אקראי
dens = 0.735 + 0.315 * striae
dens *= 0.86 + 0.28 * noise((H, W), int(7 * PXMM), 2, .5)     # לחץ יד משתנה

# 8ד. דילוגים: רק במקומות דלילים, ורק היכן שהעט "המריא"
gate = (noise((H, W), int(3.2 * PXMM), 2, .5) > 0.56).astype(np.float32)
gate = ndimage.gaussian_filter(gate, 2.0)
skip = np.clip((0.26 - striae) / 0.26, 0, 1) * gate

# 8ה. סיבי הנייר מכרסמים בשולי המשיכה
rim_band = np.clip(1 - np.abs(sdf) / 2.6, 0, 1)
bite = rim_band * np.clip(norm(fiber_fine) - 0.5, 0, 1) * 1.6

ink = np.clip(a * dens * (1 - 0.9 * skip) - bite, 0, 1)

# 8ו. הצטברות דיו בשוליים — סימן ההיכר של עט כדורי
rim = np.clip(ndimage.gaussian_filter(ink, 0.9) - ndimage.grey_erosion(ink, size=9), 0, 1)
# 8ז. נזילה זעירה לתוך הסיבים
feather = ndimage.gaussian_filter(ink, 2.8) * 0.22
# 8ח. הצטברות בפניות ובסופי משיכות
pool = np.clip(ndimage.gaussian_filter(ink, 6) - 0.60, 0, 1) * 0.8

ink = np.clip(ink + feather * (1 - ink), 0, 1)
ink = warp(ink)
rim = warp(rim)
pool = warp(pool)

INK_CORE = np.array([0.098, 0.196, 0.502], np.float32)   # כחול כדורי
INK_DEEP = np.array([0.043, 0.086, 0.278], np.float32)   # שוליים והצטברות
ink_rgb = INK_CORE[None, None, :] * np.ones((H, W, 3), np.float32)
mix = np.clip(rim * 1.05 + pool * 0.9, 0, 1)[..., None]
ink_rgb = ink_rgb * (1 - mix) + INK_DEEP[None, None, :] * mix

img = paper * (1 - ink[..., None]) + ink_rgb * ink[..., None]

# ------------------------------------------------------------ 9. טבעת קפה
cy, cx = 166.0 * PXMM, 32.5 * PXMM
r = np.hypot(Y - cy, (X - cx) * 1.07)
R = 17.0 * PXMM
wobr = ndimage.gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), 60) * 120
ring = np.exp(-((r - R + wobr) ** 2) / (2 * (1.5 * PXMM) ** 2))
ring *= (0.25 + 0.75 * noise((H, W), int(11 * PXMM), 2, .5))
inner = np.clip(1 - r / R, 0, 1) ** 0.6 * 0.10
stain = np.clip(ring * 0.55 + inner, 0, 1)
img -= stain[..., None] * np.array([0.12, 0.19, 0.27], np.float32)

# ------------------------------------------- 10. קרע ההדבקה בראש הדף
tear_y = 12.6 * PXMM + (noise((H, W), int(4 * PXMM), 3, .5)[0:1, :] - .5) * 3.2 * PXMM
tear_prof = ndimage.gaussian_filter1d((noise((60, W), 24, 3, .5).mean(0) - .5), 3) * 2.4 * PXMM
tear_line = 12.6 * PXMM + tear_prof[None, :]
strip = np.clip((tear_line - Y) / 1.6, 0, 1)
fuzz = np.clip((tear_line + 1.6 * PXMM - Y) / (2.2 * PXMM), 0, 1) * (1 - strip)
fuzz *= (noise((H, W), 2, 1) > 0.45)
img = img * (1 - strip[..., None]) + strip[..., None] * (
        np.array([0.749, 0.668, 0.379], np.float32)[None, None, :]
        * (0.94 + 0.10 * fiber)[..., None])
img += (fuzz * 0.10)[..., None]                       # ליבת הנייר הלבנה בקרע
shadow = np.clip((Y - tear_line) / (5.0 * PXMM), 0, 1)
img *= (0.905 + 0.095 * shadow)[..., None]

# ------------------------------------------------- 11. תאורה מהמשטח
hs = ndimage.gaussian_filter(cockle, 14)
ny, nx = np.gradient(hs)
LX, LY = -0.62, -0.78                                  # אור מלמעלה-שמאל
lam = 1.0 + (nx * LX + ny * LY) * 15
lam = np.clip(ndimage.gaussian_filter(lam, 12), 0.976, 1.026)
ao = 1 - np.clip(ndimage.gaussian_filter(cockle, 45) - cockle, 0, None) * 2.4
img *= (lam * np.clip(ao, 0.978, 1.0))[..., None]

# נפילת אור רחבה על פני הגיליון + הצללה בקצה הכריכה
falloff = 1.028 - 0.072 * np.clip(np.hypot((X / W - 0.34) * 1.25, (Y / H - 0.30) * 0.95), 0, 1) ** 1.25
img *= falloff[..., None]
spine = 1 - 0.075 * np.clip(1 - X / (8 * PXMM), 0, 1) ** 1.6
img *= spine[..., None]
img[..., 2] *= 1.0 + 0.020 * (1 - falloff)             # צללים נוטים לכחול
img[..., 0] *= 1.0 + 0.014 * (falloff - 1)             # אורות נוטים לחום

# --------------------------------------------------- 12. גרעיניות צילום
grain = rng.standard_normal((H, W, 3)).astype(np.float32)
grain = ndimage.gaussian_filter(grain, (0.55, 0.55, 0))
img += grain * 0.0055

img = np.clip(img, 0, 1)
out = Image.fromarray((img ** (1 / 1.015) * 255).astype(np.uint8))
out = out.filter(ImageFilter.UnsharpMask(radius=1.2, percent=32, threshold=2))

bleed_path = "final_bleed.png"
out.save(bleed_path)
m = round(3 * 300 / 25.4)
out.crop((m, m, W - m, H - m)).save("final_trim.png")
print("done", out.size)
