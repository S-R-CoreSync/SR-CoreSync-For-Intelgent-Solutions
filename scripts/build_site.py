# -*- coding: utf-8 -*-
"""
P1 · structure extraction.

Splits index.html into ordered partials, then rebuilds the page from those
files and proves the result is identical. Nothing in index.html is touched.

    python scripts/build_site.py --extract
    python scripts/build_site.py --check
    python scripts/build_site.py --build      # writes build/index.html
"""
import re, os, sys, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(ROOT, 'index.html')
PARTS = os.path.join(ROOT, 'partials')
BUILD = os.path.join(ROOT, 'build')

# regions we lift out, in document order; everything between them is kept verbatim
REGIONS = [
    ('10-header', r'<header\b[^>]*class="[^"]*tf-header', 'header'),
    ('20-hero',   r'<section\b[^>]*\bid="hero"',          'section'),
    ('21-services',   r'<section\b[^>]*\bid="services"',         'section'),
    ('22-pricing',    r'<section\b[^>]*\bid="pricing"',          'section'),
    ('23-store',      r'<section\b[^>]*\bid="software-hub"',     'section'),
    ('24-about',      r'<section\b[^>]*\bid="about"',            'section'),
    ('25-leadership', r'<section\b[^>]*\bid="founders-showcase"','section'),
    ('30-footer', r'<footer\b[^>]*\bclass="[^"]*srf',     'footer'),
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
    raise SystemExit('unbalanced region at %d' % i)


def regions(src):
    out = []
    for name, pat, tag in REGIONS:
        m = re.search(pat, src)
        if not m:
            raise SystemExit('region not found: ' + name)
        a, b = span(src, m, tag)
        out.append((name, a, b))
    out.sort(key=lambda r: r[1])
    return out


def extract():
    src = open(MASTER, encoding='utf-8', newline='').read()
    regs = regions(src)
    os.makedirs(PARTS, exist_ok=True)
    pieces, cursor = [], 0
    for idx, (name, a, b) in enumerate(regs):
        if a > cursor:
            nm = '%02d-gap' % idx
            pieces.append((nm, src[cursor:a]))
        pieces.append((name, src[a:b]))
        cursor = b
    if cursor < len(src):
        pieces.append(('99-tail', src[cursor:]))

    for nm, text in pieces:
        with open(os.path.join(PARTS, nm + '.html'), 'w', encoding='utf-8', newline='') as f:
            f.write(text)
    with open(os.path.join(PARTS, 'order.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(nm for nm, _ in pieces) + '\n')

    total = sum(len(t) for _, t in pieces)
    print('partials: %d files, %d chars (source %d)' % (len(pieces), total, len(src)))


def assemble():
    order = [l.strip() for l in open(os.path.join(PARTS, 'order.txt'), encoding='utf-8') if l.strip()]
    out = []
    for nm in order:
        p = os.path.join(PARTS, nm + '.html')
        if not os.path.exists(p):
            raise SystemExit('missing partial: ' + p)
        out.append(open(p, encoding='utf-8', newline='').read())
    return ''.join(out)


def check():
    src = open(MASTER, encoding='utf-8', newline='').read()
    built = assemble()
    if built == src:
        print('PASSED - the parts rebuild index.html byte for byte')
        return 0
    n = min(len(src), len(built))
    at = next((i for i in range(n) if src[i] != built[i]), n)
    print('FAILED - first difference at char %d' % at)
    print('  source: %r' % src[max(0, at - 60):at + 60])
    print('  built : %r' % built[max(0, at - 60):at + 60])
    return 1


def build():
    os.makedirs(BUILD, exist_ok=True)
    p = os.path.join(BUILD, 'index.html')
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(assemble())
    print('built:', p)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--extract', action='store_true')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--build', action='store_true')
    a = ap.parse_args()
    if a.extract:
        extract()
    elif a.build:
        build()
    else:
        sys.exit(check())
