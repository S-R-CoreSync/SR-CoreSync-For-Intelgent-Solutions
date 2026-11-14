# -*- coding: utf-8 -*-
"""The two Finnish lines that resisted exact matching."""
import re, os

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
P = os.path.join(ROOT, 'fi', 'index.html')
s = open(P, encoding='utf-8', newline='').read()

LONG = ('S&R CoreSync For Intelligent Solutions leverer en kommersialiseringsinfrastruktur på bedriftsnivå, '
        'utviklet for programvarearkitekter og senioringeniører. Publiser dine egne skrivebordsverktøy, API-er '
        'og SaaS-prosjekter innenfor vårt verifiserte juridiske rammeverk, med kryptografiske lisensnøkler, '
        'automatisert SEPA- og iDEAL-fakturering og europeisk etterlevelse.')

FI_LONG = ('S&R CoreSync For Intelligent Solutions tarjoaa yritystason kaupallistamisinfrastruktuurin, joka on '
           'rakennettu ohjelmistoarkkitehdeille ja kokeneille insinööreille. Julkaise omat työpöytätyökalusi, '
           'API:t ja SaaS-hankkeesi vahvistetussa oikeudellisessa kehyksessämme: kryptografiset lisenssiavaimet, '
           'automatisoitu SEPA- ja iDEAL-laskutus sekä eurooppalainen vaatimustenmukaisuus.')

# 1 - the long paragraph, anchored on its first and last words
pat = re.compile(r'S&amp;R CoreSync For Intelligent Solutions delivers an enterprise-grade.*?European enterprise compliance\.', re.S)
s, n1 = pat.subn(FI_LONG.replace('&', '&amp;'), s)

# 2 - the licence note, anchored after the emoji
pat2 = re.compile(r'Software License Management Portal.*?S&amp;R CoreSync For Intelligent Solutions', re.S)
s, n2 = pat2.subn('Ohjelmistolisenssien hallintaportaali — yksinoikeudella Eng. Salim Azizalle, perustaja ja pääarkkitehti — S&amp;R CoreSync For Intelligent Solutions', s)

open(P, 'w', encoding='utf-8', newline='').write(s)
print('long paragraph replaced:', n1, '· licence note:', n2)
