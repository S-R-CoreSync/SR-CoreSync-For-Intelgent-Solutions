#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""البند 24أ-ج الموجة الثانية: بناء كتلي التسعير المفقودتين على الأسطول.
لكل صفحة لغة (المرجع العربي لا يُمس):
  (1) إدراج كتلة sr-pricing-extras كاملة قبل cost-estimator (الموضع المرجعي المكافئ)
      — CTA + اقتباسات ×3 بفوتراتها + إضافات + خطوات ما بعد الحجز + أسئلة الأسعار + شارة.
  (2) إدراج sr-roi-calculator-wrap بعد es-currency-bar-pricing (الموضع المرجعي).
  (3) إدراج رأس cost-estimator-header قبل cost-estimator-grid.
القوالب تُستخرج من index.html المرجع بايت-دقيقة، والنصوص العربية تُستبدل بترجمات
wave2_translations.py (أطول-أولاً بمرونة \s+). إثبات ذاتي: صفر حرف عربي متبقٍ في
الكتل المترجمة لكل لغة غير ckb — وإلا يُجهض تشغيل اللغة. idempotent + --check.
لاحظ: ملف services-enhancements-locale.js يُرفع إصداره (-j2) مع مُهيّئ آمن للحاسبة."""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from wave2_translations import T

with open(ROOT / 'index.html', encoding='utf-8', newline='') as fh:
    MASTER = fh.read()
LANGS = ['bg', 'ckb', 'cs', 'da', 'de', 'el', 'en', 'es', 'et', 'fi', 'fr', 'ga', 'hr',
         'hu', 'it', 'ku', 'lt', 'lv', 'mt', 'nl', 'no', 'pl', 'pt', 'ro', 'sk', 'sl',
         'sv', 'tr']
OLD_JS = 'services-enhancements-locale.js?v=20261118-j'
NEW_JS = 'services-enhancements-locale.js?v=20261118-j2'
ROI_INIT = ('<script>document.addEventListener("DOMContentLoaded",function(){'
            'var a=document.getElementById("roiSalesRange"),b=document.getElementById("roiTeamRange");'
            'if(a&&!a.dataset.srRoiInit){a.dataset.srRoiInit="1";a.addEventListener("input",updateRoiCalc);'
            'if(b&&!b.dataset.srRoiInit){b.dataset.srRoiInit="1";b.addEventListener("input",updateRoiCalc);}updateRoiCalc();}});</script>')

# (المفتاح، النص العربي المرجعي — مطابقة \s+ المرنة)
SOURCE = [
 ('c2', 'احجز استشارة مجانية 30 دقيقة — سنراجع حالتك ونوصي بالباقة الأنسب، بدون التزام.'),
 ('q1', '"Core Starter أطلق منصتنا في 3 أسابيع. الدعم (30 يومًا) كان كافياً لفريقنا."'),
 ('q2', '"Full ERP Sync وحّد شجرة الحسابات + SEPA + BTW. وفر 15 ساعة/أسبوع."'),
 ('q3', '"Custom ERP Ecosystem: 100% White-Label + BYOK. أمان على مستوى بنكي."'),
 ('s3b', '(بدون BTW). جميع الفواتير تصدر بفاتورة ضريبية رسمية (BTW 21%) متوافقة مع Belastingdienst — مؤهلة للخصم كنفقات تشغيلية.'),
 ('s5', 'Core Starter: 30 يومًا · Enterprise Growth: 60 يومًا · Core MAX: 180 يومًا · ERP Setup: 30 يومًا · Full ERP Sync: 60 يومًا · Custom: 180 يومًا. يمكن تمديد الدعم (Add-on).'),
 ('s11', 'ضمان رضا 14 يومًا: إن لم تكن راضياً خلال 14 يوماً من kickoff، نُعيد المبلغ كاملاً. استشارة مجانية 30 دقيقة قبل الالتزام.'),
 ('g1', '🛡️ ضمان الرضا 14 يومًا · استشارة مجانية 30 دقيقة · فاتورة BTW رسمية'),
 ('r3', 'اكتشف حجم التوفير في التكاليف التشغيلية والأرباح السنوية المتوقعة مع منظومة S&amp;R CoreSync الذكية.'),
 ('c3', '📅 احجز استشارة مجانية 30 دقيقة'),
 ('r6', 'حجم المبيعات / الإيرادات الشهرية المتوقعة:'),
 ('r7', 'عدد الموظفين أو العمليات اليدوية شهرياً:'),
 ('r9', 'التوفير السنوي في تكاليف الأتمتة والسحابة:'),
 ('r10', 'النمو التقديري في صافي المبيعات:'),
 ('r11', 'فترة استرداد تكلفة المنظومة (Payback):'),
 ('e1', 'صمّم باقتك الخاصة واحسب تكلفتك ومدة التنفيذ فوراً'),
 ('h_est1', 'حاسبة الميزانية الفورية التفاعلية // تقدير التكلفة ونطاق العمل'),
 ('h_est2', 'اختر نوع مشروعك والمواصفات المطلوبة لتحصل على تسعير فوري دقيق وشفاف، مع إمكانية التثبيت الفوري والحجز المباشر.'),
 ('p5', 'جلسة 60 دقيقة — تحديد النطاق'),
 ('p7', 'تهيئة ERP + ربط الحسابات + اختبار'),
 ('p9', 'نظام جاهز + وثائق + دعم'),
 ('c1', 'غير متأكد أي باقة تناسبك؟'),
 ('s2', 'هل السعر يشمل BTW (ضريبة القيمة المضافة)؟'),
 ('s4', 'ما مدة الدعم (Support) لكل باقة؟'),
 ('s7', 'نعم — يمكنك الترقية في أي وقت. نحتسب الفرق (pro-rata) بناءً على ما دفعته.'),
 ('s6', 'هل يمكن الترقية (Upgrade) لاحقاً؟'),
 ('s8', 'ما طرق الدفع المقبولة؟'),
 ('s10', 'هل يوجد ضمان (Guarantee)؟'),
 ('r2', 'احسب العائد الاستثماري التقديري لمشروعك (ROI Calculator)'),
 ('p1', 'ما بعد الحجز — 4 خطوات واضحة'),
 ('s1', 'أسئلة شائعة حول الأسعار'),
 ('t1', 'ماذا يقول عملاؤنا'),
 ('a0', 'إضافات (Add-ons)'),
 ('a1', 'وحدات إضافية'),
 ('a6', 'ساعات تدريب'),
 ('a7', 'تمديد دعم'),
 ('a8', 'لغة إضافية'),
 ('a2', '+1 وحدة عمل (module)'),
 ('a3', '+5 ساعات (Zoom)'),
 ('a4', '+30 يوم (SLA)'),
 ('a5', '+1 لغة (i18n)'),
 ('p2', 'تأكيد (24 ساعة)'),
 ('p3', 'بريد تأكيد + فاتورة BTW'),
 ('p4', 'Kickoff (3 أيام)'),
 ('p6', 'التنفيذ'),
 ('p8', 'التسليم'),
 ('s3a', 'الأسعار'),
 ('s9', 'iDEAL, Stripe, Mollie, Bancontact, Apple Pay, SEPA Direct Debit, تحويل بنكي. فاتورة رسمية (PDF) مع BTW.'),
 ('f1', '— مدير عمليات، شركة لوجستية (NL)'),
 ('f2', '— CFO، شركة تجارة (EU)'),
 ('f3', '— CTO، FinTech (UAE)'),
 ('r1', '📊 حاسبة النمو المالي'),
 ('r4', 'العائد الاستثماري المتوقع'),
 ('r5', 'خلال أول 6 أشهر تشغيل'),
 ('r8', '15 عملية/فرد'),
 ('r12', '2.1 شهر'),
]
# ترتيب أطول-أولاً لمنع الاستبدالات الجزئية المتداخلة
SOURCE.sort(key=lambda kv: len(kv[1]), reverse=True)

VOID = {'br', 'img', 'input', 'meta', 'link', 'hr', 'source', 'area', 'col', 'embed', 'track', 'wbr'}

def span_of_element(s, open_start):
    m = re.match(r'<([a-zA-Z][a-zA-Z0-9]*)', s[open_start:])
    if not m:
        return None
    tag = m.group(1)
    open_end = s.find('>', open_start)
    if open_end < 0:
        return None
    open_end += 1
    if s[open_start:open_end].rstrip('>').endswith('/') or tag.lower() in VOID:
        return open_end
    depth = 1
    for mm in re.finditer(r'<(/?)' + tag + r'\b[^>]*>', s[open_end:]):
        if mm.group(1) == '/':
            depth -= 1
        elif not mm.group(0).endswith('/>'):
            depth += 1
        if depth == 0:
            return open_end + mm.end()
    return None

def extract_template(cls):
    m = re.search(r'<div class="[^"]*\b%s\b[^"]*"' % cls, MASTER)
    assert m, cls
    e = span_of_element(MASTER, m.start())
    assert e, cls
    return MASTER[m.start():e]

TPL_EXTRAS = extract_template('sr-pricing-extras')
TPL_ROI = extract_template('sr-roi-calculator-wrap')
TPL_HEADER = extract_template('cost-estimator-header')

def ar_regex(ar):
    parts = [re.escape(tok) for tok in re.split(r'\s+', ar.strip()) if tok]
    return re.compile(r'\s+'.join(parts))

def translate(block, lang):
    tr = T[lang]
    out = block
    for key, ar in SOURCE:
        out = ar_regex(ar).sub(tr[key], out)
    # الترجمة تُدرج بنص خام S&R — يُشفّر كما في المرجع
    out = out.replace('S&R', 'S&amp;R')
    # hrefs: ترميز أي عربية خام (نمط الموجة الأولى — النقاء)
    def _fix(m):
        val = m.group(1)
        if not re.search('[\u0600-\u06FF]', val):
            return m.group(0)
        parts = []
        for ch in val:
            if ord(ch) > 127:
                parts.append(''.join('%%%02X' % x for x in ch.encode('utf-8')))
            else:
                parts.append(ch)
        return 'href="%s"' % ''.join(parts)
    return re.sub(r'href="([^"]*)"', _fix, out)

def insert_before(s, m_open, chunk, what):
    s2 = s[:m_open] + chunk + s[m_open:]
    assert s2[m_open:m_open + len(chunk)] == chunk and s2[:m_open] == s[:m_open] and s2[m_open + len(chunk):] == s[m_open:], what
    return s2

def insert_after(s, pos, chunk, what):
    s2 = s[:pos] + chunk + s[pos:]
    assert s2[pos:pos + len(chunk)] == chunk and s2[:pos] == s[:pos] and s2[pos + len(chunk):] == s[pos:], what
    return s2

def pricing_span(s):
    m = re.search(r'<section[^>]*id="pricing"', s)
    assert m
    e = span_of_element(s, m.start())
    return m.start(), e

def apply_lang(lang):
    p = ROOT / lang / 'index.html'
    with open(p, encoding='utf-8', newline='') as fh:
        orig = fh.read()
    s = orig
    report = []
    ps, pe = pricing_span(s)

    def in_pricing(m):  # الوسم داخل قسم التسعير
        return ps <= m < pe

    # (1) extras قبل cost-estimator-wrapper|grid
    n_ex = 0
    if 'sr-pricing-extras' not in s[ps:pe]:
        m_est = None
        for mm in re.finditer(r'<div class="[^"]*\bcost-estimator-(?:wrapper|grid)\b[^"]*"', s):
            if in_pricing(mm.start()):
                m_est = mm.start()
                break
        if m_est:
            block = translate(TPL_EXTRAS, lang)
            s = insert_before(s, m_est, block, 'extras')
            n_ex = 1
        else:
            report.append('extras: لا مرساة')
    # (2) ROI بعد currency bar
    n_roi = 0
    if 'sr-roi-calculator-wrap' not in s[ps:pe]:
        m_bar = None
        for mm in re.finditer(r'<div class="[^"]*\bes-currency-bar-pricing\b[^"]*"', s):
            if in_pricing(mm.start()):
                m_bar = mm.start()
                break
        if m_bar:
            pos = span_of_element(s, m_bar)
            block = translate(TPL_ROI, lang)
            s = insert_after(s, pos, block, 'roi')
            n_roi = 1
        else:
            report.append('roi: لا مرساة')
    # (3) رأس الحاسبة قبل cost-estimator-grid
    n_hdr = 0
    if 'cost-estimator-header' not in s[ps:pe]:
        m_grid = None
        for mm in re.finditer(r'<div class="[^"]*\bcost-estimator-grid\b[^"]*"', s):
            if in_pricing(mm.start()):
                m_grid = mm.start()
                break
        if m_grid:
            block = translate(TPL_HEADER, lang)
            s = insert_before(s, m_grid, block, 'est-header')
            n_hdr = 1
        else:
            report.append('est-header: لا مرساة')
    # (4) إثبات صفر عربي متبقٍ (غير ckb)
    ps2, pe2 = pricing_span(s)
    seg = re.sub(r'<!--.*?-->', '', s[ps2:pe2], flags=re.S)  # التعليقات محرومة من النقاء
    if lang != 'ckb':
        leftover = re.findall(r'[^<>\n]*[\u0600-\u06FF][^<>\n]*', seg)
        # استثنِ الرموز المئوية (روابط مرمّزة) والواسطة
        leftover = [x for x in leftover if '%' not in x]
        if leftover:
            return False, '⚠ بقايا عربية %d: %s' % (len(leftover), [x.strip()[:40] for x in leftover[:3]])
    # (4ب) إصلاح صفحة-عريض: ترميز hrefs ذات عربية خام (الكتل المدرجة سابقاً)
    n_hr = 0
    def _fix2(m):
        nonlocal n_hr
        val = m.group(1)
        if not re.search('[\u0600-\u06FF]', val):
            return m.group(0)
        n_hr += 1
        parts = []
        for ch in val:
            if ord(ch) > 127:
                parts.append(''.join('%%%02X' % x for x in ch.encode('utf-8')))
            else:
                parts.append(ch)
        return 'href="%s"' % ''.join(parts)
    s = re.sub(r'href="([^"]*)"', _fix2, s)

    # (5) رفع إصدار السكربت المشتق + مُهيّئ الحاسبة (محدود بعلامة الاقتباس — لا substring)
    n_js = 0
    if OLD_JS + '"' in s and NEW_JS + '"' not in s:
        s = s.replace(OLD_JS + '"', NEW_JS + '"')
        n_js += 1
    if '20261118-j22"' in s:  # إصلاح خطأ الجولة السابقة (substring)
        s = s.replace('20261118-j22"', NEW_JS.split('?v=')[1] + '"')
        n_js += 1
    if NEW_JS in s and ROI_INIT not in s:
        m_tag = re.search(r'<script src="\.\./js/services-enhancements-locale\.js[^"]*"[^>]*></script>', s)
        if m_tag:
            s = insert_after(s, m_tag.end(), ROI_INIT, 'roi-init')
            n_js += 1
    if s != orig:
        with open(p, 'w', encoding='utf-8', newline='') as fh:
            fh.write(s)
    report.append('extras+%d roi+%d hdr+%d js+%d' % (n_ex, n_roi, n_hdr, n_js))
    return s != orig, ' · '.join(report)

def check_lang(lang):
    with open(ROOT / lang / 'index.html', encoding='utf-8', newline='') as fh:
        s = fh.read()
    pend = []
    for cls in ('sr-pricing-extras', 'sr-roi-calculator-wrap', 'cost-estimator-header'):
        if cls not in s:
            pend.append(cls)
    if NEW_JS not in s:
        pend.append('js-v2')
    return pend

def main():
    only = None
    for a in sys.argv[1:]:
        if a.startswith('--lang'):
            only = a.split('=')[1] if '=' in a else None
    langs = [only] if only else LANGS
    if '--check' in sys.argv:
        bad = 0
        for L in langs:
            pend = check_lang(L)
            if pend:
                bad += 1
                print('⚠ %-4s %s' % (L, ' · '.join(pend)))
        print('CHECK: %d/%d مكتملة' % (len(langs) - bad, len(langs)))
        sys.exit(1 if bad else 0)
    changed = 0
    for L in langs:
        ch, rep = apply_lang(L)
        changed += 1 if ch else 0
        print('◆ %-4s %s' % (L, rep))
    print('\nتغيرت %d/%d' % (changed, len(langs)))

if __name__ == '__main__':
    main()
