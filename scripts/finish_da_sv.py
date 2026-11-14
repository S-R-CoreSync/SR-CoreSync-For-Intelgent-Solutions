# -*- coding: utf-8 -*-
"""Finish da/sv: the strings the first pass missed, including the & variants."""
import os

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'

SV = {
 'Integrated Software Systems & AI Solutions': 'Integrerade mjukvarusystem och AI-lösningar',
 'Custom Cloud Software': 'Skräddarsydd molnmjukvara',
 'Complete ERP for any bakery or chain: cloud POS, production & oven scheduling, inventory, and driver app with route optimization & proof of delivery.': 'Komplett ERP för varje bageri eller kedja: molnkassa, produktions- och ugnsplanering, lager samt förarapp med ruttoptimering och leveransbevis.',
 'Have Proprietary Software or Systems You Want to License & Distribute Commercially?': 'Har du egen mjukvara eller egna system som du vill licensiera och distribuera kommersiellt?',
 'Publish & Monetize Your Software': 'Publicera och tjäna pengar på din mjukvara',
 'The mobile platforms and executive cloud dashboards engineered by S&R CoreSync operate with blazing speed and bank-grade security. Our trusted technical partner.': 'Mobilplattformarna och molndashboardarna från S&R CoreSync går blixtsnabbt och med banksäkerhet. Vår betrodda tekniska partner.',
 'Our e-store design and iDEAL + Apple Pay integration doubled our Dutch sales within 2 months. Lightning-fast checkout and flawless UX from day one.': 'Vår webbutiksdesign och integrationen med iDEAL + Apple Pay fördubblade vår nederländska försäljning inom två månader. Blixtsnabb kassa och felfri UX från dag ett.',
 'Our brand identity and Brand Book were crafted with the finesse of world-class design houses in London and Milan. It won investor trust instantly.': 'Vår varumärkesidentitet och Brand Book formgavs med elegans från designhus i London och Milano. Det vann investerarnas förtroende direkt.',
 'Calculate the exact financial savings and reclaimed administrative hours unlocked when automating your workflows and integrating your ERP with our architects.': 'Beräkna den exakta besparingen och de återvunna administrationstimmarna när du automatiserar arbetsflöden och kopplar ditt ERP till våra arkitekter.',
 '🛡️ Software License Management Portal • Exclusively for Salim Aziza, Founder & Chief Architect • S&R CoreSync For Intelligent Solutions': '🛡️ Portal för hantering av mjukvarulicenser • Exklusivt för Eng. Salim Aziza, grundare och chefsarkitekt • S&R CoreSync For Intelligent Solutions',
}

DA = {
 'Integrated Software Systems & AI Solutions': 'Integrerede softwaresystemer og AI-løsninger',
 'Custom Cloud Software': 'Skræddersyet cloud-software',
 'Complete ERP for any bakery or chain: cloud POS, production & oven scheduling, inventory, and driver app with route optimization & proof of delivery.': 'Komplet ERP til ethvert bageri eller kæde: cloud-kasse, produktions- og ovnplanlægning, lager samt chaufførapp med ruteoptimering og leveringsbevis.',
 'Have Proprietary Software or Systems You Want to License & Distribute Commercially?': 'Har du egen software eller systemer, du vil licensere og distribuere kommercielt?',
 'Publish & Monetize Your Software': 'Udgiv og tjen penge på din software',
 'The mobile platforms and executive cloud dashboards engineered by S&R CoreSync operate with blazing speed and bank-grade security. Our trusted technical partner.': 'Mobilplatformene og cloud-dashboards fra S&R CoreSync kører med lynets hast og sikkerhed på bankniveau. Vores betroede tekniske partner.',
 'Our e-store design and iDEAL + Apple Pay integration doubled our Dutch sales within 2 months. Lightning-fast checkout and flawless UX from day one.': 'Vores webshopdesign og integration med iDEAL + Apple Pay fordoblede vores hollandske salg inden for to måneder. Lynhurtig betaling og fejlfri UX fra dag ét.',
 'Our brand identity and Brand Book were crafted with the finesse of world-class design houses in London and Milan. It won investor trust instantly.': 'Vores brandidentitet og Brand Book blev skabt med elegance fra designhuse i London og Milano. Det vandt investorens tillid med det samme.',
 'Calculate the exact financial savings and reclaimed administrative hours unlocked when automating your workflows and integrating your ERP with our architects.': 'Beregn den præcise besparelse og de genvundne administrative timer ved at automatisere arbejdsgange og koble dit ERP til vores arkitekter.',
 '🛡️ Software License Management Portal • Exclusively for Salim Aziza, Founder & Chief Architect • S&R CoreSync For Intelligent Solutions': '🛡️ Portal til styring af softwarelicenser • Eksklusivt for Eng. Salim Aziza, grundlægger og chefarkitekt • S&R CoreSync For Intelligent Solutions',
}

for lang, table in (('da', DA), ('sv', SV)):
    p = os.path.join(ROOT, lang, 'index.html')
    s = open(p, encoding='utf-8', newline='').read()
    hits = 0
    for en, tr in table.items():
        for variant in (en, en.replace('&', '&amp;')):
            n = s.count(variant)
            if n:
                s = s.replace(variant, tr.replace('&', '&amp;'))
                hits += n
    open(p, 'w', encoding='utf-8', newline='').write(s)
    left = sum(1 for en in table if en in s or en.replace('&', '&amp;') in s)
    print('%-3s replaced %-3d · left %d' % (lang, hits, left))
