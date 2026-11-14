# -*- coding: utf-8 -*-
"""
Phase 1: Header & Shared Chrome Multilingual Purity.
Replaces all Arabic remnants in <header> and launchpad dock button with the pure target language.
"""
import os, re, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Base English for fallback on minor languages, plus native translations for major ones
EN_BASE = {
    'brand_title': 'S&R CoreSync For Intelligent Solutions - Click to view full brand identity',
    'brand_aria': 'S&R CoreSync For Intelligent Solutions Official Brandmark',
    'nav_more_aria': 'More links and sections',
    'nav_res_aria': 'Additional resources and sections',
    'pwa_title': 'Install S&R CoreSync as standalone app on your device',
    'support_tools_title': 'Enterprise Support Tools & Evaluation',
    'support_tools_aria': 'Support Tools and Simulation',
    'interactive_services': 'Live Interactive Services',
    'readiness_strong': 'Digital Readiness Check 🎯',
    'readiness_span': 'Assess cloud infrastructure & automation maturity',
    'consultation_strong': 'Executive Consultation Booking 👔',
    'consultation_span': 'Book strategic meeting with the founders',
    'feedback_strong': 'Experience Rating & Feedback 💬',
    'feedback_span': 'Send direct feedback to enhance and develop service',
    'mobile_menu_aria': 'Open Main Navigation Menu',
    'menu_text': 'Menu',
    'dock_launchpad_tooltip': 'All 29 Languages (Launchpad)',
    'nav_services': 'Services & Systems',
    'nav_pricing': 'Pricing & Plans',
    'nav_software': 'Software Hub',
    'nav_about': 'About & Leadership',
    'nav_resources': 'Resources & ROI',
    'nav_roi': 'ROI Calculator',
    'nav_faq': 'FAQ',
    'nav_blog': 'Tech Blog',
    'nav_api': 'API Docs'
}

