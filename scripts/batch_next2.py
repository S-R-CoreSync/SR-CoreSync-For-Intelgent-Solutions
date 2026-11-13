# -*- coding: utf-8 -*-
"""Batch 3: tr, el, da, no, fi."""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)

TR = {
  "أنظمة برمجية متقدمة": "Gelişmiş yazılım sistemleri",
  "تطبيقات ومنصات رقمية": "Dijital uygulamalar ve platformlar",
  "هويات بصرية تُبنى لتدوم": "Kalıcı marka kimlikleri",
  "اكتب فكرة مشروعك هنا…": "Proje fikrinizi yazın…",
  "حلّل فكرتي ✦": "Fikrimi analiz et ✦",
  "تجربة النظام السحابي الحي": "Canlı bulut sistemini deneyin",
  "نسخة تجريبية حيّة": "Canlı demo",
  "أو ابدأ من الأقرب إلى مشروعك:": "Ya da projenize en yakın olandan başlayın:",
  "متجر إلكتروني فاخر": "Lüks online mağaza",
  "نظام ERP متكامل": "Tam ERP sistemi",
  "هوية بصرية كاملة": "Eksiksiz marka kimliği",
  "موقع تعريفي عالي التحويل": "Yüksek dönüşümlü web sitesi",
  "أتمتة وربط الأنظمة": "Otomasyon ve entegrasyonlar",
  "استشارة تقنية": "Teknik danışmanlık",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Proje fikrinizi yazın…",
  "حلل فكرتي بالـ AI ⚡": "Fikrimi analiz et ⚡",
  "حلّل فكرتي": "Fikrimi analiz et",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Fikrinizi sesle anlatın",
  "فكرة المشروع": "Proje fikri",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "S&amp;R CoreSync'i cihazınıza kurun",
  "تثبيت التطبيق": "Uygulamayı kur",
  "أدوات الدعم": "Destek araçları",
  "خريطة 34 سوقاً": "34 pazar haritası",
}

EL = {
  "أنظمة برمجية متقدمة": "Προηγμένα συστήματα λογισμικού",
  "تطبيقات ومنصات رقمية": "Ψηφιακές εφαρμογές και πλατφόρμες",
  "هويات بصرية تُبنى لتدوم": "Ταυτότητες μάρκας που διαρκούν",
  "اكتب فكرة مشروعك هنا…": "Γράψτε την ιδέα του έργου σας…",
  "حلّل فكرتي ✦": "Ανάλυσε την ιδέα μου ✦",
  "تجربة النظام السحابي الحي": "Δοκιμάστε το ζωντανό σύστημα cloud",
  "نسخة تجريبية حيّة": "Ζωντανή επίδειξη",
  "أو ابدأ من الأقرب إلى مشروعك:": "Ή ξεκινήστε από αυτό που ταιριάζει:",
  "متجر إلكتروني فاخر": "Πολυτελές ηλεκτρονικό κατάστημα",
  "نظام ERP متكامل": "Πλήρες σύστημα ERP",
  "هوية بصرية كاملة": "Πλήρης ταυτότητα μάρκας",
  "موقع تعريفي عالي التحويل": "Ιστοσελίδα υψηλής μετατροπής",
  "أتمتة وربط الأنظمة": "Αυτοματοποίηση και ενσωματώσεις",
  "استشارة تقنية": "Τεχνική συμβουλευτική",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Γράψτε την ιδέα του έργου σας…",
  "حلل فكرتي بالـ AI ⚡": "Ανάλυσε την ιδέα μου ⚡",
  "حلّل فكرتي": "Ανάλυσε την ιδέα μου",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Περιγράψτε την ιδέα σας με φωνή",
  "فكرة المشروع": "Ιδέα έργου",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Εγκαταστήστε το S&amp;R CoreSync στη συσκευή σας",
  "تثبيت التطبيق": "Εγκατάσταση εφαρμογής",
  "أدوات الدعم": "Εργαλεία υποστήριξης",
  "خريطة 34 سوقاً": "Χάρτης 34 αγορών",
}

DA = {
  "أنظمة برمجية متقدمة": "Avancerede softwaresystemer",
  "تطبيقات ومنصات رقمية": "Digitale apps og platforme",
  "هويات بصرية تُبنى لتدوم": "Brandidentiteter der holder",
  "اكتب فكرة مشروعك هنا…": "Beskriv din projektidé…",
  "حلّل فكرتي ✦": "Analysér min idé ✦",
  "تجربة النظام السحابي الحي": "Prøv det live cloudsystem",
  "نسخة تجريبية حيّة": "Live-demo",
  "أو ابدأ من الأقرب إلى مشروعك:": "Eller start med det, der passer:",
  "متجر إلكتروني فاخر": "Luksus webshop",
  "نظام ERP متكامل": "Komplet ERP-system",
  "هوية بصرية كاملة": "Komplet brandidentitet",
  "موقع تعريفي عالي التحويل": "Hjemmeside med høj konvertering",
  "أتمتة وربط الأنظمة": "Automatisering og integrationer",
  "استشارة تقنية": "Teknisk rådgivning",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Beskriv din projektidé…",
  "حلل فكرتي بالـ AI ⚡": "Analysér min idé ⚡",
  "حلّل فكرتي": "Analysér min idé",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Beskriv din idé med stemme",
  "فكرة المشروع": "Projektidé",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Installer S&amp;R CoreSync på din enhed",
  "تثبيت التطبيق": "Installer appen",
  "أدوات الدعم": "Supportværktøjer",
  "خريطة 34 سوقاً": "Kort over 34 markeder",
}

