import json, os
ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
P = os.path.join(ROOT, 'i18n', 'nav', 'header-labels.json')
m = json.load(open(P, encoding='utf-8'))

# href -> {lang: label}
BATCH = {
 '#service':          {'de':'Leistungen','nl':'Diensten','fr':'Services','es':'Servicios','it':'Servizi'},
 '#pricing':          {'de':'Preise','nl':'Prijzen','fr':'Tarifs','es':'Precios','it':'Prezzi'},
 '#software-hub':     {'de':'Shop','nl':'Winkel','fr':'Boutique','es':'Tienda','it':'Negozio'},
 '#about':            {'de':'Über uns','nl':'Over ons','fr':'À propos','es':'Sobre nosotros','it':'Chi siamo'},
 '#founders-showcase':{'de':'Führung','nl':'Leiderschap','fr':'Direction','es':'Liderazgo','it':'Direzione'},
 '#roi-calculator':   {'de':'ROI','nl':'ROI','fr':'ROI','es':'ROI','it':'ROI'},
 '#faq':              {'de':'FAQ','nl':'FAQ','fr':'FAQ','es':'FAQ','it':'FAQ'},
 './blog.html':       {'de':'Journal','nl':'Journal','fr':'Journal','es':'Revista','it':'Journal'},
 './api-docs.html':   {'de':'API-Dokumentation','nl':'API-docs','fr':'Documentation API','es':'Documentación API','it':'Documentazione API'},
}

added = 0
for href, langs in BATCH.items():
    if href not in m:
        continue
    for lang, label in langs.items():
        if lang not in m[href]:
            m[href][lang] = label
            added += 1

json.dump(m, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('labels added:', added)

langs = ['de','nl','fr','es','it','pl','pt','ro','sv','cs','tr','el','da','no','fi','hu','sk','sl','hr','lt','lv','et','mt','ga','ku','bg']
print('\nheader label coverage per locale:')
for l in langs:
    have = sum(1 for v in m.values() if l in v)
    print('  %-3s %2d/%d' % (l, have, len(m)))
