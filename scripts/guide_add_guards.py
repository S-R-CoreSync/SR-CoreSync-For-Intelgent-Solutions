P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\docs\workflow-guide.html'
s = open(P, encoding='utf-8', newline='').read()

AR = """<h2>5ب · الحراس الآليون</h2>
<p>ستة فحوص تحمي الموقع من الأخطاء الصامتة. تُشغَّل قبل كل نشر، ويفشل البناء إن أخفق أحدها:</p>
<table>
<tr><th>الحارس</th><th>يمنع</th><th>الأمر</th></tr>
<tr><td>حمولات الأحداث</td><td>سطر جديد أو اقتباس داخل JSON يعطّل زراً بلا رسالة</td><td><code>check_sr_args.py</code></td></tr>
<tr><td>الأجزاء ↔ الجذر</td><td>تعديل صفحة دون تحديث أجزائها</td><td><code>build_site.py --check</code></td></tr>
<tr><td>الأجزاء ↔ الإنجليزية</td><td>انحراف الصفحة اللغوية عن أجزائها</td><td><code>build_lang.py --check en</code></td></tr>
<tr><td>توليد الهيرو</td><td>قاموس لغة لا يطابق صفحته</td><td><code>verify_hero_build.py</code></td></tr>
<tr><td>توليد الفوتر</td><td>نموذج الفوتر لا يطابق الصفحة</td><td><code>verify_footer_build.py</code></td></tr>
<tr><td>ترتيب القائمة</td><td>قائمة خارج الترتيب المتفق عليه</td><td><code>verify_nav_build.py</code></td></tr>
</table>
<div class="rule"><strong>قاعدة الحارس:</strong> إن أخفق فحص، لا يُستثنى — يُصلَح. الاستثناء يحوّل الحارس إلى زينة.</div>

"""

NL = """<p><strong>Twee bewakers, één regel:</strong> de publicatie bouwt de pagina's uit hun delen en verifieert daarna.
<code>check_sr_args.py</code> weigert een gebroken <code>data-sr-args</code>-lading — de fout die een knop
stilzwijgend doodt. Faalt een controle, dan wordt ze hersteld, nooit uitgezonderd.</p>

"""

EN = """<p><strong>Two guards, one rule:</strong> the deploy builds the pages from their parts, then verifies them.
<code>check_sr_args.py</code> rejects a broken <code>data-sr-args</code> payload — the failure that kills a
button without a word. A failing check is fixed, never excused.</p>

"""

changed = 0
if '5ب · الحراس الآليون' not in s:
    anchor = '<h2>6 · سجل ما جرى + الدروس</h2>'
    assert anchor in s
    s = s.replace(anchor, AR + anchor, 1)
    changed += 1

if 'Twee bewakers' not in s:
    anchor = '<p><strong>Drie bronnen van waarheid:</strong>'
    assert anchor in s
    s = s.replace(anchor, NL + anchor, 1)
    changed += 1

if 'Two guards, one rule' not in s:
    anchor = '<p><strong>Three sources of truth:</strong>'
    assert anchor in s
    s = s.replace(anchor, EN + anchor, 1)
    changed += 1

open(P, 'w', encoding='utf-8', newline='').write(s)
print('sections added:', changed)