CUSTOM = {
    'tr': {
        'brand_title': 'S&R CoreSync For Intelligent Solutions - Tam marka kimliğini görüntülemek için tıklayın',
        'brand_aria': 'S&R CoreSync For Intelligent Solutions Resmi Markası',
        'nav_more_aria': 'Daha fazla bağlantı ve bölüm',
        'nav_res_aria': 'Ek kaynaklar ve bölümler',
        'pwa_title': 'S&R CoreSync uygulamasını cihazınıza bağımsız uygulama olarak yükleyin',
        'support_tools_title': 'Kurumsal Destek Araçları ve Değerlendirme',
        'support_tools_aria': 'Destek Araçları ve Simülasyon',
        'interactive_services': 'Canlı Etkileşimli Hizmetler',
        'readiness_strong': 'Dijital Hazırlık Kontrolü 🎯',
        'readiness_span': 'Bulut altyapısı ve otomasyon olgunluğunu değerlendirin',
        'consultation_strong': 'Yönetici Danışmanlığı Randevusu 👔',
        'consultation_span': 'Kurucularla stratejik toplantı planlayın',
        'feedback_strong': 'Deneyim Değerlendirmesi ve Geri Bildirim 💬',
        'feedback_span': 'Hizmet kalitesini artırmak için doğrudan geri bildirim gönderin',
        'mobile_menu_aria': 'Ana Menüyü Aç',
        'menu_text': 'Menü',
        'dock_launchpad_tooltip': 'Tüm 29 Dil (Launchpad)',
        'nav_services': 'Hizmetler & Sistemler',
        'nav_pricing': 'Fiyatlar & Paketler',
        'nav_software': 'Yazılım Merkezi',
        'nav_about': 'Hakkımızda & Liderlik',
        'nav_resources': 'Kaynaklar & ROI',
        'nav_roi': 'ROI Hesaplayıcı',
        'nav_faq': 'SSS',
        'nav_blog': 'Teknoloji Blogu',
        'nav_api': 'API Belgeleri'
    },
    'de': {
        'brand_title': 'S&R CoreSync For Intelligent Solutions - Klicken Sie hier, um die vollständige Markenidentität anzuzeigen',
        'brand_aria': 'Offizielles Markenzeichen von S&R CoreSync For Intelligent Solutions',
        'nav_more_aria': 'Weitere Links und Bereiche',
        'nav_res_aria': 'Zusätzliche Ressourcen und Bereiche',
        'pwa_title': 'S&R CoreSync als eigenständige App auf Ihrem Gerät installieren',
        'support_tools_title': 'Enterprise Support-Tools & Bewertung',
        'support_tools_aria': 'Support-Tools und Simulation',
        'interactive_services': 'Interaktive Live-Dienste',
        'readiness_strong': 'Digital-Readiness-Check 🎯',
        'readiness_span': 'Reifegrad von Cloud-Infrastruktur & Automatisierung bewerten',
        'consultation_strong': 'Executive-Beratung buchen 👔',
        'consultation_span': 'Strategisches Meeting mit den Gründern vereinbaren',
        'feedback_strong': 'Erfahrungsbewertung & Feedback 💬',
        'feedback_span': 'Direktes Feedback zur Serviceverbesserung senden',
        'mobile_menu_aria': 'Hauptmenü öffnen',
        'menu_text': 'Menü',
        'dock_launchpad_tooltip': 'Alle 29 Sprachen (Launchpad)',
        'nav_services': 'Dienste & Systeme',
        'nav_pricing': 'Preise & Pläne',
        'nav_software': 'Software-Hub',
        'nav_about': 'Über uns & Führung',
        'nav_resources': 'Ressourcen & ROI',
        'nav_roi': 'ROI-Rechner',
        'nav_faq': 'FAQ',
        'nav_blog': 'Tech-Blog',
        'nav_api': 'API-Dokumentation'
    },
    'nl': {
        'brand_title': 'S&R CoreSync For Intelligent Solutions - Klik om volledige merkidentiteit te bekijken',
        'brand_aria': 'Officieel merkbeeld van S&R CoreSync For Intelligent Solutions',
        'nav_more_aria': 'Meer links en secties',
        'nav_res_aria': 'Aanvullende bronnen en secties',
        'pwa_title': 'Installeer S&R CoreSync als zelfstandige app op uw apparaat',
        'support_tools_title': 'Enterprise Support Tools & Evaluatie',
        'support_tools_aria': 'Support Tools en Simulatie',
        'interactive_services': 'Live Interactieve Diensten',
        'readiness_strong': 'Digitale Gereedheidscontrole 🎯',
        'readiness_span': 'Beoordeel cloudinfrastructuur & automatiseringsvolwassenheid',
        'consultation_strong': 'Executive Consultatie Boeken 👔',
        'consultation_span': 'Plan een strategische meeting met de oprichters',
        'feedback_strong': 'Ervaringsbeoordeling & Feedback 💬',
        'feedback_span': 'Stuur directe feedback om de dienstverlening te verbeteren',
        'mobile_menu_aria': 'Hoofdmenu openen',
        'menu_text': 'Menu',
        'dock_launchpad_tooltip': 'Alle 29 Talen (Launchpad)',
        'nav_services': 'Diensten & Systemen',
        'nav_pricing': 'Prijzen & Pakketten',
        'nav_software': 'Software Hub',
        'nav_about': 'Over ons & Leiderschap',
        'nav_resources': 'Bronnen & ROI',
        'nav_roi': 'ROI Calculator',
        'nav_faq': 'Veelgestelde Vragen',
        'nav_blog': 'Tech Blog',
        'nav_api': 'API Documentatie'
    },
    'fr': {
        'brand_title': 'S&R CoreSync For Intelligent Solutions - Cliquez pour voir l\'identité de marque complète',
        'brand_aria': 'Emblème officiel de S&R CoreSync For Intelligent Solutions',
        'nav_more_aria': 'Plus de liens et de sections',
        'nav_res_aria': 'Ressources et sections supplémentaires',
        'pwa_title': 'Installer S&R CoreSync comme application autonome sur votre appareil',
        'support_tools_title': 'Outils de support d\'entreprise & Évaluation',
        'support_tools_aria': 'Outils de support et simulation',
        'interactive_services': 'Services Interactifs en Direct',
        'readiness_strong': 'Contrôle de Préparation Numérique 🎯',
        'readiness_span': 'Évaluer la maturité du cloud et de l\'automatisation',
        'consultation_strong': 'Réserver une Consultation Dirigeant 👔',
        'consultation_span': 'Planifier une réunion stratégique avec les fondateurs',
        'feedback_strong': 'Évaluation d\'Expérience & Retours 💬',
        'feedback_span': 'Envoyer un retour direct pour améliorer le service',
        'mobile_menu_aria': 'Ouvrir le Menu Principal',
        'menu_text': 'Menu',
        'dock_launchpad_tooltip': 'Les 29 Langues (Launchpad)',
        'nav_services': 'Services & Systèmes',
        'nav_pricing': 'Tarifs & Forfaits',
        'nav_software': 'Centre Logiciel',
        'nav_about': 'À Propos & Leadership',
        'nav_resources': 'Ressources & ROI',
        'nav_roi': 'Calculateur de ROI',
        'nav_faq': 'FAQ',
        'nav_blog': 'Blog Tech',
        'nav_api': 'Documentation API'
    },
    'es': {
        'brand_title': 'S&R CoreSync For Intelligent Solutions - Haga clic para ver la identidad de marca completa',
        'brand_aria': 'Marca oficial de S&R CoreSync For Intelligent Solutions',
        'nav_more_aria': 'Más enlaces y secciones',
        'nav_res_aria': 'Recursos y secciones adicionales',
        'pwa_title': 'Instale S&R CoreSync como aplicación independiente en su dispositivo',
        'support_tools_title': 'Herramientas de Soporte Empresarial y Evaluación',
        'support_tools_aria': 'Herramientas de soporte y simulación',
        'interactive_services': 'Servicios Interactivos en Vivo',
        'readiness_strong': 'Evaluación de Preparación Digital 🎯',
        'readiness_span': 'Evalúe la madurez de la infraestructura en la nube y automatización',
        'consultation_strong': 'Reservar Consulta Ejecutiva 👔',
        'consultation_span': 'Agende una reunión estratégica con los fundadores',
        'feedback_strong': 'Calificación de Experiencia y Comentarios 💬',
        'feedback_span': 'Envíe comentarios directos para mejorar y desarrollar el servicio',
        'mobile_menu_aria': 'Abrir menú principal',
        'menu_text': 'Menú',
        'dock_launchpad_tooltip': 'Los 29 Idiomas (Launchpad)',
        'nav_services': 'Servicios y Sistemas',
        'nav_pricing': 'Precios y Planes',
        'nav_software': 'Centro de Software',
        'nav_about': 'Sobre Nosotros y Liderazgo',
        'nav_resources': 'Recursos y ROI',
        'nav_roi': 'Calculadora de ROI',
        'nav_faq': 'Preguntas Frecuentes',
        'nav_blog': 'Blog de Tecnología',
        'nav_api': 'Documentación de API'
    },
    'it': {
        'brand_title': 'S&R CoreSync For Intelligent Solutions - Clicca per visualizzare l\'identità completa del marchio',
        'brand_aria': 'Marchio ufficiale di S&R CoreSync For Intelligent Solutions',
        'nav_more_aria': 'Ulteriori link e sezioni',
        'nav_res_aria': 'Risorse e sezioni aggiuntive',
        'pwa_title': 'Installa S&R CoreSync come app autonoma sul tuo dispositivo',
        'support_tools_title': 'Strumenti di Supporto Aziendale e Valutazione',
        'support_tools_aria': 'Strumenti di supporto e simulazione',
        'interactive_services': 'Servizi Interattivi dal Vivo',
        'readiness_strong': 'Verifica Prontezza Digitale 🎯',
        'readiness_span': 'Valuta la maturità dell\'infrastruttura cloud e dell\'automazione',
        'consultation_strong': 'Prenota Consulenza Direzionale 👔',
        'consultation_span': 'Pianifica un incontro strategico con i fondatori',
        'feedback_strong': 'Valutazione Esperienza e Feedback 💬',
        'feedback_span': 'Invia feedback diretto per migliorare il servizio',
        'mobile_menu_aria': 'Apri menu principale',
        'menu_text': 'Menu',
        'dock_launchpad_tooltip': 'Tutte le 29 Lingue (Launchpad)',
        'nav_services': 'Servizi e Sistemi',
        'nav_pricing': 'Prezzi e Piani',
        'nav_software': 'Software Hub',
        'nav_about': 'Chi Siamo e Leadership',
        'nav_resources': 'Risorse e ROI',
        'nav_roi': 'Calcolatore ROI',
        'nav_faq': 'FAQ',
        'nav_blog': 'Blog Tecnologico',
        'nav_api': 'Documentazione API'
    }
}

