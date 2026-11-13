# -*- coding: utf-8 -*-
"""Batch 4: hu, sk, sl, hr, lt."""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)

HU = {
  "أنظمة برمجية متقدمة": "Fejlett szoftverrendszerek",
  "تطبيقات ومنصات رقمية": "Digitális alkalmazások és platformok",
  "هويات بصرية تُبنى لتدوم": "Időtálló márkaidentitások",
  "اكتب فكرة مشروعك هنا…": "Írja le projektötletét…",
  "حلّل فكرتي ✦": "Ötletem elemzése ✦",
  "تجربة النظام السحابي الحي": "Próbálja ki az élő felhőrendszert",
  "نسخة تجريبية حيّة": "Élő bemutató",
  "أو ابدأ من الأقرب إلى مشروعك:": "Vagy kezdje azzal, ami illik:",
  "متجر إلكتروني فاخر": "Luxus webáruház",
  "نظام ERP متكامل": "Teljes ERP rendszer",
  "هوية بصرية كاملة": "Teljes márkaidentitás",
  "موقع تعريفي عالي التحويل": "Magas konverziójú weboldal",
  "أتمتة وربط الأنظمة": "Automatizálás és integrációk",
  "استشارة تقنية": "Technikai tanácsadás",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Írja le projektötletét…",
  "حلل فكرتي بالـ AI ⚡": "Ötletem elemzése ⚡",
  "حلّل فكرتي": "Ötletem elemzése",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Írja le ötletét hanggal",
  "فكرة المشروع": "Projektötlet",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Telepítse az S&amp;R CoreSyncet eszközére",
  "تثبيت التطبيق": "Alkalmazás telepítése",
  "أدوات الدعم": "Támogatási eszközök",
  "خريطة 34 سوقاً": "34 piac térképe",
}

SK = {
  "أنظمة برمجية متقدمة": "Pokročilé softvérové systémy",
  "تطبيقات ومنصات رقمية": "Digitálne aplikácie a platformy",
  "هويات بصرية تُبنى لتدوم": "Identita značky, ktorá vydrží",
  "اكتب فكرة مشروعك هنا…": "Opíšte nápad na projekt…",
  "حلّل فكرتي ✦": "Analyzovať môj nápad ✦",
  "تجربة النظام السحابي الحي": "Vyskúšať živý cloudový systém",
  "نسخة تجريبية حيّة": "Živé demo",
  "أو ابدأ من الأقرب إلى مشروعك:": "Alebo začnite tým, čo sedí:",
  "متجر إلكتروني فاخر": "Luxusný e-shop",
  "نظام ERP متكامل": "Kompletný ERP systém",
  "هوية بصرية كاملة": "Kompletná identita značky",
  "موقع تعريفي عالي التحويل": "Web s vysokou konverziou",
  "أتمتة وربط الأنظمة": "Automatizácia a integrácie",
  "استشارة تقنية": "Technické poradenstvo",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Opíšte nápad na projekt…",
  "حلل فكرتي بالـ AI ⚡": "Analyzovať môj nápad ⚡",
  "حلّل فكرتي": "Analyzovať môj nápad",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Opíšte nápad hlasom",
  "فكرة المشروع": "Nápad na projekt",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Nainštalovať S&amp;R CoreSync do zariadenia",
  "تثبيت التطبيق": "Nainštalovať aplikáciu",
  "أدوات الدعم": "Nástroje podpory",
  "خريطة 34 سوقاً": "Mapa 34 trhov",
}

SL = {
  "أنظمة برمجية متقدمة": "Napredni programski sistemi",
  "تطبيقات ومنصات رقمية": "Digitalne aplikacije in platforme",
  "هويات بصرية تُبنى لتدوم": "Blagovne znamke, ki ostanejo",
  "اكتب فكرة مشروعك هنا…": "Opišite svojo projektno idejo…",
  "حلّل فكرتي ✦": "Analiziraj mojo idejo ✦",
  "تجربة النظام السحابي الحي": "Preizkusite živi oblačni sistem",
  "نسخة تجريبية حيّة": "Demo v živo",
  "أو ابدأ من الأقرب إلى مشروعك:": "Ali začnite s tem, kar ustreza:",
  "متجر إلكتروني فاخر": "Luksuzna spletna trgovina",
  "نظام ERP متكامل": "Celovit sistem ERP",
  "هوية بصرية كاملة": "Celovita identiteta blagovne znamke",
  "موقع تعريفي عالي التحويل": "Spletna stran z visoko konverzijo",
  "أتمتة وربط الأنظمة": "Avtomatizacija in integracije",
  "استشارة تقنية": "Tehnično svetovanje",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Opišite svojo projektno idejo…",
  "حلل فكرتي بالـ AI ⚡": "Analiziraj mojo idejo ⚡",
  "حلّل فكرتي": "Analiziraj mojo idejo",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Opišite idejo z glasom",
  "فكرة المشروع": "Projektna ideja",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Namestite S&amp;R CoreSync v napravo",
  "تثبيت التطبيق": "Namesti aplikacijo",
  "أدوات الدعم": "Orodja za podporo",
  "خريطة 34 سوقاً": "Zemljevid 34 trgov",
}

