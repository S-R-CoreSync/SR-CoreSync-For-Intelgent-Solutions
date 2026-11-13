# -*- coding: utf-8 -*-
"""Apply the calibrated footer to every locale, harvesting each page's own labels."""
import os, re, sys, json

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

# ── 1 · patch the renderer to accept harvested labels ───────────────────────
q = os.path.join(ROOT, 'scripts', 'sync_footer.py')
t = open(q, encoding='utf-8', newline='').read().replace('\r\n', '\n')

old_label = """def label(link, lang):
    v = link.get(lang)
    return v if v else link.get('en') or link.get('ar') or link['href']"""
new_label = """def key_of(href):
    h = href.split('#')[0]
    return h.split('/')[-1]


def label(link, lang, labels=None):
    if labels:
        k = key_of(link['href'])
        if k in labels:
            return labels[k]
    v = link.get(lang)
    return v if v else link.get('en') or link.get('ar') or link['href']"""

if 'def key_of(href)' not in t:
    assert old_label in t
    t = t.replace(old_label, new_label, 1)
if 'labels=None):' not in t:
    t = t.replace("def render(model, lang, base=''):", "def render(model, lang, base='', labels=None):", 1)
    t = t.replace("label(l, lang)", "label(l, lang, labels)")
open(q, 'w', encoding='utf-8', newline='').write(t.replace('\n', '\r\n'))

import sync_footer as SF

LANGS = ['de', 'nl', 'fr', 'es', 'it', 'pl', 'pt', 'ro', 'sv', 'cs', 'tr', 'el',
         'da', 'no', 'fi', 'hu', 'sk', 'sl', 'hr', 'lt', 'lv', 'et', 'mt', 'ga', 'ku', 'bg']


def footer_span(s):
    best = None
    for m in re.finditer(r'<footer\b[^>]*>', s):
        i = m.start()
        depth, end = 0, None
        for x in re.finditer(r'<footer\b|</footer>', s[i:]):
            if x.group(0).startswith('</'):
                depth -= 1
                if depth == 0:
                    end = i + x.end()
                    break
            else:
                depth += 1
        if end and (best is None or (end - i) > (best[1] - best[0])):
            best = (i, end)
    return best


def harvest(block):
    out = {}
    for m in re.finditer(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', block, re.S):
        href, inner = m.group(1), m.group(2)
        text = re.sub(r'<[^>]+>', ' ', inner)
        text = re.sub(r'\s+', ' ', text).strip()
        if text and href and not href.startswith('#'):
            out.setdefault(SF.key_of(href), text)
    return out


model = json.load(open(SF.MODEL, encoding='utf-8'))
done = 0
for lang in LANGS:
    p = os.path.join(ROOT, lang, 'index.html')
    if not os.path.exists(p):
        print(lang, 'missing'); continue
    s = open(p, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in s else '\n'
    span = footer_span(s)
    labels = harvest(s[span[0]:span[1]]) if span else {}
    block = SF.render(model, lang, '../', labels)

    m2 = re.search(r'<footer class="srf".*?</footer>', s, re.S)
    if m2:
        s = s[:m2.start()] + block + s[m2.end():]
    elif span:
        s = s[:span[0]] + block + s[span[1]:]
    else:
        print(lang, 'no footer'); continue

    if 'id="srf-css"' not in s:
        low = s.lower()
        i = low.find('</head')
        if i != -1:
            k = s.index('>', i) + 1
        else:
            j = low.find('<body')
            k = j if j != -1 else len(s)
        s = s[:k] + '<style id="srf-css">' + nl + SF.CSS + nl + '</style>' + nl + s[k:]

    open(p, 'w', encoding='utf-8', newline='').write(s)
    done += 1
    print('%-3s labels=%-2d' % (lang, len(labels)))

print('applied:', done)
