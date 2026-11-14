# -*- coding: utf-8 -*-
"""Last three strings on da, last one on sv - matched tolerantly so a newline
inside the sentence cannot hide them again."""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'

PAIRS = {
 'da': [
   ('A genuine quantum leap in our multi-warehouse management and accounting workflows after deploying S&R CoreSync custom ERP. Exceptional precision and architectural rigor.',
    'Et reelt kvantespring i vores lagerstyring og bogholderi efter implementeringen af S&R CoreSync specialbyggede ERP. Enestående præcision og arkitektonisk stringens.'),
   ('Their dual mastery of cutting-edge software engineering and financial regulations saved us hundreds of manual hours every monthly close and revenue reconciliation.',
    'Deres dobbelte ekspertise i avanceret softwareudvikling og finansiel regulering sparer os hundredvis af manuelle timer ved hver månedsafslutning og afstemning.'),
 ],
 'sv': [
   ('A genuine quantum leap in our multi-warehouse management and accounting workflows after deploying S&R CoreSync custom ERP. Exceptional precision and architectural rigor.',
    'Ett verkligt kvantsprång i vår lagerhantering och redovisning efter införandet av S&R CoreSync skräddarsydda ERP. Enastående precision och arkitektonisk stringens.'),
   ('Their dual mastery of cutting-edge software engineering and financial regulations saved us hundreds of manual hours every monthly close and revenue reconciliation.',
    'Deras dubbla expertis inom avancerad mjukvaruutveckling och finansiell reglering sparar oss hundratals manuella timmar vid varje månadsavslut och avstämning.'),
 ],
}

PORTAL = '🛡️ Software License Management Portal • Exclusively for Salim Aziza, Founder & Chief Architect • S&R CoreSync For Intelligent Solutions'
PORTAL_TR = {
 'da': '🛡️ Portal til styring af softwarelicenser • Eksklusivt for Eng. Salim Aziza, grundlægger og chefarkitekt • S&R CoreSync For Intelligent Solutions',
 'sv': '🛡️ Portal för hantering av mjukvarulicenser • Exklusivt för Eng. Salim Aziza, grundare och chefsarkitekt • S&R CoreSync For Intelligent Solutions',
}

for lang, pairs in PAIRS.items():
    p = os.path.join(ROOT, lang, 'index.html')
    s = open(p, encoding='utf-8', newline='').read()
    n = 0

    for en, tr in pairs + [(PORTAL, PORTAL_TR[lang])]:
        # tolerate any whitespace between words
        pattern = re.compile(r'\s+'.join(re.escape(w) for w in en.split()), re.S)
        s, k = pattern.subn(lambda m: tr, s)
        n += k

    open(p, 'w', encoding='utf-8', newline='').write(s)
    print('%-3s replacements: %d' % (lang, n))