HR = {
  "أنظمة برمجية متقدمة": "Napredni softverski sustavi",
  "تطبيقات ومنصات رقمية": "Digitalne aplikacije i platforme",
  "هويات بصرية تُبنى لتدوم": "Identiteti brenda koji traju",
  "اكتب فكرة مشروعك هنا…": "Opišite ideju svog projekta…",
  "حلّل فكرتي ✦": "Analiziraj moju ideju ✦",
  "تجربة النظام السحابي الحي": "Isprobajte živi cloud sustav",
  "نسخة تجريبية حيّة": "Demo uživo",
  "أو ابدأ من الأقرب إلى مشروعك:": "Ili započnite s onim što odgovara:",
  "متجر إلكتروني فاخر": "Luksuzna web trgovina",
  "نظام ERP متكامل": "Potpuni ERP sustav",
  "هوية بصرية كاملة": "Potpuni identitet brenda",
  "موقع تعريفي عالي التحويل": "Web stranica visoke konverzije",
  "أتمتة وربط الأنظمة": "Automatizacija i integracije",
  "استشارة تقنية": "Tehničko savjetovanje",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Opišite ideju svog projekta…",
  "حلل فكرتي بالـ AI ⚡": "Analiziraj moju ideju ⚡",
  "حلّل فكرتي": "Analiziraj moju ideju",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Opišite ideju glasom",
  "فكرة المشروع": "Ideja projekta",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Instalirajte S&amp;R CoreSync na svoj uređaj",
  "تثبيت التطبيق": "Instaliraj aplikaciju",
  "أدوات الدعم": "Alati za podršku",
  "خريطة 34 سوقاً": "Karta 34 tržišta",
}

LT = {
  "أنظمة برمجية متقدمة": "Pažangios programinės sistemos",
  "تطبيقات ومنصات رقمية": "Skaitmeninės programėlės ir platformos",
  "هويات بصرية تُبنى لتدوم": "Prekės ženklo tapatybės, kurios išlieka",
  "اكتب فكرة مشروعك هنا…": "Aprašykite savo projekto idėją…",
  "حلّل فكرتي ✦": "Analizuoti mano idėją ✦",
  "تجربة النظام السحابي الحي": "Išbandykite gyvą debesijos sistemą",
  "نسخة تجريبية حيّة": "Gyva demonstracija",
  "أو ابدأ من الأقرب إلى مشروعك:": "Arba pradėkite nuo to, kas tinka:",
  "متجر إلكتروني فاخر": "Prabangi internetinė parduotuvė",
  "نظام ERP متكامل": "Pilna ERP sistema",
  "هوية بصرية كاملة": "Visa prekės ženklo tapatybė",
  "موقع تعريفي عالي التحويل": "Didelės konversijos svetainė",
  "أتمتة وربط الأنظمة": "Automatizavimas ir integracijos",
  "استشارة تقنية": "Techninės konsultacijos",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Aprašykite savo projekto idėją…",
  "حلل فكرتي بالـ AI ⚡": "Analizuoti mano idėją ⚡",
  "حلّل فكرتي": "Analizuoti mano idėją",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Aprašykite idėją balsu",
  "فكرة المشروع": "Projekto idėja",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Įdiekite S&amp;R CoreSync savo įrenginyje",
  "تثبيت التطبيق": "Įdiegti programėlę",
  "أدوات الدعم": "Palaikymo įrankiai",
  "خريطة 34 سوقاً": "34 rinkų žemėlapis",
}

BATCH = [('hu', HU), ('sk', SK), ('sl', SL), ('hr', HR), ('lt', LT)]

if __name__ == '__main__':
    import migrate_hero as MH
    import sync_locales as SLM
    import sync_nav as SN

    for lang, table in BATCH:
        MH.port(lang, table)
        json.dump(table, open(os.path.join(ROOT, 'i18n', 'locales', lang + '.json'), 'w',
                              encoding='utf-8'), ensure_ascii=False, indent=1)
        print('locale', lang)

    hero, css = SLM.master_parts()
    for lang, table in BATCH:
        print('sync', *SLM.sync_page(lang, hero, css, table, dry=False))

    for lang in ['tr', 'el', 'da', 'no', 'fi'] + [l for l, _ in BATCH]:
        print('nav', lang, SN.fix(os.path.join(ROOT, lang, 'index.html'))[1])