def get_trans(lang):
    t = EN_BASE.copy()
    if lang in CUSTOM:
        t.update(CUSTOM[lang])
    return t

def cleanse_page(lang):
    p = os.path.join(ROOT, lang, 'index.html')
    if not os.path.exists(p):
        return
    s = open(p, encoding='utf-8').read()
    t = get_trans(lang)

    # 1. Clean brand logo link
    s = re.sub(
        r'title="S&R CoreSync For Intelligent Solutions - انقر لعرض الهوية البصرية والشعار بالكامل"',
        f'title="{t["brand_title"]}"',
        s
    )
    s = re.sub(
        r'aria-label="عرض شعار S&R CoreSync For Intelligent Solutions بدقة فائقة"',
        f'aria-label="{t["brand_aria"]}"',
        s
    )

    # 2. Clean Nav More button and menu
    s = re.sub(
        r'aria-label="المزيد من الروابط والأقسام"',
        f'aria-label="{t["nav_more_aria"]}"',
        s
    )
    s = re.sub(
        r'aria-label="روابط الموارد والأقسام الإضافية"',
        f'aria-label="{t["nav_res_aria"]}"',
        s
    )

    # 3. Clean PWA install button title
    s = re.sub(
        r'title="تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك"',
        f'title="{t["pwa_title"]}"',
        s
    )

    # 4. Clean Support Tools button and menu
    s = re.sub(
        r'title="Support Tools والتقييم المؤسسي"',
        f'title="{t["support_tools_title"]}"',
        s
    )
    s = re.sub(
        r'aria-label="Support Tools والمحاكاة"',
        f'aria-label="{t["support_tools_aria"]}"',
        s
    )
    s = re.sub(
        r'<span>الخدمات التفاعلية المباشرة</span>',
        f'<span>{t["interactive_services"]}</span>',
        s
    )
    s = re.sub(
        r'<strong>فحص الجاهزية الرقمية 🎯</strong>',
        f'<strong>{t["readiness_strong"]}</strong>',
        s
    )
    s = re.sub(
        r'<span>تقييم نضج البنية السحابية والأتمتة</span>',
        f'<span>{t["readiness_span"]}</span>',
        s
    )
    s = re.sub(
        r'<strong>جدولة استشارة تنفيذية 👔</strong>',
        f'<strong>{t["consultation_strong"]}</strong>',
        s
    )
    s = re.sub(
        r'<span>حجز موعد استراتيجي مع المؤسسين</span>',
        f'<span>{t["consultation_span"]}</span>',
        s
    )
    s = re.sub(
        r'<strong>تقييم وملاحظات التجربة 💬</strong>',
        f'<strong>{t["feedback_strong"]}</strong>',
        s
    )
    s = re.sub(
        r'<span>إرسال تقييم مباشر لتحسين وتطوير الخدمة</span>',
        f'<span>{t["feedback_span"]}</span>',
        s
    )

    # 5. Clean Mobile Menu button
    s = re.sub(
        r'aria-label="فتح القائمة الرئيسية"',
        f'aria-label="{t["mobile_menu_aria"]}"',
        s
    )
    s = re.sub(
        r'<span>القائمة</span>',
        f'<span>{t["menu_text"]}</span>',
        s
    )

    # 6. Clean Apple Dock Launchpad button tooltip
    s = re.sub(
        r'data-tooltip="جميع اللغات الـ 29 \(Launchpad\)"',
        f'data-tooltip="{t["dock_launchpad_tooltip"]}"',
        s
    )

    # 7. Remove Arabic comments in header
    s = re.sub(r'<!-- 1\. الشعار الرسمي للشركة -->', '<!-- 1. Official Corporate Emblem -->', s)
    s = re.sub(r'<!-- 2\. روابط القائمة الرئيسية للشاشات الكبيرة -->', '<!-- 2. Main Navigation Links -->', s)
    s = re.sub(r'<!-- 3\. أدوات الاتصال السريع وتغيير اللغة وقائمة الهاتف \(مرتبة LTR بأناقة مطلقة\) -->', '<!-- 3. Header Action Utilities -->', s)
    s = re.sub(r'<!-- Support Tools المؤسسي والتقييم \(Header Support Tools Dropdown\) -->', '<!-- Enterprise Support Tools Dropdown -->', s)

    # If TR, update the 5 nav items into Turkish as well
    if lang == 'tr':
        s = s.replace('>Services & Systems<', f'>{t["nav_services"]}<')
        s = s.replace('>Pricing & Plans<', f'>{t["nav_pricing"]}<')
        s = s.replace('>Software Hub<', f'>{t["nav_software"]}<')
        s = s.replace('>About & Leadership<', f'>{t["nav_about"]}<')
        s = s.replace('<span>Resources & ROI</span>', f'<span>{t["nav_resources"]}</span>')
        s = s.replace('>ROI Calculator<', f'>{t["nav_roi"]}<')
        s = s.replace('>FAQ<', f'>{t["nav_faq"]}<')
        s = s.replace('>Tech Blog<', f'>{t["nav_blog"]}<')
        s = s.replace('>API Docs<', f'>{t["nav_api"]}<')

    open(p, 'w', encoding='utf-8').write(s)
    print(f'Cleaned header and chrome for: {lang}')

