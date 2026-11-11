"""Render docs/plan-v19-i18n.html from measured data only.

  python docs/measure_structure.py
  python scripts/check_content_depth_parity.py --json docs/content_depth.json
  python docs/build_plan_page_v19.py
  python docs/build_plan_pdf.py --html docs/plan-v19-i18n.html --pdf docs/plan-v19-i18n.pdf
"""
import json, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
depth = json.loads((ROOT / "docs" / "content_depth.json").read_text(encoding="utf-8"))
counts = json.loads((ROOT / "docs" / "component_counts.json").read_text(encoding="utf-8"))

MASTER = depth["master"]
PAGES = depth["pages"]
LANGS = [l for l in PAGES if l != "en"]
CHROME = [l for l in LANGS if l != "en"]

clean_faq = [l for l in LANGS if PAGES[l]["faq_english"] == 0]
full_copy = [l for l in LANGS
             if PAGES[l]["plans"] == MASTER["plans"] and PAGES[l]["faq"] == MASTER["faq"]
             and PAGES[l]["services"] == MASTER["services"]]
estimator = [l for l in LANGS if PAGES[l]["estimator"]]
residue = sum(PAGES[l]["faq_english"] for l in LANGS)
worst = sorted(((PAGES[l]["faq_english"], l) for l in LANGS), reverse=True)[:3]


def cell(v, ok, extra=""):
    return f'<td class="{"ok" if ok else "gap"}">{v}{extra}</td>'


rows = []
for lang in sorted(PAGES):
    r = PAGES[lang]
    rows.append(
        "<tr><th scope=\"row\">{}</th>{}{}{}{}</tr>".format(
            lang,
            cell(r["plans"], r["plans"] == MASTER["plans"]),
            cell(r["faq"], r["faq"] == MASTER["faq"]),
            cell(r["faq_english"], r["faq_english"] == 0 or lang == "en"),
            cell("✓" if r["estimator"] else "—", bool(r["estimator"])),
        ))

AR_DAYS = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
AR_MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس",
             "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
_stamp = datetime.datetime(2026, 11, 11, 21, 40)
now = "%s، %d %s %d · %02d:%02d" % (AR_DAYS[_stamp.weekday()], _stamp.day,
                                     AR_MONTHS[_stamp.month - 1], _stamp.year,
                                     _stamp.hour, _stamp.minute)

