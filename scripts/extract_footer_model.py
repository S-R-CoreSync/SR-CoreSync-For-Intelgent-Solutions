# -*- coding: utf-8 -*-
"""
Footer model extraction - phase 1.

Reads the master footer and writes i18n/footer.model.json:
blocks -> heading + links (href, label, classes). No page is modified.

    python scripts/extract_footer_model.py
"""
import os, re, json, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(ROOT, 'index.html')
OUT = os.path.join(ROOT, 'i18n', 'footer.model.json')

try:
    from lxml import html as LH
except ImportError:
    LH = None


def footer_fragment(src):
    """Pick the largest <footer> block - the site footer, not the inline ones."""
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
        if not end:
            continue
        if best is None or (end - i) > (best[1] - best[0]):
            best = (i, end)
    if not best:
        raise SystemExit('no footer found')
    return src[best[0]:best[1]]


def clean(t):
    return re.sub(r'\s+', ' ', t or '').strip()


def walk(node, out):
    """Collect links in document order: href, visible text, class."""
    for a in node.iter('a'):
        href = a.get('href') or ''
        label = clean(a.text_content())
        out.append({'href': href, 'label': label, 'class': a.get('class') or ''})


def main():
    src = open(MASTER, encoding='utf-8', newline='').read()
    frag = footer_fragment(src)
    if LH is None:
        print('lxml missing')
        return
    root = LH.fragment_fromstring(frag, create_parent='div')
    footer = root[0]

    blocks = []
    for child in footer:
        if not isinstance(child.tag, str):
            continue
        tag = child.tag.lower()
        cls = child.get('class') or ''
        heading = ''
        for h in child.iter():
            if isinstance(h.tag, str) and h.tag.lower() in ('h2', 'h3', 'h4', 'h5', 'strong'):
                txt = clean(h.text_content())
                if txt:
                    heading = txt
                    break
        links = []
        walk(child, links)
        if tag in ('footer',):
            continue
        blocks.append({
            'index': len(blocks),
            'tag': tag,
            'class': cls,
            'heading': heading,
            'link_count': len(links),
            'links': links,
        })

    all_links = []
    walk(footer, all_links)
    model = {
        'source': 'index.html',
        'footer_class': footer.get('class') or '',
        'link_total': len(all_links),
        'block_count': len(blocks),
        'blocks': blocks,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(model, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('blocks :', model['block_count'])
    print('links  :', model['link_total'])
    print('written:', OUT)
    for b in blocks[:12]:
        print('  %2d %-10s links=%-3d  %s' % (b['index'], b['tag'], b['link_count'], b['heading'][:46]))


if __name__ == '__main__':
    main()
