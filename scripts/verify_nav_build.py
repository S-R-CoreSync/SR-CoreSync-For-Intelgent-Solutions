# -*- coding: utf-8 -*-
"""
P2 · third slice: the menu order is data, and every page is checked against it.

    python scripts/verify_nav_build.py de fr it
"""
import re, os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.path.join(ROOT, 'i18n', 'nav', 'order.json')
NUM = re.compile(r'(<span[^>]*>)\s*\d{2}\s*/\s*(</span>)')


def spans(src):
    out, depth, start = [], 0, None
    for m in re.finditer(r'<li\b|</li>', src):
        if m.group(0).startswith('</'):
            depth -= 1
            if depth == 0:
                out.append((start, m.end()))
                start = None
        else:
            if depth == 0:
                start = m.start()
            depth += 1
    return out


def menu_span(s):
    i = s.index('<ul class="nav-menu-main">')
    start = s.index('>', i) + 1
    depth = 0
    for m in re.finditer(r'<ul\b|</ul>', s[start:]):
        if m.group(0) == '</ul>':
            depth -= 1
            if depth == 0:
                return start, start + m.start()
        else:
            depth += 1
    raise SystemExit('unbalanced menu')


def normalise(block, order):
    items = spans(block)
    main, rest = {}, []
    for a, b in items:
        chunk = block[a:b]
        h = re.search(r'<a[^>]*href="([^"]+)"', chunk)
        key = h.group(1) if h else None
        if key in order and key not in main:
            main[key] = chunk
        else:
            rest.append(chunk)
    out, sep = '', block[items[0][1]:items[1][1]] if len(items) > 1 else ''
    for i, key in enumerate(order, 1):
        out += NUM.sub(lambda m: m.group(1) + '%02d /' % i + m.group(2), main[key], count=1)
        if i < len(order):
            out += sep
    for chunk in rest:
        out += sep + chunk
    return out


def hrefs(block):
    out = []
    for a, b in spans(block):
        m = re.search(r'<a[^>]*href="([^"]+)"', block[a:b])
        if m:
            out.append(m.group(1))
    return out


def main():
    order = json.load(open(MODEL, encoding='utf-8'))['order']
    langs = sys.argv[1:] or ['de']
    bad = 0
    for lang in langs:
        p = os.path.join(ROOT, lang, 'index.html')
        s = open(p, encoding='utf-8', newline='').read()
        a, b = menu_span(s)
        got = hrefs(s[a:b])[:len(order)]
        if got == order:
            print('%-3s IN ORDER' % lang)
        else:
            bad += 1
            print('%-3s OUT OF ORDER -> %s' % (lang, got))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
