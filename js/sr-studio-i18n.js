/**
 * S&R CoreSync - Sovereign Multi-Language Studio i18n Engine
 * Supports 29 Sovereign Languages with Dynamic In-Place Translation,
 * Direction Switching (RTL / LTR), and Apple macOS Launchpad Modal.
 */
(function() {
    'use strict';

    var STORAGE_KEY = 'sr_lang_pref';
    var SESSION_KEY = 'sr_user_lang_locked';

    var LANGUAGES = [
        { code: 'ar', name: 'العربية', nameEn: 'Arabic (HQ Master)', flag: './assets/flags/sa.png', emoji: '🇸🇦', dir: 'rtl', vat: '0% / 15%' },
        { code: 'en', name: 'English', nameEn: 'English (UK / Global)', flag: './assets/flags/gb.png', emoji: '🇬🇧', dir: 'ltr', vat: '20%' },
        { code: 'nl', name: 'Nederlands', nameEn: 'Dutch (HQ Amsterdam)', flag: './assets/flags/nl.png', emoji: '🇳🇱', dir: 'ltr', vat: '21%' },
        { code: 'de', name: 'Deutsch', nameEn: 'German', flag: './assets/flags/de.png', emoji: '🇩🇪', dir: 'ltr', vat: '19%' },
        { code: 'fr', name: 'Français', nameEn: 'French', flag: './assets/flags/fr.png', emoji: '🇫🇷', dir: 'ltr', vat: '20%' },
        { code: 'es', name: 'Español', nameEn: 'Spanish', flag: './assets/flags/es.png', emoji: '🇪🇸', dir: 'ltr', vat: '21%' },
        { code: 'tr', name: 'Türkçe', nameEn: 'Turkish', flag: './assets/flags/tr.png', emoji: '🇹🇷', dir: 'ltr', vat: '20%' },
        { code: 'it', name: 'Italiano', nameEn: 'Italian', flag: './assets/flags/it.png', emoji: '🇮🇹', dir: 'ltr', vat: '22%' },
        { code: 'sv', name: 'Svenska', nameEn: 'Swedish', flag: './assets/flags/se.png', emoji: '🇸🇪', dir: 'ltr', vat: '25%' },
        { code: 'no', name: 'Norsk', nameEn: 'Norwegian', flag: './assets/flags/no.png', emoji: '🇳🇴', dir: 'ltr', vat: '25%' },
        { code: 'da', name: 'Dansk', nameEn: 'Danish', flag: './assets/flags/dk.png', emoji: '🇩🇰', dir: 'ltr', vat: '25%' },
        { code: 'fi', name: 'Suomi', nameEn: 'Finnish', flag: './assets/flags/fi.png', emoji: '🇫🇮', dir: 'ltr', vat: '25.5%' },
        { code: 'pl', name: 'Polski', nameEn: 'Polish', flag: './assets/flags/pl.png', emoji: '🇵🇱', dir: 'ltr', vat: '23%' },
        { code: 'pt', name: 'Português', nameEn: 'Portuguese', flag: './assets/flags/pt.png', emoji: '🇵🇹', dir: 'ltr', vat: '23%' },
        { code: 'el', name: 'Ελληνικά', nameEn: 'Greek', flag: './assets/flags/gr.png', emoji: '🇬🇷', dir: 'ltr', vat: '24%' },
        { code: 'cs', name: 'Čeština', nameEn: 'Czech', flag: './assets/flags/cz.png', emoji: '🇨🇿', dir: 'ltr', vat: '21%' },
        { code: 'ro', name: 'Română', nameEn: 'Romanian', flag: './assets/flags/ro.png', emoji: '🇷🇴', dir: 'ltr', vat: '19%' },
        { code: 'hu', name: 'Magyar', nameEn: 'Hungarian', flag: './assets/flags/hu.png', emoji: '🇭🇺', dir: 'ltr', vat: '27%' },
        { code: 'bg', name: 'Български', nameEn: 'Bulgarian', flag: './assets/flags/bg.png', emoji: '🇧🇬', dir: 'ltr', vat: '20%' },
        { code: 'sk', name: 'Slovenčina', nameEn: 'Slovak', flag: './assets/flags/sk.png', emoji: '🇸🇰', dir: 'ltr', vat: '20%' },
        { code: 'hr', name: 'Hrvatski', nameEn: 'Croatian', flag: './assets/flags/hr.png', emoji: '🇭🇷', dir: 'ltr', vat: '25%' },
        { code: 'lt', name: 'Lietuvių', nameEn: 'Lithuanian', flag: './assets/flags/lt.png', emoji: '🇱🇹', dir: 'ltr', vat: '21%' },
        { code: 'sl', name: 'Slovenščina', nameEn: 'Slovenian', flag: './assets/flags/si.png', emoji: '🇸🇮', dir: 'ltr', vat: '22%' },
        { code: 'lv', name: 'Latviešu', nameEn: 'Latvian', flag: './assets/flags/lv.png', emoji: '🇱🇻', dir: 'ltr', vat: '21%' },
        { code: 'et', name: 'Eesti', nameEn: 'Estonian', flag: './assets/flags/ee.png', emoji: '🇪🇪', dir: 'ltr', vat: '22%' },
        { code: 'ga', name: 'Gaeilge', nameEn: 'Irish', flag: './assets/flags/ie.png', emoji: '🇮🇪', dir: 'ltr', vat: '23%' },
        { code: 'mt', name: 'Malti', nameEn: 'Maltese', flag: './assets/flags/mt.png', emoji: '🇲🇹', dir: 'ltr', vat: '18%' },
        { code: 'ku', name: 'Kurdî', nameEn: 'Kurdish', flag: './assets/flags/ku.png', emoji: '🏳️', dir: 'rtl', vat: 'Exempt' },
        { code: 'ckb', name: 'سۆرانی', nameEn: 'Sorani', flag: './assets/flags/ku.png', emoji: '🏳️', dir: 'rtl', vat: 'Exempt' }
    ];

    var TRANSLATIONS = {
        ar: {
            nav_home: "الرئيسية 🏠",
            nav_matrix: "مصفوفة المقارنات ⚖️",
            nav_lottie: "استوديو Lottie ✨",
            nav_perf: "فاحص الأداء ⚡",
            nav_qr: "QR ذكي 📲",
            brand_title: "S&R CoreSync",
            brand_subtitle: "المنظومة السحابية السيادية للحلول الذكية",
            // Tech Matrix
            tm_badge: "⚖️ استوديو المقارنات السيادية • Interactive Tech Comparison Matrix",
            tm_title: "مصفوفة المقارنات الفنية والتقنية للأنظمة والباقات",
            tm_desc: "استوديو ديناميكي عالي التحويل لمقارنة الحلول السحابية ومنظومات الـ AI والباقات المؤسسية، مع إمكانية فرز الميزات، تمييز الفروقات بنقرة واحدة، وحساب العائد الاستثماري (ROI).",
            tm_filter_label: "فلترة حسب حجم المؤسسة:",
            tm_opt_all: "كافة الباقات والحلول (الكل)",
            tm_opt_startup: "شركات ناشئة ورواد أعمال (Starter)",
            tm_opt_mid: "شركات نامية ومتوسطة (Business)",
            tm_opt_enterprise: "مؤسسات وهيئات سيادية (Enterprise)",
            tm_btn_diff: "🔍 تمييز الفروقات فقط",
            tm_btn_social: "📢 بطاقة المشاركة الاجتماعية",
            tm_btn_advisor: "🤖 مستشار الـ AI للباقات",
            tm_btn_pdf: "📄 تصدير تقرير المقارنة كـ PDF",
            tm_roi_title: "حاسبة التوفير السنوي والجدوى الاستثمارية (Estimated Annual ROI):",
            tm_roi_sub: "مقارنةً بالأنظمة التقليدية وتكاليف البرمجة والصيانة المنفصلة",
            tm_roi_val: "€ 14,800 / سنوياً",
            // Lottie Studio
            lt_badge: "✨ استوديو الرسوم المتحركة • Lottie & Micro-Interactions Studio",
            lt_title: "محرر واستوديو الرسوم المتحركة التفاعلية والتفاعلات الدقيقة",
            lt_desc: "بيئة تصميم وتجربة تفاعلية لمحاكاة وتعديل رسوم Lottie الدقيقة المعتمدة على الويب، مع إمكانية ضبط السرعة، الألوان، الاتجاه، وتصدير كود CSS Keyframes فوري.",
            lt_anim_label: "الرسم التفاعلي:",
            lt_speed_label: "سرعة الحركة:",
            lt_color_label: "لون التوهج:",
            lt_btn_play: "▶ تشغيل",
            lt_btn_pause: "⏸ إيقاف مؤقت",
            lt_btn_reverse: "⇄ عكس الاتجاه",
            lt_btn_social: "📢 بطاقة المشاركة الاجتماعية",
            lt_btn_json: "💾 تحميل ملف JSON",
            lt_btn_css: "🎨 نسخ كود CSS Keyframes",
            // Perf Audit
            pf_badge: "⚡ استوديو فحص الأداء • Web Performance & Speed Audit Studio",
            pf_title: "استوديو التدقيق الحي لسرعة وأداء الويب ومؤشرات Core Web Vitals",
            pf_desc: "أداة تشخيص سيادية لفحص مقاييس تجربة المستخدم المعتمدة من Google (LCP, FID/INP, CLS, TTFB) بدقة مع عدادات Canvas حية وتقرير توصيات فوري.",
            pf_input_placeholder: "أدخل عنوان الرابط أو اتركه فارغاً لفحص الصفحة الحالية...",
            pf_btn_run: "⚡ بدء الفحص التشخيصي الفوري",
            pf_btn_social: "📢 بطاقة المشاركة الاجتماعية",
            pf_btn_pdf: "📄 استخراج تقرير الأداء PDF",
            pf_overall: "درجة الأداء الإجمالية (Performance Score)",
            pf_speed_desc: "السرعة وتجربة المستخدم العامة"
        },
        en: {
            nav_home: "Home 🏠",
            nav_matrix: "Tech Matrix ⚖️",
            nav_lottie: "Lottie Studio ✨",
            nav_perf: "Performance Audit ⚡",
            nav_qr: "Dynamic QR 📲",
            brand_title: "S&R CoreSync",
            brand_subtitle: "Sovereign Cloud Ecosystem for Intelligent Solutions",
            // Tech Matrix
            tm_badge: "⚖️ Sovereign Comparison Studio • Interactive Tech Comparison Matrix",
            tm_title: "Technical Comparison Matrix for Systems & Packages",
            tm_desc: "High-conversion dynamic studio to compare cloud solutions, AI platforms, and enterprise suites, featuring instant feature sorting, one-click difference highlighting, and ROI estimation.",
            tm_filter_label: "Filter by Organization Size:",
            tm_opt_all: "All Tiers and Solutions (All)",
            tm_opt_startup: "Startups & Entrepreneurs (Starter)",
            tm_opt_mid: "Mid-Market & Scaling (Business)",
            tm_opt_enterprise: "Sovereign & Enterprise (Enterprise)",
            tm_btn_diff: "🔍 Highlight Differences",
            tm_btn_social: "📢 Share Social Card",
            tm_btn_advisor: "🤖 AI Package Advisor",
            tm_btn_pdf: "📄 Export Matrix as PDF",
            tm_roi_title: "Estimated Annual ROI & Cost Efficiency Calculator:",
            tm_roi_sub: "Compared against legacy systems and disjointed maintenance fees",
            tm_roi_val: "€ 14,800 / year",
            // Lottie Studio
            lt_badge: "✨ Micro-Interactions Studio • Lottie & Animations Studio",
            lt_title: "Interactive Lottie & Micro-Interactions Design Studio",
            lt_desc: "Real-time design playground to simulate, customize, and inspect web-native Lottie animations with live speed, color tinting, playback reversal, and instant CSS Keyframes export.",
            lt_anim_label: "Interactive Preset:",
            lt_speed_label: "Playback Speed:",
            lt_color_label: "Glow Color:",
            lt_btn_play: "▶ Play",
            lt_btn_pause: "⏸ Pause",
            lt_btn_reverse: "⇄ Reverse",
            lt_btn_social: "📢 Share Social Card",
            lt_btn_json: "💾 Download JSON",
            lt_btn_css: "🎨 Copy CSS Keyframes",
            // Perf Audit
            pf_badge: "⚡ Performance Audit Studio • Web Speed & Core Web Vitals",
            pf_title: "Live Web Performance Audit & Core Web Vitals Studio",
            pf_desc: "Sovereign diagnostic lab measuring Google-certified user experience metrics (LCP, FID/INP, CLS, TTFB) featuring live neon canvas gauges and executive recommendations.",
            pf_input_placeholder: "Enter URL or leave blank to audit current session...",
            pf_btn_run: "⚡ Run Instant Audit",
            pf_btn_social: "📢 Share Social Card",
            pf_btn_pdf: "📄 Export Audit as PDF",
            pf_overall: "Overall Performance Score",
            pf_speed_desc: "Speed & Real User Experience"
        },
        nl: {
            nav_home: "Home 🏠",
            nav_matrix: "Vergelijkingsmatrix ⚖️",
            nav_lottie: "Lottie Studio ✨",
            nav_perf: "Prestatie-audit ⚡",
            nav_qr: "Slimme QR 📲",
            brand_title: "S&R CoreSync",
            brand_subtitle: "Soeverein Cloud Ecosysteem voor Intelligente Oplossingen",
            // Tech Matrix
            tm_badge: "⚖️ Soevereine Studio • Interactieve Technologie Vergelijkingsmatrix",
            tm_title: "Technische Vergelijkingsmatrix voor Systemen en Pakketten",
            tm_desc: "Dynamische studio om cloudoplossingen, AI-platforms en enterprise-suites te vergelijken, met functiesortering, verschilmarkering en ROI-berekening.",
            tm_filter_label: "Filter op Organisatiegrootte:",
            tm_opt_all: "Alle Pakketten en Oplossingen (Alles)",
            tm_opt_startup: "Startups & Ondernemers (Starter)",
            tm_opt_mid: "Middelgroot & Groeiend (Business)",
            tm_opt_enterprise: "Grote Ondernemingen (Enterprise)",
            tm_btn_diff: "🔍 Alleen Verschillen Tonen",
            tm_btn_social: "📢 Sociale Kaart Delen",
            tm_btn_advisor: "🤖 AI Pakketadviseur",
            tm_btn_pdf: "📄 Matrix Exporteren als PDF",
            tm_roi_title: "Geschatte Jaarlijkse ROI & Kostenbesparing:",
            tm_roi_sub: "Vergeleken met verouderde systemen en losse onderhoudscontracten",
            tm_roi_val: "€ 14.800 / per jaar",
            // Lottie Studio
            lt_badge: "✨ Micro-interacties Studio • Lottie & Animaties Studio",
            lt_title: "Interactieve Lottie & Micro-interacties Ontwerpstudio",
            lt_desc: "Realtime ontwerpomgeving om web-native Lottie-animaties te simuleren, met snelheidsregeling, kleurtinten en directe CSS-export.",
            lt_anim_label: "Preset Selecteren:",
            lt_speed_label: "Afspeelsnelheid:",
            lt_color_label: "Gloeikleur:",
            lt_btn_play: "▶ Afspelen",
            lt_btn_pause: "⏸ Pauze",
            lt_btn_reverse: "⇄ Omkeren",
            lt_btn_social: "📢 Sociale Kaart Delen",
            lt_btn_json: "💾 JSON Downloaden",
            lt_btn_css: "🎨 CSS Keyframes Kopiëren",
            // Perf Audit
            pf_badge: "⚡ Prestatie-audit Studio • Web Speed & Core Web Vitals",
            pf_title: "Live Webprestatie-audit & Core Web Vitals Studio",
            pf_desc: "Diagnostisch laboratorium dat officiële gebruikerservaring meet (LCP, FID/INP, CLS, TTFB) met neon canvas meters en auditrapport.",
            pf_input_placeholder: "Voer URL in of laat leeg voor huidige sessie...",
            pf_btn_run: "⚡ Start Diagnostische Audit",
            pf_btn_social: "📢 Sociale Kaart Delen",
            pf_btn_pdf: "📄 Prestatierapport PDF",
            pf_overall: "Totale Prestatiescore",
            pf_speed_desc: "Snelheid & Gebruikerservaring"
        },
        de: {
            nav_home: "Startseite 🏠",
            nav_matrix: "Vergleichsmatrix ⚖️",
            nav_lottie: "Lottie Studio ✨",
            nav_perf: "Geschwindigkeitsprüfung ⚡",
            nav_qr: "Dynamischer QR 📲",
            brand_title: "S&R CoreSync",
            brand_subtitle: "Souveränes Cloud-Ökosystem für Intelligente Lösungen",
            tm_badge: "⚖️ Vergleichsstudio • Interaktive Technologie-Vergleichsmatrix",
            tm_title: "Technische Vergleichsmatrix für Systeme & Pakete",
            tm_desc: "Dynamisches Studio zum Vergleich von Cloud-Lösungen, KI-Plattformen und Enterprise-Paketen mit ROI-Kalkulator.",
            tm_filter_label: "Nach Unternehmensgröße filtern:",
            tm_opt_all: "Alle Pakete & Lösungen (Alle)",
            tm_opt_startup: "Startups & Gründer (Starter)",
            tm_opt_mid: "Mittelstand & Wachstum (Business)",
            tm_opt_enterprise: "Großunternehmen (Enterprise)",
            tm_btn_diff: "🔍 Nur Unterschiede hervorheben",
            tm_btn_social: "📢 Social Card teilen",
            tm_btn_advisor: "🤖 KI-Paketberater",
            tm_btn_pdf: "📄 Matrix als PDF exportieren",
            tm_roi_title: "Geschätzter jährlicher ROI und Kostenvorteil:",
            tm_roi_sub: "Im Vergleich zu Altsystemen und getrennter Softwarewartung",
            tm_roi_val: "€ 14.800 / jährlich",
            lt_badge: "✨ Animations-Studio • Lottie & Micro-Interactions Studio",
            lt_title: "Interaktives Lottie & Animations-Design-Studio",
            lt_desc: "Design-Umgebung zur Simulation und Anpassung von Lottie-Webanimationen mit Keyframe-Export.",
            lt_anim_label: "Vorlage wählen:",
            lt_speed_label: "Geschwindigkeit:",
            lt_color_label: "Farbe:",
            lt_btn_play: "▶ Abspielen",
            lt_btn_pause: "⏸ Pause",
            lt_btn_reverse: "⇄ Richtung umkehren",
            lt_btn_social: "📢 Social Card teilen",
            lt_btn_json: "💾 JSON herunterladen",
            lt_btn_css: "🎨 CSS Keyframes kopieren",
            pf_badge: "⚡ Geschwindigkeitsprüfung • Web Speed & Core Web Vitals",
            pf_title: "Live Web-Performance-Audit & Core Web Vitals Studio",
            pf_desc: "Diagnoselabor zur Messung offizieller Google-Kennzahlen (LCP, FID/INP, CLS, TTFB) mit Neon-Canvas-Anzeigen.",
            pf_input_placeholder: "URL eingeben oder leer lassen für aktuelle Seite...",
            pf_btn_run: "⚡ Sofortprüfung starten",
            pf_btn_social: "📢 Social Card teilen",
            pf_btn_pdf: "📄 Prüfbericht als PDF",
            pf_overall: "Gesamtleistungspunktzahl",
            pf_speed_desc: "Geschwindigkeit & Nutzererlebnis"
        },
        fr: {
            nav_home: "Accueil 🏠",
            nav_matrix: "Matrice Comparatif ⚖️",
            nav_lottie: "Studio Lottie ✨",
            nav_perf: "Audit Performance ⚡",
            nav_qr: "QR Dynamique 📲",
            brand_title: "S&R CoreSync",
            brand_subtitle: "Écosystème Cloud Souverain pour Solutions Intelligentes",
            tm_badge: "⚖️ Studio de Comparaison • Matrice Technique Interactive",
            tm_title: "Matrice de Comparaison Technique des Systèmes & Forfaits",
            tm_desc: "Studio interactif pour comparer les solutions cloud, IA et suites d'entreprise avec calcul du retour sur investissement (ROI).",
            tm_filter_label: "Filtrer selon la taille:",
            tm_opt_all: "Tous les forfaits et solutions (Tous)",
            tm_opt_startup: "Startups & PME (Starter)",
            tm_opt_mid: "Entreprises en croissance (Business)",
            tm_opt_enterprise: "Grandes entreprises souveraines (Enterprise)",
            tm_btn_diff: "🔍 Afficher les différences",
            tm_btn_social: "📢 Carte Réseaux Sociaux",
            tm_btn_advisor: "🤖 Conseiller IA Forfaits",
            tm_btn_pdf: "📄 Exporter en PDF",
            tm_roi_title: "Estimation du ROI Annuel & Économies Réalisées :",
            tm_roi_sub: "Comparé aux architectures traditionnelles et coûts de maintenance tiers",
            tm_roi_val: "14 800 € / an",
            lt_badge: "✨ Studio Animations • Lottie & Micro-Interactions",
            lt_title: "Studio Interactif d'Animations Lottie et Micro-Interactions",
            lt_desc: "Atelier interactif de simulation et personnalisation d'animations web Lottie avec export instantané CSS.",
            lt_anim_label: "Modèle d'animation :",
            lt_speed_label: "Vitesse :",
            lt_color_label: "Couleur néon :",
            lt_btn_play: "▶ Lecture",
            lt_btn_pause: "⏸ Pause",
            lt_btn_reverse: "⇄ Inverser",
            lt_btn_social: "📢 Carte Réseaux Sociaux",
            lt_btn_json: "💾 Télécharger JSON",
            lt_btn_css: "🎨 Copier CSS Keyframes",
            pf_badge: "⚡ Studio d'Audit • Web Performance & Core Web Vitals",
            pf_title: "Audit de Performance Web en Direct & Core Web Vitals",
            pf_desc: "Outil de diagnostic haute précision pour mesurer LCP, FID/INP, CLS, TTFB avec jauges visuelles dynamiques.",
            pf_input_placeholder: "Entrez l'URL ou laissez vide pour la page actuelle...",
            pf_btn_run: "⚡ Lancer le Diagnostic Immédiat",
            pf_btn_social: "📢 Carte Réseaux Sociaux",
            pf_btn_pdf: "📄 Rapport PDF Officiel",
            pf_overall: "Score Global de Performance",
            pf_speed_desc: "Vitesse et Expérience Utilisateur"
        }
    };

    function getCurrentLanguage() {
        var urlParams = new URLSearchParams(window.location.search);
        var urlLang = urlParams.get('lang');
        if (urlLang) return urlLang.toLowerCase();

        try {
            var stored = localStorage.getItem(STORAGE_KEY);
            if (stored) return stored.toLowerCase();
        } catch (e) {}

        var docLang = (document.documentElement.getAttribute('lang') || 'ar').toLowerCase();
        return docLang;
    }

    function getLangConfig(code) {
        for (var i = 0; i < LANGUAGES.length; i++) {
            if (LANGUAGES[i].code === code) return LANGUAGES[i];
        }
        return LANGUAGES[0]; // fallback Arabic
    }

    function applyLanguage(code) {
        var cfg = getLangConfig(code);
        var dict = TRANSLATIONS[code] || TRANSLATIONS.en || TRANSLATIONS.ar;

        document.documentElement.lang = cfg.code;
        document.documentElement.dir = cfg.dir;

        try {
            localStorage.setItem(STORAGE_KEY, cfg.code);
            sessionStorage.setItem(SESSION_KEY, cfg.code);
        } catch (e) {}

        // 1. Update Navigation Links
        var navLinks = document.querySelectorAll('.studio-nav-links a');
        if (navLinks.length >= 4 && dict.nav_home) {
            navLinks[0].textContent = dict.nav_home;
            navLinks[1].textContent = dict.nav_matrix;
            navLinks[2].textContent = dict.nav_lottie;
            navLinks[3].textContent = dict.nav_perf;
            if (navLinks[4] && dict.nav_qr) navLinks[4].textContent = dict.nav_qr;
        }

        // 2. Update Brand
        var brandSub = document.querySelector('.brand-text span');
        if (brandSub && dict.brand_subtitle) {
            brandSub.textContent = dict.brand_subtitle;
        }

        // 3. Tech Matrix page
        var tmBadge = document.querySelector('.hero-badge');
        var tmTitle = document.querySelector('.matrix-title');
        var tmDesc = document.querySelector('.matrix-desc');
        var tmFilterLabel = document.querySelector('.filter-label');
        var sizeFilter = document.getElementById('sizeFilter');
        var btnDiff = document.getElementById('btnDiff');
        var btnExportPdf = document.querySelector('.btn-export-matrix');
        var roiTitle = document.querySelector('.savings-info strong');
        var roiSub = document.querySelector('.savings-info span');
        var roiVal = document.getElementById('costSavings');

        if (tmTitle && dict.tm_title) {
            if (tmBadge && dict.tm_badge) tmBadge.textContent = dict.tm_badge;
            tmTitle.textContent = dict.tm_title;
            if (tmDesc && dict.tm_desc) tmDesc.textContent = dict.tm_desc;
            if (tmFilterLabel && dict.tm_filter_label) tmFilterLabel.textContent = dict.tm_filter_label;
            if (btnDiff && dict.tm_btn_diff) btnDiff.textContent = dict.tm_btn_diff;
            if (btnExportPdf && dict.tm_btn_pdf) btnExportPdf.textContent = dict.tm_btn_pdf;
            if (roiTitle && dict.tm_roi_title) roiTitle.textContent = dict.tm_roi_title;
            if (roiSub && dict.tm_roi_sub) roiSub.textContent = dict.tm_roi_sub;
            if (roiVal && dict.tm_roi_val) roiVal.textContent = dict.tm_roi_val;

            if (sizeFilter && sizeFilter.options && sizeFilter.options.length >= 4) {
                sizeFilter.options[0].text = dict.tm_opt_all || sizeFilter.options[0].text;
                sizeFilter.options[1].text = dict.tm_opt_startup || sizeFilter.options[1].text;
                sizeFilter.options[2].text = dict.tm_opt_mid || sizeFilter.options[2].text;
                sizeFilter.options[3].text = dict.tm_opt_enterprise || sizeFilter.options[3].text;
            }
        }

        // 4. Lottie Studio page
        var ltBadge = document.querySelector('.lottie-badge');
        var ltTitle = document.querySelector('.lottie-title');
        var ltDesc = document.querySelector('.lottie-desc');
        var btnPlay = document.getElementById('btnPlay');
        var btnReverse = document.getElementById('btnReverse');
        var btnExportJson = document.getElementById('btnExportJson');
        var btnExportCss = document.getElementById('btnExportCss');

        if (ltTitle && dict.lt_title) {
            if (ltBadge && dict.lt_badge) ltBadge.textContent = dict.lt_badge;
            ltTitle.textContent = dict.lt_title;
            if (ltDesc && dict.lt_desc) ltDesc.textContent = dict.lt_desc;
            if (btnPlay && dict.lt_btn_play) btnPlay.textContent = dict.lt_btn_play;
            if (btnReverse && dict.lt_btn_reverse) btnReverse.textContent = dict.lt_btn_reverse;
            if (btnExportJson && dict.lt_btn_json) btnExportJson.textContent = dict.lt_btn_json;
            if (btnExportCss && dict.lt_btn_css) btnExportCss.textContent = dict.lt_btn_css;
        }

        // 5. Perf Audit page
        var pfBadge = document.querySelector('.perf-badge');
        var pfTitle = document.querySelector('.perf-title');
        var pfDesc = document.querySelector('.perf-desc');
        var urlInput = document.getElementById('targetUrl');
        var btnRunAudit = document.getElementById('btnRunAudit');
        var btnExportPdfAudit = document.getElementById('btnExportPdf');
        var overallLabel = document.querySelector('.overall-label');
        var overallSub = document.querySelector('.overall-sub');

        if (pfTitle && dict.pf_title) {
            if (pfBadge && dict.pf_badge) pfBadge.textContent = dict.pf_badge;
            pfTitle.textContent = dict.pf_title;
            if (pfDesc && dict.pf_desc) pfDesc.textContent = dict.pf_desc;
            if (urlInput && dict.pf_input_placeholder) urlInput.placeholder = dict.pf_input_placeholder;
            if (btnRunAudit && dict.pf_btn_run) btnRunAudit.textContent = dict.pf_btn_run;
            if (btnExportPdfAudit && dict.pf_btn_pdf) btnExportPdfAudit.textContent = dict.pf_btn_pdf;
            if (overallLabel && dict.pf_overall) overallLabel.textContent = dict.pf_overall;
            if (overallSub && dict.pf_speed_desc) overallSub.textContent = dict.pf_speed_desc;
        }

        // Update Pill in header
        updatePillUI(cfg);

        // Dispatch Event for modules
        try {
            var evt = new CustomEvent('sr-language-changed', {
                detail: { lang: cfg.code, dir: cfg.dir, config: cfg }
            });
            window.dispatchEvent(evt);
        } catch (e) {}
    }

    function updatePillUI(cfg) {
        var flagEl = document.getElementById('srStudioLangFlag');
        var nameEl = document.getElementById('srStudioLangName');
        if (flagEl) flagEl.textContent = cfg.emoji;
        if (nameEl) nameEl.textContent = cfg.name;

        // Highlight active card in launchpad
        var cards = document.querySelectorAll('.sr-i18n-launchpad-card');
        for (var i = 0; i < cards.length; i++) {
            if (cards[i].getAttribute('data-code') === cfg.code) {
                cards[i].classList.add('active');
            } else {
                cards[i].classList.remove('active');
            }
        }
    }

    function injectStyles() {
        if (document.getElementById('srStudioI18nStyles')) return;
        var style = document.createElement('style');
        style.id = 'srStudioI18nStyles';
        style.textContent = `
            .sr-lang-pill-wrap {
                display: flex;
                align-items: center;
                margin-inline-start: 12px;
            }
            .sr-lang-pill-btn {
                display: inline-flex;
                align-items: center;
                gap: 7px;
                background: rgba(212,175,55, 0.12);
                border: 1px solid rgba(212,175,55, 0.35);
                color: #f3dfba;
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 0.84rem;
                font-weight: 700;
                font-family: inherit;
                cursor: pointer;
                transition: all 0.22s ease;
                backdrop-filter: blur(8px);
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
            }
            .sr-lang-pill-btn:hover {
                background: rgba(212,175,55, 0.24);
                border-color: #f3dfba;
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(212,175,55, 0.35);
            }
            .sr-lang-arrow {
                font-size: 0.72rem;
                opacity: 0.75;
                transition: transform 0.2s;
            }
            /* Launchpad Modal */
            .sr-i18n-overlay {
                position: fixed;
                inset: 0;
                z-index: 100050;
                display: none;
                align-items: center;
                justify-content: center;
                padding: 20px;
                background: rgba(3, 8, 5, 0.82);
                backdrop-filter: blur(24px);
                opacity: 0;
                transition: opacity 0.25s ease;
            }
            .sr-i18n-overlay.active {
                display: flex;
                opacity: 1;
            }
            .sr-i18n-window {
                width: 100%;
                max-width: 820px;
                max-height: 86vh;
                background: linear-gradient(135deg, rgba(8, 22, 16, 0.98), rgba(4, 10, 8, 0.98));
                border: 1px solid rgba(212,175,55, 0.45);
                border-radius: 18px;
                box-shadow: 0 30px 80px rgba(0, 0, 0, 0.8), 0 0 40px rgba(212,175,55, 0.15);
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            .sr-i18n-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 16px 22px;
                background: rgba(13, 34, 26, 0.6);
                border-bottom: 1px solid rgba(212,175,55, 0.2);
            }
            .sr-i18n-title {
                margin: 0;
                font-size: 1.05rem;
                color: #f3dfba;
                font-weight: 800;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .sr-i18n-search-wrap {
                padding: 12px 20px;
                background: rgba(0, 0, 0, 0.3);
                border-bottom: 1px solid rgba(212,175,55, 0.15);
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .sr-i18n-search-input {
                flex: 1;
                background: transparent;
                border: none;
                outline: none;
                color: #ffffff;
                font-size: 0.9rem;
                font-family: inherit;
            }
            .sr-i18n-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
                gap: 10px;
                padding: 18px 20px;
                overflow-y: auto;
                max-height: calc(86vh - 140px);
            }
            .sr-i18n-launchpad-card {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 10px 14px;
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(212,175,55, 0.18);
                border-radius: 10px;
                cursor: pointer;
                transition: all 0.2s ease;
                text-align: inherit;
            }
            .sr-i18n-launchpad-card:hover {
                background: rgba(212,175,55, 0.15);
                border-color: #f3dfba;
                transform: translateY(-2px);
            }
            .sr-i18n-launchpad-card.active {
                background: rgba(16, 185, 129, 0.2);
                border-color: #10b981;
                box-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
            }
            .sr-i18n-card-meta {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .sr-i18n-flag {
                font-size: 1.3rem;
            }
            .sr-i18n-native {
                font-size: 0.85rem;
                font-weight: 700;
                color: #f8fafc;
                display: block;
            }
            .sr-i18n-sub {
                font-size: 0.7rem;
                color: #94a3b8;
                display: block;
            }
            .sr-i18n-vat {
                font-size: 0.65rem;
                color: #f3dfba;
                background: rgba(212,175,55, 0.12);
                border: 1px solid rgba(212,175,55, 0.25);
                padding: 2px 5px;
                border-radius: 5px;
            }
            .sr-i18n-close-btn {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(212,175,55, 0.25);
                color: #cbd5e1;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                transition: all 0.2s;
            }
            .sr-i18n-close-btn:hover {
                background: rgba(239, 68, 68, 0.2);
                border-color: #ef4444;
                color: #ef4444;
            }
        `;
        document.head.appendChild(style);
    }

    function injectNavbarPill() {
        var navbar = document.querySelector('.studio-navbar');
        if (!navbar || document.getElementById('srStudioLangPill')) return;

        var navContainer = navbar.querySelector('nav') || navbar;
        var pillWrap = document.createElement('div');
        pillWrap.className = 'sr-lang-pill-wrap';
        pillWrap.id = 'srStudioLangPill';

        var curLang = getCurrentLanguage();
        var cfg = getLangConfig(curLang);

        pillWrap.innerHTML = `
            <button type="button" class="sr-lang-pill-btn" onclick="SRStudioI18n.toggleModal()" aria-label="Switch Language / تبديل اللغة">
                <span class="sr-lang-flag" id="srStudioLangFlag">${cfg.emoji}</span>
                <span class="sr-lang-name" id="srStudioLangName">${cfg.name}</span>
                <span class="sr-lang-arrow">▾</span>
            </button>
        `;

        // Insert pill next to nav
        if (navbar.querySelector('nav')) {
            navbar.querySelector('nav').appendChild(pillWrap);
        } else {
            navbar.appendChild(pillWrap);
        }
    }

    function injectModal() {
        if (document.getElementById('srStudioI18nModal')) return;

        var modal = document.createElement('div');
        modal.id = 'srStudioI18nModal';
        modal.className = 'sr-i18n-overlay';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('aria-label', 'Sovereign Language Selector');
        modal.setAttribute('translate', 'no');

        var curLang = getCurrentLanguage();

        var cardsHtml = LANGUAGES.map(function(l) {
            var activeClass = l.code === curLang ? ' active' : '';
            var current = l.code === curLang ? ' aria-current="true"' : '';
            return `
                <div class="sr-i18n-launchpad-card${activeClass}" lang="${l.code}"${current} data-code="${l.code}" data-search="${l.name.toLowerCase()} ${l.nameEn.toLowerCase()} ${l.code}" onclick="SRStudioI18n.selectLanguage('${l.code}')">
                    <div class="sr-i18n-card-meta">
                        <span class="sr-i18n-flag">${l.emoji}</span>
                        <div>
                            <span class="sr-i18n-native">${l.name}</span>
                            <span class="sr-i18n-sub">${l.nameEn}</span>
                        </div>
                    </div>
                    <span class="sr-i18n-vat">${l.vat}</span>
                </div>
            `;
        }).join('');

        modal.innerHTML = `
            <div class="sr-i18n-window">
                <div class="sr-i18n-header">
                    <h3 class="sr-i18n-title">
                        <span>🌐</span>
                        <span>اللغات والأنظمة السيادية المعتمدة (29 لغة)</span>
                    </h3>
                    <button type="button" class="sr-i18n-close-btn" onclick="SRStudioI18n.toggleModal()">✕</button>
                </div>
                <div class="sr-i18n-search-wrap">
                    <span style="font-size:1.1rem; opacity:0.7;">🔍</span>
                    <input type="text" id="srStudioI18nSearch" class="sr-i18n-search-input" placeholder="ابحث عن لغة، دولة، أو كود... / Search language, country, code..." oninput="SRStudioI18n.filterLanguages(this.value)">
                </div>
                <div class="sr-i18n-grid" id="srStudioI18nGrid">
                    ${cardsHtml}
                </div>
            </div>
        `;

        modal.addEventListener('click', function(e) {
            if (e.target === modal) SRStudioI18n.toggleModal();
        });

        document.body.appendChild(modal);
    }

    window.SRStudioI18n = {
        init: function() {
            injectStyles();
            injectNavbarPill();
            injectModal();

            var lang = getCurrentLanguage();
            applyLanguage(lang);
        },
        toggleModal: function() {
            var modal = document.getElementById('srStudioI18nModal');
            if (!modal) return;
            var isActive = modal.classList.contains('active');
            if (isActive) {
                modal.classList.remove('active');
            } else {
                modal.classList.add('active');
                var search = document.getElementById('srStudioI18nSearch');
                if (search) {
                    search.value = '';
                    SRStudioI18n.filterLanguages('');
                    setTimeout(function() { search.focus(); }, 100);
                }
            }
        },
        selectLanguage: function(code) {
            applyLanguage(code);
            SRStudioI18n.toggleModal();
        },
        filterLanguages: function(query) {
            var q = (query || '').toLowerCase().trim();
            var cards = document.querySelectorAll('.sr-i18n-launchpad-card');
            for (var i = 0; i < cards.length; i++) {
                var searchData = (cards[i].getAttribute('data-search') || '').toLowerCase();
                if (!q || searchData.indexOf(q) !== -1) {
                    cards[i].style.display = 'flex';
                } else {
                    cards[i].style.display = 'none';
                }
            }
        },
        getCurrent: function() {
            return getCurrentLanguage();
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', window.SRStudioI18n.init);
    } else {
        window.SRStudioI18n.init();
    }
})();

