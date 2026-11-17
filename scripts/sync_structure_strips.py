#!/usr/bin/env python3
"""Structural parity sync: give every localized portal the ar root's two
missing sections (#trust-metrics after the hero, #portals before
#services-compare) with localized strip content.

Approved suggestion #11 (2026-11-18): the Arabic root page is the normative
reference - every portal must share its ordered section skeleton (21
sections) and carry the same strips. Idempotent: sections already present
are skipped, so repeat runs produce zero diff.

Dictionaries are the single text source; guards read them directly.
"""
import argparse
import html
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Root-page trust metrics strip: 4 metric values are language-neutral
# (99.9% / EU & BTW / < 30s / Amsterdam HQ); the 4 labels + 2 aria labels
# are localized per language (source: ar root index.html).
TRUST_METRICS_LOCALIZATIONS = {
    'en': {
        'aria_section': 'S&R CoreSync in numbers',
        'aria_strip': 'Performance and European accreditation indicators',
        'l1': 'Cloud readiness',
        'l2': 'EU tax compliance',
        'l3': 'Instant start',
        'l4': 'Amsterdam HQ',
    },
    'nl': {
        'aria_section': 'S&R CoreSync in cijfers',
        'aria_strip': 'Prestatie- en Europese accreditatie-indicatoren',
        'l1': 'Cloudgereedheid',
        'l2': 'EU-belastingnaleving',
        'l3': 'Directe start',
        'l4': 'Hoofdkantoor Amsterdam',
    },
    'de': {
        'aria_section': 'S&R CoreSync in Zahlen',
        'aria_strip': 'Indikatoren für Leistung und europäische Akkreditierung',
        'l1': 'Cloud-Bereitschaft',
        'l2': 'EU-Steuer-Compliance',
        'l3': 'Sofortiger Start',
        'l4': 'Hauptsitz Amsterdam',
    },
    'fr': {
        'aria_section': 'S&R CoreSync en chiffres',
        'aria_strip': "Indicateurs de performance et d'accréditation européenne",
        'l1': 'Disponibilité cloud',
        'l2': 'Conformité fiscale UE',
        'l3': 'Démarrage instantané',
        'l4': "Siège social à Amsterdam",
    },
    'es': {
        'aria_section': 'S&R CoreSync en cifras',
        'aria_strip': 'Indicadores de rendimiento y acreditación europea',
        'l1': 'Disponibilidad en la nube',
        'l2': 'Cumplimiento fiscal de la UE',
        'l3': 'Inicio instantáneo',
        'l4': 'Sede en Ámsterdam',
    },
    'it': {
        'aria_section': 'S&R CoreSync in numeri',
        'aria_strip': 'Indicatori di prestazioni e accreditamento europeo',
        'l1': 'Prontezza cloud',
        'l2': 'Conformità fiscale UE',
        'l3': 'Avvio immediato',
        'l4': 'Sede di Amsterdam',
    },
    'pt': {
        'aria_section': 'S&R CoreSync em números',
        'aria_strip': 'Indicadores de desempenho e acreditação europeia',
        'l1': 'Prontidão na nuvem',
        'l2': 'Conformidade fiscal da UE',
        'l3': 'Início imediato',
        'l4': 'Sede em Amsterdão',
    },
    'tr': {
        'aria_section': 'Rakamlarla S&R CoreSync',
        'aria_strip': 'Performans ve Avrupa akreditasyon göstergeleri',
        'l1': 'Bulut hazırlığı',
        'l2': 'AB vergi uyumu',
        'l3': 'Anında başlangıç',
        'l4': 'Amsterdam Merkez Ofisi',
    },
    'pl': {
        'aria_section': 'S&R CoreSync w liczbach',
        'aria_strip': 'Wskaźniki wydajności i europejskiej akredytacji',
        'l1': 'Gotowość chmurowa',
        'l2': 'Zgodność z podatkami UE',
        'l3': 'Natychmiastowy start',
        'l4': 'Centrala w Amsterdamie',
    },
    'cs': {
        'aria_section': 'S&R CoreSync v číslech',
        'aria_strip': 'Ukazatele výkonnosti a evropské akreditace',
        'l1': 'Připravenost cloudu',
        'l2': 'Daňová shoda s EU',
        'l3': 'Okamžitý start',
        'l4': 'Centrála v Amsterdamu',
    },
    'sk': {
        'aria_section': 'S&R CoreSync v číslach',
        'aria_strip': 'Ukazovatele výkonnosti a európskej akreditácie',
        'l1': 'Pripravenosť cloudu',
        'l2': 'Daňová zhoda s EÚ',
        'l3': 'Okamžitý štart',
        'l4': 'Centrála v Amsterdame',
    },
    'hu': {
        'aria_section': 'S&R CoreSync számokban',
        'aria_strip': 'Teljesítmény- és európai akkreditációs mutatók',
        'l1': 'Felhőkészültség',
        'l2': 'EU-s adómegfelelés',
        'l3': 'Azonnali indulás',
        'l4': 'Amsterdami központ',
    },
    'ro': {
        'aria_section': 'S&R CoreSync în cifre',
        'aria_strip': 'Indicatori de performanță și acreditare europeană',
        'l1': 'Pregătire cloud',
        'l2': 'Conformitate fiscală UE',
        'l3': 'Start imediat',
        'l4': 'Sediu în Amsterdam',
    },
    'bg': {
        'aria_section': 'S&R CoreSync в цифри',
        'aria_strip': 'Индикатори за производителност и европейска акредитация',
        'l1': 'Готовност на облака',
        'l2': 'Съответствие с данъци на ЕС',
        'l3': 'Незабавен старт',
        'l4': 'Централа в Амстердам',
    },
    'el': {
        'aria_section': 'S&R CoreSync σε αριθμούς',
        'aria_strip': 'Δείκτες απόδοσης και ευρωπαϊκής πιστοποίησης',
        'l1': 'Ετοιμότητα cloud',
        'l2': 'Φορολογική συμμόρφωση ΕΕ',
        'l3': 'Άμεση έναρξη',
        'l4': 'Έδρα στο Άμστερνταμ',
    },
    'da': {
        'aria_section': 'S&R CoreSync i tal',
        'aria_strip': 'Indikatorer for ydeevne og europæisk akkreditering',
        'l1': 'Cloud-parathed',
        'l2': 'EU-skatteoverholdelse',
        'l3': 'Øjeblikkelig start',
        'l4': 'Hovedsæde i Amsterdam',
    },
    'sv': {
        'aria_section': 'S&R CoreSync i siffror',
        'aria_strip': 'Indikatorer för prestanda och europeisk ackreditering',
        'l1': 'Molnberedskap',
        'l2': 'EU-skatteefterlevnad',
        'l3': 'Omedelbar start',
        'l4': 'Huvudkontor i Amsterdam',
    },
    'no': {
        'aria_section': 'S&R CoreSync i tall',
        'aria_strip': 'Indikatorer for ytelse og europeisk akkreditering',
        'l1': 'Skyberedskap',
        'l2': 'EU-skatteoverholdelse',
        'l3': 'Umiddelbar start',
        'l4': 'Hovedkontor i Amsterdam',
    },
    'fi': {
        'aria_section': 'S&R CoreSync lukuina',
        'aria_strip': 'Suorituskyvyn ja eurooppalaisen akkreditoinnin mittarit',
        'l1': 'Pilvivalmius',
        'l2': 'EU-veronmukaisuus',
        'l3': 'Välitön aloitus',
        'l4': 'Pääkonttori Amsterdamissa',
    },
    'et': {
        'aria_section': 'S&R CoreSync numbrites',
        'aria_strip': 'Jõudluse ja Euroopa akrediteerimise näitajad',
        'l1': 'Pilvevalmidus',
        'l2': 'EL-i maksunõuetele vastavus',
        'l3': 'Kohene algus',
        'l4': 'Peakontor Amsterdamis',
    },
    'lv': {
        'aria_section': 'S&R CoreSync skaitļos',
        'aria_strip': 'Veiktspējas un Eiropas akreditācijas rādītāji',
        'l1': 'Mākoņu gatavība',
        'l2': 'ES nodokļu atbilstība',
        'l3': 'Tūlītējs sākums',
        'l4': 'Galvenais birojs Amsterdamā',
    },
    'lt': {
        'aria_section': 'S&R CoreSync skaičiais',
        'aria_strip': 'Veiklos ir Europos akreditavimo rodikliai',
        'l1': 'Debesų pasirengimas',
        'l2': 'ES mokesčių atitiktis',
        'l3': 'Greitas paleidimas',
        'l4': 'Būstinė Amsterdame',
    },
    'sl': {
        'aria_section': 'S&R CoreSync v številkah',
        'aria_strip': 'Kazalniki delovanja in evropske akreditacije',
        'l1': 'Pripravljenost oblaka',
        'l2': 'Skladnost z davki EU',
        'l3': 'Takojšen začetek',
        'l4': 'Sedež v Amsterdamu',
    },
    'hr': {
        'aria_section': 'S&R CoreSync u brojkama',
        'aria_strip': 'Pokazatelji učinka i europske akreditacije',
        'l1': 'Spremnost za oblak',
        'l2': 'Usklađenost s porezima EU',
        'l3': 'Neposredni početak',
        'l4': 'Sjedište u Amsterdamu',
    },
    'ga': {
        'aria_section': 'S&R CoreSync in uimhreacha',
        'aria_strip': 'Táscaí feidhmíochta agus creidmheasa na hEorpa',
        'l1': 'Réidheas na scamaill',
        'l2': 'Comhlíonadh cáin AE',
        'l3': 'Tús láithreach',
        'l4': 'Ceanncheathrú in Amstardam',
    },
    'mt': {
        'aria_section': "S&R CoreSync fin-numri",
        'aria_strip': "Indikaturi ta' prestazzjoni u akkreditazzjoni Ewropea",
        'l1': 'Prontezza tas-sħab',
        'l2': "Konformità fiskali ta' l-UE",
        'l3': 'Bidu immedjat',
        'l4': "Sede ċentrali f'Amsterdam",
    },
    'ku': {
        'aria_section': 'S&R CoreSync bi hejmaran',
        'aria_strip': 'Nîşaneyên performans û pejirandina Ewropayî',
        'l1': 'Amedehîya ewranê',
        'l2': 'Guncandina bacê ya YE',
        'l3': 'Destpêka tavilê',
        'l4': 'Navenda Amsterdamê',
    },
    'ckb': {
        'aria_section': 'S&R CoreSync بە ژمارەکان',
        'aria_strip': 'نیشاندەرەکانی کارایی و پەسەندنامەی ئەورووپی',
        'l1': 'ئامادەیی هەور',
        'l2': 'گونجانى باجى ئەورووپى',
        'l3': 'دەستپێکردنی دەستبەجێ',
        'l4': 'ناوەندی ئەمستردام',
    },
}

