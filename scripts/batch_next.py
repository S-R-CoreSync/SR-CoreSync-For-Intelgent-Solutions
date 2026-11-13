# -*- coding: utf-8 -*-
"""Batch 2: pl, pt, ro, sv, cs — first port, then sync, then static nav."""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'

PL = {
  "أنظمة برمجية متقدمة": "Zaawansowane systemy software",
  "تطبيقات ومنصات رقمية": "Aplikacje i platformy cyfrowe",
  "هويات بصرية تُبنى لتدوم": "Tożsamości marek, które trwają",
  "اكتب فكرة مشروعك هنا…": "Opisz pomysł na projekt…",
  "حلّل فكرتي ✦": "Przeanalizuj pomysł ✦",
  "تجربة النظام السحابي الحي": "Przetestuj system cloud na żywo",
  "نسخة تجريبية حيّة": "Demo na żywo",
  "أو ابدأ من الأقرب إلى مشروعك:": "Albo zacznij od tego, co pasuje:",
  "متجر إلكتروني فاخر": "Luksusowy sklep online",
  "نظام ERP متكامل": "Kompletny system ERP",
  "هوية بصرية كاملة": "Pełna identyfikacja marki",
  "موقع تعريفي عالي التحويل": "Strona o wysokiej konwersji",
  "أتمتة وربط الأنظمة": "Automatyzacja i integracje",
  "استشارة تقنية": "Konsultacja techniczna",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Opisz pomysł na projekt…",
  "حلل فكرتي بالـ AI ⚡": "Przeanalizuj pomysł ⚡",
  "حلّل فكرتي": "Przeanalizuj pomysł",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Opisz pomysł głosem",
  "فكرة المشروع": "Pomysł na projekt",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Zainstaluj S&amp;R CoreSync na swoim urządzeniu",
  "تثبيت التطبيق": "Zainstaluj aplikację",
  "أدوات الدعم": "Narzędzia wsparcia",
  "خريطة 34 سوقاً": "Mapa 34 rynków",
}

PT = {
  "أنظمة برمجية متقدمة": "Sistemas de software avançados",
  "تطبيقات ومنصات رقمية": "Aplicações e plataformas digitais",
  "هويات بصرية تُبنى لتدوم": "Identidades de marca duradouras",
  "اكتب فكرة مشروعك هنا…": "Descreva a ideia do seu projeto…",
  "حلّل فكرتي ✦": "Analisar a minha ideia ✦",
  "تجربة النظام السحابي الحي": "Testar o sistema cloud ao vivo",
  "نسخة تجريبية حيّة": "Demonstração ao vivo",
  "أو ابدأ من الأقرب إلى مشروعك:": "Ou comece pelo que melhor se adequa:",
  "متجر إلكتروني فاخر": "Loja online de luxo",
  "نظام ERP متكامل": "Sistema ERP completo",
  "هوية بصرية كاملة": "Identidade de marca completa",
  "موقع تعريفي عالي التحويل": "Website de alta conversão",
  "أتمتة وربط الأنظمة": "Automação e integrações",
  "استشارة تقنية": "Consultoria técnica",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Descreva a ideia do seu projeto…",
  "حلل فكرتي بالـ AI ⚡": "Analisar a minha ideia ⚡",
  "حلّل فكرتي": "Analisar a minha ideia",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Descreva a sua ideia por voz",
  "فكرة المشروع": "Ideia de projeto",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Instalar o S&amp;R CoreSync no seu dispositivo",
  "تثبيت التطبيق": "Instalar a aplicação",
  "أدوات الدعم": "Ferramentas de suporte",
  "خريطة 34 سوقاً": "Mapa de 34 mercados",
}

RO = {
  "أنظمة برمجية متقدمة": "Sisteme software avansate",
  "تطبيقات ومنصات رقمية": "Aplicații și platforme digitale",
  "هويات بصرية تُبنى لتدوم": "Identități de marcă durabile",
  "اكتب فكرة مشروعك هنا…": "Descrieți ideea proiectului…",
  "حلّل فكرتي ✦": "Analizează ideea mea ✦",
  "تجربة النظام السحابي الحي": "Testează sistemul cloud în direct",
  "نسخة تجريبية حيّة": "Demo în direct",
  "أو ابدأ من الأقرب إلى مشروعك:": "Sau începeți de la ce se potrivește:",
  "متجر إلكتروني فاخر": "Magazin online de lux",
  "نظام ERP متكامل": "Sistem ERP complet",
  "هوية بصرية كاملة": "Identitate de marcă completă",
  "موقع تعريفي عالي التحويل": "Site cu conversie ridicată",
  "أتمتة وربط الأنظمة": "Automatizare și integrări",
  "استشارة تقنية": "Consultanță tehnică",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Descrieți ideea proiectului…",
  "حلل فكرتي بالـ AI ⚡": "Analizează ideea mea ⚡",
  "حلّل فكرتي": "Analizează ideea mea",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Descrieți ideea prin voce",
  "فكرة المشروع": "Ideea proiectului",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Instalați S&amp;R CoreSync pe dispozitiv",
  "تثبيت التطبيق": "Instalează aplicația",
  "أدوات الدعم": "Instrumente de suport",
  "خريطة 34 سوقاً": "Harta a 34 de piețe",
}

