# -*- coding: utf-8 -*-
"""
ניצחונות קטנים — כריכה קדמית, סימולציית נייר וכתיבה.

הרעיון: לא לצייר נייר, אלא לבנות משטח פיזי.

שני שדות גובה, לא אחד:
  cockle — גלי נייר בסקאלה של סנטימטרים. ממנו נגזרות ההזחה (warp),
           התאורה הרחבה וההאפלה בשקעים.
  tooth  — מרקם הנייר עצמו בסקאלה של פיקסלים. ממנו נגזרת התאורה
           המיקרוסקופית, וגם *דילוגי הדיו*: הכדור נוגע בפסגות ומחטיא
           את השקעים. זה מה שקושר את הדיו למשטח.

הדיו נבנה משדה כיוון קוהרנטי (טנזור מבנה), ולא מהניצב לגרדיאנט של שדה
המרחק. הסיבה: באמצע אות עבה הגרדיאנט מתנוון (הציר המדיאלי) והכיוון
מסתחרר — מה שיצר מערבולות שנראו כמו שיש. הטנזור חסין לזה כי הוא לא
מבדיל בין שני צדי המשיכה.

הצטברות הדיו בשוליים היא כיוונית: הכדור דוחס דיו *הצידה* בעודו מתגלגל
קדימה, ולכן הרכס הכהה יושב על האגפים ולא על קצות המשיכה. שפה כהה אחידה
סביב כל אות היא קו מכחול, לא עט.
"""
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

W, H = 1666, 2553          # 141x216 mm @300dpi (כולל 3 מ"מ בליד)
PXMM = 300 / 25.4
rng = np.random.default_rng(20260825)

LX, LY = -0.62, -0.78      # וקטור אל האור: מלמעלה-שמאל, מלטף את פני הגיליון

# ---- הכריכה העברית נכרכת בימין. השדרה בצד ימין של הכריכה הקדמית. ----
GUTTER_RIGHT = True


def noise(shape, cell_px, octaves=1, persistence=0.5):
    """רעש חלק ע"י הגדלה ביקובית של רשת אקראית — לסקאלות גדולות."""
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


def fbm(shape, octaves=5, sigma0=0.55, persistence=0.62):
    """
    רעש 1/f עם תוכן ספקטרלי עד רמת הפיקסל.
    הגדלה ביקובית של רשת 2-3 פיקסלים מחזירה משטח *חלק*; זו הסיבה
    שהנייר נראה כמו מילוי שטוח עם ענן מעליו. סינון רעש לבן שומר על
    התדרים הגבוהים.
    """
    out = np.zeros(shape, np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        n = ndimage.gaussian_filter(rng.standard_normal(shape).astype(np.float32),
                                    sigma0 * (2 ** o))
        out += amp * (n / (n.std() + 1e-9))
        tot += amp
        amp *= persistence
    return out / tot


def unit(a):
    """נרמול לסטיית תקן 1, ממוצע 0."""
    return (a - a.mean()) / (a.std() + 1e-9)


def norm(a):
    return (a - a.min()) / (np.ptp(a) + 1e-9)


def soft(x, k):
    """רולאוף רך במקום חיתוך — מצלמה מגלגלת אורות, לא קוצצת אותם."""
    return k * np.tanh(x / k)


def shade(h, sigma, amp):
    """הצללה דיפוזית משדה גובה: n=(-hx,-hy,1), ולכן השינוי הוא -(hx*Lx+hy*Ly)."""
    hs = ndimage.gaussian_filter(h, sigma) if sigma else h
    hy, hx = np.gradient(hs)
    s = -(hx * LX + hy * LY)
    return s / (s.std() + 1e-9) * amp


# ------------------------------------------------- 1. משטח מאקרו: גלי נייר
# אורך גל 25-70 מ"מ, אמפליטודה זעירה.
# גלי נייר אינם כתמים עגולים: הדף מודבק בראשו ומתקמר בין הראש הכבול
# לתחתית החופשית, ולכן הגלים הם רכסים *מאונכים* ארוכים. סינון איזוטרופי
# נותן כתמים, והם נקראים כלכלוך ולא כצורה.
cockle = (noise((H, W), int(58 * PXMM), 3, .55) - .5) * 2.0
cockle += (noise((H, W), int(23 * PXMM), 2, .5) - .5) * 0.9
yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
cockle += (yy ** 1.6) * 0.55
cockle = ndimage.gaussian_filter(cockle, (62, 13)) * 0.34

# ------------------------------------------- 2. משטח מיקרו: מרקם הנייר
# עיסת נייר: גרעין איזוטרופי + נטייה קלה לכיוון המכונה.
# ב-300dpi פיקסל אחד הוא 0.085 מ"מ. שן של נייר בונד חלק היא בסדר גודל
# של 0.05-0.15 מ"מ, כלומר *בגבול* הרזולוציה. אוקטבות רחבות מזה נותנות
# בד פשתן או נייר אקוורל — וזה מה שקרה כאן קודם.
grain = fbm((H, W), 3, 0.50, 0.50)
fib_md = ndimage.gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), (0.5, 3.0))
tooth = unit(0.88 * grain + 0.12 * unit(fib_md))

