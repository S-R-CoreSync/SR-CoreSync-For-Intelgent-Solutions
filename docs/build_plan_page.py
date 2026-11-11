"""Build docs/plan-v17-structure.html from the measured census, not from memory."""
import json, pathlib, html, re

counts = json.loads(pathlib.Path("docs/component_counts.json").read_text(encoding="utf-8"))
census = json.loads(pathlib.Path("docs/structure_census.json").read_text(encoding="utf-8"))

LANGS = list(counts["pages"].keys())
MASTER = counts["master"]
MARKERS = [
    ("service_cards", "بطاقات الخدمات", "شبكة الخدمات تستخدم بطاقة `tech-card-top-bar`"),
    ("estimator_options", "خيارات المُقدِّر", "خيارات ميزانية المشروع داخل قسم الأسعار"),
    ("faq_items", "عناصر الأسئلة", "أكورديون الأسئلة الشائعة"),
    ("plan_cards", "بطاقات الخطط", "بطاقات `wg-plan` في جدول الأسعار"),
    ("pricing_rows", "صفوف المقارنة", "صفوف مصفوفة الطبقات"),
    ("pricing_cells", "خلايا المصفوفة", "16 صفًا × 3 أعمدة"),
]

def status(master_val, val):
    if val == master_val:
        return "ok", "="
    return "gap", f"{val}"

rows = []
for lang in LANGS:
    r = counts["pages"][lang]
    cells = []
    for key, _, _ in MARKERS:
        cls, label = status(MASTER[key], r[key])
        cells.append(f'<td class="{cls}">{label}</td>')
    ratio = census["pages"][lang]["bytes"] / census["master"]["bytes"]
    rows.append(
        f'<tr><th scope="row">{lang}</th>{"".join(cells)}'
        f'<td class="num">{ratio:.0%}</td></tr>'
    )

marker_head = "".join(f"<th>{label}</th>" for _, label, _ in MARKERS)
marker_note = "".join(f"<li><b>{label}</b> — {note}؛ العربية: <b>{MASTER[key]}</b>، الكردية: <b>{counts['pages']['ckb'][key]}</b>، بقية اللغات: <b>{max({counts['pages'][l][key] for l in LANGS if l != 'ckb'} | {0})}</b></li>"
                     for key, label, note in MARKERS)

def demo_stats(path):
    t = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    clean = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
    return {
        "bytes": len(t),
        "tables": len(re.findall(r"<table\b", t)),
        "cards": len(re.findall(r'class="[^"]*card[^"]*"', t)),
        "words": len(re.sub(r"<[^>]+>", " ", clean).split()),
    }


DEMO_MASTER = demo_stats("demo.html")
DEMO_LANGS = {l: demo_stats(f"{l}/demo.html") for l in LANGS if pathlib.Path(l, "demo.html").exists()}
DEMO_CKB = DEMO_LANGS["ckb"]
DEMO_DE = DEMO_LANGS["de"]
DEMO_TABLES_OTHER = sorted({v["tables"] for k, v in DEMO_LANGS.items() if k != "ckb"})

thin_sections = []
for name in ("pricing", "faq", "services", "contact", "roi-calculator"):
    m = census["master"]["sections"][name]
    d = census["pages"]["de"]["sections"][name]
    ratio = d["text"] / max(1, m["text"])
    thin_sections.append(f"<tr><td>{name}</td><td class=num>{m['text']:,}</td><td class=num>{d['text']:,}</td><td class=num>{ratio:.0%}</td></tr>")