def main():
    langs = [d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)) and os.path.exists(os.path.join(ROOT, d, 'index.html')) and d not in ['.git', 'node_modules', '_site', '.venv', 'partials', 'scratch']]
    for lang in sorted(langs):
        if lang not in ['ckb']:  # ckb uses Arabic Kurdish script legitimately
            cleanse_page(lang)

    # Also clean partials/en/10-header.html
    en_hdr_path = os.path.join(ROOT, 'partials', 'en', '10-header.html')
    if os.path.exists(en_hdr_path):
        s = open(en_hdr_path, encoding='utf-8').read()
        t = EN_BASE
        s = re.sub(r'title="S&R CoreSync For Intelligent Solutions - انقر لعرض الهوية البصرية والشعار بالكامل"', f'title="{t["brand_title"]}"', s)
        s = re.sub(r'aria-label="عرض شعار S&R CoreSync For Intelligent Solutions بدقة فائقة"', f'aria-label="{t["brand_aria"]}"', s)
        s = re.sub(r'aria-label="المزيد من الروابط والأقسام"', f'aria-label="{t["nav_more_aria"]}"', s)
        s = re.sub(r'aria-label="روابط الموارد والأقسام الإضافية"', f'aria-label="{t["nav_res_aria"]}"', s)
        s = re.sub(r'title="تثبيت S&amp;R CoreSync كتطبيق مستقل على جهازك"', f'title="{t["pwa_title"]}"', s)
        s = re.sub(r'title="Support Tools والتقييم المؤسسي"', f'title="{t["support_tools_title"]}"', s)
        s = re.sub(r'aria-label="Support Tools والمحاكاة"', f'aria-label="{t["support_tools_aria"]}"', s)
        s = re.sub(r'<span>الخدمات التفاعلية المباشرة</span>', f'<span>{t["interactive_services"]}</span>', s)
        s = re.sub(r'<strong>فحص الجاهزية الرقمية 🎯</strong>', f'<strong>{t["readiness_strong"]}</strong>', s)
        s = re.sub(r'<span>تقييم نضج البنية السحابية والأتمتة</span>', f'<span>{t["readiness_span"]}</span>', s)
        s = re.sub(r'<strong>جدولة استشارة تنفيذية 👔</strong>', f'<strong>{t["consultation_strong"]}</strong>', s)
        s = re.sub(r'<span>حجز موعد استراتيجي مع المؤسسين</span>', f'<span>{t["consultation_span"]}</span>', s)
        s = re.sub(r'<strong>تقييم وملاحظات التجربة 💬</strong>', f'<strong>{t["feedback_strong"]}</strong>', s)
        s = re.sub(r'<span>إرسال تقييم مباشر لتحسين وتطوير الخدمة</span>', f'<span>{t["feedback_span"]}</span>', s)
        s = re.sub(r'aria-label="فتح القائمة الرئيسية"', f'aria-label="{t["mobile_menu_aria"]}"', s)
        s = re.sub(r'<span>القائمة</span>', f'<span>{t["menu_text"]}</span>', s)
        s = re.sub(r'<!-- 1\. الشعار الرسمي للشركة -->', '<!-- 1. Official Corporate Emblem -->', s)
        s = re.sub(r'<!-- 2\. روابط القائمة الرئيسية للشاشات الكبيرة -->', '<!-- 2. Main Navigation Links -->', s)
        s = re.sub(r'<!-- 3\. أدوات الاتصال السريع وتغيير اللغة وقائمة الهاتف \(مرتبة LTR بأناقة مطلقة\) -->', '<!-- 3. Header Action Utilities -->', s)
        s = re.sub(r'<!-- Support Tools المؤسسي والتقييم \(Header Support Tools Dropdown\) -->', '<!-- Enterprise Support Tools Dropdown -->', s)
        open(en_hdr_path, 'w', encoding='utf-8').write(s)
        print('Cleaned partials/en/10-header.html')

if __name__ == '__main__':
    main()
