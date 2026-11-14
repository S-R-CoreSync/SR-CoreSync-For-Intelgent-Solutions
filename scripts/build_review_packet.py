# -*- coding: utf-8 -*-
"""A translator's packet: the exact source strings, where they sit, and a place to write.

Nothing is machine-translated here. The four languages that remain need a native
ear: Greek, Sorani Kurdish, Irish and Maltese. This file gives the reviewer the
source, the context and the rules, and leaves the four columns empty.
"""
import csv, os, re
import lxml.html

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
STOP = re.compile(r'\b(the|and|with|your|from|that|this|will|have|about|package|price|request|'
                  r'software|solutions|included|everything|built|designed|complete|custom|'
                  r'partner|trusted|months|within|study|capital|highlight)\b', re.I)

SECTION_AR = {
 'hero': 'الهيرو (أعلى الصفحة)',
 'services': 'بطاقات الخدمات',
 'pricing': 'بطاقات الأسعار',
 'software': 'شبكة البرمجيات',
 'lab': 'مختبر المؤسس',
 'compliance': 'الامتثال والثقة',
 'testimonials': 'شهادات العملاء',
 'roi': 'حاسبة العائد',
 'exec': 'القيادة التنفيذية',
 'newsletter': 'النشرة البريدية',
 'modal': 'نافذة منبثقة',
 'tech': 'البنية التقنية',
 'body': 'عام',
 'about': 'نبذة',
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


doc = lxml.html.fromstring(open(os.path.join(ROOT, 'el', 'index.html'), encoding='utf-8', newline='').read())
for bad in doc.xpath('//script|//style|//noscript'):
    bad.getparent().remove(bad)

seen, rows = set(), []
for el in doc.iter():
    if not isinstance(el.tag, str):
        continue
    for chunk in (el.text, el.tail):
        t = re.sub(r'\s+', ' ', (chunk or '').strip())
        if len(t) >= 18 and len(STOP.findall(t)) >= 2 and t not in seen:
            seen.add(t)
            rows.append((section_of(el), t))

# keep the order of appearance, which is also the order a reader meets them
out = os.path.join(ROOT, 'docs', 'حزمة-المراجعة-الناطقة.csv')
with open(out, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['#', 'القسم', 'السياق', 'english_source', 'chars',
                'el_ελληνικά', 'ku_سۆرانی', 'ga_Gaeilge', 'mt_Malti'])
    for i, (sec, text) in enumerate(rows, 1):
        w.writerow([i, sec, SECTION_AR.get(sec, sec), text, len(text), '', '', '', ''])

print('strings for review:', len(rows))
print('written:', out)
print('sections:', sorted({r[0] for r in rows}))
