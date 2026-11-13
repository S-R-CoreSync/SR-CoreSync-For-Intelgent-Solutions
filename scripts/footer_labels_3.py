# -*- coding: utf-8 -*-
"""Footer labels batch 3: tr, el, da, no, fi."""
import os, re, sys, json

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import sync_footer as SF

MODEL = os.path.join(ROOT, 'i18n', 'footer.calibrated.json')

DATA = {
 'tr': {
   'titles': ['Hizmetler', 'Şirket', 'Hukuk ve uyum', 'İletişim'],
   'labels': ['Bulut yazılımı', 'Hazır platformlar', 'Lisans hesaplayıcı', 'Proje hesaplayıcı',
              'Şirket hakkında', 'Yönetim', 'Portföy', 'Günlük',
              'Gizlilik ve çerezler', 'Koşullar', 'Belge doğrula', 'Güven merkezi', 'Analiz ayarları',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Danışmanlık randevusu'],
   'tag': "Amsterdam'dan egemen sistem mühendisliği",
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Tüm hakları saklıdır.'},
 'el': {
   'titles': ['Υπηρεσίες', 'Εταιρεία', 'Νομικά & συμμόρφωση', 'Επικοινωνία'],
   'labels': ['Λογισμικό cloud', 'Έτοιμες πλατφόρμες', 'Υπολογιστής αδειών', 'Υπολογιστής έργων',
              'Σχετικά με την εταιρεία', 'Διοίκηση', 'Χαρτοφυλάκιο', 'Ημερολόγιο',
              'Απόρρητο & cookies', 'Όροι', 'Επαλήθευση εγγράφου', 'Κέντρο εμπιστοσύνης', 'Ρυθμίσεις ανάλυσης',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Κλείστε μια συμβουλευτική'],
   'tag': 'Κυρίαρχη μηχανική συστημάτων από το Άμστερνταμ',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Όλα τα δικαιώματα διατηρούνται.'},
 'da': {
   'titles': ['Ydelser', 'Virksomhed', 'Jura og overholdelse', 'Kontakt'],
   'labels': ['Cloudsoftware', 'Klar-til-brug platforme', 'Licensberegner', 'Projektberegner',
              'Om virksomheden', 'Ledelse', 'Portfolio', 'Journal',
              'Privatliv og cookies', 'Vilkår', 'Verificér et dokument', 'Trustcenter', 'Analyseindstillinger',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Book en konsultation'],
   'tag': 'Suveræn systemteknik fra Amsterdam',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Alle rettigheder forbeholdes.'},
 'no': {
   'titles': ['Tjenester', 'Selskap', 'Jus og etterlevelse', 'Kontakt'],
   'labels': ['Skybasert programvare', 'Ferdige plattformer', 'Lisenskalkulator', 'Prosjektkalkulator',
              'Om selskapet', 'Ledelse', 'Portefølje', 'Journal',
              'Personvern og informasjonskapsler', 'Vilkår', 'Verifiser et dokument', 'Trustsenter', 'Analyseinnstillinger',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Book en konsultasjon'],
   'tag': 'Suveren systemteknikk fra Amsterdam',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Alle rettigheter forbeholdt.'},
 'fi': {
   'titles': ['Palvelut', 'Yritys', 'Juridiikka ja vaatimustenmukaisuus', 'Yhteystiedot'],
   'labels': ['Pilviohjelmisto', 'Valmiit alustat', 'Lisenssilaskuri', 'Projektlaskuri',
              'Tietoa yrityksestä', 'Johto', 'Portfolio', 'Journal',
              'Tietosuoja ja evästeet', 'Ehdot', 'Vahvista asiakirja', 'Luottamuskeskus', 'Analytiikka-asetukset',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Varaa konsultaatio'],
   'tag': 'Suvereenia järjestelmäsuunnittelua Amsterdamista',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Kaikki oikeudet pidätetään.'},
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
