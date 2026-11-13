# -*- coding: utf-8 -*-
"""Footer parity: how far each locale's footer has drifted from the master."""
import re, os, sys

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
MASTER = os.path.join(ROOT, 'index.html')


def footer_links(path):
    s = open(path, encoding='utf-8', newline='').read()
    i = s.find('<footer')
    if i == -1:
        return None
    # footer usually ends at the last </footer> in the document
    j = s.rfind('</footer>')
    seg = s[i:j] if j > i else s[i:]
    return [h for h in re.findall(r'<a[^>]*href="([^"]+)"', seg)]


def main():
    base = footer_links(MASTER)
    if base is None:
        print('master has no <footer>')
        return
    print('master footer links:', len(base))
    rows = []
    for d in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, d, 'index.html')
        if not os.path.isdir(os.path.join(ROOT, d)) or not os.path.exists(p):
            continue
        if d in ('scripts', 'i18n', 'css', 'js', 'docs', 'assets', 'templates'):
            continue
        links = footer_links(p)
        if links is None:
            rows.append((d, 'no footer', 0, 0))
            continue
        missing = [h for h in base if h not in links]
        extra = [h for h in links if h not in base]
        same_order = (links[:len(base)] == base)
        rows.append((d, 'order-ok' if same_order else 'order-differs', len(missing), len(extra)))
    bad = [r for r in rows if r[1] != 'order-ok']
    print('locales with a footer:', len(rows))
    print('locales differing:', len(bad))
    for r in bad[:30]:
        print('  %-4s %-14s missing=%-3d extra=%d' % r)


if __name__ == '__main__':
    main()