NO = {
  "أنظمة برمجية متقدمة": "Avanserte softwaresystemer",
  "تطبيقات ومنصات رقمية": "Digitale apper og plattformer",
  "هويات بصرية تُبنى لتدوم": "Merkevareidentiteter som varer",
  "اكتب فكرة مشروعك هنا…": "Beskriv prosjektideen din…",
  "حلّل فكرتي ✦": "Analyser ideen min ✦",
  "تجربة النظام السحابي الحي": "Prøv det levende skysystemet",
  "نسخة تجريبية حيّة": "Live-demo",
  "أو ابدأ من الأقرب إلى مشروعك:": "Eller start med det som passer:",
  "متجر إلكتروني فاخر": "Luksus nettbutikk",
  "نظام ERP متكامل": "Komplett ERP-system",
  "هوية بصرية كاملة": "Komplett merkevareidentitet",
  "موقع تعريفي عالي التحويل": "Nettside med høy konvertering",
  "أتمتة وربط الأنظمة": "Automatisering og integrasjoner",
  "استشارة تقنية": "Teknisk rådgivning",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Beskriv prosjektideen din…",
  "حلل فكرتي بالـ AI ⚡": "Analyser ideen min ⚡",
  "حلّل فكرتي": "Analyser ideen min",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Beskriv ideen din med stemme",
  "فكرة المشروع": "Prosjektidé",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Installer S&amp;R CoreSync på enheten din",
  "تثبيت التطبيق": "Installer appen",
  "أدوات الدعم": "Støtteverktøy",
  "خريطة 34 سوقاً": "Kart over 34 markeder",
}

FI = {
  "أنظمة برمجية متقدمة": "Edistyneet ohjelmistojärjestelmät",
  "تطبيقات ومنصات رقمية": "Digitaaliset sovellukset ja alustat",
  "هويات بصرية تُبنى لتدوم": "Brändi-identiteetit, jotka kestävät",
  "اكتب فكرة مشروعك هنا…": "Kirjoita projektisi idea…",
  "حلّل فكرتي ✦": "Analysoi ideasi ✦",
  "تجربة النظام السحابي الحي": "Kokeile live-pilvijärjestelmää",
  "نسخة تجريبية حيّة": "Live-demo",
  "أو ابدأ من الأقرب إلى مشروعك:": "Tai aloita siitä, mikä sopii:",
  "متجر إلكتروني فاخر": "Ylellinen verkkokauppa",
  "نظام ERP متكامل": "Täydellinen ERP-järjestelmä",
  "هوية بصرية كاملة": "Täydellinen brändi-identiteetti",
  "موقع تعريفي عالي التحويل": "Korkean konversion verkkosivusto",
  "أتمتة وربط الأنظمة": "Automaatio ja integraatiot",
  "استشارة تقنية": "Tekninen konsultointi",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Kirjoita projektisi idea…",
  "حلل فكرتي بالـ AI ⚡": "Analysoi ideasi ⚡",
  "حلّل فكرتي": "Analysoi ideasi",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Kuvaile ideasi äänellä",
  "فكرة المشروع": "Projekti-idea",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Asenna S&amp;R CoreSync laitteeseesi",
  "تثبيت التطبيق": "Asenna sovellus",
  "أدوات الدعم": "Tukityökalut",
  "خريطة 34 سوقاً": "34 markkinan kartta",
}

BATCH = [('tr', TR), ('el', EL), ('da', DA), ('no', NO), ('fi', FI)]

if __name__ == '__main__':
    import migrate_hero as MH
    import sync_locales as SL
    import sync_nav as SN

    for lang, table in BATCH:
        MH.port(lang, table)
        json.dump(table, open(os.path.join(ROOT, 'i18n', 'locales', lang + '.json'), 'w',
                              encoding='utf-8'), ensure_ascii=False, indent=1)
        print('locale', lang)

    hero, css = SL.master_parts()
    for lang, table in BATCH:
        print('sync', *SL.sync_page(lang, hero, css, table, dry=False))

    for lang in ['pl', 'pt', 'ro', 'sv', 'cs'] + [l for l, _ in BATCH]:
        print('nav', lang, SN.fix(os.path.join(ROOT, lang, 'index.html'))[1])
