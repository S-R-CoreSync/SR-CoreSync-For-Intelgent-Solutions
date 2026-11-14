# -*- coding: utf-8 -*-
"""Apply one language map tolerantly: whitespace inside sentences, & as &amp;."""
import os, re, sys

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'


def apply(lang, table):
    p = os.path.join(ROOT, lang, 'index.html')
    s = open(p, encoding='utf-8', newline='').read()
    hits = 0
    for en, tr in table.items():
        # tolerate any run of whitespace between words, and both & forms
        pattern = re.compile(r'\s+'.join(re.escape(w) for w in en.split()), re.S)
        s, k = pattern.subn(lambda m: tr, s)
        hits += k

        if '&' in en:
            alt = en.replace('&', '&amp;')
            pattern2 = re.compile(r'\s+'.join(re.escape(w) for w in alt.split()), re.S)
            s, k2 = pattern2.subn(lambda m: tr.replace('&', '&amp;'), s)
            hits += k2

    open(p, 'w', encoding='utf-8', newline='').write(s)
    return hits


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from translations_no import NO
    n = apply('no', NO)
    print('no replacements:', n)
