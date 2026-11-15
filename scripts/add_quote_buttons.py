# -*- coding: utf-8 -*-
"""Clone the Arabic 'official quote' button into every card that lacks one.

Each card in the master carries two actions: a WhatsApp/gold button and a quote
button, with a per-plan data-sr-args. Twenty-six languages kept only the first
and the English page kept only one card's worth. The args come from the master
block at the same index, so the handler opens the right context.
"""
import os, re, sys

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
MASTER = os.path.join(ROOT, 'index.html')

QUOTE = {
 'bg': 'Заявете официална оферта', 'ckb': 'داواکاری پێشنیاری فەرمی', 'cs': 'Vyžádat oficiální nabídku',
 'da': 'Anmod om et officielt tilbud', 'de': 'Offizielles Angebot anfordern', 'el': 'Ζητήστε επίσημη προσφορά',
 'en': 'Request an official quote', 'es': 'Solicitar presupuesto oficial', 'et': 'Küsi ametlikku pakkumist',
 'fi': 'Pyydä virallinen tarjous', 'fr': 'Demander un devis officiel', 'hr': 'Zatražite službenu ponudu',
 'hu': 'Kérjen hivatalos ajánlatot', 'it': 'Richiedi un preventivo ufficiale', 'ku': 'Daxwaza pêşniyareke fermî',
 'lt': 'Prašyti oficialaus pasiūlymo', 'lv': 'Pieprasīt oficiālu piedāvājumu', 'mt': 'Itlob kwotazzjoni uffiċjali',
 'nl': 'Officiële offerte aanvragen', 'no': 'Be om et offisielt tilbud', 'pl': 'Poproś o oficjalną ofertę',
 'pt': 'Solicitar orçamento oficial', 'ro': 'Solicitați o ofertă oficială', 'sk': 'Vyžiadať oficiálnu ponuku',
 'sl': 'Zahtevajte uradno ponudbo', 'sv': 'Begär en officiell offert', 'tr': 'Resmî teklif isteyin',
 'ga': 'Iarr luacháil oifigiúil',
}


def blocks(html):
    out = []
    for m in re.finditer(r'<div class="pricing-card-actions">', html):
        start = m.start()
        depth = 0
        for t in re.finditer(r'<div\b|</div>', html[start:], re.I):
            depth += -1 if t.group(0).startswith('</') else 1
            if depth == 0:
                out.append((start, start + t.end(), html[start:start + t.end()]))
                break
    return out


master = open(MASTER, encoding='utf-8', newline='').read()
mblocks = blocks(master)
pdf_buttons = []
for _, _, b in mblocks:
    m = re.search(r'<button[^>]*class="pricing-card-btn-pdf".*?</button>', b, re.S)
    pdf_buttons.append(m.group(0) if m else None)
print('master blocks: %d · quote buttons extracted: %d'
      % (len(mblocks), sum(1 for b in pdf_buttons if b)))

dry = '--dry' in sys.argv
pages = []
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        pages.append((os.path.join(ROOT, n, 'index.html'), n))

report = []
for path, lang in pages:
    s = open(path, encoding='utf-8', newline='').read()
    if 'pricing-card-btn-pdf' not in s and lang not in QUOTE:
        continue
    label = QUOTE.get(lang)
    if not label:
        report.append((lang, 'no label', 0))
        continue

    added = 0
    # work from the last block backwards so offsets stay valid
    for idx in range(len(blocks(s)) - 1, -1, -1):
        bstart, bend, markup = blocks(s)[idx]
        if 'pricing-card-btn-pdf' in markup:
            continue
        src = pdf_buttons[idx] if idx < len(pdf_buttons) else None
        if not src:
            continue
        new_btn = re.sub(r'<span>[^<]*</span>', '<span>%s 📄</span>' % label, src, count=1)
        # insert before the closing </div> of the action block
        close = markup.rfind('</div>')
        new_markup = markup[:close] + new_btn + markup[close:]
        s = s[:bstart] + new_markup + s[bend:]
        added += 1

    if added and not dry:
        open(path, 'w', encoding='utf-8', newline='').write(s)
    report.append((lang, 'ok', added))

for lang, note, n in report:
    if n or note != 'ok':
        print('%-4s %-8s %d' % (lang, note, n))
print('\nbuttons added in total:', sum(n for _, _, n in report))
