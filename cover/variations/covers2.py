# -*- coding: utf-8 -*-
"""Nine variations, built on the visual system of the three covers Carmela chose:
ivory stock, one thin slate-indigo line, Frank Ruhl for type,
and two accents only — the red lift-point and the gold mend.
All cover text is HTML, not SVG <text>: SVG bidi is unreliable outside Chrome."""

import math

TITLE1, TITLE2 = "ניצחונות", "קטנים"
TITLE  = "ניצחונות קטנים"
SUB    = "מסע בשלוש מערכות"
AUTHOR = "כרמלה מרינגר-גינת"

INK  = "#3E4A76"   # the drawn line
TYP  = "#2B3358"   # type
RED  = "#D24329"   # the point where the pen left the paper
GOLD = "#C7A22B"   # the mend
HAIR = "#75756D"   # form rules
LAB  = "#8E8E85"   # form labels

# ---------------------------------------------------------------- primitives
def T(cls, top, size, text, extra=""):
    return (f'<div class="tx {cls}" style="top:{top}%;font-size:{size}cqw;{extra}" '
            f'dir="rtl">{text}</div>')

def arc(cx, cy, r, a0, a1, sw, colour, cap="round", op="1"):
    """Open arc in a 540x840 viewBox, angles in degrees, 0 = 3 o'clock."""
    x0, y0 = cx + r*math.cos(math.radians(a0)), cy + r*math.sin(math.radians(a0))
    x1, y1 = cx + r*math.cos(math.radians(a1)), cy + r*math.sin(math.radians(a1))
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    return (f'<path d="M {x0:.1f} {y0:.1f} A {r} {r} 0 {large} {sweep} {x1:.1f} {y1:.1f}" '
            f'fill="none" stroke="{colour}" stroke-width="{sw}" stroke-linecap="{cap}" opacity="{op}"/>')

def ring(cx, cy, r, sw, colour, op="1"):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{colour}" '
            f'stroke-width="{sw}" opacity="{op}"/>')

def dot(cx, cy, r, colour):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{colour}"/>'

def at(cx, cy, r, deg):
    return cx + r*math.cos(math.radians(deg)), cy + r*math.sin(math.radians(deg))

def svg(inner):
    return f'<svg viewBox="0 0 540 840" aria-hidden="true" focusable="false">{inner}</svg>'

def gold_chord(cx, cy, r, deg=-16, over=1.34, gid="mend"):
    """The mend: a straight gold line through a broken circle, fading at both ends.

    The fade starts exactly where the line leaves the ring, so the gold is solid
    everywhere it crosses the blue — otherwise the ramp paints paper-tinted gold
    over the arc and notches it. Stops come from r/L, not from fixed values."""
    dx, dy = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    L = r*over
    edge = min(r/L, 0.97)
    p0, p1 = (1 - edge)/2, (1 + edge)/2
    x0, y0, x1, y1 = cx-dx*L, cy-dy*L, cx+dx*L, cy+dy*L
    grad = (f'<defs><linearGradient id="{gid}" gradientUnits="userSpaceOnUse" '
            f'x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}">'
            f'<stop offset="0" stop-color="{PAPER}"/>'
            f'<stop offset="{p0:.3f}" stop-color="{GOLD}"/>'
            f'<stop offset="{p1:.3f}" stop-color="{GOLD}"/>'
            f'<stop offset="1" stop-color="{PAPER}"/>'
            '</linearGradient></defs>')
    return (grad + f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
            f'stroke="url(#{gid})" stroke-width="7" stroke-linecap="butt"/>')

# ---------------------------------------------------------------- A · טופס 17
def form_rules(top, bottom, n, x0=9.5, x1=90.5):
    step = (bottom - top)/n
    return "".join(f'<i style="top:{top+step*k:.2f}%;right:{x0}%;width:{x1-x0}%"></i>'
                   for k in range(n+1))

def form_frame(t, b, x0=8, x1=92):
    return f'<div class="frame" style="top:{t}%;bottom:{100-b}%;right:{x0}%;left:{100-x1}%"></div>'

def cell(top, h, right, w, labels_right, txt, last=False):
    edge = "" if last else "border-left:1px solid var(--hair);"
    return (f'<div class="cell" style="top:{top}%;height:{h}%;right:{right}%;width:{w}%;{edge}">'
            f'<span dir="rtl">{txt}</span></div>')

