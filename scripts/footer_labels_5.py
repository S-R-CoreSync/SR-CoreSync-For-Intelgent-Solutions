# -*- coding: utf-8 -*-
"""Footer labels batch 5 (final): lv, et, mt, ga, ku, bg."""
import os, re, sys, json

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import sync_footer as SF

MODEL = os.path.join(ROOT, 'i18n', 'footer.calibrated.json')

DATA = {
 'lv': {
   'titles': ['Pakalpojumi', 'Uzņēmums', 'Juridiskie jautājumi un atbilstība', 'Kontakti'],
   'labels': ['Mākoņprogrammatūra', 'Gatavas platformas', 'Licenču kalkulators', 'Projektu kalkulators',
              'Par uzņēmumu', 'Vadība', 'Portfelis', 'Žurnāls',
              'Privātums un sīkfaili', 'Noteikumi', 'Pārbaudīt dokumentu', 'Uzticības centrs', 'Analītikas iestatījumi',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Rezervēt konsultāciju'],
   'tag': 'Suverēna sistēmu inženierija no Amsterdamas',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Visas tiesības aizsargātas.'},
 'et': {
   'titles': ['Teenused', 'Ettevõte', 'Õigus ja vastavus', 'Kontakt'],
   'labels': ['Pilvtarkvara', 'Valmis platvormid', 'Litsentsikalkulaator', 'Projektikalkulaator',
              'Ettevõttest', 'Juhtkond', 'Portfell', 'Ajakiri',
              'Privaatsus ja küpsised', 'Tingimused', 'Kontrolli dokumenti', 'Usalduskeskus', 'Analüütika seaded',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Broneeri konsultatsioon'],
   'tag': 'Suveräänne süsteemiinseneeria Amsterdamist',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Kõik õigused kaitstud.'},
 'mt': {
   'titles': ['Servizzi', 'Kumpanija', 'Legali u konformità', 'Kuntatt'],
   'labels': ['Software cloud', 'Pjattaformi lesti', 'Kalkulatur tal-liċenzji', 'Kalkulatur tal-proġetti',
              'Dwar il-kumpanija', 'Tmexxija', 'Portfolio', 'Ġurnal',
              'Privatezza u cookies', 'Termini', 'Ivverifika dokument', 'Ċentru tal-fiduċja', 'Settings tal-analitika',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Ibbukkja konsultazzjoni'],
   'tag': 'Inġinerija tas-sistemi sovrani minn Amsterdam',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Id-drittijiet kollha riservati.'},
 'ga': {
   'titles': ['Seirbhísí', 'Cuideachta', 'Dlí agus comhlíonadh', 'Teagmháil'],
   'labels': ['Bogearraí scamall', 'Ardáin réidh', 'Áireamhán ceadúnas', 'Áireamhán tionscadail',
              'Faoin gcuideachta', 'Ceannaireacht', 'Punann', 'Dialann',
              'Príobháideachas agus fianáin', 'Téarmaí', 'Fíoraigh doiciméad', 'Lár iontaoibhe', 'Socruithe anailíse',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Cuir coinne le comhairle'],
   'tag': 'Innealtóireacht córas ceannasach ó Amstardam',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Gach ceart ar cosaint.'},
 'ku': {
   'titles': ['Xizmet', 'Pargîdan', 'Hiqûq û lihevhatin', 'Têkilî'],
   'labels': ['Nermalava cloud', 'Platformên amade', 'Hesabkera lîsansan', 'Hesabkera projeyan',
              'Derbarê pargîdanê', 'Rêveberî', 'Portfolîo', 'Kovar',
              'Nepenî û cookies', 'Merc', 'Belgeyê piştrast bike', 'Navenda baweriyê', 'Sazkariyên analîzê',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Şêwirmendiyê tomar bike'],
   'tag': 'Endezyariya pergalên serwer ji Amsterdamê',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Hemû maf parastî ne.'},
 'bg': {
   'titles': ['Услуги', 'Компания', 'Правно и съответствие', 'Контакт'],
   'labels': ['Облачен софтуер', 'Готови платформи', 'Калкулатор за лицензи', 'Калкулатор за проекти',
              'За компанията', 'Ръководство', 'Портфолио', 'Дневник',
              'Поверителност и бисквитки', 'Условия', 'Провери документ', 'Център за доверие', 'Настройки за анализ',
              'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Запази консултация'],
   'tag': 'Суверенно системно инженерство от Амстердам',
   'legal': '© 2026 S&R CoreSync For Intelligent Solutions — Всички права запазени.'},
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