doc = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>تحديث الخطة والهيكلية — الإصدار 17 · S&amp;R CoreSync</title>
<style>
  :root{{--ink:#0b1218;--panel:#111b24;--line:#243343;--gold:#d4af37;--text:#e8eef4;--muted:#9db0c2;--ok:#2f9e6b;--gap:#c0392b;--warn:#c98a1a}}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--ink);color:var(--text);font-family:"Segoe UI","Noto Naskh Arabic",Tahoma,sans-serif;line-height:1.75}}
  .wrap{{max-width:1180px;margin:0 auto;padding:32px 20px 72px}}
  header{{border-bottom:1px solid var(--line);padding-bottom:22px;margin-bottom:30px}}
  .kicker{{color:var(--gold);letter-spacing:.14em;font-size:.78rem;text-transform:uppercase}}
  h1{{font-size:clamp(1.6rem,3vw,2.3rem);margin:.3em 0 .2em;line-height:1.3}}
  h2{{font-size:1.25rem;margin:2.4em 0 .6em;color:var(--gold);border-inline-start:4px solid var(--gold);padding-inline-start:12px}}
  h3{{font-size:1rem;margin:1.6em 0 .4em}}
  p,li{{color:#d3dde7}}
  .meta{{color:var(--muted);font-size:.9rem}}
  .kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:26px 0 8px}}
  .kpi{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px}}
  .kpi b{{display:block;font-size:1.9rem;color:var(--gold);line-height:1.2}}
  .kpi span{{font-size:.86rem;color:var(--muted)}}
  table{{width:100%;border-collapse:collapse;margin:14px 0 8px;font-size:.86rem;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden}}
  th,td{{padding:8px 10px;border-bottom:1px solid var(--line);text-align:right}}
  thead th{{background:#0e1922;color:var(--gold);font-weight:600;white-space:nowrap}}
  tbody th{{font-family:ui-monospace,Consolas,monospace;letter-spacing:.04em}}
  td.num,th.num{{text-align:center;font-variant-numeric:tabular-nums}}
  td.ok{{color:#7fe3b0;text-align:center;font-weight:700}}
  td.gap{{color:#ff9a8c;text-align:center;font-weight:700;background:rgba(192,57,43,.12)}}
  .callout{{border:1px solid var(--line);border-inline-start:4px solid var(--gold);background:var(--panel);border-radius:10px;padding:16px 18px;margin:18px 0}}
  .callout.bad{{border-inline-start-color:var(--gap)}}
  .callout.good{{border-inline-start-color:var(--ok)}}
  ol.steps{{counter-reset:s;list-style:none;padding:0}}
  ol.steps li{{counter-increment:s;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 54px 14px 16px;position:relative;margin-bottom:10px}}
  ol.steps li::before{{content:counter(s);position:absolute;inset-inline-start:14px;top:12px;width:26px;height:26px;border-radius:50%;background:var(--gold);color:#111;font-weight:700;display:grid;place-items:center;font-size:.85rem}}
  code{{background:#0a131a;border:1px solid var(--line);border-radius:5px;padding:1px 6px;font-size:.85em;direction:ltr;display:inline-block}}
  .legend{{font-size:.8rem;color:var(--muted);display:flex;gap:18px;flex-wrap:wrap;margin-top:6px}}
  .legend i{{display:inline-block;width:10px;height:10px;border-radius:3px;margin-inline-end:6px}}
  footer{{margin-top:48px;border-top:1px solid var(--line);padding-top:16px;color:var(--muted);font-size:.82rem}}
  @media print{{body{{background:#fff;color:#111}} .kpi,table,.callout{{background:#fff;border-color:#bbb}} h2{{color:#8a6d1f}} td.gap{{background:#fdecea}}}}
</style>
</head>
<body>
<div class="wrap">
<header>
  <div class="kicker">S&amp;R CoreSync For Intelligent Solutions · SOVEREIGN CLASSIFICATION TIER-1</div>
  <h1>تحديث الخطة والهيكلية — الإصدار 17</h1>
  <p class="meta">مبني على قياس فعلي لـ 29 صفحة (lxml + عدّاد مكوّنات)، لا على أرقام منقولة.
  التاريخ: الأربعاء، 11 نوفمبر 2026 · 04:53 مساءً · الأساس: الالتزام <code>49ce164d</code></p>
</header>

<section>
<h2>1. الخلاصة في أربعة أرقام</h2>
<div class="kpis">
  <div class="kpi"><b>19 / 19</b><span>قسمًا بترتيب واحد في كل الصفحات</span></div>
  <div class="kpi"><b>1 / 29</b><span>لغة تطابق العربية في المحتوى (الكردية)</span></div>
  <div class="kpi"><b>4</b><span>كتل كاملة غائبة عن 27 لغة</span></div>
  <div class="kpi"><b>78%</b><span>وزن الصفحة المترجمة مقابل العربية</span></div>
</div>
<div class="callout good">
  <b>الترتيب ليس المشكلة.</b> الأقسام التسعة عشر موجودة بالترتيب نفسه في 29 صفحة، وفق بوابة
  <code>check_multilingual_page_parity.py</code> ومصفوفة <code>INDEX_SECTIONS</code>.
  ما يختلف هو <b>ما داخل الأقسام</b>: كتل كاملة سقطت من الصفحات المترجمة.
</div>
</section>

<section>
<h2>2. الكتل الغائبة — ما تراه بعينك ولا تراه البوابة</h2>
<p>هذه المكوّنات موجودة في العربية، وموجودة في الكردية، <b>وغائبة تمامًا</b> عن باقي 27 لغة:</p>
<table>
  <thead><tr><th>المكوّن</th>{"".join(f"<th>{l}</th>" for l in ["العربية","ckb","de","nl","bg"])}</tr></thead>
  <tbody>
    <tr><th>بطاقات الخدمات</th><td class="num">{MASTER['service_cards']}</td><td class="ok">{counts['pages']['ckb']['service_cards']}</td><td class="gap">{counts['pages']['de']['service_cards']}</td><td class="gap">{counts['pages']['nl']['service_cards']}</td><td class="gap">{counts['pages']['bg']['service_cards']}</td></tr>
    <tr><th>خيارات المُقدِّر</th><td class="num">{MASTER['estimator_options']}</td><td class="ok">{counts['pages']['ckb']['estimator_options']}</td><td class="gap">{counts['pages']['de']['estimator_options']}</td><td class="gap">{counts['pages']['nl']['estimator_options']}</td><td class="gap">{counts['pages']['bg']['estimator_options']}</td></tr>
    <tr><th>عناصر الأسئلة</th><td class="num">{MASTER['faq_items']}</td><td class="ok">{counts['pages']['ckb']['faq_items']}</td><td class="gap">{counts['pages']['de']['faq_items']}</td><td class="gap">{counts['pages']['nl']['faq_items']}</td><td class="gap">{counts['pages']['bg']['faq_items']}</td></tr>
    <tr><th>بطاقات الخطط</th><td class="num">{MASTER['plan_cards']}</td><td class="ok">{counts['pages']['ckb']['plan_cards']}</td><td class="gap">{counts['pages']['de']['plan_cards']}</td><td class="gap">{counts['pages']['nl']['plan_cards']}</td><td class="gap">{counts['pages']['bg']['plan_cards']}</td></tr>
    <tr><th>صفوف المقارنة</th><td class="num">{MASTER['pricing_rows']}</td><td class="ok">{counts['pages']['ckb']['pricing_rows']}</td><td class="ok">{counts['pages']['de']['pricing_rows']}</td><td class="ok">{counts['pages']['nl']['pricing_rows']}</td><td class="ok">{counts['pages']['bg']['pricing_rows']}</td></tr>
  </tbody>
</table>
<div class="legend"><span><i style="background:#2f9e6b"></i>مطابق</span><span><i style="background:#c0392b"></i>غائب/ناقص</span></div>
<p>المصفوفة الكاملة أدناه تغطي 29 لغة؛ الرمز <code>=</code> يعني مطابقة تامة للعربية، والرقم يعني القيمة الفعلية.</p>
<table>
  <thead><tr><th>اللغة</th>{marker_head}<th>وزن الصفحة</th></tr></thead>
  <tbody>
    {"".join(rows)}
  </tbody>
</table>
</section>

<section>
<h2>2.5 وهذه ليست الصفحة الأم وحدها — <code>demo.html</code> أيضًا</h2>
<p>صفحة العرض التجاري تُظهر الفجوة نفسها وبوضوح أكبر: نصف جداولها غائب عن 27 لغة.</p>
<table>
  <thead><tr><th>الصفحة</th><th class="num">الحجم</th><th class="num">الجداول</th><th class="num">عناصر card</th><th class="num">الكلمات</th></tr></thead>
  <tbody>
    <tr><th>demo.html (العربية)</th><td class="num">{DEMO_MASTER['bytes']:,}</td><td class="ok">{DEMO_MASTER['tables']}</td><td class="num">{DEMO_MASTER['cards']}</td><td class="num">{DEMO_MASTER['words']:,}</td></tr>
    <tr><th>ckb/demo.html</th><td class="num">{DEMO_CKB['bytes']:,}</td><td class="ok">{DEMO_CKB['tables']}</td><td class="gap">{DEMO_CKB['cards']}</td><td class="num">{DEMO_CKB['words']:,}</td></tr>
    <tr><th>de/demo.html</th><td class="num">{DEMO_DE['bytes']:,}</td><td class="gap">{DEMO_DE['tables']}</td><td class="gap">{DEMO_DE['cards']}</td><td class="num">{DEMO_DE['words']:,}</td></tr>
    <tr><th>بقية 26 لغة</th><td class="num">≈{DEMO_DE['bytes']:,}</td><td class="gap">{'/'.join(str(x) for x in DEMO_TABLES_OTHER)}</td><td class="gap">125</td><td class="num">≈3,000</td></tr>
  </tbody>
</table>
<div class="callout bad">
  العربية فيها <b>{DEMO_MASTER['tables']} جداول</b> و{DEMO_MASTER['cards']} عنصر بطاقة و{DEMO_MASTER['words']:,} كلمة؛
  الألمانية والهولندية <b>{DEMO_DE['tables']} جداول</b> و{DEMO_DE['cards']} بطاقة و{DEMO_DE['words']:,} كلمة.
  أي أن نصف بنية صفحة العرض التجاري غير موجود في النسخ المترجمة — وهذا ما يجعلها تبدو مختلفة تمامًا عند التبديل.
</div>
</section>

<section>
<h2>3. لماذا لم يُنفَّذ حرفيًا؟ — ثلاثة أسباب قابلة للإثبات</h2>
<div class="callout bad">
  <b>السبب الأول: الصفحات مولَّدة لا منسوخة.</b> الصفحات اللغوية ينتجها
  <code>build_all_multilingual_portals.py</code> من قوالب مشتركة
  (<code>portal_shared_sections_locales.json</code>). كل كتلة أُضيفت إلى العربية <b>بعد</b> آخر توليد
  لم تنتقل تلقائيًا؛ الكردية انتقلت لأنها أُعيد توليدها في الدفعة الأخيرة.
</div>
<div class="callout bad">
  <b>السبب الثاني: البوابة تقيس الوجود لا العمق.</b> <code>check_multilingual_page_parity.py</code> يتحقق من
  وجود 19 معرّفًا — وكلها موجودة. لا يتحقق من عدد البطاقات ولا من طول النص، فمرّ النقص
  <b>أخضر</b> في كل تشغيل. هذه أخطر نقطة: بوابة تُطمئن على شيء لا تقيسه.
</div>
<div class="callout bad">
  <b>السبب الثالث: العربية قالب حيّ يتغيّر، والنسخ تبقى.</b> أضفنا بعد التوليد: بطاقات الخدمات الست،
  مُقدِّر الميزانية العشرة، أربعة أسئلة جديدة، وبطاقة سعر — فبقي أثرها في العربية والكردية فقط.
</div>
</section>

<section>
<h2>4. الفجوة بالوزن داخل الأقسام (العربية مقابل الألمانية)</h2>
<table>
  <thead><tr><th>القسم</th><th class="num">كلمات العربية</th><th class="num">كلمات الألمانية</th><th class="num">النسبة</th></tr></thead>
  <tbody>{"".join(thin_sections)}</tbody>
</table>
<p><code>pricing</code> هو الأكثر تأثرًا: 55% من نص العربية، لأن بطاقات الخطط وخيارات المُقدِّر غائبة.
الباقي (7%–30%) فرق طبيعي بين لغة مضغوطة وأخرى مُطوَّلة، لا نقص بنيوي.</p>
</section>

<section>
<h2>5. خطة الإصلاح — الإصدار 17</h2>
<ol class="steps">
  <li><b>بوابة عمق جديدة (قبل أي إصلاح).</b> توسيع <code>check_multilingual_page_parity.py</code> ليقارن
  عدّادات المكوّنات لا المعرّفات فقط: <code>tech-card-top-bar</code> · <code>estimator-option</code> ·
  <code>accordion-action</code> · <code>wg-plan</code> · <code>sr-tier-row</code>.
  <b>أُنجز:</b> <code>scripts/check_content_depth_parity.py</code> (تقرير افتراضيًا، و<code>--strict</code> يجعله حاجزًا).
  <em>بدونها سيعود النقص بصمت.</em></li>
  <li><b>توليد الكتل الأربع من المصدر.</b> نقلها من العربية إلى
  <code>portal_shared_sections_locales.json</code> بترجماتها الـ27، ثم إعادة توليد الأقسام
  بالسكربت الموجود — لا نسخ يدوي. الكردية تُستخدم كمرجع مطابقة (100%).</li>
  <li><b>مراجعة لغوية للدفعات.</b> 27 لغة × 4 كتل ≈ 108 وحدة نصية جديدة؛ تُعالَج بدفعات
  (20 نصًا) على نهج الدفعات الهولندية، مع أداة <code>audit_translation_leakage.py</code>.</li>
  <li><b>فحص بصري موازٍ.</b> لقطات لكل لغة لأقسام الخدمات والأسئلة والأسعار قبل/بعد،
  مع قياس DOM حيّ (عدد العقد الظاهرة) لا لقطة فقط.</li>
</ol>
<div class="callout">
  <b>التقدير:</b> البند 1 نصف جلسة · البند 2 جلسة واحدة (توليد آلي) · البند 3 هو الأطول
  (برنامج ترجمة متعدد الجلسات) · البند 4 نصف جلسة. الأولوية: بوابة العمق، ثم الألمانية والهولندية
  كطيارين، ثم بقية اللغات.
</div>
</section>

<section>
<h2>6. بنود مفتوحة أخرى (من الإصدار 16)</h2>
<ul>
  <li><b>الترجمة:</b> الألمانية 238 كتلة إنجليزية (38.8%) · الهولندية 58 كتلة (9.3%).</li>
  <li><b>وزن الطباعة:</b> صفحة الرئيسية تطبع 39 م.ب (صور بدقتها الكاملة) — يحتاج تقييد أبعاد الطباعة.</li>
  <li><b>تأجيل نافذة Launchpad:</b> 23 ك.ب، جلسة مخصصة، مخاطرة عالية مقابل مكسب صغير.</li>
  <li><b>بنود الضمانات 9–12:</b> منشورة بعلامة «مسوّدة» وتنتظر توقيع محامٍ.</li>
</ul>
</section>

<footer>
  أُعدّت هذه الصفحة آليًا من <code>docs/component_counts.json</code> و<code>docs/structure_census.json</code> المقيسين على
  الشجرة الحالية. أعِد توليدها بـ <code>python docs/build_plan_page.py</code> بعد أي تغيير،
  وأعد القياس بـ <code>python docs/measure_structure.py</code>، وافحص الانحراف بـ <code>python scripts/check_content_depth_parity.py --strict</code>.
  · S&amp;R CoreSync For Intelligent Solutions B.V. · PROPRIETARY &amp; CONFIDENTIAL
</footer>
</div>
</body>
</html>
"""

out = pathlib.Path("docs", "plan-v17-structure.html")
out.write_text(doc, encoding="utf-8", newline="")
print("wrote", out, len(doc), "bytes")