# Root-page quick portals strip (section #portals): 2 portal links +
# private-consultation booking button + UI sound toggle. Portal pages use
# ../-prefixed hrefs; the ar root uses same-dir hrefs.
PORTALS_STRIP_LOCALIZATIONS = {
    'en': {
        'aria_section': 'S&R CoreSync portals',
        'dev': 'Developer Portal ⚡',
        'partner': 'Partners & Licensing Portal 💼',
        'book': 'Book a private consultation 👔',
        'sound': '🔊 UI sound',
        'sound_title': 'Toggle the interface sound effects',
    },
    'nl': {
        'aria_section': 'S&R CoreSync portalen',
        'dev': 'Ontwikkelaarsportaal ⚡',
        'partner': 'Partners- & Licentieportaal 💼',
        'book': 'Privéconsultatie boeken 👔',
        'sound': '🔊 Interfacegeluid',
        'sound_title': 'Geluidseffecten van de interface aan- of uitschakelen',
    },
    'de': {
        'aria_section': 'S&R CoreSync-Portale',
        'dev': 'Entwicklerportal ⚡',
        'partner': 'Partner- & Lizenzportal 💼',
        'book': 'Private Beratung buchen 👔',
        'sound': '🔊 Interface-Sound',
        'sound_title': 'Soundeffekte der Oberfläche ein- oder ausschalten',
    },
    'fr': {
        'aria_section': 'Portails S&R CoreSync',
        'dev': 'Portail Développeurs ⚡',
        'partner': 'Portail Partenaires & Licences 💼',
        'book': 'Réserver une consultation privée 👔',
        'sound': "🔊 Son de l'interface",
        'sound_title': "Activer ou couper les effets sonores de l'interface",
    },
    'es': {
        'aria_section': 'Portales de S&R CoreSync',
        'dev': 'Portal de Desarrolladores ⚡',
        'partner': 'Portal de Socios y Licencias 💼',
        'book': 'Reservar una consulta privada 👔',
        'sound': '🔊 Sonido de la interfaz',
        'sound_title': 'Activar o desactivar los efectos de sonido de la interfaz',
    },
    'it': {
        'aria_section': 'Portali S&R CoreSync',
        'dev': 'Portale Sviluppatori ⚡',
        'partner': 'Portale Partner & Licenze 💼',
        'book': 'Prenota una consulenza privata 👔',
        'sound': "🔊 Suono dell'interfaccia",
        'sound_title': "Attiva o disattiva gli effetti sonori dell'interfaccia",
    },
    'pt': {
        'aria_section': 'Portais S&R CoreSync',
        'dev': 'Portal de Desenvolvedores ⚡',
        'partner': 'Portal de Parceiros e Licenciamento 💼',
        'book': 'Agendar uma consultoria privada 👔',
        'sound': '🔊 Som da interface',
        'sound_title': 'Ativar ou desativar os efeitos sonoros da interface',
    },
    'tr': {
        'aria_section': 'S&R CoreSync Portalları',
        'dev': 'Geliştirici Portalı ⚡',
        'partner': 'Ortaklık ve Lisans Portalı 💼',
        'book': 'Özel danışmanlık rezervasyonu 👔',
        'sound': '🔊 Arayüz sesi',
        'sound_title': 'Arayüz ses efektlerini aç veya kapat',
    },
    'pl': {
        'aria_section': 'Portale S&R CoreSync',
        'dev': 'Portal Programistów ⚡',
        'partner': 'Portal Partnerów i Licencji 💼',
        'book': 'Umów prywatną konsultację 👔',
        'sound': '🔊 Dźwięk interfejsu',
        'sound_title': 'Włącz lub wyłącz efekty dźwiękowe interfejsu',
    },
    'cs': {
        'aria_section': 'Portály S&R CoreSync',
        'dev': 'Vývojářský portál ⚡',
        'partner': 'Portál partnerů a licencí 💼',
        'book': 'Rezervovat soukromou konzultaci 👔',
        'sound': '🔊 Zvuk rozhraní',
        'sound_title': 'Zapnout nebo vypnout zvukové efekty rozhraní',
    },
    'sk': {
        'aria_section': 'Portály S&R CoreSync',
        'dev': 'Vývojársky portál ⚡',
        'partner': 'Portál partnerov a licencií 💼',
        'book': 'Rezervovať súkromnú konzultáciu 👔',
        'sound': '🔊 Zvuk rozhrania',
        'sound_title': 'Zapnúť alebo vypnúť zvukové efekty rozhrania',
    },
    'hu': {
        'aria_section': 'S&R CoreSync portálok',
        'dev': 'Fejlesztői portál ⚡',
        'partner': 'Partner- és licencportál 💼',
        'book': 'Személyes konzultáció foglalása 👔',
        'sound': '🔊 Felület hangja',
        'sound_title': 'A felület hangeffektjeinek be- vagy kikapcsolása',
    },
    'ro': {
        'aria_section': 'Portalurile S&R CoreSync',
        'dev': 'Portal Dezvoltatori ⚡',
        'partner': 'Portal Parteneri & Licențe 💼',
        'book': 'Rezervă o consultanță privată 👔',
        'sound': '🔊 Sunetul interfeței',
        'sound_title': 'Activați sau dezactivați efectele sonore ale interfeței',
    },
    'bg': {
        'aria_section': 'Порталите на S&R CoreSync',
        'dev': 'Портал за разработчици ⚡',
        'partner': 'Портал за партньори и лицензи 💼',
        'book': 'Резервирайте частна консултация 👔',
        'sound': '🔊 Звук на интерфейса',
        'sound_title': 'Включване или изключване на звуковите ефекти на интерфейса',
    },
    'el': {
        'aria_section': 'Πύλες S&R CoreSync',
        'dev': 'Πύλη Προγραμματιστών ⚡',
        'partner': 'Πύλη Συνεργατών & Αδειών 💼',
        'book': 'Κλείστε ιδιωτική συμβουλευτική 👔',
        'sound': '🔊 Ήχος διεπαφής',
        'sound_title': 'Ενεργοποίηση ή απενεργοποίηση των ηχητικών εφέ της διεπαφής',
    },
    'da': {
        'aria_section': 'S&R CoreSync-portaler',
        'dev': 'Udviklerportal ⚡',
        'partner': 'Partner- & Licensportal 💼',
        'book': 'Book en privat konsultation 👔',
        'sound': '🔊 Interface-lyd',
        'sound_title': 'Slå grænsefladens lydeffekter til eller fra',
    },
    'sv': {
        'aria_section': 'S&R CoreSync-portaler',
        'dev': 'Utvecklarportal ⚡',
        'partner': 'Partner- & Licensportal 💼',
        'book': 'Boka en privat konsultation 👔',
        'sound': '🔊 Gränssnittsljud',
        'sound_title': "Slå på eller av gränssnittets ljudeffekter",
    },
    'no': {
        'aria_section': 'S&R CoreSync-portaler',
        'dev': 'Utviklerportal ⚡',
        'partner': 'Partner- & Lisensportal 💼',
        'book': 'Bestill en privat konsultasjon 👔',
        'sound': '🔊 Grensesnittlyd',
        'sound_title': "Slå av eller på grensesnittets lydeffekter",
    },
    'fi': {
        'aria_section': 'S&R CoreSync -portaalit',
        'dev': 'Kehittäjäportaali ⚡',
        'partner': 'Kumppani- ja lisenssiportaali 💼',
        'book': 'Varaa yksityinen konsultaatio 👔',
        'sound': '🔊 Käyttöliittymän ääni',
        'sound_title': 'Ota käyttöliittymän äänitehosteet käyttöön tai pois käytöstä',
    },
    'et': {
        'aria_section': 'S&R CoreSync portaalid',
        'dev': 'Arendajate portaal ⚡',
        'partner': 'Partnerite ja litsentside portaal 💼',
        'book': 'Broneeri privaatne konsultatsioon 👔',
        'sound': '🔊 Liidese heli',
        'sound_title': 'Lülita liidese heliefektid sisse või välja',
    },
    'lv': {
        'aria_section': 'S&R CoreSync portāli',
        'dev': 'Izstrādātāju portāls ⚡',
        'partner': 'Partneru un licenču portāls 💼',
        'book': 'Rezervēt privātu konsultāciju 👔',
        'sound': '🔊 Saskarnes skaņa',
        'sound_title': 'Ieslēgt vai izslēgt saskarnes skaņas efektus',
    },
    'lt': {
        'aria_section': 'S&R CoreSync portalai',
        'dev': 'Kūrėjų portalas ⚡',
        'partner': 'Partnerių ir licencijų portalas 💼',
        'book': 'Rezervuoti privatų konsultaciją 👔',
        'sound': '🔊 Sąsajos garsas',
        'sound_title': 'Įjungti arba išjungti sąsajos garso efektus',
    },
    'sl': {
        'aria_section': 'Portali S&R CoreSync',
        'dev': 'Portal za razvijalce ⚡',
        'partner': 'Portal za partnerje in licence 💼',
        'book': 'Rezervirajte zasebno posvetovanje 👔',
        'sound': '🔊 Zvok vmesnika',
        'sound_title': 'Vklopite ali izklopite zvočne učinke vmesnika',
    },
    'hr': {
        'aria_section': 'S&R CoreSync portali',
        'dev': 'Portal za programere ⚡',
        'partner': 'Portal za partnere i licence 💼',
        'book': 'Rezervirajte privatnu konzultaciju 👔',
        'sound': '🔊 Zvuk sučelja',
        'sound_title': 'Uključite ili isključite zvučne efekte sučelja',
    },
    'ga': {
        'aria_section': 'Tairseacha S&R CoreSync',
        'dev': 'Tairseach Forbróirí ⚡',
        'partner': 'Tairseach Comhpháirtithe & Ceadúnaithe 💼',
        'book': 'Áirithint comhairle phríobháideach 👔',
        'sound': '🔊 Fuaim na comhéadain',
        'sound_title': 'Athraigh fuaiméifeachtaí na comhéadain',
    },
    'mt': {
        'aria_section': "Portali ta' S&R CoreSync",
        'dev': 'Portal tal-Iżviluppaturi ⚡',
        'partner': 'Portal tal-Imsieħba u Liċenzji 💼',
        'book': 'Ippreżerva konsultazzjoni privata 👔',
        'sound': '🔊 Ħoss tal-interfaċċa',
        'sound_title': "Ixkew jew ixkekkel l-effetti ta' ħoss tal-interfaċċa",
    },
    'ku': {
        'aria_section': 'Portalên S&R CoreSync',
        'dev': 'Portala Pêşvebiran ⚡',
        'partner': 'Portala Hevalbendan & Lîsansê 💼',
        'book': 'Rezervekirina şêwirmendiya taybet 👔',
        'sound': '🔊 Dengê navrûyê',
        'sound_title': 'Vegerandina efektên dengê navrûyê',
    },
    'ckb': {
        'aria_section': 'پۆرتاڵەکانی S&R CoreSync',
        'dev': 'پۆرتاڵی گەشەپێدەران ⚡',
        'partner': 'پۆرتاڵی هاوبەشان و مۆڵەتەکان 💼',
        'book': 'دەستەبەرکردنی ئامۆژگاری تایبەت 👔',
        'sound': '🔊 دەنگی ڕووکار',
        'sound_title': 'کردنەوە یان داخستنی دەنگە کاریگەرەکانی ڕووکار',
    },
}

