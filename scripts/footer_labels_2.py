# -*- coding: utf-8 -*-
"""Footer labels batch 2: pl, pt, ro, sv, cs."""
import os, re, sys, json

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import sync_footer as SF

MODEL = os.path.join(ROOT, 'i18n', 'footer.calibrated.json')

DATA = {
 'pl': {
   'titles': ['Usługi', 'Firma', 'Prawo i zgodność', 'Kontakt'],
   'labels': ['Oprogramowanie chmurowe', 'Gotowe platformy', 'Kalkulator licencji', 'Kalkulator projektów',
              'O firmie', 'Kierownictwo', 'Portfolio', 'Dziennik',
              'Prywatność i pliki cookie', 'Regulamin', 'Zweryfikuj dokument', 'Centrum zaufania', 'Ustawienia analityki',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Zarezerwuj konsultację'],
   'tag': 'Suwerenna inżynieria systemów z Amsterdamu',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Wszelkie prawa zastrzeżone.'},
 'pt': {
   'titles': ['Serviços', 'Empresa', 'Jurídico e conformidade', 'Contacto'],
   'labels': ['Software cloud', 'Plataformas prontas', 'Calculadora de licenças', 'Estimador de projetos',
              'Sobre a empresa', 'Direção', 'Portfólio', 'Jornal',
              'Privacidade e cookies', 'Termos', 'Verificar um documento', 'Centro de confiança', 'Definições de análise',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Marcar uma consulta'],
   'tag': 'Engenharia de sistemas soberanos de Amesterdão',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Todos os direitos reservados.'},
 'ro': {
   'titles': ['Servicii', 'Companie', 'Juridic și conformitate', 'Contact'],
   'labels': ['Software cloud', 'Platforme gata', 'Calculator de licențe', 'Estimator de proiecte',
              'Despre companie', 'Conducere', 'Portofoliu', 'Jurnal',
              'Confidențialitate și cookie-uri', 'Termeni', 'Verifică un document', 'Centru de încredere', 'Setări analitice',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Rezervă o consultație'],
   'tag': 'Inginerie de sisteme suverane din Amsterdam',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Toate drepturile rezervate.'},
 'sv': {
   'titles': ['Tjänster', 'Företag', 'Juridik och efterlevnad', 'Kontakt'],
   'labels': ['Molnprogramvara', 'Färdiga plattformar', 'Licenskalkylator', 'Projektkalkylator',
              'Om företaget', 'Ledning', 'Portfolio', 'Journal',
              'Integritet och cookies', 'Villkor', 'Verifiera ett dokument', 'Trustcenter', 'Analysinställningar',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Boka en konsultation'],
   'tag': 'Suverän systemteknik från Amsterdam',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Alla rättigheter förbehållna.'},
 'cs': {
   'titles': ['Služby', 'Společnost', 'Právo a shoda', 'Kontakt'],
   'labels': ['Cloudový software', 'Hotové platformy', 'Kalkulačka licencí', 'Kalkulačka projektů',
              'O společnosti', 'Vedení', 'Portfolio', 'Journal',
              'Soukromí a cookies', 'Podmínky', 'Ověřit dokument', 'Centrum důvěry', 'Nastavení analytiky',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Rezervovat konzultaci'],
   'tag': 'Suverénní systémové inženýrství z Amsterdamu',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Všechna práva vyhrazena.'},
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
