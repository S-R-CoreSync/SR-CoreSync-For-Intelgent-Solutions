# -*- coding: utf-8 -*-
"""Union the four remaining languages, so the packet covers every string at least one of them shows."""
import csv, os, re
import lxml.html

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
SOURCES = ['el', 'ku', 'ga', 'mt']
STOP = re.compile(r'\b(the|and|with|your|from|that|this|will|have|about|package|price|request|'
                  r'software|solutions|included|everything|built|designed|complete|custom|'
                  r'partner|trusted|months|within|study|capital|highlight)\b', re.I)

SECTION_AR = {
 'heroEmblemStage': 'الهيرو — شريط الشعار', 'services': 'بطاقات الخدمات', 'wg-plan': 'بطاقات الأسعار',
 'softwareGridContainer': 'شبكة البرمجيات', 'softwareArchitectLab': 'مختبر المؤسس',
 'compliance': 'الامتثال والثقة', 'testimonials': 'شهادات العملاء', 'roi-calculator': 'حاسبة العائد',
 'roiPrintablePaper': 'ملف العائد المطبوع', 'execStageDesc': 'القيادة التنفيذية',
 'newsletter': 'النشرة البريدية', 'directCallModal': 'نافذة الاتصال المباشر',
 'projectModalDescription': 'نافذة المشروع — الوصف', 'projectModalQuote': 'نافذة المشروع — اقتباس',
 'liveDemoQuickModal': 'نافذة العرض الحي', 'clientPortalModal': 'نافذة بوابة العميل',
 'salimLicenseManagerModal': 'نافذة إدارة التراخيص', 'checkoutSuccessView': 'شكر بعد الدفع',
 'wg-tech-v2': 'البنية التقنية', 'body': 'عام',
}


def section_of(el):
    n = el
    while n is not None and getattr(n, 'tag', None) not in ('body', 'html'):
        i = n.get('id') or ''
        c = (n.get('class') or '').split()
        if i:
            return i
        if c and ('section' in c[0] or c[0].startswith('wg')):
            return c[0]
        n = n.getparent()
    return 'body'


seen, rows = set(), []
for lang in SOURCES:
    doc = lxml.html.fromstring(open(os.path.join(ROOT, lang, 'index.html'), encoding='utf-8', newline='').read())
    for bad in doc.xpath('//script|//style|//noscript'):
        bad.getparent().remove(bad)
    for el in doc.iter():
        if not isinstance(el.tag, str):
            continue
        for chunk in (el.text, el.tail):
            t = re.sub(r'\s+', ' ', (chunk or '').strip())
            if len(t) >= 18 and len(STOP.findall(t)) >= 2 and t not in seen:
                seen.add(t)
                rows.append((section_of(el), t))

out = os.path.join(ROOT, 'docs', 'حزمة-المراجعة-الناطقة.csv')
with open(out, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['#', 'section', 'السياق', 'english_source', 'chars',
                'el_ελληνικά', 'ku_سۆرانی', 'ga_Gaeilge', 'mt_Malti'])
    for i, (sec, text) in enumerate(rows, 1):
        w.writerow([i, sec, SECTION_AR.get(sec, sec), text, len(text), '', '', '', ''])

print('strings:', len(rows))
print('sections:', len({r[0] for r in rows}))
print('written:', out)
