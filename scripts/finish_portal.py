# -*- coding: utf-8 -*-
"""The portal footer note: replace from a plain anchor, whatever emoji precedes it."""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
TR = {
 'da': 'Portal til styring af softwarelicenser — eksklusivt for Eng. Salim Aziza, grundlægger og chefarkitekt — S&R CoreSync For Intelligent Solutions',
 'sv': 'Portal för hantering av mjukvarulicenser — exklusivt för Eng. Salim Aziza, grundare och chefsarkitekt — S&R CoreSync For Intelligent Solutions',
}

ANCHOR = re.compile(r'Software License Management Portal.*?S&R CoreSync For Intelligent Solutions', re.S)

for lang, tr in TR.items():
    p = os.path.join(ROOT, lang, 'index.html')
    s = open(p, encoding='utf-8', newline='').read()
    s2, n = ANCHOR.subn(tr, s)
    open(p, 'w', encoding='utf-8', newline='').write(s2)
    print('%-3s replaced: %d' % (lang, n))
