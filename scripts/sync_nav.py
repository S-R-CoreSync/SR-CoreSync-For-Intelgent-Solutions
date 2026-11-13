# -*- coding: utf-8 -*-
"""
Static main menu: permute only the five primary items, nothing else.

The dropdown ("More") and its nested list are never rebuilt — they are left
byte-for-byte in place. Only the first five <li> blocks are reordered and
renumbered, so the markup becomes the source of truth without touching
anything the browser would have to infer.
"""
import re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDER = ['#service', '#pricing', '#software-hub', '#about', '#founders-showcase']
PAGES = ['index.html', 'en/index.html', 'de/index.html', 'nl/index.html',
         'fr/index.html', 'es/index.html', 'it/index.html']
NUM = re.compile(r'(<span[^>]*>)\s*\d{2}\s*/\s*(</span>)')


def li_spans(body):
    out, depth, start = [], 0, None
    for m in re.finditer(r'<li\b|</li>', body):
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


def renumber(chunk, n):
    return NUM.sub(lambda m: m.group(1) + '%02d /' % n + m.group(2), chunk, count=1)


def fix(path):
    s = open(path, encoding='utf-8', newline='').read()
    m = re.search(r'<ul class="nav-menu-main">', s)
    if not m:
        return path, 'no menu'
    start = m.end()
    depth, end = 0, None
    for mm in re.finditer(r'<ul\b|</ul>', s[start:]):
        if mm.group(0) == '</ul>':
            depth -= 1
            if depth == 0:
                end = start + mm.start()
                break
        else:
            depth += 1
    body = s[start:end]
    spans = li_spans(body)

    chunks = []
    for a, b in spans:
        chunk = body[a:b]
        h = re.search(r'<a[^>]*href="([^"]+)"', chunk)
        chunks.append((h.group(1) if h else None, a, b, chunk))

    index = {}
    for key, a, b, chunk in chunks:
        if key in ORDER and key not in index:
            index[key] = (a, b, chunk)
    if len(index) != len(ORDER):
        return path, 'missing %s' % [k for k in ORDER if k not in index]

    # the five primary items must be the first five blocks, in any order
    first_five = chunks[:5]
    if any(k not in ORDER for k, *_ in first_five):
        return path, 'primary items are not the first five'

    lo = min(a for _, a, _, _ in first_five)
    hi = max(b for _, _, b, _ in first_five)
    separator = body[first_five[0][2]:first_five[1][1]] if len(first_five) > 1 else ''

    rebuilt = ''
    for i, key in enumerate(ORDER, 1):
        rebuilt += renumber(index[key][2], i)
        if i < len(ORDER):
            rebuilt += separator

    new_body = body[:lo] + rebuilt + body[hi:]
    new_s = s[:start] + new_body + s[end:]

    if new_s != s:
        open(path, 'w', encoding='utf-8', newline='').write(new_s)
        return path, 'ordered'
    return path, 'ok'


if __name__ == '__main__':
    for rel in PAGES:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            print('%-16s %s' % fix(p))
