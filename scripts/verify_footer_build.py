# -*- coding: utf-8 -*-
"""
P2 · second slice: the footer of any locale is generated, not pasted.

    python scripts/verify_footer_build.py de fr it
"""
import re, os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import sync_footer as SF


def current(lang):
    p = os.path.join(ROOT, lang, 'index.html')
    s = open(p, encoding='utf-8', newline='').read()
    m = re.search(r'<footer class="srf".*?</footer>', s, re.S)
    return m.group(0) if m else None


def norm(t):
    return re.sub(r'\s+', ' ', t or '').strip()


def main():
    langs = sys.argv[1:] or ['de']
    model = json.load(open(SF.MODEL, encoding='utf-8'))
    bad = 0
    for lang in langs:
        cur = current(lang)
        if cur is None:
            print('%-3s no srf footer' % lang)
            continue
        gen = SF.render(model, lang, '../', None)
        if norm(gen) == norm(cur):
            print('%-3s IDENTICAL  (%d chars)' % (lang, len(norm(cur))))
        else:
            bad += 1
            a, b = norm(gen), norm(cur)
            k = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), min(len(a), len(b)))
            print('%-3s DIFFERS at %d' % (lang, k))
            print('   generated: %r' % a[max(0, k - 40):k + 40])
            print('   current  : %r' % b[max(0, k - 40):k + 40])
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