# נקודות עיסה — סיב כהה בודד שלא נטחן
speck = (fbm((H, W), 2, 0.5, 0.5) > 2.55).astype(np.float32)
speck = ndimage.gaussian_filter(speck, 0.6)

# --------------------------------------------- 3. הזחה לפי משטח המאקרו
gy, gx = np.gradient(ndimage.gaussian_filter(cockle, 18))
DISP = 5.2 * PXMM / 11.81                      # עד ~5 פיקסלים
Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
map_y = np.clip(Y + gy * DISP * 260, 0, H - 1)
map_x = np.clip(X + gx * DISP * 260, 0, W - 1)


def warp(a):
    return ndimage.map_coordinates(a, [map_y, map_x], order=1, mode="nearest")


# ------------------------------------------------------ 4. צבע נייר בסיס
# צהוב פנקס אמיתי: פחות רווי ממה שנדמה, ונוטה לירקרק
base = np.zeros((H, W, 3), np.float32)
base[..., 0] = 0.949
base[..., 1] = 0.906
base[..., 2] = 0.639
# שונות צבע מקומית מהעיסה — עדינה, אחרת מתקבל "ענן" של פוטושופ
tint = (noise((H, W), int(9 * PXMM), 2, .5) - .5)
base[..., 0] += tint * 0.022
base[..., 1] += tint * 0.019
base[..., 2] += tint * 0.034
# אלבדו המרקם: הצבע עצמו משתנה מעט עם צפיפות העיסה
base *= (1.0 + 0.013 * tooth)[..., None]
base -= (speck * 0.055)[..., None]

# ------------------------------------------------------- 5. קווי הסרגל
# פנקס אמיתי: 11/32 אינץ' = 8.73 מ"מ
rules = np.zeros((H, W), np.float32)
y0, step = 34 * PXMM, 8.73 * PXMM
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
# הדפסה יושבת על פסגות המרקם ומחטיאה שקעים — כך הקו מקבל את הנייר
rules *= np.clip(0.90 + 0.10 * (tooth + 0.4), 0.78, 1.08)
rules = warp(rules)

# ---------------------------------------------------- 6. שוליים אדומים
red = np.zeros((H, W), np.float32)
for xc, wgt in ((121.4 * PXMM, 1.0), (122.8 * PXMM, 0.62)):
    bow = np.sin(row / H * np.pi * 1.3) * 2.2
    d = np.abs(col - (xc + bow))
    red = np.maximum(red, wgt * np.clip(1 - (d - 0.34 * PXMM) / 1.1, 0, 1))
red *= (0.55 + 0.40 * noise((H, W), int(7 * PXMM), 2, .5))
red *= np.clip(0.90 + 0.10 * (tooth + 0.4), 0.78, 1.08)
red = warp(red)

