# -*- coding: utf-8 -*-
import covers2, proofcss

def cover(key, n, name, note):
    cid = f"cap-{key}"
    cls = "form" if key.startswith("a") else ""
    return f'''<figure class="cover">
  <button class="shot" type="button" aria-label="להגדלה: {name}">
    <div class="cv {cls}" role="img" aria-labelledby="{cid}">{covers2.COVERS[key]()}</div>
  </button>
  <figcaption id="{cid}"><span class="vnum">{n}</span><b>{name}</b>{note}</figcaption>
</figure>'''

CONCEPTS = [
 dict(id="tofes", tag="א", he="טופס 17", en="הטופס שהיא ממלאת בעצמה",
   lead="""המקור שלך עושה דבר אחד חד: הכותרת כתובה בכתב ידך וחוצה את קווי הטופס, ו<b>שמך
   חתום על שורת חתימת הרופא</b>. לא המבוטחת חותמת — היא חותמת במקומו. זה כל הרעיון,
   והוא נשמר בשלוש הגרסאות.""",
   why="""זו היחידה מהשלוש שמצחיקה, והספר מצחיק. הבדיחה אינה קריקטורה אלא שגיאת קטגוריה —
   מסמך מנהלי שמחליף את המחלה — ולכן היא לא מתעייפת כמו בדיחה מצוירת. תת־הכותרת באדום
   היא הצבע היחיד בעטיפה, וזה מה שמחזיק אותה.""",
   risk="""ככל שיש יותר משבצות, כך גדל הסיכוי שהעטיפה תיקרא כטופס אמיתי ולא כספר. שלוש
   הגרסאות נבדלות בעיקר בכמות הטופס, ובשאלה אחת: האם הכותרת בכתב יד או מודפסת.""",
   covers=[("a1","1","הטופס המלא","המקור שלך, עם הכותרת מוזזת למעלה. כתב היד חוצה את הקווים והחתימה על שורת הרופא."),
           ("a2","2","הכותרת מודפסת","אותו טופס, אבל הכותרת מוקלדת בתוך שדה. הבדיחה יבשה יותר, החתימה עדיין בכתב יד."),
           ("a3","3","בלי משבצות","מספר הטופס, הקווים והחתימה בלבד. הכי קרובה לדף אמיתי מתוך תיק.")]),
 dict(id="enso", tag="ב", he="האנסו", en="קו אחד שאינו נסגר",
   lead="""קו כחול דק אחד, נפתח בראש, ונקודה אדומה במקום שבו העט הורם. הכותרת יושבת
   <b>בתוך</b> העיגול. זה כל מה שיש על העטיפה, וזה מספיק.""",
   why="""היחידה מהשלוש שאין בה שום דבר מצויר — רק סימן אחד של יד. היא גם הכי זולה
   להפקה: שני צבעים, בלי הדפסה מיוחדת. והפתח בעיגול אינו פגם אלא הסירוב להיסגר.""",
   risk="""הכול תלוי במשיכה אחת. אם הקו לא מדויק, אין לה מאחורי מה להסתתר. שווה לבדוק
   על חמישה אנשים שהעיגול לא נקרא כאפס או כאות ס.""",
   covers=[("b1","1","המעגל מוגבה","המקור שלך. העיגול עלה מעט כדי שהכותרת תשב בחציו העליון והשם ינשום למטה."),
           ("b2","2","הכותרת מעל","העיגול יורד ונעשה סימן ולא מסגרת. השקטה מהתשע."),
           ("b3","3","גדול מהדף","העיגול נחתך בשני הצדדים. הכי חזקה בממוזערת מכל התשע.")]),
 dict(id="shalosh", tag="ג", he="שלוש מערכות", en="שלושה מעגלים, לא שלושה דפים",
   lead="""שלושה מעגלים: הראשון סגור, השני נשבר ומאוחה בקו זהב, השלישי פתוח ונשאר פתוח.
   במקור שלך השם למעלה והכותרת למטה — כאן זה <b>מוחלף</b>, לפי מה שביקשת.""",
   why="""היחידה שמראה את מבנה הספר עצמו במקום פרט מתוכו, ולכן תת־הכותרת בה אינה חזרה
   אלא הוראת קריאה. קו הזהב הוא הרכיב היחיד שעולה כסף בדפוס — והוא שווה את זה.""",
   risk="""בגודל בול היא החלשה מהשלוש: שלושה מעגלים קטנים נקראים כדיאגרמה. אם הולכים
   לכאן, הכותרת צריכה לגדול.""",
   covers=[("c1","1","טור","הסידור שלך, עם הכותרת למעלה והשם למטה."),
           ("c2","2","שורה","שלושתם זה על זה, נקראים מימין לשמאל — סדר הקריאה העברי."),
           ("c3","3","מרכז אחד","אותו מרכז, כל מעגל פתוח מקודמו. הזמן נקרא מבפנים החוצה.")]),
]