# Metric values shared by every language (kept identical to the ar root).
METRIC_VALUES = ['99.9%', 'EU &amp; BTW', '&lt; 30s', 'Amsterdam HQ']

IND = ' ' * 40


def esc(s):
    return html.escape(s, quote=False).replace('"', '&quot;')


def build_trust_metrics(loc):
    items = []
    for val, key in zip(METRIC_VALUES, ('l1', 'l2', 'l3', 'l4')):
        items.append(
            f'{IND}<div class="trust-metric-item">\n'
            f'{IND}    <span class="metric-val">{val}</span>\n'
            f'{IND}    <span class="metric-lbl">{esc(loc[key])}</span>\n'
            f'{IND}</div>'
        )
    sep = f'{IND}<div class="trust-metric-separator" aria-hidden="true"></div>'
    inner = f'\n{sep}\n'.join(items)
    return (
        f'<section id="trust-metrics" class="section-trust-metrics" '
        f'aria-label="{esc(loc["aria_section"])}">'
        f'<div class="hero-trust-metrics-strip hero-trust-compact" '
        f'aria-label="{esc(loc["aria_strip"])}">\n'
        f'{inner}\n'
        f'{IND}</div></section>'
    )


def build_portals_strip(loc, prefix='../'):
    return (
        f'<section id="portals" class="section-portals" '
        f'aria-label="{esc(loc["aria_section"])}">'
        f'<div class="hero-quick-portals-strip hero-quick-portals-strip--quiet">\n'
        f'{IND}<a href="{prefix}developer-portal.html" '
        f'class="hero-quick-portal-link">{esc(loc["dev"])}</a>\n'
        f'{IND}<span class="hero-portal-sep">•</span>\n'
        f'{IND}<a href="{prefix}partner-portal.html" '
        f'class="hero-quick-portal-link">{esc(loc["partner"])}</a>\n'
        f'{IND}<span class="hero-portal-sep">•</span>\n'
        f'{IND}<button type="button" class="hero-quick-portal-btn" '
        f'data-sr-call="openExecutiveBookingModal">{esc(loc["book"])}</button>\n'
        f'{IND}<span class="hero-portal-sep">•</span>\n'
        f'{IND}<button type="button" class="hero-sound-toggle-btn" '
        f'id="srSoundToggleBtn" onclick="toggleSoundMute()" '
        f'title="{esc(loc["sound_title"])}">{esc(loc["sound"])}</button>\n'
        f'{IND}</div></section>'
    )


