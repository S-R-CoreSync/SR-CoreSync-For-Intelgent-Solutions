# -*- coding: utf-8 -*-
"""Footer parity: how far each locale's footer has drifted from the master."""
import re, os

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
MASTER = os.path.join(ROOT, 'index.html')


def footer_span(src):
    best = None
    for m in re.finditer(r'<footer\b[^>]*>', src):
        i = m.start()
        depth, end = 0, None
        for t in re.finditer(r'<footer\b|</footer>', src[i:]):
            if t.group(0).startswith('</'):
                depth -= 1
                if depth == 0:
                    end = i + t.end()
                    break
            else:
                depth += 1
        if end and (best is None or (end - i) > (best[1] - best[0])):
            best = (i, end)
    return src[best[0]:best[1]] if best else None


def footer_links(path):
    s = open(path, encoding='utf-8', newline='').read()
    span = footer_span(s)
    if not span:
        return None
    return re.findall(r'<a[^>]*href="([^"]+)"', span)


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
        if d in ('scripts', 'i18n', 'css', 'js', 'docs', 'assets', 'templates', 'node_modules'):
            continue
        links = footer_links(p)
        if links is None:
            rows.append((d, 'no footer', 0, 0))
            continue
        missing = [h for h in base if h not in links]
        extra = [h for h in links if h not in base]
        same_order = links == base
        rows.append((d, 'order-ok' if same_order else 'order-differs', len(missing), len(extra)))
    bad = [r for r in rows if r[1] != 'order-ok']
    print('locales with a footer:', len(rows))
    print('locales identical  :', len(rows) - len(bad))
    print('locales differing  :', len(bad))
    for r in bad[:30]:
        print('  %-4s %-14s missing=%-3d extra=%d' % r)


if __name__ == '__main__':
    main()