def a1():
    """The form as she chose it — reordered so the title is upper and her hand signs it off."""
    s = ['<div class="rules">' + form_rules(30, 88, 8) + '</div>',
         form_frame(6, 92)]
    s.append('<div class="hline" style="top:15%;right:8%;width:84%"></div>')
    s.append(T("form-h", 7.6, 5.0, 'טופס <span dir="ltr">17</span>',
               "text-align:right;padding-right:11%;letter-spacing:.22em"))
    for r, w, lab, lastc in ((8, 27, "שם המבוטחת", False), (35, 27, "מספר זהות", False),
                             (62, 30, "תאריך", True)):
        s.append(cell(15, 8, r, w, True, lab, lastc))
    s.append('<div class="hline" style="top:23%;right:8%;width:84%"></div>')
    for r, w, lab, lastc in ((8, 27, "סעיף", False), (35, 27, "אבחנה", False),
                             (62, 30, "תוקף", True)):
        s.append(cell(23, 7, r, w, True, lab, lastc))
    s.append('<div class="hline" style="top:30%;right:8%;width:84%"></div>')
    s.append(T("form-lab", 30.6, 1.75, "פירוט", "text-align:right;padding-right:11%"))
    s.append(T("sub-red", 34.5, 3.0, SUB, "letter-spacing:.3em"))
    s.append(T("hand-t", 38.5, 15.5, TITLE1, ""))
    s.append(T("hand-t", 50.5, 15.5, TITLE2, ""))
    s.append('<div class="hline" style="top:80%;right:8%;width:84%"></div>')
    s.append('<div class="vline" style="top:80%;height:12%;right:47%"></div>')
    s.append(T("form-lab", 80.8, 1.75, "חתימת הרופא", "text-align:right;padding-right:11%"))
    s.append(T("form-lab", 80.8, 1.75, "תאריך", "text-align:left;padding-left:11%"))
    s.append(T("hand-a", 82.5, 8.6, AUTHOR, ""))
    return "".join(s)

def a2():
    """Same form, but the title is set rather than written — the driest reading of the joke."""
    s = [form_frame(6, 92)]
    s.append('<div class="hline" style="top:15%;right:8%;width:84%"></div>')
    s.append(T("form-h", 7.6, 5.0, 'טופס <span dir="ltr">17</span>',
               "text-align:right;padding-right:11%;letter-spacing:.22em"))
    for r, w, lab, lastc in ((8, 27, "שם המבוטחת", False), (35, 27, "מספר זהות", False),
                             (62, 30, "תאריך", True)):
        s.append(cell(15, 8, r, w, True, lab, lastc))
    s.append('<div class="hline" style="top:23%;right:8%;width:84%"></div>')
    s.append(T("form-lab", 23.7, 1.75, "מהות הבקשה", "text-align:right;padding-right:11%"))
    s.append('<div class="box" style="top:23%;height:27.5%;right:8%;width:84%"></div>')
    s.append(T("t-serif", 29.5, 11.6, TITLE1, ""))
    s.append(T("t-serif", 38.5, 11.6, TITLE2, ""))
    s.append(T("sub-red", 46.4, 2.7, SUB, "letter-spacing:.3em"))
    s.append('<div class="rules">' + form_rules(57, 78, 4) + '</div>')
    s.append(T("form-lab", 51.2, 1.75, "פירוט", "text-align:right;padding-right:11%"))
    s.append('<div class="hline" style="top:80%;right:8%;width:84%"></div>')
    s.append('<div class="vline" style="top:80%;height:12%;right:47%"></div>')
    s.append(T("form-lab", 80.8, 1.75, "חתימת הרופא", "text-align:right;padding-right:11%"))
    s.append(T("form-lab", 80.8, 1.75, "תאריך", "text-align:left;padding-left:11%"))
    s.append(T("hand-a", 82.5, 8.6, AUTHOR, ""))
    return "".join(s)

def a3():
    """No boxes at all: a ruled page with a form number on it."""
    s = ['<div class="rules">' + form_rules(24, 86, 9) + '</div>']
    s.append('<div class="hline" style="top:13%;right:9.5%;width:81%"></div>')
    s.append(T("form-h", 8.2, 3.6, 'טופס <span dir="ltr">17</span>',
               "text-align:right;padding-right:11%;letter-spacing:.3em"))
    s.append(T("form-lab", 9.4, 1.75, "התחייבות לתשלום", "text-align:left;padding-left:11%"))
    s.append(T("sub-red", 20.5, 2.9, SUB, "letter-spacing:.3em"))
    s.append(T("hand-t", 24.5, 15.5, TITLE1, ""))
    s.append(T("hand-t", 36.5, 15.5, TITLE2, ""))
    s.append('<div class="vline" style="top:78%;height:12%;right:47%"></div>')
    s.append(T("form-lab", 78.8, 1.75, "חתימת הרופא", "text-align:right;padding-right:11%"))
    s.append(T("hand-a", 80.5, 8.6, AUTHOR, ""))
    return "".join(s)

