# -*- coding: utf-8 -*-
"""Footer labels batch 1: de, nl, fr, es, it."""
import os, re, sys, json

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import sync_footer as SF

MODEL = os.path.join(ROOT, 'i18n', 'footer.calibrated.json')

TITLES = {
 'de': ['Leistungen', 'Unternehmen', 'Recht & Compliance', 'Kontakt'],
 'nl': ['Diensten', 'Bedrijf', 'Juridisch & compliance', 'Contact'],
 'fr': ['Services', 'Entreprise', 'Juridique & conformité', 'Contact'],
 'es': ['Servicios', 'Empresa', 'Legal y cumplimiento', 'Contacto'],
 'it': ['Servizi', 'Azienda', 'Legale e conformità', 'Contatti'],
}

L = {
 'de': ['Cloud-Software', 'Fertige Plattformen', 'Lizenzrechner', 'Projekt-Kalkulator',
        'Über das Unternehmen', 'Geschäftsführung', 'Referenzen', 'Journal',
        'Datenschutz & Cookies', 'AGB', 'Dokument prüfen', 'Trust Center', 'Analyse-Einstellungen',
        'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Beratung buchen'],
 'nl': ['Cloudsoftware', 'Kant-en-klare platforms', 'Licentiecalculator', 'Projectcalculator',
        'Over het bedrijf', 'Directie', 'Portfolio', 'Journaal',
        'Privacy & cookies', 'Voorwaarden', 'Document verifiëren', 'Trustcentrum', 'Analyse-instellingen',
        'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Adviesgesprek boeken'],
 'fr': ['Logiciel cloud', 'Plateformes prêtes', 'Calculateur de licences', 'Estimateur de projet',
        'À propos', 'Direction', 'Réalisations', 'Journal',
        'Confidentialité & cookies', 'Conditions', 'Vérifier un document', 'Centre de confiance', "Paramètres d'analyse",
        'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Réserver une consultation'],
 'es': ['Software cloud', 'Plataformas listas', 'Calculadora de licencias', 'Estimador de proyectos',
        'Sobre la empresa', 'Dirección', 'Portafolio', 'Revista',
        'Privacidad y cookies', 'Términos', 'Verificar un documento', 'Centro de confianza', 'Ajustes de analítica',
        'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Reservar una consulta'],
 'it': ['Software cloud', 'Piattaforme pronte', 'Calcolatore licenze', 'Stima progetto',
        'Chi siamo', 'Direzione', 'Portfolio', 'Journal',
        'Privacy e cookie', 'Termini', 'Verifica un documento', 'Centro fiducia', 'Impostazioni analisi',
        'info@sr-coresync.com', '+31 6 1811 1116', 'WhatsApp', 'Prenota una consulenza'],
}

TAG = {
 'de': 'Souveräne Systemtechnik aus Amsterdam',
 'nl': 'Soevereine systeemtechniek uit Amsterdam',
 'fr': 'Ingénierie de systèmes souverains depuis Amsterdam',
 'es': 'Ingeniería de sistemas soberanos desde Ámsterdam',
 'it': 'Ingegneria di sistemi sovrani da Amsterdam',
}
LEGAL = {
 'de': '© 2026 S&R CoreSync For Intelligent Solutions — Alle Rechte vorbehalten.',
 'nl': '© 2026 S&R CoreSync For Intelligent Solutions — Alle rechten voorbehouden.',
 'fr': '© 2026 S&R CoreSync For Intelligent Solutions — Tous droits réservés.',
 'es': '© 2026 S&R CoreSync For Intelligent Solutions — Todos los derechos reservados.',
 'it': '© 2026 S&R CoreSync For Intelligent Solutions — Tutti i diritti riservati.',
}

model = json.load(open(MODEL, encoding='utf-8'))
for lang in L:
    i = 0
    for b, title in zip(model['blocks'], TITLES[lang]):
        b['title_' + lang] = title
        for l in b['links']:
            l[lang] = L[lang][i]
            i += 1
    model['tagline'][lang] = TAG[lang]
    model['legal_line'][lang] = LEGAL[lang]

json.dump(model, open(MODEL, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('model updated for', ', '.join(L))

# render those five pages straight from the model (no harvesting)
for lang in L:
    p = os.path.join(ROOT, lang, 'index.html')
    s = open(p, encoding='utf-8', newline='').read()
    block = SF.render(model, lang, '../', None)
    m = re.search(r'<footer class="srf".*?</footer>', s, re.S)
    if not m:
        print(lang, 'no srf'); continue
    s = s[:m.start()] + block + s[m.end():]
    open(p, 'w', encoding='utf-8', newline='').write(s)
    print(lang, 'rendered')
