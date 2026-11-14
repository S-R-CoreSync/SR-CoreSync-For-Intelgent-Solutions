# -*- coding: utf-8 -*-
"""The three lines that survived, matched on their plain form."""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'

PAIRS = {
 'da': [
  ('Everything included in the Starter package',
   'Alt inkluderet i Starter-pakken'),
  ('Everything in the Enterprise Growth package',
   'Alt i Enterprise Growth-pakken'),
  ('The study highlights rapid capital payback within 2 months, converting routine administrative overhead into high-velocity operational capacity and scalable enterprise growth.',
   'Analysen viser hurtig tilbagebetaling af kapitalen inden for 2 måneder og omdanner rutinemæssige administrative omkostninger til højhastigheds-driftskapacitet og skalerbar virksomhedsvækst.'),
 ],
 'sv': [
  ('Everything included in the Starter package',
   'Allt ingår i Starter-paketet'),
  ('Everything in the Enterprise Growth package',
   'Allt i Enterprise Growth-paketet'),
  ('The study highlights rapid capital payback within 2 months, converting routine administrative overhead into high-velocity operational capacity and scalable enterprise growth.',
   'Studien visar snabb återbetalning av kapital inom 2 månader och omvandlar rutinmässiga administrativa kostnader till höghastighetskapacitet och skalbar företagstillväxt.'),
 ],
}

for lang, pairs in PAIRS.items():
    p = os.path.join(ROOT, lang, 'index.html')
    s = open(p, encoding='utf-8', newline='').read()
    n = 0
    for en, tr in pairs:
        pattern = re.compile(r'\s+'.join(re.escape(w) for w in en.split()), re.S)
        s, k = pattern.subn(lambda m: tr, s)
        n += k
    open(p, 'w', encoding='utf-8', newline='').write(s)
    print('%-3s replaced: %d' % (lang, n))