# ---------------------------------------------------------------- B · אנסו
def enso_svg(cx, cy, r, sw, a0=-52, a1=258, dotdeg=-52, dr=9):
    dx, dy = at(cx, cy, r, dotdeg)
    return svg(arc(cx, cy, r, a0, a1, sw, INK, "butt") + dot(dx, dy, dr, RED))

def b1():
    """Her cover, with the circle lifted so the title sits in the upper half."""
    return (enso_svg(268, 340, 190, 10) +
            T("t-serif", 29.0, 12.2, TITLE1, "") +
            T("t-serif", 38.4, 12.2, TITLE2, "") +
            T("sub", 47.4, 2.8, SUB, "letter-spacing:.28em") +
            T("auth", 87.0, 3.4, AUTHOR, "letter-spacing:.34em"))

def b2():
    """Title above the circle, so the circle is a mark and not a frame."""
    return (enso_svg(270, 528, 172, 8.5) +
            T("t-serif", 13.0, 12.6, TITLE1, "") +
            T("t-serif", 22.4, 12.6, TITLE2, "") +
            T("sub", 31.6, 2.9, SUB, "letter-spacing:.28em") +
            T("auth", 88.5, 3.4, AUTHOR, "letter-spacing:.34em"))

def b3():
    """One size larger than the page: the circle runs off both edges."""
    return (enso_svg(270, 402, 288, 12, -56, 254, -56, 11) +
            T("t-serif", 21.0, 13.4, TITLE1, "") +
            T("t-serif", 31.1, 13.4, TITLE2, "") +
            T("sub", 40.6, 2.9, SUB, "letter-spacing:.28em") +
            T("auth", 89.5, 3.4, AUTHOR, "letter-spacing:.34em"))

# ------------------------------------------------------- C · שלוש מערכות
PAPER = "#ECE8DF"   # the ivory stock; the mend fades into it rather than to alpha

# Fading to the paper colour instead of to transparency keeps the page vector on
# export — a gradient carrying alpha makes Chrome flatten the whole PDF page to a
# 72dpi bitmap. Both ends of every chord sit over bare paper, so this is identical
# on screen.
MEND_DEF = ""

def c1():
    """Her three acts, stacked — closed, broken and mended, open. Title and name swapped."""
    r, sw = 84, 9
    g = (MEND_DEF
         + ring(270, 265, r, sw, INK)
         + arc(270, 450, r, -66, 246, sw, INK) + gold_chord(270, 450, r, -16, 1.34, "mend1")
         + arc(270, 635, r, -30, 188, sw, INK))
    return (svg(g) +
            T("t-serif", 8.0, 10.2, TITLE, "") +
            T("sub", 16.4, 2.7, SUB, "letter-spacing:.28em") +
            T("auth", 89.5, 3.2, AUTHOR, "letter-spacing:.34em"))

def c2():
    """The same three, laid out right to left — the order the book is read in."""
    r, sw = 104, 9
    cy = 486
    g = (MEND_DEF
         + ring(392, cy, r, sw, INK)
         + arc(270, cy, r, -66, 246, sw, INK) + gold_chord(270, cy, r, -16, 1.24, "mend2")
         + arc(148, cy, r, -30, 188, sw, INK))
    return (svg(g) +
            T("t-serif", 15.0, 11.6, TITLE, "") +
            T("sub", 24.4, 2.9, SUB, "letter-spacing:.28em") +
            T("act", 76.0, 2.0, '<span>מערכה א׳</span><span>מערכה ב׳</span><span>מערכה ג׳</span>',
              "letter-spacing:.2em") +
            T("auth", 87.5, 3.4, AUTHOR, "letter-spacing:.34em"))

def c3():
    """Three circles on one centre, each more open than the last."""
    g = (MEND_DEF
         + ring(270, 530, 78, 9, INK)
         + arc(270, 530, 132, -66, 246, 9, INK) + gold_chord(270, 530, 132, -16, 1.06, "mend3")
         + arc(270, 530, 186, -30, 188, 9, INK))
    return (svg(g) +
            T("t-serif", 10.5, 11.8, TITLE, "") +
            T("sub", 19.8, 2.9, SUB, "letter-spacing:.28em") +
            T("auth", 89.5, 3.4, AUTHOR, "letter-spacing:.34em"))

COVERS = {"a1": a1, "a2": a2, "a3": a3, "b1": b1, "b2": b2, "b3": b3,
          "c1": c1, "c2": c2, "c3": c3}