paper = base.copy()
paper -= (rules * 0.44)[..., None] * np.array([0.40, 0.28, -0.03], np.float32)
paper -= (red * 0.70)[..., None] * np.array([0.07, 0.38, 0.24], np.float32)

# ------------------------------------------------- 7. רושם מהדף הקודם
ghost = np.array(Image.open("inkmask.png").split()[-1], np.float32) / 255
ghost = ndimage.shift(ndimage.gaussian_filter(ghost, 7.5), (31 * PXMM, -13 * PXMM))
paper -= (ghost * 0.013)[..., None] * np.array([0.55, 0.5, 0.28], np.float32)

# ------------------------------------------------------------- 8. הדיו
a = np.array(Image.open("inkmask.png").split()[-1], np.float32) / 255

# 8א. רעידת יד ברמת הסיב
wob = ndimage.gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), 11) * 55
wob2 = ndimage.gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), 11) * 55
a = ndimage.map_coordinates(a, [np.clip(Y + wob, 0, H - 1),
                                np.clip(X + wob2, 0, W - 1)], order=1, mode="constant")

# 8ב. שדה כיוון המשיכה מטנזור המבנה.
#     הגרדיאנט מתהפך בין שני אגפי המשיכה, אבל הטנזור g⊗g לא — ולכן
#     הכיוון יוצא קוהרנטי לרוחב כל המשיכה, גם על הציר המדיאלי.
ab = ndimage.gaussian_filter(a, 2.6)
agy, agx = np.gradient(ab)
TS = 7.0
Jxx = ndimage.gaussian_filter(agx * agx, TS)
Jyy = ndimage.gaussian_filter(agy * agy, TS)
Jxy = ndimage.gaussian_filter(agx * agy, TS)
theta = 0.5 * np.arctan2(2 * Jxy, Jxx - Jyy)        # כיוון הגרדיאנט השולט = *לרוחב*
tx = (-np.sin(theta)).astype(np.float32)            # ניצב לו = *לאורך* המשיכה
ty = (np.cos(theta)).astype(np.float32)
coher = (np.hypot(Jxx - Jyy, 2 * Jxy) / (Jxx + Jyy + 1e-9)).astype(np.float32)

# שדה המרחק — לשוליים, לליבה ולנשיכת הסיבים
inside = a > 0.5
sdf = (ndimage.distance_transform_edt(inside)
       - ndimage.distance_transform_edt(~inside)).astype(np.float32)
sdf = ndimage.gaussian_filter(sdf, 3)
sgy, sgx = np.gradient(sdf)
smg = np.hypot(sgx, sgy) + 1e-6
nx, ny = (sgx / smg).astype(np.float32), (sgy / smg).astype(np.float32)


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


striae = norm(lic(fbm((H, W), 3, 0.5, 0.55)))

# 8ג. עקמומיות שדה הכיוון. זווית מתהפכת ב-pi, ולכן נגזור את הווקטור
#     הכפול (cos2θ, sin2θ) שאין בו קיפול.
c2, s2 = np.cos(2 * theta).astype(np.float32), np.sin(2 * theta).astype(np.float32)
curv = np.hypot(np.hypot(*np.gradient(ndimage.gaussian_filter(c2, 2))),
                np.hypot(*np.gradient(ndimage.gaussian_filter(s2, 2))))
curv = norm(ndimage.gaussian_filter(curv, 3))

# 8ד. צפיפות כדור העט — משתנה לאורך המשיכה, לא באופן אקראי
dens = 0.700 + 0.360 * striae
dens *= 0.86 + 0.28 * noise((H, W), int(7 * PXMM), 2, .5)     # לחץ יד משתנה

