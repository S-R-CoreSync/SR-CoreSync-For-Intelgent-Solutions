# -*- coding: utf-8 -*-
"""
Put the five sections in the menu order, in any locale page.

Only the relative order of these five blocks changes; everything else keeps its
byte-for-byte position.

    python scripts/reorder_lang.py en
"""
import re, os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDER = json.load(open(os.path.join(ROOT, 'i18n', 'sections', 'order.json'), encoding='utf-8'))['order']


def span(s, ident):
    m = re.search(r'<section\b[^>]*\bid="%s"' % re.escape(ident), s)
    if not m:
        return None
    i = m.start()
    depth = 0
    for t in re.finditer(r'<section\b|</section>', s[i:]):
        if t.group(0).startswith('</'):
            depth -= 1
            if depth == 0:
                return i, i + t.end()
        else:
            depth += 1
    return None


def process(lang):
    p = os.path.join(ROOT, lang, 'index.html')
    s = open(p, encoding='utf-8', newline='').read()

    spans = {}
    for sid in ORDER:
        sp = span(s, sid)
        if not sp:
            print('%-3s missing #%s - skipped' % (lang, sid))
            return
        spans[sid] = sp

    current = [sid for sid in sorted(ORDER, key=lambda k: spans[k][0])]
    if current == ORDER:
        print('%-3s already in order' % lang)
        return

    insert_at = min(sp[0] for sp in spans.values())
    block = ''.join(s[spans[sid][0]:spans[sid][1]] for sid in ORDER)

    for sid in sorted(ORDER, key=lambda k: -spans[k][0]):
        a, b = spans[sid]
        s = s[:a] + s[b:]
    s = s[:insert_at] + block + s[insert_at:]

    open(p, 'w', encoding='utf-8', newline='').write(s)
    print('%-3s reordered  %s -> %s' % (lang, ' '.join(current), ' '.join(ORDER)))


if __name__ == '__main__':
    for lang in sys.argv[1:]:
        process(lang)
