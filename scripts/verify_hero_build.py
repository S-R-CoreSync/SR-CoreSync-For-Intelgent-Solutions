# -*- coding: utf-8 -*-
"""
P2 · first slice: the hero of any locale can be *generated*, not patched.

Reads partials/20-hero.html, translates it with i18n/locales/<lang>.json,
and compares the result with the hero currently inside <lang>/index.html.

    python scripts/verify_hero_build.py en de fr
"""
import re, os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERO_PART = os.path.join(ROOT, 'partials', '20-hero.html')
LOCALES = os.path.join(ROOT, 'i18n', 'locales')
BEGIN, END = '<!-- SR:BEGIN hero -->', '<!-- SR:END hero -->'


def translate(text, table):
    for k, v in sorted(table.items(), key=lambda kv: -len(kv[0])):
        text = text.replace(k, v)
    return text


def hero_block(text):
    i = text.index('<div class="hv2" id="hv2-hero">')
    depth = 0
    for m in re.finditer(r'<div\b|</div>', text[i:]):
        if m.group(0).startswith('</'):
            depth -= 1
            if depth == 0:
                return text[i:i + m.end()]
        else:
            depth += 1
    raise SystemExit('unbalanced hv2')


def generated(lang):
    hero = hero_block(open(HERO_PART, encoding='utf-8', newline='').read())
    table = json.load(open(os.path.join(LOCALES, lang + '.json'), encoding='utf-8'))
    return translate(hero, table).replace('./assets/', '../assets/')


def current(lang):
    p = os.path.join(ROOT, lang, 'index.html')
    s = open(p, encoding='utf-8', newline='').read()
    if BEGIN not in s:
        return None
    a = s.index(BEGIN) + len(BEGIN)
    b = s.index(END)
    return s[a:b]


def norm(t):
    t = re.sub(r'\s+', ' ', t or '').strip()
    return t


def main():
    langs = sys.argv[1:] or ['en']
    worst = 0
    for lang in langs:
        cur = current(lang)
        if cur is None:
            print('%-3s no hero markers' % lang)
            continue
        gen = generated(lang)
        if norm(gen) == norm(cur):
            print('%-3s IDENTICAL  (%d chars)' % (lang, len(norm(cur))))
        else:
            worst += 1
            a, b = norm(gen), norm(cur)
            k = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), min(len(a), len(b)))
            print('%-3s DIFFERS at %d' % (lang, k))
            print('   generated: %r' % a[max(0, k - 50):k + 50])
            print('   current  : %r' % b[max(0, k - 50):k + 50])
    sys.exit(1 if worst else 0)


if __name__ == '__main__':
    main()