# 8ה. מרקם הנייר קובע היכן הכדור נוגע: פסגות נצבעות, שקעים מוחמצים.
#     זה החיבור הפיזי בין הדיו למשטח, והוא חזק יותר באגפים הדקים.
flank_soft = np.clip(1 - np.abs(sdf) / 5.5, 0, 1)
touch = np.clip(0.5 + 0.5 * ndimage.gaussian_filter(tooth, 0.7) * 1.5, 0, 1)
# משחת דיו *ממלאת* את השן; היא לא נוגעת רק בפסגות כמו גיר. מודולציה
# חזקה כאן הפכה את הכתיבה לעיפרון על נייר גס.
dens *= 1 - (0.09 + 0.15 * flank_soft) * (1 - touch)

# 8ו. דילוגים: העט מדלג בפניות ובראשי משיכות, לא במקומות אקראיים
gate = norm(ndimage.gaussian_filter(fbm((H, W), 3, 1.1, 0.5), 1.4))
skip = np.clip((0.30 - striae) / 0.30, 0, 1) * np.clip(gate * 0.7 + curv * 1.5, 0, 1)

# 8ז. סיבי הנייר מכרסמים בשולי המשיכה
rim_band = np.clip(1 - np.abs(sdf) / 2.6, 0, 1)
bite = rim_band * np.clip(unit(grain) * 0.5 + 0.5 - 0.54, 0, 1) * 1.15

ink = np.clip(a * dens * (1 - 0.9 * skip) - bite, 0, 1)

# 8ח. שוקת: בלחץ כבד הכדור דוחק דיו מהמרכז אל האגפים
core = np.clip((sdf - 2.2) / 3.2, 0, 1)
ink *= 1 - 0.10 * core

# 8ט. הצטברות באגפים — כיוונית.
#     נורמל השפה מקביל לכיוון הנסיעה בקצה המשיכה, וניצב לו באגף.
#     ולכן: מקדם = 1-|n·t| מדגיש אגפים ומכבה קצות.
flank = np.clip(1 - np.abs(nx * tx + ny * ty), 0, 1) ** 0.85
flank = 0.20 + 0.80 * flank                   # רצפה: גם קצה אוסף קצת
flank *= np.clip(coher * 2.6, 0.35, 1.0)      # בצמתים אין כיוון, אין רכס
# העט מוטה, ולכן אגף אחד אוסף יותר מהשני
tilt_side = 0.5 + 0.5 * (nx * (-0.42) + ny * 0.91)
rim = np.clip(ndimage.gaussian_filter(ink, 0.7) - ndimage.grey_erosion(ink, size=7), 0, 1)
rim *= flank * (0.75 + 0.85 * tilt_side)

# 8י. הצטברות בפניות — גוֹאפּ. מתרכזת היכן שהכיוון מתהפך.
pool = np.clip(ndimage.gaussian_filter(ink, 5) - 0.55, 0, 1)
pool *= np.clip(curv * 2.6, 0, 1) * 1.5

# 8יא. נזילה זעירה לתוך הסיבים
feather = ndimage.gaussian_filter(ink, 2.4) * 0.20
ink = np.clip(ink + feather * (1 - ink), 0, 1)

ink = warp(ink)
rim = warp(rim)
pool = warp(pool)

INK_CORE = np.array([0.098, 0.196, 0.502], np.float32)   # כחול כדורי
INK_DEEP = np.array([0.043, 0.086, 0.278], np.float32)   # שוליים והצטברות
ink_rgb = INK_CORE[None, None, :] * np.ones((H, W, 3), np.float32)
mix = np.clip(rim * 1.05 + pool * 0.9, 0, 1)[..., None]
ink_rgb = ink_rgb * (1 - mix) + INK_DEEP[None, None, :] * mix

# הדיו שקוף למחצה באגפים הדקים — הנייר והסרגל מציצים מתחת
alpha = np.clip(ink * 1.12, 0, 1)
img = paper * (1 - alpha[..., None]) + ink_rgb * alpha[..., None]

