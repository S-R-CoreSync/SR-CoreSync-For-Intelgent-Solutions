# -*- coding: utf-8 -*-
"""Anchor on text that contains no ampersand at all - that was the whole problem."""
import re, os

P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\fi\index.html'
s = open(P, encoding='utf-8', newline='').read()

FI_LONG = ('S&amp;R CoreSync For Intelligent Solutions tarjoaa yritystason kaupallistamisinfrastruktuurin, joka on '
           'rakennettu ohjelmistoarkkitehdeille ja kokeneille insinööreille. Julkaise omat työpöytätyökalusi, '
           'API:t ja SaaS-hankkeesi vahvistetussa oikeudellisessa kehyksessämme: kryptografiset lisenssiavaimet, '
           'automatisoitu SEPA- ja iDEAL-laskutus sekä eurooppalainen vaatimustenmukaisuus.')

pat1 = re.compile(r'S&amp;R CoreSync For Intelligent Solutions delivers an enterprise-grade.*?European enterprise compliance\.', re.S)
if pat1.search(s) is None:
    pat1 = re.compile(r'S&R CoreSync For Intelligent Solutions delivers an enterprise-grade.*?European enterprise compliance\.', re.S)
s, n1 = pat1.subn(FI_LONG, s)

pat2 = re.compile(r'Software License Management Portal.*?For Intelligent Solutions', re.S)
s, n2 = pat2.subn('Ohjelmistolisenssien hallintaportaali — yksinoikeudella Eng. Salim Azizalle, perustaja ja pääarkkitehti — S&amp;R CoreSync For Intelligent Solutions', s)

open(P, 'w', encoding='utf-8', newline='').write(s)
print('long:', n1, '· note:', n2)
