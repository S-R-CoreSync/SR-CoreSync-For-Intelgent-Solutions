# -*- coding: utf-8 -*-
"""
S&R CoreSync — locale sync engine (stage C).

One source of truth: the hero region of index.html, marked with
  <!-- SR:BEGIN hero --> ... <!-- SR:END hero -->
and the three shared style layers (#hv2-css, #hv2-fixes, #hv2-order).

    python scripts/sync_locales.py --write   # push the master into every locale
    python scripts/sync_locales.py --check   # exit 1 if any locale drifted

Only the locales that have i18n/locales/<lang>.json are touched.
"""
import re, os, sys, json, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(ROOT, 'index.html')
LOCALES = os.path.join(ROOT, 'i18n', 'locales')
AR = re.compile(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]')
BEGIN, END = '<!-- SR:BEGIN hero -->', '<!-- SR:END hero -->'

LTR = """
/* LTR corrections for localized pages */
html[dir="ltr"] .hv2__copy{align-items:flex-start !important; text-align:left !important}
html[dir="ltr"] .hv2__chips .hv2__chiprow{direction:ltr !important; justify-content:flex-start !important}
html[dir="ltr"] .hv2__badge, html[dir="ltr"] .hv2__h1{text-align:left !important}
html[dir="ltr"] .hv2__rot span{inset-inline-start:0}

/* legacy hero remnants must not survive beside the new hero */
#hero > *:not(.hv2):not(.hero-motion-canvas):not(.overlay){display:none !important}
#hero .hero-sectors-marquee, #hero .hero-compact-sectors-row{display:none !important}
"""


def span(src, marker, tag='div'):
    i = src.index(marker)
    depth = 0
    for m in re.finditer(r'<%s\b|</%s>' % (tag, tag), src[i:]):
        if m.group(0).startswith('</'):
            depth -= 1
            if depth == 0:
                return i, i + m.end()
        else:
            depth += 1
    raise SystemExit('unbalanced ' + marker)


def read(p):
    return open(p, encoding='utf-8', newline='').read()


def write(p, s):
    open(p, 'w', encoding='utf-8', newline='').write(s)


def master_parts():
    s = read(MASTER)
    if BEGIN in s:
        a = s.index(BEGIN) + len(BEGIN)
        b = s.index(END)
        hero = s[a:b]
    else:
        i, j = span(s, '<div class="hv2" id="hv2-hero">')
        hero = s[i:j]
    styles = []
    for sid in ('hv2-css', 'hv2-fixes', 'hv2-order'):
        m = re.search(r'<style id="%s">(.*?)</style>' % sid, s, re.S)
        assert m, sid
        styles.append(re.sub(r'/\*.*?\*/', '', m.group(1), flags=re.S).strip())
    return hero, '\n'.join(styles) + LTR


def translate(text, table):
    for k, v in sorted(table.items(), key=lambda kv: -len(kv[0])):
        text = text.replace(k, v)
    return text


def render(hero, css, table):
    h = translate(hero, table).replace('./assets/', '../assets/')
    c = translate(css, table)
    left = AR.findall(h + c)
    if left:
        raise SystemExit('Arabic left after translation: %r' % ''.join(left[:20]))
    return h, c


def sync_page(lang, hero_tpl, css_tpl, table, dry):
    p = os.path.join(ROOT, lang, 'index.html')
    if not os.path.exists(p):
        return lang, 'missing'
    s = read(p)
    nl = '\r\n' if '\r\n' in s else '\n'
    head, css = render(hero_tpl, css_tpl, table)

    # 1 · hero region
    if BEGIN in s and END in s:
        a = s.index(BEGIN) + len(BEGIN)
        b = s.index(END)
        s = s[:a] + nl + head + nl + s[b:]
        action = 'updated'
    else:
        i, j = span(s, '<div class="hv2" id="hv2-hero">')
        s = s[:i] + BEGIN + nl + head + nl + END + s[j:]
        action = 'marked'

    # 2 · style layer
    m = re.search(r'(<style id="hv2-port">)(.*?)(</style>)', s, re.S)
    if m:
        s = s[:m.start(2)] + nl + css + nl + s[m.end(2):]
    else:
        k = s.lower().rindex('</head>')
        s = s[:k] + '<style id="hv2-port">' + nl + css + nl + '</style>' + nl + s[k:]

    if dry:
        return lang, 'DRIFT' if s != read(p) else 'ok'
    if s != read(p):
        write(p, s)
        return lang, action
    return lang, 'ok'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    hero_tpl, css_tpl = master_parts()

    langs = sorted(f[:-5] for f in os.listdir(LOCALES) if f.endswith('.json'))
    drift = 0
    for lang in langs:
        table = json.load(open(os.path.join(LOCALES, lang + '.json'), encoding='utf-8'))
        name, state = sync_page(lang, hero_tpl, css_tpl, table, dry=a.check)
        print('%-3s %s' % (name, state))
        if a.check and state == 'DRIFT':
            drift += 1
    if a.check:
        print('\n%d page(s) drifted' % drift)
        sys.exit(1 if drift else 0)


if __name__ == '__main__':
    main()