# ------------------------------------------------------- 9. טבעת קפה
# הקו שנשאר הוא *קו המגע*: האידוי סוחב מוצקים אל השפה החיצונית, ולכן
# מחוץ לטבעת החתך חד ובפנים הוא נמשך פנימה בהדרגה.
cy, cx = 168.0 * PXMM, 31.0 * PXMM
r = np.hypot(Y - cy, (X - cx) * 1.07)
R = 17.0 * PXMM
# הכוס לא עומדת ישר ולא עגולה לגמרי
wobr = ndimage.gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), 60) * 120
rr = r + wobr - R
# רוחב קו המגע משתנה סביב ההיקף: היכן שהמניסקוס נסוג מהר הוא דק,
# והיכן שהוא נתקע הוא עבה. טבעת ברוחב אחיד נראית מצוירת בעיפרון.
ang = np.arctan2(Y - cy, X - cx)
wid = 0.38 + 0.55 * (0.5 + 0.5 * np.sin(ang * 3.0 + 0.7)) \
           + 0.30 * (0.5 + 0.5 * np.sin(ang * 7.0 - 2.1))
edge = np.clip(1 - rr / (0.42 * PXMM), 0, 1)              # חד בחוץ
tail = np.clip(1 + rr / ((1.1 + 2.6 * wid) * PXMM), 0, 1) ** 2.0   # נמשך פנימה
ring = np.minimum(edge, tail)
# והטבעת נקטעת: היכן שהנוזל נסוג בבת אחת לא נשאר כלום
ring *= np.clip(-0.10 + 1.9 * (0.5 + 0.5 * np.sin(ang * 2.0 - 1.2))
                * (0.30 + 0.70 * noise((H, W), int(14 * PXMM), 2, .5)), 0, 1)
ring *= 0.80 + 0.20 * unit(fib_md)                        # מכתים לאורך הסיב
inner = np.clip(1 - r / R, 0, 1) ** 0.6 * 0.10
stain = np.clip(ring * 1.05 + inner, 0, 1)
img -= stain[..., None] * np.array([0.06, 0.17, 0.30], np.float32)

# --------------------------------- 10. שפת הקרע בראש הדף + המשטח שמתחת
# מה שמעל הקרע איננו נייר: זה השולחן שהדף מונח עליו. זה מה שנותן
# לתמונה עומק — הגיליון *על* משהו, ולא ממלא את המסגרת בלי הקשר.
tear_prof = ndimage.gaussian_filter1d((noise((60, W), 24, 3, .5).mean(0) - .5), 3) * 2.4 * PXMM
tear_line = 12.6 * PXMM + tear_prof[None, :]
page = np.clip((Y - tear_line) / 1.5, 0, 1)               # 1 = נייר, 0 = שולחן

desk = np.array([0.300, 0.246, 0.201], np.float32)        # עץ כהה, לא רווי
desk_tex = (0.80 + 0.40 * norm(ndimage.gaussian_filter(
    rng.standard_normal((H, W)).astype(np.float32), (1.1, 9.0))))
desk_rgb = desk[None, None, :] * desk_tex[..., None]
desk_rgb *= (1.0 + 0.09 * shade(unit(desk_tex), 0.8, 1.0))[..., None]
# אותו אור מלטף מלמעלה-שמאל חייב לחול גם על השולחן, אחרת הוא פס צבע
desk_rgb *= (1.06 - 0.16 * np.clip(X / W, 0, 1))[..., None]

# הדף מתולל מעט בקרע: פסגה מוארת מתחת לשפה, והשפה מאפילה על השולחן מעליה
curl = np.exp(-np.clip(Y - tear_line, 0, None) / (2.1 * PXMM)) * page
occl = np.exp(-np.clip(tear_line - Y, 0, None) / (1.5 * PXMM)) * (1 - page)
fuzz = np.clip((tear_line + 1.7 * PXMM - Y) / (2.2 * PXMM), 0, 1) * page
fuzz *= (fbm((H, W), 2, 0.5, 0.5) > 0.15)                 # סיבים קרועים

