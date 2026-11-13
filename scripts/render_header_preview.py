# -*- coding: utf-8 -*-
"""
Render the English header from the master header + i18n/nav/header-labels.json.

Writes:
  build/en-header.html     the generated header on its own
  _preview-en.html         a full English page wearing it (temporary, deleted after review)
"""
import re, os, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(ROOT, 'partials', '10-header.html')
EN_PAGE = os.path.join(ROOT, 'partials', 'en', '10-header.html')
LABELS = os.path.join(ROOT, 'i18n', 'nav', 'header-labels.json')
BUILD = os.path.join(ROOT, 'build')

EXTRA = {
    'أدوات الدعم': 'Support tools',
    'تثبيت التطبيق': 'Install app',
    'الخدمات التفاعلية المباشرة': 'Live interactive services',
    'المزيد': 'More',
    'الأسئلة الشائعة': 'FAQ',
    'المدونة': 'Journal',
    'توثيق API': 'API docs',
    'حاسبة العائد': 'ROI',
}


def translate(header, model):
    out = header
    for href, pair in model.items():
        en = pair.get('en')
        ar = pair.get('ar')
        if not en or not ar:
            continue
        out = out.replace('>%s<' % ar, '>%s<' % en)
    for ar, en in EXTRA.items():
        out = out.replace(ar, en)
    return out


def main():
    header = open(MASTER, encoding='utf-8', newline='').read()
    model = json.load(open(LABELS, encoding='utf-8'))
    gen = translate(header, model)

    os.makedirs(BUILD, exist_ok=True)
    open(os.path.join(BUILD, 'en-header.html'), 'w', encoding='utf-8', newline='').write(gen)

    ar_left = re.findall(r'[\u0600-\u06FF][\u0600-\u06FF\s]*', re.sub(r'<[^>]+>', ' ', gen))
    ar_left = [a.strip() for a in ar_left if len(a.strip()) > 1]

    # full page preview: english body, new header
    order = [l.strip() for l in open(os.path.join(ROOT, 'partials', 'en', 'order.txt'), encoding='utf-8') if l.strip()]
    parts = []
    for n in order:
        if n == '10-header':
            parts.append(gen)
        else:
            parts.append(open(os.path.join(ROOT, 'partials', 'en', n + '.html'), encoding='utf-8', newline='').read())
    page = ''.join(parts).replace('src="assets/', 'src="./assets/').replace('href="assets/', 'href="./assets/')
    open(os.path.join(ROOT, '_preview-en.html'), 'w', encoding='utf-8', newline='').write(page)

    print('generated header bytes:', len(gen))
    print('arabic fragments left  :', len(ar_left))
    for a in ar_left[:8]:
        print('   ', a[:60])


if __name__ == '__main__':
    main()
