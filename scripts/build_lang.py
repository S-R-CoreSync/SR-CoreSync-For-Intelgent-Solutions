# -*- coding: utf-8 -*-
"""
P4 · first full page from parts.

Extracts a locale page into partials/<lang>/, then rebuilds it and proves the
result is identical. Nothing published changes.

    python scripts/build_lang.py --extract en
    python scripts/build_lang.py --check en
"""
import re, os, sys, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REGIONS = [
    ('10-header', r'<header\b[^>]*class="[^"]*tf-header', 'header'),
    ('30-footer', r'<footer\b[^>]*\bclass="[^"]*srf', 'footer'),
]


def span(src, m, tag):
    i = m.start()
    depth = 0
    for t in re.finditer(r'<%s\b|</%s>' % (tag, tag), src[i:]):
        if t.group(0).startswith('</'):
            depth -= 1
            if depth == 0:
                return i, i + t.end()
        else:
            depth += 1
    return None


def parts_dir(lang):
    return os.path.join(ROOT, 'partials', lang)


def source(lang):
    return os.path.join(ROOT, lang, 'index.html')


def extract(lang):
    src = open(source(lang), encoding='utf-8', newline='').read()
    found = []
    for name, pat, tag in REGIONS:
        m = re.search(pat, src)
        if not m:
            print('  skip (not found):', name)
            continue
        sp = span(src, m, tag)
        if sp:
            found.append((name, sp[0], sp[1]))
    found.sort(key=lambda r: r[1])

    d = parts_dir(lang)
    os.makedirs(d, exist_ok=True)
    pieces, cursor = [], 0
    for idx, (name, a, b) in enumerate(found):
        if a > cursor:
            pieces.append(('%02d-gap' % idx, src[cursor:a]))
        pieces.append((name, src[a:b]))
        cursor = b
    if cursor < len(src):
        pieces.append(('99-tail', src[cursor:]))

    for nm, text in pieces:
        open(os.path.join(d, nm + '.html'), 'w', encoding='utf-8', newline='').write(text)
    open(os.path.join(d, 'order.txt'), 'w', encoding='utf-8').write('\n'.join(n for n, _ in pieces) + '\n')
    print('%s: %d parts, %d chars' % (lang, len(pieces), sum(len(t) for _, t in pieces)))


def assemble(lang):
    d = parts_dir(lang)
    order = [l.strip() for l in open(os.path.join(d, 'order.txt'), encoding='utf-8') if l.strip()]
    return ''.join(open(os.path.join(d, n + '.html'), encoding='utf-8', newline='').read() for n in order)


def check(lang):
    src = open(source(lang), encoding='utf-8', newline='').read()
    built = assemble(lang)
    if built == src:
        print('%s: PASSED - the parts rebuild the page byte for byte' % lang)
        return 0
    n = min(len(src), len(built))
    at = next((i for i in range(n) if src[i] != built[i]), n)
    print('%s: FAILED at char %d' % (lang, at))
    return 1


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--extract')
    ap.add_argument('--check')
    a = ap.parse_args()
    if a.extract:
        extract(a.extract)
    elif a.check:
        sys.exit(check(a.check))
