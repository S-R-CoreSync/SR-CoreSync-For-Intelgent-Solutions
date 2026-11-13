# -*- coding: utf-8 -*-
"""
Header label model: pair every header link in the master with its English
counterpart, and name the ones that have none yet.

    python scripts/header_labels.py
"""
import re, os, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(ROOT, 'partials', '10-header.html')
EN = os.path.join(ROOT, 'partials', 'en', '10-header.html')
OUT = os.path.join(ROOT, 'i18n', 'nav', 'header-labels.json')


def anchors(path):
    s = open(path, encoding='utf-8', newline='').read()
    out = []
    for m in re.finditer(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', s, re.S):
        href, inner = m.group(1), m.group(2)
        text = re.sub(r'<[^>]+>', ' ', inner)
        text = re.sub(r'\d{2}\s*/', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        if href and text and not href.startswith('#'):
            out.append((href, text))
        elif href and text:
            out.append((href, text))
    return out


def main():
    ar = anchors(MASTER)
    en = dict(anchors(EN))
    model, missing = {}, []
    for href, label in ar:
        pair = model.setdefault(href, {'ar': label})
        if href in en:
            pair['en'] = en[href]
        else:
            missing.append((href, label))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(model, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('header links in master :', len(model))
    print('with an English label  :', sum(1 for v in model.values() if 'en' in v))
    print('still untranslated    :', len(missing))
    for href, label in missing[:12]:
        print('   %-38s %s' % (href, label))


if __name__ == '__main__':
    main()