sections = []
for c in CONCEPTS:
    shots = "\n".join(cover(*x) for x in c["covers"])
    sections.append(f'''<section class="concept" id="{c['id']}">
  <header class="chead">
    <span class="ctag" aria-hidden="true">{c['tag']}</span>
    <h2>{c['he']}<span class="cen">{c['en']}</span></h2>
  </header>
  <div class="cbody">
    <p class="lead">{c['lead']}</p>
    <div class="notes">
      <div><h3>למה זה עובד</h3><p>{c['why']}</p></div>
      <div><h3>איפה זה עלול ליפול</h3><p>{c['risk']}</p></div>
    </div>
  </div>
  <div class="grid">
{shots}
  </div>
</section>''')

HTML = f'''<title>תשע עטיפות</title>
<style>
{proofcss.FONTS}
:root{{
  --ground:#DEDACF; --panel:#EFECE4; --hair:#C5C0B2; --rule:#B6B0A0;
  --text:#232A45; --dim:#565C70; --faint:#868B99;
  --accent:#3E4A76; --red:#C24229; --gold:#A8871F;
  --shadow:0 1px 2px rgba(35,42,69,.10),0 14px 34px rgba(35,42,69,.16);
  --heb:FRL,"Frank Ruhl Libre","New Peninim MT","Times New Roman",serif;
  --sans:"Arial Hebrew",-apple-system,"Helvetica Neue",Arial,sans-serif;
}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{
  --ground:#141620; --panel:#1C1F2B; --hair:#2C3040; --rule:#3A3F52;
  --text:#E7E5DD; --dim:#A3A7B6; --faint:#7B8090;
  --accent:#98A3E4; --red:#DC8471; --gold:#D6BC63;
  --shadow:0 1px 2px rgba(0,0,0,.5),0 16px 40px rgba(0,0,0,.55);
}}}}
:root[data-theme="dark"]{{
  --ground:#141620; --panel:#1C1F2B; --hair:#2C3040; --rule:#3A3F52;
  --text:#E7E5DD; --dim:#A3A7B6; --faint:#7B8090;
  --accent:#98A3E4; --red:#DC8471; --gold:#D6BC63;
  --shadow:0 1px 2px rgba(0,0,0,.5),0 16px 40px rgba(0,0,0,.55);
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--text);font-family:var(--heb);
  font-size:18.5px;line-height:1.7;direction:rtl;text-align:right;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1160px;margin:0 auto;padding:clamp(26px,5vw,60px) clamp(16px,4vw,40px) 96px}}
.hero{{border-bottom:1px solid var(--text);padding-bottom:30px}}
.eyebrow{{font-family:var(--sans);font-size:11.5px;letter-spacing:.2em;color:var(--faint);margin:0 0 20px}}
.eyebrow .hand{{font-family:Hand;font-size:21px;letter-spacing:0;color:var(--accent);vertical-align:-4px}}
h1{{font-size:clamp(30px,5.6vw,50px);line-height:1.16;margin:0 0 20px;font-weight:500;
  letter-spacing:-.005em;text-wrap:balance}}
.stand{{max-width:58ch;color:var(--dim);font-size:19px;margin:0 0 14px}}
.stand b{{color:var(--text);font-weight:500}}
.bar{{display:flex;flex-wrap:wrap;gap:14px;align-items:center;margin:28px 0 0;padding:16px 0 0;
  border-top:1px solid var(--hair);font-family:var(--sans);font-size:13px;color:var(--faint)}}
.bar span{{max-width:56ch}}
button.tool{{font-family:var(--sans);font-size:12.5px;letter-spacing:.06em;color:var(--text);
  background:var(--panel);border:1px solid var(--rule);padding:9px 16px;cursor:pointer}}
button.tool[aria-pressed="true"]{{background:var(--text);color:var(--ground);border-color:var(--text)}}
button.tool:hover{{border-color:var(--text)}}
:focus-visible{{outline:2px solid var(--accent);outline-offset:3px}}
.concept{{margin:76px 0 0;padding-top:28px;border-top:1px solid var(--hair)}}
.concept:first-of-type{{border-top:0;padding-top:0;margin-top:64px}}
.chead{{display:flex;align-items:baseline;gap:16px;margin:0 0 20px}}
.ctag{{font-family:var(--sans);font-size:13px;color:var(--gold);border:1px solid var(--gold);
  width:28px;height:28px;flex:0 0 28px;display:grid;place-items:center;border-radius:50%;
  transform:translateY(2px)}}
h2{{margin:0;font-size:clamp(26px,4vw,36px);font-weight:500;display:flex;flex-wrap:wrap;
  align-items:baseline;gap:14px}}
.cen{{font-family:var(--sans);font-size:14px;font-weight:400;color:var(--faint);letter-spacing:.04em}}
.cbody{{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:clamp(20px,4vw,48px);
  align-items:start}}
.lead{{margin:0;max-width:50ch}}
.lead b{{font-weight:500}}
.notes{{display:flex;flex-direction:column;gap:18px;background:var(--panel);
  border:1px solid var(--hair);padding:20px 22px}}
.notes h3{{font-family:var(--sans);font-size:11px;letter-spacing:.16em;color:var(--faint);
  margin:0 0 5px;font-weight:400}}
.notes p{{margin:0;font-size:16.5px;line-height:1.66;color:var(--dim)}}
.notes b{{color:var(--text);font-weight:500}}
.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(16px,3vw,34px);
  margin:34px 0 0;align-items:start}}
figure.cover{{margin:0;display:flex;flex-direction:column;gap:12px}}
.shot{{padding:0;border:0;background:none;cursor:zoom-in;display:block;width:100%}}
figcaption{{font-family:var(--sans);font-size:13px;line-height:1.6;color:var(--dim)}}
figcaption b{{display:block;color:var(--text);font-size:14.5px;font-weight:400;margin-bottom:2px;
  font-family:var(--heb)}}
.vnum{{float:left;font-size:11px;color:var(--faint);letter-spacing:.1em;padding-right:8px}}
body.thumbs .grid{{justify-items:center}}
body.thumbs .shot{{width:100px}}
body.thumbs figcaption{{display:none}}
.close{{margin:88px 0 0;padding-top:30px;border-top:1px solid var(--text)}}
.close h2{{font-size:clamp(24px,3.6vw,32px);margin:0 0 18px;display:block}}
.close ol{{margin:0;padding-inline-start:24px;max-width:60ch}}
.close li{{margin-bottom:14px}}
.close li b{{font-weight:500}}
.caveat{{margin:42px 0 0;padding-top:20px;border-top:1px solid var(--hair);font-family:var(--sans);
  font-size:13.5px;line-height:1.85;color:var(--faint);max-width:62ch}}
.caveat b{{color:var(--dim);font-weight:400}}
dialog.lb{{border:0;padding:0;background:none;max-width:100vw;max-height:100vh}}
dialog.lb::backdrop{{background:rgba(14,15,22,.88)}}
dialog.lb .cv{{height:min(92vh,1040px);width:auto;box-shadow:0 30px 90px rgba(0,0,0,.5)}}
dialog.lb form{{position:fixed;top:16px;left:16px}}
dialog.lb button{{font-family:var(--sans);font-size:12px;letter-spacing:.1em;background:#EFECE4;
  color:#232A45;border:0;padding:9px 15px;cursor:pointer}}
@media screen and (max-width:860px){{
  .cbody{{grid-template-columns:1fr}}
  .grid{{grid-template-columns:1fr;gap:28px}}
  body.thumbs .grid{{grid-template-columns:repeat(3,minmax(0,1fr))}}
}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;transition:none!important}}}}
@page{{size:A4;margin:14mm}}
@media print{{
  :root{{
    --ground:#fff; --panel:#F2EFE7; --hair:#C5C0B2; --rule:#B6B0A0;
    --text:#232A45; --dim:#4C5266; --faint:#7A7F8D;
    --accent:#3E4A76; --red:#C24229; --gold:#8E7119;
    --shadow:0 0 0 1px rgba(35,42,69,.10);
  }}
  body{{background:#fff;font-size:11pt}}
  .wrap{{max-width:none;padding:0}}
  .bar,dialog.lb{{display:none!important}}
  .shot{{cursor:default}}
  h1{{font-size:24pt}} h2{{font-size:16pt}}
  .stand{{font-size:11.5pt}}
  .concept{{margin-top:0;padding-top:0;border-top:0;
    page-break-before:always;break-before:page}}
  .concept:first-of-type{{page-break-before:always;break-before:page}}
  .chead{{margin-bottom:10pt}}
  .cbody{{display:flex;gap:10mm;align-items:flex-start;
    break-inside:avoid;page-break-inside:avoid}}
  .lead{{flex:1 1 55%;max-width:none}}
  .notes{{flex:1 1 45%}}
  .notes p{{font-size:10pt;line-height:1.5}}
  .grid{{display:flex;gap:7mm;align-items:flex-start;margin-top:9mm;
    break-inside:avoid;page-break-inside:avoid}}
  figure.cover{{flex:1 1 0;min-width:0;gap:5pt;
    break-inside:avoid;page-break-inside:avoid}}
  figure.cover .shot,figure.cover .cv{{width:100%}}
  figcaption{{font-size:8.5pt;line-height:1.45}}
  figcaption b{{font-size:9.5pt;margin-bottom:1pt}}
  .close{{page-break-before:always;break-before:page;margin-top:0;padding-top:0;border-top:0}}
  .close ol{{max-width:none}} .caveat{{max-width:none}}
}}
{proofcss.COVERCSS}
</style>

<div class="wrap">
<header class="hero">
  <p class="eyebrow"><span class="hand">ניצחונות קטנים</span> &nbsp;·&nbsp; כרמלה מרינגר-גינת &nbsp;·&nbsp; שלושה קונספטים, תשע גרסאות</p>
  <h1>שלוש העטיפות שבחרת, כל אחת בשלוש גרסאות</h1>
  <p class="stand">הבסיס כאן הוא שלוש העטיפות עצמן ששלחת, ולא תיאור שלהן: <b>אותו נייר שנהב,
  אותו קו כחול דק, אותו פרנק־ריהל, אותה נקודה אדומה, אותו קו זהב</b>.
  אף גרסה כאן אינה מתחילה מחדש — כולן וריאציות על מה שכבר עובד.</p>
  <p class="stand">שני השינויים שביקשת נעשו בכל תשע: השם הוא <b>כרמלה מרינגר-גינת</b>,
  <b>שם הספר בחלק העליון ושם המחברת בחלק התחתון</b>. בשלוש מערכות זה אומר שהשם והכותרת
  החליפו מקומות ביחס למקור שלך. <b>שכבת כתב היד החיוורת הוסרה</b> — הנייר נקי בכל התשע.</p>
  <div class="bar">
    <button class="tool" type="button" id="thumb" aria-pressed="false">מבחן הממוזערת</button>
    <span>מכווץ הכול ל־100 פיקסלים — הגודל שבו רואים ספר בחנות מקוונת.
    לחיצה על עטיפה פותחת אותה בגודל מלא.</span>
  </div>
</header>

{"".join(sections)}

<section class="close">
  <h2>מה הייתי בוחר</h2>
  <ol>
    <li><b>ב1 · המעגל מוגבה.</b> זו העטיפה שלך, בלי שאיבדה דבר: הכותרת עלתה,
    השם ירד, והסימן נשאר בדיוק מה שהיה. אין בה שום דבר מצויר, והיא הזולה ביותר להפקה.</li>
    <li><b>ב3 · גדול מהדף</b> — אם את רוצה שיבחינו בה על מדף. אותו רעיון בדיוק, בעוצמה
    אחרת. במבחן הממוזערת היא ניצחה את כל השאר, ולא במעט.</li>
    <li><b>א1 · הטופס המלא.</b> היחידה שמצחיקה, וזו סיבה טובה. הפתעה אחת: כתב היד
    שורד את מבחן הממוזערת <em>טוב יותר</em> מהכותרת המודפסת שבגרסה 2, כי הוא פשוט גדול
    וכהה יותר.</li>
    <li><b>ג2 · שורה.</b> החזקה מבין השלוש של הקונספט הזה. אבל שימי לב שכל משפחת
    שלוש מערכות היא החלשה בגודל בול — הכותרת שם צריכה לגדול לפני שמחליטים.</li>
  </ol>
  <p class="caveat">שלוש הערות. <b>העברית ההפוכה שראית</b> נבעה מכך שהטקסט בעטיפות
  נבנה כטקסט של SVG, שהיפוך הכיוון בו אינו אמין מחוץ לכרום; עכשיו כל טקסט בעטיפה הוא HTML
  ונבדק. <b>הגופן הוא פרנק־ריהל אמיתי</b> ברישיון חופשי, כמו במקור שלך.
  <b>כתב היד שנשאר</b> — הכותרת והחתימה בטופס 17 — הוא גופן גברת לוין, ולא היד שלך;
  בהפקה כדאי לסרוק את הכתב האמיתי. <b>ושם המחברת נכתב
  עם מקף רגיל</b> כפי שנמסר; בדפוס עברי נהוג מקף עברי (מרינגר־גינת). הגב עדיין חסר.</p>
</section>
</div>

<dialog class="lb" id="lb">
  <form method="dialog"><button type="submit">סגירה ✕</button></form>
  <div id="lbslot"></div>
</dialog>
<script>
(function(){{
  var body=document.body, tb=document.getElementById('thumb');
  tb.addEventListener('click',function(){{
    var on=body.classList.toggle('thumbs');
    tb.setAttribute('aria-pressed',on?'true':'false');
  }});
  var lb=document.getElementById('lb'), slot=document.getElementById('lbslot');
  document.querySelectorAll('.shot').forEach(function(b){{
    b.addEventListener('click',function(){{
      slot.innerHTML='';
      slot.appendChild(b.querySelector('.cv').cloneNode(true));
      if(lb.showModal) lb.showModal();
    }});
  }});
  lb.addEventListener('click',function(e){{ if(e.target===lb) lb.close(); }});
}})();
</script>
'''
open("../nine-covers.html","w",encoding="utf-8").write(HTML)
print("written", len(HTML))