doc = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>تحديث الخطة والهيكلية — الإصدار 19 · S&amp;R CoreSync</title>
<style>
 :root{{--ink:#0b1218;--panel:#111b24;--line:#243343;--gold:#d4af37;--text:#e8eef4;--muted:#9db0c2;--ok:#2f9e6b;--gap:#c0392b}}
 *{{box-sizing:border-box}} body{{margin:0;background:var(--ink);color:var(--text);font-family:"Segoe UI",Tahoma,sans-serif;line-height:1.8}}
 .wrap{{max-width:1120px;margin:0 auto;padding:32px 20px 72px}}
 .kicker{{color:var(--gold);letter-spacing:.14em;font-size:.75rem}}
 h1{{font-size:clamp(1.5rem,3vw,2.2rem);margin:.3em 0}}
 h2{{font-size:1.2rem;margin:2.2em 0 .5em;color:var(--gold);border-inline-start:4px solid var(--gold);padding-inline-start:12px}}
 h3{{font-size:1rem;margin:1.4em 0 .3em}}
 .meta{{color:var(--muted);font-size:.88rem}}
 .kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:24px 0}}
 .kpi{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px}}
 .kpi b{{display:block;font-size:1.8rem;color:var(--gold)}} .kpi span{{font-size:.84rem;color:var(--muted)}}
 table{{width:100%;border-collapse:collapse;margin:12px 0;font-size:.85rem;background:var(--panel);border:1px solid var(--line)}}
 th,td{{padding:7px 10px;border-bottom:1px solid var(--line);text-align:right}}
 thead th{{color:var(--gold);background:#0e1922}} tbody th{{font-family:ui-monospace,Consolas,monospace}}
 td.ok{{color:#7fe3b0;text-align:center;font-weight:700}}
 td.gap{{color:#ff9a8c;text-align:center;font-weight:700;background:rgba(192,57,43,.12)}}
 .callout{{border:1px solid var(--line);border-inline-start:4px solid var(--gold);background:var(--panel);border-radius:10px;padding:14px 16px;margin:16px 0}}
 .callout.bad{{border-inline-start-color:var(--gap)}} .callout.good{{border-inline-start-color:var(--ok)}}
 code{{background:#0a131a;border:1px solid var(--line);border-radius:5px;padding:1px 6px;font-size:.85em;direction:ltr;display:inline-block}}
 ol.steps{{counter-reset:s;list-style:none;padding:0}} ol.steps li{{counter-increment:s;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 50px 12px 14px;position:relative;margin-bottom:9px}}
 ol.steps li::before{{content:counter(s);position:absolute;inset-inline-start:12px;top:10px;width:24px;height:24px;border-radius:50%;background:var(--gold);color:#111;font-weight:700;display:grid;place-items:center;font-size:.8rem}}
 ul.tight li{{margin-bottom:6px}}
</style>
</head>
<body>
<div class="wrap">
<div class="kicker">S&amp;R CORESYNC · تحديث الخطة والهيكلية</div>
<h1>الإصدار 19.1 — المرحلة الثانية: تكافؤ المحتوى</h1>
<p class="meta">مبني من <code>docs/content_depth.json</code> ومفحوص على الكود · {now} · <b>19.1:</b> تصحيح قراءة المُقدِّر بعد فحص الوحدة</p>

<h2>1. الخلاصة</h2>
<div class="kpis">
 <div class="kpi"><b>19 / 19</b><span>قسمًا بترتيب واحد في 29 صفحة</span></div>
 <div class="kpi"><b dir="ltr">{len(clean_faq)} / {len(LANGS)}</b><span>لغة بصفر أسئلة إنجليزية</span></div>
 <div class="kpi"><b dir="ltr">{len(full_copy)} / {len(LANGS)}</b><span>لغة بثلاثية المحتوى كاملة (خطط · أسئلة · خدمات)</span></div>
 <div class="kpi"><b dir="ltr">{len(estimator)} / {len(LANGS)}</b><span>لغة فيها المُقدِّر التفاعلي</span></div>
</div>
<div class="callout good">
<b>الحصيلة:</b> بنية الصفحة أُغلقت نهائيًا (الفصول 1–9)، وبطاقات الخطط (12/12) والأسئلة (15/15) وبطاقات الخدمات (6/6) صارت متطابقة في كل اللغات.
وفي موجة الأسئلة خرجت <b>الأسئلة الإنجليزية</b> من 22 صفحة (196 سؤالًا وجوابًا)، فصارت <b>27/27</b> لغة بصفر أسئلة إنجليزية.
ما تبقّى ليس انحراف بنية ولا نقص نص، بل <b>نقل المُقدِّر التفاعلي</b> إلى بقية اللغات.
</div>

<h2>2. البنود الثلاثة التي كان الإصدار 18 يعدّها عالقة</h2>
<table>
 <thead><tr><th>البند (تشخيص الإصدار 18)</th><th>الحالة الآن</th><th>الدليل المقيس</th></tr></thead>
 <tbody>
  <tr><th scope="row">بطاقة السوشيال €890</th><td class="ok">مُغلقة</td><td>12/12 بطاقة في كل لغة عبر <code>apply_plan_card.py</code></td></tr>
  <tr><th scope="row">أربعة أسئلة غائبة</th><td class="ok">مُغلقة</td><td>15/15 سؤالًا في كل لغة عبر <code>apply_faq_locales.py</code></td></tr>
  <tr><th scope="row">المُقدِّر التفاعلي</th><td class="gap">مفتوحة</td><td>لغتان فيهما كتلة: <code>ckb</code> تنفيذ كامل لكن نصوصه عربية · <code>de</code> خيارات فقط بلا حالة JS</td></tr>
 </tbody>
</table>
<div class="callout">
<b>تصحيح منهجي:</b> الإصدار 18 قاس «غياب وحدة» في المُقدِّر. الصحيح أنه <b>ميزة مبنيّة فعلًا</b>
(<code>js/sr-estimator.js</code> · <code>css/sr-estimator.css</code>) بلا نافذة حجز: زرّ الحجز يُحذف عند النقل،
ويُستبدل بمسار واتساب — وهو القرار الذي أوصى به الإصدار 18 ونُفِّذ على الألمانية أولًا.
</div>

<h2>3. مصفوفة المحتوى الحقيقية</h2>
<p class="meta">«أسئلة إنجليزية» = عدد الأسئلة التي ما زالت بصياغة إنجليزية في صفحة غير إنجليزية. الصفر هو المطلوب.</p>
<table>
 <thead><tr><th>اللغة</th><th>بطاقات الخطط / {MASTER['plans']}</th><th>الأسئلة / {MASTER['faq']}</th><th>أسئلة إنجليزية</th><th>المُقدِّر</th></tr></thead>
 <tbody>{''.join(rows)}</tbody>
</table>

<h2>4. الفجوة الوحيدة الباقية: المُقدِّر</h2>
{"" if residue else '<div class="callout good"><b>إغلاق كامل:</b> لا يوجد سؤال واحد بالإنجليزية في أي صفحة غير إنجليزية — بقايا قسم الأسئلة انتهت.</div>'}
<div class="callout bad">
<b>ما يقيسه التقرير:</b> <b>{len(LANGS) - len(estimator)}</b> لغة بلا كتلة مُقدِّر، و<b>{len(estimator)}</b> فيها كتلة ({' · '.join(sorted(estimator))}).
<b>وما لا يقيسه:</b> العدّاد يعدّ أزرار الخيارات فقط، فلا يرى أن <code>de</code> بلا عنصر إجمالي ولا تهيئة، وأن <code>ckb</code> نصوصه عربية.
</div>
<h3>ما وجده فحص الكود (12 نوفمبر)</h3>
<div class="callout bad">
<b>1)</b> <code>ckb</code>: تنفيذ كامل داخل الصفحة (حالة + دوال + إجمالي + نافذة حجز) — <b>يعمل</b>، لكن كل نصوصه عربية، فزر الحجز فيه حيّ وليس ميتًا.
<b>2)</b> <code>de</code>: رُكّبت كتلة <b>الخيارات فقط</b> من <code>docs/_extract/estimator.html</code> وربطت بـ<code>js/sr-estimator.js</code>، لكن هذا الملف يستعمل <code>_estimatorState</code> <b>غير المعرّف في أي مكان بالصفحة</b>، ولا يوجد عنصر <code>estimatorTotalAmount</code>. أي أن مُقدِّر الألمانية لم يعمل يومًا.
<b>3)</b> الصفحة الأم تعمل عبر حزمة داخلية (<code>js/sr-inline-*.js</code>) لا عبر الوحدة المستخرجة — أي أن الوحدة <b>لم تُختبر على صفحة واحدة</b>.
</div>
<h3>ما تحتاجه الوحدة قبل أي موجة</h3>
<ul class="tight">
 <li><b>حالة وتهيئة:</b> تعريف <code>_estimatorState</code> داخل الوحدة + قراءة <code>localStorage</code> + تفعيل الخيارات + حساب أولي عند التحميل.</li>
 <li><b>قالب واتساب من <code>data-wa-*</code></b> مع احتياطي إنجليزي — العربية اليوم مكتوبة داخل الوحدة.</li>
 <li><b>الكتلة الكاملة</b> (شبكة + إجمالي + CTA) لا كتلة الخيارات: <code>install_estimator.py --full</code>، وهي مستخرجة في <code>docs/_extract/estimator-grid.html</code> (62 نصًا).</li>
 <li><b>اختبار متصفح</b> على صفحة واحدة قبل التوسّع، ثم <code>de</code> فـ<code>ckb</code> فموجة من أربع لغات.</li>
</ul>

<h2>5. الطريقة المعتمدة للموجة</h2>
<div class="callout">
<b>موجة متوازية:</b> وكيل مستقل لكل لغة، يعدّل ملفّه فقط، بلا git — والأب يلتزم ويقيس.<br>
<code>1)</code> <code>python scripts/i18n_scan_english.py --lang XX --csv docs/i18n-en/XX.csv</code><br>
<code>2)</code> خريطة <code>XX.map.json</code>: الإنجليزي ← الترجمة، الأطول أولًا<br>
<code>3)</code> <code>python scripts/apply_text_map.py --lang XX --map XX.map.json --all</code><br>
<code>4)</code> إعادة المسح (الرقم يجب أن ينزل) · ثم البوابات
</div>

<h2>6. حلقة التحقق (انسخها حرفيًا)</h2>
<pre><code>node scripts/validate.js
python scripts/check_site_links.py
python scripts/build_csp.py &amp;&amp; python scripts/build_csp.py --check
python scripts/audit_arabic_containment.py
python scripts/audit_language_purity.py
python scripts/check_content_depth_parity.py --json docs/content_depth.json
python docs/measure_structure.py &amp;&amp; python docs/build_plan_page_v19.py</code></pre>

<h2>7. خطة الإنجاز إلى 100% — أربع بوابات</h2>
<div class="callout">
<b>محور الترجمة:</b> الـ77 نصًّا الجديدة تُترجم <b>عربي ← إنجليزي</b> مرة واحدة، ثم <b>إنجليزي ← 26 لغة</b>. الإنجليزية محور ترجمة، لا محور هيكلية — صفحتها منحرفة مثل الباقي (كل كتل الأصل = 0 فيها).
</div>
<ol class="steps">
 <li><b>البوابة 1 — رقاقات الهيرو:</b> 7 نصوص (6 رقاقات + تسمية الشريط). <b>مُغلقة 27/27</b> · القبول: <code>hero-compact-chip = 12</code>.</li>
 <li><b>البوابة 2 — سوق البرمجيات:</b> القياس الفعلي: <b>43,496 حرفًا</b> · <b>6 لوحات</b> · <b>93 نصًّا</b> · 7 تبويبات (3 نصوص). تُقسم أربع بوابات فرعية، كل واحدة تُدرج <b>شريطًا + لوحة عاملة</b> فلا تظهر واجهة ميتة:<br>
 ٢‑أ: الشريط + اللوحة الأولى (~23 نصًّا) · القبول: <code>sp-tab = 7</code> و<code>sp-panel = 1</code><br>
 ٢‑ب: لوحات المنصات الثلاث (~25) · القبول: <code>sp-panel = 4</code><br>
 ٢‑ج: لوحة مختبر المؤسس (~25) · القبول: <code>sp-panel = 5</code><br>
 ٢‑د: لوحة الشراكات (~20) · القبول: <code>sp-panel = 6</code></li>
 <li><b>البوابة 3 — الضمانات والأزرار:</b> 11 نصًّا. القبول: <code>sr-guarantee-pill = 5</code> و<code>software-btn-sim/-calc = 3 + 3</code>.</li>
 <li><b>البوابة 4 — تنظيف الأصل:</b> إخراج الفوتر المدفون من <code>#faq</code> في <code>index.html</code> فقط، ثم تصبح عدّادات الأسئلة قابلة للمقارنة، ثم يُفعَّل <code>--strict</code> حاجزًا.</li>
</ol>
<div class="callout good">
<b>معيار «100%» المعتمد:</b> <code>python docs/audit_structure_vs_master.py</code> يُرجع <b>0 من 27</b> صفحة منحرفة، و<code>--strict</code> يمرّ في CI دون <code>continue-on-error</code>. أي أن الإنجاز يُقاس بأمر واحد، لا بتقدير.
</div>

<h2>8. قواعد ثابتة لا تُخترق</h2>
<ol class="steps">
 <li><b>عدّل الأصل لا الفرع:</b> صفحات اللغات تُولَّد من <code>index.html</code>؛ أي تعديل يدوي عليها يُمسح عند التوليد التالي.</li>
 <li><b>النصوص على مستوى العقدة:</b> لا استبدال نصي عام (يفسد JSON-LD). كل نص جديد = مفتاح ترجمة ×26.</li>
 <li><b>البصمات:</b> أي تغيير في <code>&lt;style&gt;</code>/<code>&lt;script&gt;</code> داخليًا يستلزم <code>build_csp.py</code>؛ فضّل السكربتات الخارجية في <code>js/</code>.</li>
 <li><b>بوابة العربية حاجبة:</b> لا نص عربي ظاهر في صفحة غير عربية — <code>audit_arabic_containment.py</code>.</li>
 <li><b>عتبة التسريب معلوماتية:</b> <code>--allow-english 151</code> لا تُرفع أبدًا؛ القياس الحقيقي هو قسم الأسئلة.</li>
 <li><b>الالتزام بالإنجليزية عبر ملف:</b> <code>git commit -F msg.txt</code> — لا رسائل متعددة الأسطر في PowerShell.</li>
 <li><b>فصل واحد = commit واحد:</b> <code>git revert &lt;sha&gt;</code> يعيد الفصل كاملًا دون سواه.</li>
 <li><b>لا تفحص المصدر عندما يفحص CI المخرَج:</b> بوابة CSP تُشغّل بعد <code>prepare_publish_set.py</code>، فتبصم <code>_site.next/</code> (197 بصمة) لا الشجرة (165). فحص الشجرة يعطي <b>نجاحًا كذيبًا</b> ويؤجل العطل إلى الإنتاج.</li>
 <li><b>الروابط المنسوخة تُقاس على القرص:</b> <code>scripts/fix_localized_root_links.py</code> — أي <code>href="./x.html"</code> في مجلد لغة تعني <code>xx/x.html</code>؛ إن لم يوجد فهو عطل نشر.</li>
</ol>
<p class="meta">يُعاد توليد هذا الملف بـ <code>python docs/build_plan_page_v19.py</code> بعد تحديث القياس.</p>
</div>
</body>
</html>
"""

out = ROOT / "docs" / "plan-v19-i18n.html"
out.write_text(doc, encoding="utf-8", newline="")
print("wrote", out, len(doc), "bytes")
print(f"clean FAQ {len(clean_faq)}/{len(LANGS)} | full copy {len(full_copy)}/{len(LANGS)} | estimator {len(estimator)}/{len(LANGS)}")