img = img * (1 + 0.085 * curl)[..., None]                 # הפסגה תופסת אור
img += (fuzz * 0.085)[..., None]                          # ליבת הנייר הלבנה בקרע
img = img * page[..., None] + desk_rgb * (1 - page)[..., None]
img *= (1 - 0.55 * occl)[..., None]                       # צל מגע על השולחן

# ---------------------------------------------- 11. תאורה משני המשטחים
# אור מלטף: המאקרו נותן את הגלים הרחבים, המיקרו נותן את המרקם עצמו.
# חיתוך קשה שיטח את שניהם קודם; כאן יש רולאוף.
lit = shade(cockle, 14, 0.027) + shade(tooth, 0.0, 0.013)
lam = 1.0 + soft(lit, 0.075)
# האפלת סביבה על גיליון שטוח היא זניחה פיזיקלית: התבליט הוא כעשירית
# מילימטר, ואין מה שיסתיר. בעוצמה גבוהה זה מצטבר לכתמי לכלוך.
ao = 1 - np.clip(ndimage.gaussian_filter(cockle, 45) - cockle, 0, None) * 0.35
mao = 1 - np.clip(-ndimage.gaussian_filter(tooth, 1.6), 0, None) * 0.014
img *= (lam * np.clip(ao, 0.988, 1.0) * mao)[..., None] * page[..., None] \
       + (1 - page)[..., None]

# נפילת אור רחבה על פני הגיליון
falloff = 1.022 - 0.055 * np.clip(np.hypot((X / W - 0.38) * 1.05,
                                           (Y / H - 0.32) * 0.80), 0, 1) ** 1.35
img *= falloff[..., None]
# צל השדרה — הכריכה העברית נכרכת בימין, ולכן הגָּב בצד ימין של הגיליון
gx_n = (1 - X / W) if GUTTER_RIGHT else (X / W)
gutter = 1 - 0.085 * np.clip(1 - gx_n / (9 * PXMM / W), 0, 1) ** 1.6
img *= gutter[..., None]
img[..., 2] *= 1.0 + 0.030 * (1 - falloff)             # צללים נוטים לכחול
img[..., 0] *= 1.0 + 0.020 * (falloff - 1)             # אורות נוטים לחום

# ------------------------------------------------------- 12. המצלמה
# סטייה כרומטית רוחבית: הזכוכית מפצלת צבע, וההפרדה גדלה אל שולי הפריים
def lat_ca(chan, kk):
    return ndimage.map_coordinates(
        chan, [np.clip(H / 2 + (Y - H / 2) * (1 + kk), 0, H - 1),
               np.clip(W / 2 + (X - W / 2) * (1 + kk), 0, W - 1)],
        order=1, mode="nearest")


img[..., 0] = lat_ca(img[..., 0], 0.00042)
img[..., 2] = lat_ca(img[..., 2], -0.00042)

# ריכוך אופטי אל הפינות — עדשה לא נשארת חדה בקצה השדה
soft_img = ndimage.gaussian_filter(img, (0.9, 0.9, 0))
edge_w = np.clip(np.hypot((X / W - 0.5) * 2, (Y / H - 0.5) * 2) - 0.62, 0, 1) ** 1.7
img = img * (1 - edge_w[..., None]) + soft_img * edge_w[..., None]

# גרעיניות תלוית-אות: החיישן רועש יותר בצללים ביחס לאות
lum = img.mean(2, keepdims=True)
gr = ndimage.gaussian_filter(rng.standard_normal((H, W, 3)).astype(np.float32),
                             (0.55, 0.55, 0))
img += gr * (0.0040 + 0.0075 * (1 - np.clip(lum, 0, 1)))

img = np.clip(img, 0, 1)
out = Image.fromarray((img ** (1 / 1.015) * 255).astype(np.uint8))
out = out.filter(ImageFilter.UnsharpMask(radius=1.0, percent=17, threshold=3))

bleed_path = "final_bleed.png"
out.save(bleed_path)
m = round(3 * 300 / 25.4)
out.crop((m, m, W - m, H - m)).save("final_trim.png")
print("done", out.size)
