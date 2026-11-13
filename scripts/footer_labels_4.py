# -*- coding: utf-8 -*-
"""Footer labels batch 4: hu, sk, sl, hr, lt."""
import os, re, sys, json

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import sync_footer as SF

MODEL = os.path.join(ROOT, 'i18n', 'footer.calibrated.json')

DATA = {
 'hu': {
   'titles': ['Szolgáltatások', 'Vállalat', 'Jog és megfelelés', 'Kapcsolat'],
   'labels': ['Felhőalapú szoftver', 'Kész platformok', 'Lizenkalkulátor', 'Projektkalkulátor',
              'A vállalatról', 'Vezetés', 'Portfólió', 'Napló',
              'Adatvédelem és sütik', 'Feltételek', 'Dokumentum ellenőrzése', 'Bizalmi központ', 'Analitikai beállítások',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Konzultáció foglalása'],
   'tag': 'Szuverén rendszertervezés Amszterdamból',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Minden jog fenntartva.'},
 'sk': {
   'titles': ['Služby', 'Spoločnosť', 'Právo a zhoda', 'Kontakt'],
   'labels': ['Cloudový softvér', 'Hotové platformy', 'Kalkulačka licencií', 'Kalkulačka projektov',
              'O spoločnosti', 'Vedenie', 'Portfólio', 'Denník',
              'Súkromie a cookies', 'Podmienky', 'Overiť dokument', 'Centrum dôvery', 'Nastavenia analytiky',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Rezervovať konzultáciu'],
   'tag': 'Suverénne systémové inžinierstvo z Amsterdamu',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Všetky práva vyhradené.'},
 'sl': {
   'titles': ['Storitve', 'Podjetje', 'Pravno in skladnost', 'Kontakt'],
   'labels': ['Oblačna programska oprema', 'Pripravljene platforme', 'Kalkulator licenc', 'Kalkulator projektov',
              'O podjetju', 'Vodstvo', 'Portfelj', 'Dnevnik',
              'Zasebnost in piškotki', 'Pogoji', 'Preveri dokument', 'Center zaupanja', 'Nastavitve analitike',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Rezervirajte posvet'],
   'tag': 'Suvereno sistemsko inženirstvo iz Amsterdama',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Vse pravice pridržane.'},
 'hr': {
   'titles': ['Usluge', 'Tvrtka', 'Pravno i usklađenost', 'Kontakt'],
   'labels': ['Cloud softver', 'Gotove platforme', 'Kalkulator licenci', 'Kalkulator projekata',
              'O tvrtki', 'Uprava', 'Portfolio', 'Dnevnik',
              'Privatnost i kolačići', 'Uvjeti', 'Provjeri dokument', 'Centar povjerenja', 'Postavke analitike',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Rezervirajte konzultacije'],
   'tag': 'Suvereno sistemsko inženjerstvo iz Amsterdama',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Sva prava pridržana.'},
 'lt': {
   'titles': ['Paslaugos', 'Įmonė', 'Teisė ir atitiktis', 'Kontaktai'],
   'labels': ['Debesų programinė įranga', 'Paruoštos platformos', 'Licencijų skaičiuoklė', 'Projektų skaičiuoklė',
              'Apie įmonę', 'Vadovybė', 'Portfelis', 'Žurnalas',
              'Privatumas ir slapukai', 'Sąlygos', 'Patvirtinti dokumentą', 'Pasitikėjimo centras', 'Analitikos nustatymai',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Rezervuoti konsultaciją'],
   'tag': 'Suvereni sistemų inžinerija iš Amsterdamo',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Visos teisės saugomos.'},
}

model = json.load(open(MODEL, encoding='utf-8'))
for lang, d in DATA.items():
    i = 0
    for b, title in zip(model['blocks'], d['titles']):
        b['title_' + lang] = title
        for l in b['links']:
            l[lang] = d['labels'][i]
            i += 1
    model['tagline'][lang] = d['tag']
    model['legal_line'][lang] = d['legal']

json.dump(model, open(MODEL, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('model updated:', ', '.join(DATA))

for lang in DATA:
    p = os.path.join(ROOT, lang, 'index.html')
    s = open(p, encoding='utf-8', newline='').read()
    block = SF.render(model, lang, '../', None)
    m = re.search(r'<footer class="srf".*?</footer>', s, re.S)
    if not m:
        print(lang, 'no srf'); continue
    s = s[:m.start()] + block + s[m.end():]
    open(p, 'w', encoding='utf-8', newline='').write(s)
    print(lang, 'rendered')
