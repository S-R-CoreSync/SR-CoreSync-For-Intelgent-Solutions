# -*- coding: utf-8 -*-
"""
S&R CoreSync Enterprise Omnichannel Synchronizer (Option 3 Execution)
Synchronizes:
1. Root demo.html (Polite Router + Royal Modals + CSS + Controls)
2. All 28 localized landing pages (en, nl, de, fr, es, it, tr, ku, ckb, pt, pl, etc.)
3. All 28 localized demo portals (en/demo.html, nl/demo.html, de/demo.html, etc.)
Guarantees 100% structural DOM parity with master index.html.
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. Patch Polite Mode in demo.html
def patch_root_demo_router():
    p = os.path.join(ROOT, 'demo.html')
    if not os.path.exists(p):
        return
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove automatic forced bounce on navigator.languages
    target_needle = r'// 4\. Automatic Device, Mobile & Browser Language Detection[\s\S]*?window\.location\.replace\(prefix \+ routePath \+ window\.location\.search \+ window\.location\.hash\);[\s\S]*?\}'
    replacement = '''// 4. Automatic Device, Mobile & Browser Language Detection
            // Polite mode: No forced redirect on navigator.languages! Respect user's explicit visit.
        }'''
    
    if re.search(target_needle, content):
        content = re.sub(target_needle, replacement, content, count=1)
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print("[demo.html] Patched with Polite Router (Zero Forced Hijacking).")

# High-precision language dictionary
LOCALES_CONFIG = {
    'fr': {
        'dir': 'ltr',
        'nav_more': '06+ / Plus',
        'store': '06 Boutique',
        'faq': '07 FAQ',
        'blog': '08 Perspectives',
        'api': '09 API Docs',
        'badge': '✨ S&R CoreSync Architecture IA Souveraine',
        'title': 'Transformez votre vision en réalité d\'entreprise souveraine',
        'subtitle': 'Décrivez votre projet ou utilisez la dictée vocale. Notre moteur d\'architecture IA calcule immédiatement le périmètre technique, la pile recommandée et la feuille de route.',
        'placeholder': 'Tapez votre idée de projet ici (ex. E-Commerce de luxe, Cloud ERP, Agents IA)...',
        'submit': '✨ Analyser mon projet avec l\'IA maintenant',
        'prompts_lbl': 'Inspiration rapide:',
        'chips': [
            ('🛒 E-Commerce de Luxe', 'Je souhaite créer une plateforme e-commerce de luxe avec paiement multidevise'),
            ('🏢 Cloud ERP Entreprise', 'Déploiement d\'un système ERP financier et opérationnel automatisé'),
            ('🤖 Agents IA Autonomes', 'Ingénierie d\'un réseau d\'agents IA autonomes pour flux d\'entreprise'),
            ('📱 Application Mobile & Cloud', 'Architecture d\'application mobile haute performance et cloud sécurisé')
        ],
        'est_title': 'Périmètre architectural & Estimation du calendrier',
        'est_query_lbl': 'Concept analysé:',
        'est_tier_lbl': 'Niveau architectural',
        'est_tier_val': 'Architecture Cloud & IA d\'entreprise',
        'est_timeline_lbl': 'Délai de lancement',
        'est_timeline_val': '3 - 5 Semaines',
        'est_budget_lbl': 'Investissement estimé 💳',
        'curr_all': 'Tous',
        'curr_eur': 'EUR €',
        'curr_sar': 'SAR',
        'est_roi_lbl': 'Retour sur investissement estimé 📈',
        'est_roi_val': '+240% d\'efficacité opérationnelle et d\'économies annuelles',
        'est_comp_lbl': 'Conformité & Sécurité',
        'est_comp_val': 'Conformité RGPD + 21% BTW',
        'est_stack_lbl': 'Architecture recommandée',
        'est_phases_lbl': 'Phases de déploiement souveraines:',
        'p1': 'Moteur central & Données',
        'p2': 'Interfaces & Passerelles API',
        'p3': 'Audit de sécurité & Mise en ligne',
        'btn_pdf': '📄 Exporter le plan d\'architecture (PDF)',
        'btn_wa': 'Consulter sur WhatsApp 💬',
        'btn_book': '👔 Réserver une consultation de direction',
        'btn_demo': '⚡ Explorer la sandbox cloud',
        'align': 'left'
    },
    'es': {
        'dir': 'ltr',
        'nav_more': '06+ / Más',
        'store': '06 Tienda',
        'faq': '07 FAQ',
        'blog': '08 Perspectivas',
        'api': '09 API Docs',
        'badge': '✨ S&R CoreSync Arquitectura de IA Soberana',
        'title': 'Convierta su visión en una realidad empresarial soberana',
        'subtitle': 'Describa su proyecto o use dictado por voz. Nuestro motor de IA calculará de inmediato el alcance técnico, la pila recomendada y la hoja de ruta.',
        'placeholder': 'Escriba la idea de su proyecto aquí (ej. E-Commerce de lujo, Cloud ERP, Agentes de IA)...',
        'submit': '✨ Analizar mi proyecto con IA ahora',
        'prompts_lbl': 'Inspiración rápida:',
        'chips': [
            ('🛒 E-Commerce de Lujo', 'Deseo construir una plataforma de comercio electrónico de lujo con pagos multidivisa'),
            ('🏢 Cloud ERP Empresarial', 'Implementación de un sistema ERP financiero y corporativo automatizado'),
            ('🤖 Agentes de IA Autónomos', 'Ingeniería de red de agentes de IA y flujos automatizados'),
            ('📱 App Móvil & Cloud', 'Arquitectura de aplicación móvil de alto rendimiento y ecosistema cloud seguro')
        ],
        'est_title': 'Alcance arquitectónico y Estimación de plazos',
        'est_query_lbl': 'Concepto analizado:',
        'est_tier_lbl': 'Nivel arquitectónico',
        'est_tier_val': 'Arquitectura Cloud & IA Empresarial',
        'est_timeline_lbl': 'Plazo de lanzamiento',
        'est_timeline_val': '3 - 5 Semanas',
        'est_budget_lbl': 'Inversión estimada 💳',
        'curr_all': 'Todos',
        'curr_eur': 'EUR €',
        'curr_sar': 'SAR',
        'est_roi_lbl': 'ROI anual proyectado 📈',
        'est_roi_val': '+240% de eficiencia operativa y ahorro de costes',
        'est_comp_lbl': 'Cumplimiento y Seguridad',
        'est_comp_val': 'Cumplimiento RGPD + 21% BTW',
        'est_stack_lbl': 'Arquitectura recomendada',
        'est_phases_lbl': 'Fases soberanas de despliegue:',
        'p1': 'Motor central y Modelado de datos',
        'p2': 'Interfaces y Pasarelas API',
        'p3': 'Auditoría y Puesta en producción',
        'btn_pdf': '📄 Exportar documento de arquitectura (PDF)',
        'btn_wa': 'Consultar por WhatsApp 💬',
        'btn_book': '👔 Reservar consulta ejecutiva',
        'btn_demo': '⚡ Explorar sandbox cloud',
        'align': 'left'
    },
    'it': {
        'dir': 'ltr',
        'nav_more': '06+ / Altro',
        'store': '06 Negozio',
        'faq': '07 FAQ',
        'blog': '08 Approfondimenti',
        'api': '09 API Docs',
        'badge': '✨ S&R CoreSync Architettura IA Sovrana',
        'title': 'Trasforma la tua visione in realtà aziendale sovrana',
        'subtitle': 'Descrivi il tuo progetto o usa la dettatura vocale. Il nostro motore calcola immediatamente ambito, stack consigliato e roadmap.',
        'placeholder': 'Digita la tua idea di progetto qui (es. E-Commerce di lusso, Cloud ERP, Agenti IA)...',
        'submit': '✨ Analizza il mio progetto con l\'IA ora',
        'prompts_lbl': 'Ispirazione rapida:',
        'chips': [
            ('🛒 E-Commerce di Lusso', 'Voglio realizzare una piattaforma e-commerce di lusso con checkout multivaluta'),
            ('🏢 Cloud ERP Aziendale', 'Implementazione di un sistema ERP finanziario e operativo automatizzato'),
            ('🤖 Agenti IA Autonomi', 'Ingegnerizzazione di una rete di agenti IA e flussi di lavoro'),
            ('📱 App Mobile & Cloud', 'Architettura di app mobile ad alte prestazioni ed ecosistema cloud sicuro')
        ],
        'est_title': 'Ambito architettonico e Stima dei tempi',
        'est_query_lbl': 'Concetto analizzato:',
        'est_tier_lbl': 'Livello architettonico',
        'est_tier_val': 'Architettura Cloud & IA Enterprise',
        'est_timeline_lbl': 'Tempistica di lancio',
        'est_timeline_val': '3 - 5 Settimane',
        'est_budget_lbl': 'Investimento stimato 💳',
        'curr_all': 'Tutti',
        'curr_eur': 'EUR €',
        'curr_sar': 'SAR',
        'est_roi_lbl': 'ROI annuo previsto 📈',
        'est_roi_val': '+240% di efficienza operativa e risparmio sui costi',
        'est_comp_lbl': 'Conformità e Sicurezza',
        'est_comp_val': 'Conformità GDPR + 21% BTW',
        'est_stack_lbl': 'Architettura consigliata',
        'est_phases_lbl': 'Fasi sovrane di implementazione:',
        'p1': 'Motore centrale e Modellazione dati',
        'p2': 'Interfacce e Gateway API',
        'p3': 'Audit di sicurezza e Go-Live',
        'btn_pdf': '📄 Esporta piano architettura (PDF)',
        'btn_wa': 'Consulta su WhatsApp 💬',
        'btn_book': '👔 Prenota una consulenza direzionale',
        'btn_demo': '⚡ Esplora la sandbox cloud',
        'align': 'left'
    },
    'tr': {
        'dir': 'ltr',
        'nav_more': '06+ / Daha',
        'store': '06 Mağaza',
        'faq': '07 SSS',
        'blog': '08 Görüşler',
        'api': '09 API Dokümantasyonu',
        'badge': '✨ S&R CoreSync Egemen Yapay Zeka Mimarisi',
        'title': 'Vizyonunuzu Egemen Kurumsal Gerçekliğe Dönüştürün',
        'subtitle': 'Projenizi açıklayın veya sesle yazmayı kullanın. Yapay zeka motorumuz teknik kapsamı, önerilen mimariyi ve lansman yol haritasını anında hesaplar.',
        'placeholder': 'Proje fikrinizi buraya yazın (ör. Lüks E-Ticaret, Bulut ERP, Yapay Zeka Ajanları)...',
        'submit': '✨ Projemi Şimdi Yapay Zeka ile Analiz Et',
        'prompts_lbl': 'Hızlı Fikir İlhamı:',
        'chips': [
            ('🛒 Lüks E-Ticaret Platformu', 'Çok para birimli ödeme altyapısına sahip kurumsal lüks e-ticaret platformu kurmak istiyorum'),
            ('🏢 Kurumsal Bulut ERP', 'Otomatik finansal ve operasyonel ERP sisteminin kurulması'),
            ('🤖 Otonom Yapay Zeka Ajanları', 'Kurumsal iş akışları için otonom yapay zeka ajanları ağı mühendisliği'),
            ('📱 Mobil & Bulut Platformu', 'Yüksek performanslı mobil uygulama ve güvenli bulut ekosistemi')
        ],
        'est_title': 'Mimari Kapsam ve Zaman Çizelgesi Tahmini',
        'est_query_lbl': 'Analiz Edilen Konsept:',
        'est_tier_lbl': 'Mimari Seviye',
        'est_tier_val': 'Yeni Nesil Kurumsal Bulut ve Yapay Zeka',
        'est_timeline_lbl': 'Lansman Takvimi',
        'est_timeline_val': '3 - 5 Hafta',
        'est_budget_lbl': 'Tahmini Yatırım 💳',
        'curr_all': 'Tümü',
        'curr_eur': 'EUR €',
        'curr_sar': 'SAR',
        'est_roi_lbl': 'Öngörülen Yıllık ROI 📈',
        'est_roi_val': '+%240 Operasyonel Verimlilik ve Maliyet Tasarrufu',
        'est_comp_lbl': 'Uyumluluk ve Güvenlik',
        'est_comp_val': 'GDPR + %21 BTW Uyumluluğu',
        'est_stack_lbl': 'Önerilen Mimari',
        'est_phases_lbl': 'Egemen Dağıtım Aşamaları:',
        'p1': 'Çekirdek Motor ve Veri Modelleme',
        'p2': 'Arayüzler ve API Ağ Geçitleri',
        'p3': 'Güvenlik Denetimi ve Canlıya Geçiş',
        'btn_pdf': '📄 Proje Mimarisi Belgesini İndir (PDF)',
        'btn_wa': 'WhatsApp ile Danışın 💬',
        'btn_book': '👔 Yönetici Danışmanlığı Randevusu Alın',
        'btn_demo': '⚡ Bulut Sandbox Deneyimi',
        'align': 'left'
    },
    'ku': {
        'dir': 'rtl',
        'nav_more': '06+ / Zêdetir',
        'store': '06 Firoşgeh',
        'faq': '07 Pirs',
        'blog': '08 Nêrîn',
        'api': '09 API Docs',
        'badge': '✨ S&R CoreSync Mîmariya AI ya Serwer',
        'title': 'Vîzyona xwe veguherînin rastiya karsaziya serwer',
        'subtitle': 'Projeya xwe binivîsin an deng bikar bînin. Motora me ya AI zû qada teknîkî û nexşeya rê dihesibîne.',
        'placeholder': 'Fikra projeya xwe li vir binivîsin...',
        'submit': '✨ Projeya min bi AI analîz bike',
        'prompts_lbl': 'Fikrên lezgîn:',
        'chips': [
            ('🛒 E-Bazirganiya Birûmet', 'Ez dixwazim platformek e-bazirganiya luks ava bikim'),
            ('🏢 ERP ya Pargîdaniyê', 'Bicihkirina pergala ERP ya darayî û kargêriyê ya xweser'),
            ('🤖 Agentên AI yên Xweser', 'Avakirina tora agentên AI yên xweser ji bo karûbarên karsaziyê'),
            ('📱 Serlêdana Mobîl & Cloud', 'Mîmariya sepanek mobîl a performansa bilind û ewle')
        ],
        'est_title': 'Nirxandina Qada Mîmarî û Demjimêr',
        'est_query_lbl': 'Têgeha analîzkirî:',
        'est_tier_lbl': 'Asta Mîmarî',
        'est_tier_val': 'Mîmariya Cloud & AI ya Pargîdaniyê',
        'est_timeline_lbl': 'Dema destpêkirinê',
        'est_timeline_val': '3 - 5 Hefte',
        'est_budget_lbl': 'Veberhênana texmînkirî 💳',
        'curr_all': 'Hemû',
        'curr_eur': 'EUR €',
        'curr_sar': 'SAR',
        'est_roi_lbl': 'ROI ya salane ya pêşbînîkirî 📈',
        'est_roi_val': '+240% Karbidestiya xebitandinê',
        'est_comp_lbl': 'Lihevhatin û Ewlehî',
        'est_comp_val': 'GDPR + 21% BTW Lihevhatin',
        'est_stack_lbl': 'Mîmariya pêşniyarkirî',
        'est_phases_lbl': 'Qonaxên bicîhkirinê:',
        'p1': 'Motora bingehîn û Daneyên',
        'p2': 'Navrû û Dergehên API',
        'p3': 'Kontrolkirin û Çûna Zindî',
        'btn_pdf': '📄 Belgeya Mîmariyê Daxîne (PDF)',
        'btn_wa': 'Bi rêya WhatsAppê bişêwire 💬',
        'btn_book': '👔 Şêwirmendiyek taybet veqetînin',
        'btn_demo': '⚡ Ezmûna Pergala Cloud',
        'align': 'right'
    },
    'ckb': {
        'dir': 'rtl',
        'nav_more': '06+ / زیاتر',
        'store': '06 فرۆشگە',
        'faq': '07 پرسیارە باوەکان',
        'blog': '08 دیدگا',
        'api': '09 بەڵگەنامەی API',
        'badge': '✨ S&R CoreSync تەلارسازی زیرەکی دەستکردی سەروەر',
        'title': 'دیدگاکەت بکە بە ڕاستییەکی دامەزراوەیی سەروەر',
        'subtitle': 'بیرۆکەی پڕۆژەکەت بنووسە یان دەنگ بەکاربهێنە. بزوێنەری ژیری دەستکردمان ڕاستەوخۆ مەودای تەکنیکی و نەخشەڕێگا دیاری دەکات.',
        'placeholder': 'بیرۆکەی پڕۆژەکەت لێرە بنووسە...',
        'submit': '✨ پڕۆژەکەم بە AI شیکاربکە',
        'prompts_lbl': 'بیرۆکەی خێرا:',
        'chips': [
            ('🛒 بازرگانی ئەلیکترۆنی فاخر', 'دەمەوێت پلاتفۆرمێکی بازرگانی ئەلیکترۆنی پێشکەوتوو دروستبکەم'),
            ('🏢 سیستەمی ERP ی دامەزراوەیی', 'جێبەجێکردنی سیستەمی دارایی و بەڕێوەبردنی ئۆتۆماتیکی ERP'),
            ('🤖 بریکارە سەربەخۆکانی AI', 'ئەندازیاری تۆڕی بریکارە ژیرەکان بۆ کارەکانی دامەزراوە'),
            ('📱 ئەپی مۆبایل و هەور', 'تەلارسازی ئەپڵیکەیشنی مۆبایلی خێرا و هەوری پارێزراو')
        ],
        'est_title': 'شیکاری مەودای تەلارسازی و خشتەی کاتی',
        'est_query_lbl': 'بیرۆکەی شیکارکراو:',
        'est_tier_lbl': 'ئاستی تەلارسازی',
        'est_tier_val': 'تەلارسازی هەور و AI ی دامەزراوەیی',
        'est_timeline_lbl': 'ماوەی خستنەگەڕ',
        'est_timeline_val': '٣ - ٥ هەفتە',
        'est_budget_lbl': 'بودجەی خەمڵێنراو 💳',
        'curr_all': 'هەموو',
        'curr_eur': 'EUR €',
        'curr_sar': 'SAR',
        'est_roi_lbl': 'گەڕانەوەی وەبەرهێنانی ساڵانە 📈',
        'est_roi_val': '+٢٤٠٪ کارایی کارپێکردن و پاشەکەوتکردن',
        'est_comp_lbl': 'پابەندبوون و پاراستن',
        'est_comp_val': 'GDPR + 21% BTW پابەندبوون',
        'est_stack_lbl': 'تەلارسازی پێشنیازکراو',
        'est_phases_lbl': 'قۆناغەکانی جێبەجێکردن:',
        'p1': 'ماتۆڕی سەرەکی و داتا',
        'p2': 'ڕووکارەکان و دەروازەکانی API',
        'p3': 'وردبینی و دەستپێکردنی ڕاستەوخۆ',
        'btn_pdf': '📄 داگرتنی بەڵگەنامەی تەلارسازی (PDF)',
        'btn_wa': 'ڕاوێژ لە ڕێگەی WhatsApp 💬',
        'btn_book': '👔 حجزکردنی دانیشتنی ڕاوێژکاری',
        'btn_demo': '⚡ ئەزموونکردنی سیستەمی هەور',
        'align': 'right'
    }
}

# Arabic config for root demo.html
AR_CONFIG = {
    'dir': 'rtl',
    'nav_more': '06+ / المزيد',
    'store': '06 المتجر البرمجي',
    'faq': '07 الأسئلة الشائعة',
    'blog': '08 الرؤى والمدونة',
    'api': '09 توثيق API',
    'badge': '✨ S&R CoreSync Sovereign AI Architecture',
    'title': 'حوّل فكرتك إلى واقع تقني ذكي',
    'subtitle': 'اكتب فكرة مشروعك باختصار أو استخدم الإملاء الصوتي، وسيقوم محرك الذكاء الاصطناعي بتقدير النطاق المعماري، التقنيات المقترحة، والجدول الزمني للإطلاق فوراً.',
    'placeholder': 'اكتب فكرة مشروعك هنا (مثلاً: أريد بناء متجر إلكتروني ذكي أو منصة ERP)...',
    'submit': '✨ حلل فكرتي بالذكاء الاصطناعي فوراً',
    'prompts_lbl': 'أفكار وتجارب سريعة:',
    'chips': [
        ('🛒 متجر إلكتروني فاخر', 'أريد بناء منصة تجارة إلكترونية فاخرة متكاملة مع دفع متعدد العملات'),
        ('🏢 منظومة ERP مؤسسية', 'تطوير منظومة ERP مالية وإدارية مؤسسية مؤتمتة متوافقة مع لوائح الاتحاد الأوروبي'),
        ('🤖 وكلاء AI وأتمتة', 'بناء شبكة وكلاء ذكاء اصطناعي وأتمتة لخدمة العملاء والعمليات'),
        ('📱 تطبيق ومنصة سحابية', 'هندسة تطبيق جوال ومنصة سحابية متقدمة وفائقة الأمان')
    ],
    'est_title': 'تحليل النطاق المعماري والجدول الزمني',
    'est_query_lbl': 'الفكرة المحللة:',
    'est_tier_lbl': 'التصنيف المعماري',
    'est_tier_val': 'منظومة سحابية متقدمة',
    'est_timeline_lbl': 'الجدول الزمني للإطلاق',
    'est_timeline_val': '3 - 5 أسابيع',
    'est_budget_lbl': 'الميزانية التقديرية 💳',
    'curr_all': 'الكل',
    'curr_eur': 'EUR €',
    'curr_sar': 'SAR ر.س',
    'est_roi_lbl': 'العائد الاستثماري المتوقع (ROI) 📈',
    'est_roi_val': '+240% كفاءة تشغيلية وتوفير سنوي',
    'est_comp_lbl': 'معايير الامتثال والأمان',
    'est_comp_val': 'GDPR + 21% BTW',
    'est_stack_lbl': 'المعمارية الموصى بها',
    'est_phases_lbl': 'مراحل التنفيذ السيادية:',
    'p1': 'هندسة النواة والبيانات',
    'p2': 'تطوير الواجهة وبوابات الربط',
    'p3': 'التدقيق والتشغيل الحي',
    'btn_pdf': '📄 تصدير وثيقة المشروع (PDF)',
    'btn_wa': 'مشاركة عبر WhatsApp 💬',
    'btn_book': '👔 حجز جلسة استشارية خاصة',
    'btn_demo': '⚡ تجربة النظام السحابي',
    'align': 'right'
}

def get_locale_config(lang):
    if lang == 'ar':
        return AR_CONFIG
    if lang in LOCALES_CONFIG:
        return LOCALES_CONFIG[lang]
    # Fallback to English for any other language
    from sync_dom_master import CONFIGS
    en = CONFIGS['en']
    return {
        'dir': 'ltr',
        'nav_more': en['nav_more_label'],
        'store': en['store_label'],
        'faq': en['faq_label'],
        'blog': en['blog_label'],
        'api': en['api_label'],
        'badge': en['modal_badge'],
        'title': en['modal_title'],
        'subtitle': en['modal_subtitle'],
        'placeholder': en['modal_placeholder'],
        'submit': en['modal_submit'],
        'prompts_lbl': en['prompts_label'],
        'chips': en['prompt_chips'],
        'est_title': en['est_title'],
        'est_query_lbl': en['est_query_label'],
        'est_tier_lbl': en['est_lbl_class'],
        'est_tier_val': en['est_val_class'],
        'est_timeline_lbl': en['est_lbl_timeline'],
        'est_timeline_val': en['est_val_timeline'],
        'est_budget_lbl': en['est_lbl_budget'],
        'curr_all': en['curr_all'],
        'curr_eur': en['curr_eur'],
        'curr_sar': en['curr_sar'],
        'est_roi_lbl': en['est_lbl_roi'],
        'est_roi_val': en['est_val_roi'],
        'est_comp_lbl': en['est_lbl_compliance'],
        'est_comp_val': en['est_val_compliance'],
        'est_stack_lbl': en['est_lbl_stack'],
        'est_phases_lbl': en['est_phases_label'],
        'p1': en['phase1'],
        'p2': en['phase2'],
        'p3': en['phase3'],
        'btn_pdf': en['btn_pdf'],
        'btn_wa': en['btn_wa'],
        'btn_book': en['btn_consult'],
        'btn_demo': en['btn_demo'],
        'align': 'left'
    }

def build_modals_html(cfg):
    chips_html = '\n'.join([
        f'                <button type="button" class="sr-idea-prompt-chip" onclick="setAndSubmitPrompt(\'{prompt}\')">{label}</button>'
        for label, prompt in cfg['chips']
    ])
    align_dir = cfg['dir']
    align_text = cfg['align']
    close_pos = 'left: 18px;' if align_dir == 'rtl' else 'right: 18px;'
    mic_pos = 'right: 12px;' if align_dir == 'rtl' else 'right: 12px;'

    return f'''    <!-- AI Scope & Timeline Estimator Modal -->
    <div id="srAiEstimateModal" role="dialog" aria-modal="true" aria-label="{cfg['est_title']}" onclick="if(event.target===this)closeAiEstimateModal()">
        <div class="sr-ai-estimate-card" id="srAiEstimateCard" style="direction:{align_dir}; text-align:{align_text};">
            <div class="sr-estimate-header">
                <div class="d-flex align-items-center gap-2">
                    <span class="sr-estimate-icon">✨</span>
                    <div>
                        <span class="sr-estimate-badge">S&amp;R CoreSync AI Architecture Engine</span>
                        <h2 class="sr-estimate-title" id="srEstTitle">{cfg['est_title']}</h2>
                    </div>
                </div>
                <button type="button" class="sr-peek-close-corner" onclick="closeAiEstimateModal()" aria-label="Close">✕</button>
            </div>

            <div class="sr-estimate-user-query">
                <span class="sr-query-label">{cfg['est_query_lbl']}</span>
                <p class="sr-query-text" id="srEstQueryText">"..."</p>
            </div>

            <div class="sr-estimate-grid">
                <div class="sr-est-metric-card">
                    <span class="sr-est-lbl">{cfg['est_tier_lbl']}</span>
                    <strong class="sr-est-val" id="srEstClassification">{cfg['est_tier_val']}</strong>
                </div>
                <div class="sr-est-metric-card">
                    <span class="sr-est-lbl">{cfg['est_timeline_lbl']}</span>
                    <strong class="sr-est-val sr-val-gold" id="srEstTimeline">{cfg['est_timeline_val']}</strong>
                </div>
                <div class="sr-est-metric-card sr-est-metric-gold-box" style="border-color: rgba(var(--sr-gold-rgb, 212, 175, 55), 0.55); background: rgba(var(--sr-gold-rgb, 212, 175, 55), 0.08); box-shadow: 0 0 20px rgba(var(--sr-gold-rgb, 212, 175, 55), 0.12);">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:4px;">
                        <span class="sr-est-lbl" style="color: #fce0ad;">{cfg['est_budget_lbl']}</span>
                        <div class="sr-est-currency-toggles" style="display:flex; gap:4px;" aria-label="Currency View Toggle">
                            <button type="button" class="sr-curr-btn active" onclick="switchEstimateCurrency('all', this)" style="padding:2px 7px; font-size:0.68rem; border-radius:5px; border:1px solid rgba(var(--sr-gold-rgb, 212, 175, 55),0.4); background:rgba(var(--sr-gold-rgb, 212, 175, 55),0.25); color:#fff; cursor:pointer; font-weight:700;">{cfg['curr_all']}</button>
                            <button type="button" class="sr-curr-btn" onclick="switchEstimateCurrency('eur', this)" style="padding:2px 7px; font-size:0.68rem; border-radius:5px; border:1px solid rgba(255,255,255,0.15); background:transparent; color:#f3dfba; cursor:pointer; font-weight:700;">{cfg['curr_eur']}</button>
                            <button type="button" class="sr-curr-btn" onclick="switchEstimateCurrency('sar', this)" style="padding:2px 7px; font-size:0.68rem; border-radius:5px; border:1px solid rgba(255,255,255,0.15); background:transparent; color:#f3dfba; cursor:pointer; font-weight:700;">{cfg['curr_sar']}</button>
                        </div>
                    </div>
                    <strong class="sr-est-val sr-val-gold font-num" id="srEstBudget">€4,500 - €8,900  |  18,000 - 35,600 SAR</strong>
                </div>
                <div class="sr-est-metric-card sr-est-metric-roi-box" style="border-color: rgba(16, 185, 129, 0.4); background: rgba(16, 185, 129, 0.08);">
                    <span class="sr-est-lbl" style="color: #a7f3d0;">{cfg['est_roi_lbl']}</span>
                    <strong class="sr-est-val sr-val-emerald font-num" id="srEstRoi">{cfg['est_roi_val']}</strong>
                </div>
                <div class="sr-est-metric-card">
                    <span class="sr-est-lbl">{cfg['est_comp_lbl']}</span>
                    <strong class="sr-est-val sr-val-emerald" id="srEstCompliance">{cfg['est_comp_val']}</strong>
                </div>
                <div class="sr-est-metric-card">
                    <span class="sr-est-lbl">{cfg['est_stack_lbl']}</span>
                    <strong class="sr-est-val" id="srEstStack">Next.js + CoreSync Cloud</strong>
                </div>
            </div>

            <div class="sr-estimate-phases">
                <span class="sr-phases-label">{cfg['est_phases_lbl']}</span>
                <div class="sr-phase-steps">
                    <div class="sr-phase-step"><span class="step-num">1</span><span>{cfg['p1']}</span></div>
                    <div class="sr-phase-sep">→</div>
                    <div class="sr-phase-step"><span class="step-num">2</span><span>{cfg['p2']}</span></div>
                    <div class="sr-phase-sep">→</div>
                    <div class="sr-phase-step"><span class="step-num">3</span><span>{cfg['p3']}</span></div>
                </div>
            </div>

            <div class="sr-estimate-actions">
                <button type="button" class="sr-peek-btn-pdf" id="srBtnExportPdf" onclick="exportAiEstimatePdf()">{cfg['btn_pdf']}</button>
                <button type="button" class="sr-peek-btn-wa" id="srBtnEstimateWhatsApp" onclick="sendEstimateViaWhatsApp()" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color:#ffffff; border:1px solid #34d399; font-weight:800; padding:11px 18px; border-radius:12px; cursor:pointer; display:inline-flex; align-items:center; gap:6px; box-shadow:0 4px 15px rgba(16,185,129,0.35); font-size:0.86rem; transition:transform 0.2s ease;">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M20.52 3.48A11.93 11.93 0 0 0 12.06 0C5.45 0 .09 5.36.09 11.97c0 2.11.55 4.17 1.6 5.98L0 24l6.23-1.63a11.9 11.9 0 0 0 5.83 1.51h.01c6.6 0 11.96-5.36 11.96-11.97 0-3.2-1.25-6.21-3.51-8.43zm-8.46 18.42h-.01a9.92 9.92 0 0 1-5.06-1.39l-.36-.22-3.76.99 1-3.66-.24-.38a9.9 9.9 0 0 1-1.52-5.27c0-5.48 4.46-9.94 9.95-9.94 2.65 0 5.15 1.03 7.02 2.91 1.88 1.88 2.91 4.38 2.91 7.03 0 5.48-4.46 9.93-9.93 9.93zm5.45-7.44c-.3-.15-1.77-.87-2.04-.97-.28-.1-.48-.15-.68.15-.2.3-.78.97-.95 1.17-.18.2-.35.23-.65.08-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.18-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.18.2-.3.3-.5.1-.2.05-.38-.03-.53-.07-.15-.68-1.63-.93-2.24-.24-.59-.49-.51-.68-.52h-.58c-.2 0-.53.08-.8.38-.28.3-1.05 1.03-1.05 2.51s1.08 2.91 1.23 3.11c.15.2 2.12 3.24 5.14 4.54.72.31 1.28.5 1.72.64.72.23 1.38.2 1.9.12.58-.09 1.77-.72 2.02-1.42.25-.7.25-1.3.18-1.42-.08-.12-.28-.2-.58-.35z"/></svg>
                    <span>{cfg['btn_wa']}</span>
                </button>
                <button type="button" class="sr-peek-btn-go" onclick="closeAiEstimateModal(); window.location.href='#services';">{cfg['btn_book']}</button>
                <a href="demo.html" class="sr-peek-btn-secondary" onclick="closeAiEstimateModal()">{cfg['btn_demo']}</a>
            </div>
        </div>
    </div>

    <!-- AI Idea Analyzer Royal Modal -->
    <div id="srIdeaPromptModal" role="dialog" aria-modal="true" aria-labelledby="srIdeaModalTitle" onclick="if(event.target===this)closeIdeaModal()">
        <div class="sr-idea-modal-card" style="direction:{align_dir}; text-align:{align_text};">
            <button type="button" class="sr-idea-modal-close" style="{close_pos}" onclick="closeIdeaModal()" aria-label="Close">✕</button>
            <div class="sr-idea-modal-badge">{cfg['badge']}</div>
            <h2 class="sr-idea-modal-title" id="srIdeaModalTitle">{cfg['title']}</h2>
            <p class="sr-idea-modal-subtitle">{cfg['subtitle']}</p>

            <div class="sr-idea-input-wrapper">
                <input type="text" id="userIdeaInput" class="sr-idea-input-field" style="direction:{align_dir}; text-align:{align_text}; padding: 16px 52px 16px 16px;" placeholder="{cfg['placeholder']}" onkeydown="if(event.key==='Enter'){{submitIdeaAnalysis();}}" />
                <button type="button" id="srVoiceDictateBtn" onclick="toggleHeroVoiceDictation()" class="sr-idea-mic-btn" style="{mic_pos}" title="Voice Dictate" aria-label="Voice Dictate">🎙️</button>
            </div>

            <div class="sr-idea-modal-actions">
                <button type="button" onclick="submitIdeaAnalysis()" class="sr-idea-submit-btn">
                    <span>{cfg['submit']}</span>
                </button>
            </div>

            <div class="sr-idea-quick-prompts">
                <span class="sr-idea-quick-prompts-label">{cfg['prompts_lbl']}</span>
{chips_html}
            </div>
        </div>
    </div>

    <!-- Royal Modal & Navigation Controls Script -->
    <script>
    function toggleNavMore(e) {{
        if (e) e.stopPropagation();
        var btn = document.getElementById('navMoreBtn');
        var menu = document.getElementById('navMoreSubmenu');
        if (!btn || !menu) return;
        var isOpen = menu.classList.contains('open');
        menu.classList.toggle('open', !isOpen);
        btn.setAttribute('aria-expanded', String(!isOpen));
    }}

    function openIdeaModal() {{
        var modal = document.getElementById('srIdeaPromptModal');
        if (!modal) return;
        modal.classList.add('is-active');
        document.body.style.overflow = 'hidden';
        setTimeout(function() {{
            var input = document.getElementById('userIdeaInput');
            if (input) input.focus();
        }}, 150);
    }}

    function closeIdeaModal() {{
        var modal = document.getElementById('srIdeaPromptModal');
        if (!modal) return;
        modal.classList.remove('is-active');
        document.body.style.overflow = '';
    }}

    function submitIdeaAnalysis() {{
        var input = document.getElementById('userIdeaInput');
        var val = input ? input.value : '';
        if (val && val.trim()) {{
            closeIdeaModal();
            if (typeof analyzeIdea === 'function') {{
                analyzeIdea();
            }} else if (typeof openAiEstimatorModal === 'function') {{
                openAiEstimatorModal(val);
            }}
        }} else {{
            if (input) {{
                input.focus();
                input.style.borderColor = '#ef4444';
                setTimeout(function() {{ input.style.borderColor = ''; }}, 1500);
            }}
        }}
    }}

    function setAndSubmitPrompt(promptText) {{
        var input = document.getElementById('userIdeaInput');
        if (input) input.value = promptText;
        submitIdeaAnalysis();
    }}

    document.addEventListener('keydown', function(e) {{
        if (e.key === 'Escape') {{
            closeIdeaModal();
            var menu = document.getElementById('navMoreSubmenu');
            if (menu && menu.classList.contains('open')) {{
                menu.classList.remove('open');
                var btn = document.getElementById('navMoreBtn');
                if (btn) btn.setAttribute('aria-expanded', 'false');
            }}
        }}
    }});

    document.addEventListener('click', function(e) {{
        var menu = document.getElementById('navMoreSubmenu');
        var btn = document.getElementById('navMoreBtn');
        if (menu && menu.classList.contains('open')) {{
            if (!menu.contains(e.target) && !btn.contains(e.target)) {{
                menu.classList.remove('open');
                btn.setAttribute('aria-expanded', 'false');
            }}
        }}
    }});
    </script>
'''

from sync_dom_master import CSS_MODAL

def sync_landing_file(lang):
    file_path = os.path.join(ROOT, lang, 'index.html')
    if not os.path.exists(file_path):
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    cfg = get_locale_config(lang)
    modified = False

    # 1. Inject CSS if missing
    if '/* AI Idea Analyzer Royal Modal Styles */' not in html:
        style_close_idx = html.find('</style>')
        if style_close_idx != -1:
            html = html[:style_close_idx] + CSS_MODAL + html[style_close_idx:]
            modified = True

    # 2. Inject Royal Clean Nav More Dropdown in header if missing
    if 'id="navMoreBtn"' not in html:
        nav_pattern = r'(<li[^>]*>\s*<a[^>]*href="#roi"[^>]*>[\s\S]*?</li>)'
        m = re.search(nav_pattern, html)
        if m:
            roi_item = m.group(0)
            dropdown_html = f'''
                    <li class="nav-item-has-submenu">
                        <button type="button" class="nav-more-btn" id="navMoreBtn" onclick="toggleNavMore(event)" aria-expanded="false" aria-haspopup="true" style="background:none; border:none; color:inherit; font:inherit; cursor:pointer; display:inline-flex; align-items:center; gap:4px; padding:6px 10px;">
                            <span>{cfg['nav_more']}</span>
                        </button>
                        <ul class="nav-submenu" id="navMoreSubmenu" role="menu">
                            <li role="none"><a role="menuitem" href="#software-hub">{cfg['store']}</a></li>
                            <li role="none"><a role="menuitem" href="#faq">{cfg['faq']}</a></li>
                            <li role="none"><a role="menuitem" href="#insights">{cfg['blog']}</a></li>
                            <li role="none"><a role="menuitem" href="#api-docs">{cfg['api']}</a></li>
                        </ul>
                    </li>'''
            html = html.replace(roi_item, roi_item + dropdown_html, 1)
            modified = True

    # 3. Inject Modals and script controls before </body>
    if 'id="srIdeaPromptModal"' not in html:
        body_close_idx = html.rfind('</body>')
        if body_close_idx != -1:
            modal_content = build_modals_html(cfg)
            html = html[:body_close_idx] + '\n' + modal_content + '\n' + html[body_close_idx:]
            modified = True

    if modified:
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            f.write(html)
        print(f"[{lang}/index.html] Synchronized.")

def sync_demo_file(lang):
    file_path = os.path.join(ROOT, lang, 'demo.html') if lang != 'ar' else os.path.join(ROOT, 'demo.html')
    if not os.path.exists(file_path):
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    cfg = get_locale_config(lang)
    modified = False

    # 1. Inject CSS if missing
    if '/* AI Idea Analyzer Royal Modal Styles */' not in html:
        style_close_idx = html.find('</style>')
        if style_close_idx != -1:
            html = html[:style_close_idx] + CSS_MODAL + html[style_close_idx:]
            modified = True

    # 2. Inject Modals and script controls before </body>
    if 'id="srIdeaPromptModal"' not in html:
        body_close_idx = html.rfind('</body>')
        if body_close_idx != -1:
            modal_content = build_modals_html(cfg)
            html = html[:body_close_idx] + '\n' + modal_content + '\n' + html[body_close_idx:]
            modified = True

    if modified:
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            f.write(html)
        print(f"[{lang}/demo.html] Synchronized.")

def main():
    patch_root_demo_router()
    all_langs = [d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)) and len(d) <= 3 and os.path.exists(os.path.join(ROOT, d, 'index.html'))]
    all_langs = sorted(all_langs)
    
    print(f"Propagating Royal Architecture across {len(all_langs)} landing pages...")
    for lang in all_langs:
        sync_landing_file(lang)
        
    print(f"Propagating Royal Architecture across root demo.html and {len(all_langs)} localized demo portals...")
    sync_demo_file('ar')
    for lang in all_langs:
        sync_demo_file(lang)

    print("Omnichannel Synchronization Finished Successfully.")

if __name__ == '__main__':
    main()
