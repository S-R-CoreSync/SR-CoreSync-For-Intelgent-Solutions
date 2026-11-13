# -*- coding: utf-8 -*-
"""Final batch: lv, et, mt, ga, ku, bg."""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)

LV = {
  "أنظمة برمجية متقدمة": "Uzlabotas programmatūras sistēmas",
  "تطبيقات ومنصات رقمية": "Digitālās lietotnes un platformas",
  "هويات بصرية تُبنى لتدوم": "Zīmola identitātes, kas paliek",
  "اكتب فكرة مشروعك هنا…": "Aprakstiet sava projekta ideju…",
  "حلّل فكرتي ✦": "Analizēt manu ideju ✦",
  "تجربة النظام السحابي الحي": "Izmēģiniet dzīvo mākoņsistēmu",
  "نسخة تجريبية حيّة": "Dzīva demonstrācija",
  "أو ابدأ من الأقرب إلى مشروعك:": "Vai sāciet ar to, kas atbilst:",
  "متجر إلكتروني فاخر": "Luksusa interneta veikals",
  "نظام ERP متكامل": "Pilnīga ERP sistēma",
  "هوية بصرية كاملة": "Pilnīga zīmola identitāte",
  "موقع تعريفي عالي التحويل": "Augstas konversijas vietne",
  "أتمتة وربط الأنظمة": "Automatizācija un integrācijas",
  "استشارة تقنية": "Tehniskā konsultācija",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Aprakstiet sava projekta ideju…",
  "حلل فكرتي بالـ AI ⚡": "Analizēt manu ideju ⚡",
  "حلّل فكرتي": "Analizēt manu ideju",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Aprakstiet ideju ar balsi",
  "فكرة المشروع": "Projekta ideja",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Instalējiet S&amp;R CoreSync savā ierīcē",
  "تثبيت التطبيق": "Instalēt lietotni",
  "أدوات الدعم": "Atbalsta rīki",
  "خريطة 34 سوقاً": "34 tirgu karte",
}

ET = {
  "أنظمة برمجية متقدمة": "Täiustatud tarkvarasüsteemid",
  "تطبيقات ومنصات رقمية": "Digitaalsed rakendused ja platvormid",
  "هويات بصرية تُبنى لتدوم": "Brändi identiteedid, mis püsivad",
  "اكتب فكرة مشروعك هنا…": "Kirjeldage oma projekti ideed…",
  "حلّل فكرتي ✦": "Analüüsi minu ideed ✦",
  "تجربة النظام السحابي الحي": "Proovige reaalajas pilvesüsteemi",
  "نسخة تجريبية حيّة": "Reaalajas demo",
  "أو ابدأ من الأقرب إلى مشروعك:": "Või alustage sellest, mis sobib:",
  "متجر إلكتروني فاخر": "Luksuslik veebipood",
  "نظام ERP متكامل": "Täielik ERP-süsteem",
  "هوية بصرية كاملة": "Täielik brändi identiteet",
  "موقع تعريفي عالي التحويل": "Kõrge konversiooniga veebileht",
  "أتمتة وربط الأنظمة": "Automatiseerimine ja integratsioonid",
  "استشارة تقنية": "Tehniline nõustamine",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Kirjeldage oma projekti ideed…",
  "حلل فكرتي بالـ AI ⚡": "Analüüsi minu ideed ⚡",
  "حلّل فكرتي": "Analüüsi minu ideed",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Kirjeldage ideed häälega",
  "فكرة المشروع": "Projekti idee",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Installige S&amp;R CoreSync oma seadmesse",
  "تثبيت التطبيق": "Installi rakendus",
  "أدوات الدعم": "Tugitööriistad",
  "خريطة 34 سوقاً": "34 turu kaart",
}

MT = {
  "أنظمة برمجية متقدمة": "Sistemi tas-software avvanzati",
  "تطبيقات ومنصات رقمية": "Applikazzjonijiet u pjattaformi diġitali",
  "هويات بصرية تُبنى لتدوم": "Identitajiet tal-marka li jdumu",
  "اكتب فكرة مشروعك هنا…": "Ikteb l-idea tal-proġett tiegħek…",
  "حلّل فكرتي ✦": "Analizza l-idea tiegħi ✦",
  "تجربة النظام السحابي الحي": "Ipprova s-sistema cloud live",
  "نسخة تجريبية حيّة": "Demo live",
  "أو ابدأ من الأقرب إلى مشروعك:": "Jew ibda minn dak li jaqbel:",
  "متجر إلكتروني فاخر": "Ħanut online tal-lussu",
  "نظام ERP متكامل": "Sistema ERP sħiħa",
  "هوية بصرية كاملة": "Identità tal-marka sħiħa",
  "موقع تعريفي عالي التحويل": "Websajt b'konverżjoni għolja",
  "أتمتة وربط الأنظمة": "Awtomazzjoni u integrazzjonijiet",
  "استشارة تقنية": "Konsulenza teknika",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Ikteb l-idea tal-proġett tiegħek…",
  "حلل فكرتي بالـ AI ⚡": "Analizza l-idea tiegħi ⚡",
  "حلّل فكرتي": "Analizza l-idea tiegħi",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Iddeskrivi l-idea bil-vuċi",
  "فكرة المشروع": "Idea tal-proġett",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Installa S&amp;R CoreSync fuq it-tagħmir tiegħek",
  "تثبيت التطبيق": "Installa l-app",
  "أدوات الدعم": "Għodod ta' appoġġ",
  "خريطة 34 سوقاً": "Mappa ta' 34 suq",
}