def insert_trust_metrics(content, loc):
    if '<section id="trust-metrics"' in content:
        return content, False
    hero_open = content.find('<section id="hero"')
    if hero_open < 0:
        return content, False
    hero_close = content.find('</section>', hero_open)
    if hero_close < 0:
        return content, False
    pos = hero_close + len('</section>')
    return content[:pos] + '\n' + build_trust_metrics(loc) + content[pos:], True


def insert_portals_strip(content, loc):
    if '<section id="portals"' in content:
        return content, False
    marker = content.find('id="services-compare"')
    if marker < 0:
        return content, False
    sec_open = content.rfind('<section', 0, marker)
    if sec_open < 0:
        return content, False
    return content[:sec_open] + build_portals_strip(loc) + '\n\n        ' + content[sec_open:], True


def main():
    ap = argparse.ArgumentParser(
        description='Insert the ar root parity strips (#trust-metrics, '
                    '#portals) into localized portals (idempotent).')
    ap.add_argument('--lang', default='',
                    help='comma-separated subset of languages (default: all)')
    args = ap.parse_args()
    wanted = {x.strip() for x in args.lang.split(',') if x.strip()}
    unknown = wanted - set(PORTALS_STRIP_LOCALIZATIONS)
    if unknown:
        sys.exit(f"unknown language(s): {', '.join(sorted(unknown))}")
    langs = sorted(PORTALS_STRIP_LOCALIZATIONS)
    if wanted:
        langs = [x for x in langs if x in wanted]

    tm_done, ps_done, skipped_tm, skipped_ps = [], [], [], []
    for lang in langs:
        path = f'{lang}/index.html'
        if not os.path.exists(path):
            print(f'Skipping {lang}: file not found')
            continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        content, did_tm = insert_trust_metrics(content, TRUST_METRICS_LOCALIZATIONS[lang])
        content, did_ps = insert_portals_strip(content, PORTALS_STRIP_LOCALIZATIONS[lang])
        (tm_done if did_tm else skipped_tm).append(lang)
        (ps_done if did_ps else skipped_ps).append(lang)
        if did_tm or did_ps:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
        print(f'{lang}: trust-metrics {"INSERTED" if did_tm else "exists"}, '
              f'portals {"INSERTED" if did_ps else "exists"}')

    print(f'\ntrust-metrics inserted: {len(tm_done)} ({", ".join(tm_done) or "-"})')
    print(f'portals strip inserted: {len(ps_done)} ({", ".join(ps_done) or "-"})')


if __name__ == '__main__':
    main()