SV = {
  "أنظمة برمجية متقدمة": "Avancerade mjukvarusystem",
  "تطبيقات ومنصات رقمية": "Digitala appar och plattformar",
  "هويات بصرية تُبنى لتدوم": "Varumärkesidentiteter som håller",
  "اكتب فكرة مشروعك هنا…": "Beskriv din projektidé…",
  "حلّل فكرتي ✦": "Analysera min idé ✦",
  "تجربة النظام السحابي الحي": "Testa det live molnsystemet",
  "نسخة تجريبية حيّة": "Live-demo",
  "أو ابدأ من الأقرب إلى مشروعك:": "Eller börja med det som passar:",
  "متجر إلكتروني فاخر": "Lyxig webbutik",
  "نظام ERP متكامل": "Komplett ERP-system",
  "هوية بصرية كاملة": "Komplett varumärkesidentitet",
  "موقع تعريفي عالي التحويل": "Webbplats med hög konvertering",
  "أتمتة وربط الأنظمة": "Automatisering och integrationer",
  "استشارة تقنية": "Teknisk rådgivning",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Beskriv din projektidé…",
  "حلل فكرتي بالـ AI ⚡": "Analysera min idé ⚡",
  "حلّل فكرتي": "Analysera min idé",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Beskriv din idé med röst",
  "فكرة المشروع": "Projektidé",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Installera S&amp;R CoreSync på din enhet",
  "تثبيت التطبيق": "Installera appen",
  "أدوات الدعم": "Supportverktyg",
  "خريطة 34 سوقاً": "Karta över 34 marknader",
}

CS = {
  "أنظمة برمجية متقدمة": "Pokročilé softwarové systémy",
  "تطبيقات ومنصات رقمية": "Digitální aplikace a platformy",
  "هويات بصرية تُبنى لتدوم": "Identita značky, která vydrží",
  "اكتب فكرة مشروعك هنا…": "Popište nápad na projekt…",
  "حلّل فكرتي ✦": "Analyzovat můj nápad ✦",
  "تجربة النظام السحابي الحي": "Vyzkoušet živý cloudový systém",
  "نسخة تجريبية حيّة": "Živé demo",
  "أو ابدأ من الأقرب إلى مشروعك:": "Nebo začněte tím, co sedí:",
  "متجر إلكتروني فاخر": "Luxusní e-shop",
  "نظام ERP متكامل": "Kompletní ERP systém",
  "هوية بصرية كاملة": "Kompletní identita značky",
  "موقع تعريفي عالي التحويل": "Web s vysokou konverzí",
  "أتمتة وربط الأنظمة": "Automatizace a integrace",
  "استشارة تقنية": "Technické poradenství",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Popište nápad na projekt…",
  "حلل فكرتي بالـ AI ⚡": "Analyzovat můj nápad ⚡",
  "حلّل فكرتي": "Analyzovat můj nápad",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Popište nápad hlasem",
  "فكرة المشروع": "Nápad na projekt",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Nainstalovat S&amp;R CoreSync do zařízení",
  "تثبيت التطبيق": "Nainstalovat aplikaci",
  "أدوات الدعم": "Nástroje podpory",
  "خريطة 34 سوقاً": "Mapa 34 trhů",
}

BATCH = [('pl', PL), ('pt', PT), ('ro', RO), ('sv', SV), ('cs', CS)]

if __name__ == '__main__':
    import migrate_hero as MH
    import sync_locales as SL
    import sync_nav as SN

    for lang, table in BATCH:
        MH.port(lang, table)
        p = os.path.join(ROOT, 'i18n', 'locales', lang + '.json')
        json.dump(table, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('locale file', lang)

    hero, css = SL.master_parts()
    for lang, table in BATCH:
        print('sync', *SL.sync_page(lang, hero, css, table, dry=False))

    others = ['en', 'de', 'nl', 'fr', 'es', 'it'] + [l for l, _ in BATCH]
    for lang in others:
        print('nav', lang, SN.fix(os.path.join(ROOT, lang, 'index.html')))