GA = {
  "أنظمة برمجية متقدمة": "Córais bogearraí chun cinn",
  "تطبيقات ومنصات رقمية": "Aipeanna agus ardáin dhigiteacha",
  "هويات بصرية تُبنى لتدوم": "Féiniúlachtaí branda a mhaireann",
  "اكتب فكرة مشروعك هنا…": "Scríobh smaoineamh do thionscadail…",
  "حلّل فكرتي ✦": "Déan anailís ar mo smaoineamh ✦",
  "تجربة النظام السحابي الحي": "Bain triail as an gcóras scamall beo",
  "نسخة تجريبية حيّة": "Taispeántas beo",
  "أو ابدأ من الأقرب إلى مشروعك:": "Nó tosaigh leis an rud a oireann:",
  "متجر إلكتروني فاخر": "Siopa ar líne só",
  "نظام ERP متكامل": "Córas ERP iomlán",
  "هوية بصرية كاملة": "Féiniúlacht branda iomlán",
  "موقع تعريفي عالي التحويل": "Suíomh gréasáin ard-tiontaithe",
  "أتمتة وربط الأنظمة": "Uathoibriú agus comhtháthú",
  "استشارة تقنية": "Comhairle theicniúil",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Scríobh smaoineamh do thionscadail…",
  "حلل فكرتي بالـ AI ⚡": "Déan anailís ar mo smaoineamh ⚡",
  "حلّل فكرتي": "Déan anailís ar mo smaoineamh",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Cur síos ar do smaoineamh le guth",
  "فكرة المشروع": "Smaoineamh tionscadail",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Suiteáil S&amp;R CoreSync ar do ghléas",
  "تثبيت التطبيق": "Suiteáil an aip",
  "أدوات الدعم": "Uirlisí tacaíochta",
  "خريطة 34 سوقاً": "Léarscáil de 34 margadh",
}

KU = {
  "أنظمة برمجية متقدمة": "Pergalên nermalava pêşkeftî",
  "تطبيقات ومنصات رقمية": "Serlêdan û platformên dîjîtal",
  "هويات بصرية تُبنى لتدوم": "Nasnameyên brandê yên mayînde",
  "اكتب فكرة مشروعك هنا…": "Fikra projeya xwe binivîse…",
  "حلّل فكرتي ✦": "Fikra min analîz bike ✦",
  "تجربة النظام السحابي الحي": "Pergala cloud ya zindî biceribîne",
  "نسخة تجريبية حيّة": "Demo ya zindî",
  "أو ابدأ من الأقرب إلى مشروعك:": "An jî bi ya ku li hev tê dest pê bikin:",
  "متجر إلكتروني فاخر": "Firotgeha serhêl a luks",
  "نظام ERP متكامل": "Pergala ERP ya tevahî",
  "هوية بصرية كاملة": "Nasnameya brandê ya tevahî",
  "موقع تعريفي عالي التحويل": "Malpera bi veguherîna bilind",
  "أتمتة وربط الأنظمة": "Otomatîkî û entegrasyon",
  "استشارة تقنية": "Şêwirmendiya teknîkî",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Fikra projeya xwe binivîse…",
  "حلل فكرتي بالـ AI ⚡": "Fikra min analîz bike ⚡",
  "حلّل فكرتي": "Fikra min analîz bike",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Fikra xwe bi deng vebêje",
  "فكرة المشروع": "Fikra projeyê",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "S&amp;R CoreSync li cîhaza xwe saz bikin",
  "تثبيت التطبيق": "Serlêdanê saz bikin",
  "أدوات الدعم": "Amûrên piştgiriyê",
  "خريطة 34 سوقاً": "Nexşeya 34 bazaran",
}

BG = {
  "أنظمة برمجية متقدمة": "Модерни софтуерни системи",
  "تطبيقات ومنصات رقمية": "Дигитални приложения и платформи",
  "هويات بصرية تُبنى لتدوم": "Идентичности на марката, които остават",
  "اكتب فكرة مشروعك هنا…": "Опишете идеята на проекта си…",
  "حلّل فكرتي ✦": "Анализирай идеята ми ✦",
  "تجربة النظام السحابي الحي": "Изпробвайте живата облачна система",
  "نسخة تجريبية حيّة": "Демо на живо",
  "أو ابدأ من الأقرب إلى مشروعك:": "Или започнете с това, което пасва:",
  "متجر إلكتروني فاخر": "Луксозен онлайн магазин",
  "نظام ERP متكامل": "Пълна ERP система",
  "هوية بصرية كاملة": "Пълна идентичност на марката",
  "موقع تعريفي عالي التحويل": "Сайт с висока конверсия",
  "أتمتة وربط الأنظمة": "Автоматизация и интеграции",
  "استشارة تقنية": "Техническа консултация",
  "اكتب فكرة مشروعك هنا (مثال: متجر إلكتروني بهولندا، نظام ERP، تطبيق ذكاء اصطناعي...)": "Опишете идеята на проекта си…",
  "حلل فكرتي بالـ AI ⚡": "Анализирай идеята ми ⚡",
  "حلّل فكرتي": "Анализирай идеята ми",
  "تحدث بفكرة مشروعك بالصوت التفاعلي": "Опишете идеята си с глас",
  "فكرة المشروع": "Идея за проект",
  "تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك": "Инсталирайте S&amp;R CoreSync на устройството си",
  "تثبيت التطبيق": "Инсталирай приложението",
  "أدوات الدعم": "Инструменти за поддръжка",
  "خريطة 34 سوقاً": "Карта на 34 пазара",
}

BATCH = [('lv', LV), ('et', ET), ('mt', MT), ('ga', GA), ('ku', KU), ('bg', BG)]

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

    for lang in ['hu', 'sk', 'sl', 'hr', 'lt'] + [l for l, _ in BATCH]:
        print('nav', lang, SN.fix(os.path.join(ROOT, lang, 'index.html'))[1])
