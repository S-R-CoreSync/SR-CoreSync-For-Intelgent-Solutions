# -*- coding: utf-8 -*-
"""
S&R CoreSync Master DOM Synchronizer (Single Source of Truth)
Propagates all structural additions, modal components, and navigation elements
from root index.html to the core language pages (en, nl, de).
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. Polite router patch for index.html
def patch_index_auto_detect():
    p = os.path.join(ROOT, 'index.html')
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_detect_pattern = r'<script\s+id="srLangAutoDetect">[\s\S]*?</script>'
    new_router = (
        '<!-- Sovereign Intelligent System Language Router (Polite Mode: User-driven & Zero Forced Hijacking) -->\n'
        '    <script id="srLangAutoDetect">!function () { try { if (/bot|crawl|spider|slurp|google|bing|yandex|lighthouse|headless/i.test(navigator.userAgent)) return; var a = new URLSearchParams(window.location.search); if ("1" === a.get("noredirect")) return; var e = a.get("lang"), r = ["ar", "en", "nl", "de", "fr", "tr", "sv", "no", "es", "it", "ku", "ckb", "pl", "pt", "da", "fi", "cs", "el", "ro", "hu", "bg", "sk", "hr", "lt", "sl", "lv", "et", "ga", "mt"], t = (document.documentElement.getAttribute("lang") || "ar").toLowerCase().split("-")[0], n = -1 !== window.location.pathname.indexOf("demo.html") ? "demo.html" : "index.html", o = !!window.location.pathname.match(/\\/[a-z]{2,3}\\//), i = o ? "../" : "./"; if (e && -1 !== r.indexOf(e.toLowerCase())) { var l = e.toLowerCase(); try { sessionStorage.setItem("sr_user_lang_locked", l), localStorage.setItem("sr_lang_pref", l) } catch (a) { } if (l !== t) { var s = "ar" === l ? n : l + "/" + n; window.location.replace(i + s + window.location.hash) } return } if (o) return; var c = null; try { c = sessionStorage.getItem("sr_user_lang_locked") } catch (a) { } if (c && -1 !== r.indexOf(c)) { if (c !== t) { s = "ar" === c ? n : c + "/" + n; window.location.replace(i + s + window.location.hash) } return } } catch (a) { } }();</script>'
    )
    
    if re.search(old_detect_pattern, content):
        content = re.sub(old_detect_pattern, new_router, content, count=1)
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print("Patched index.html with Polite Language Router.")

# Localized configurations for core languages
CONFIGS = {
    'en': {
        'lang': 'en',
        'dir': 'ltr',
        'nav_more_label': '06+ / More',
        'store_label': '06 Store',
        'faq_label': '07 FAQ',
        'blog_label': '08 Insights',
        'api_label': '09 API Docs',
        'hero_cta_modal': '✨ Plan with AI Architecture',
        'modal_badge': '✨ S&R CoreSync Sovereign AI Architecture',
        'modal_title': 'Turn Your Vision into Sovereign Enterprise Reality',
        'modal_subtitle': 'Describe your project or use voice dictation. Our AI architecture engine will immediately calculate technical scope, recommended stack, and launch roadmap.',
        'modal_placeholder': 'Type your project idea here (e.g. Luxury E-Commerce, Cloud ERP, Sovereign AI Agents)...',
        'modal_voice_title': 'Speak your project idea with interactive voice',
        'modal_submit': '✨ Analyze My Project with AI Now',
        'prompts_label': 'Quick Concept Inspiration:',
        'prompt_chips': [
            ('🛒 Luxury E-Commerce Platform', 'I want to build an enterprise luxury e-commerce platform with automated multi-currency checkout'),
            ('🏢 Enterprise Cloud ERP', 'Deploying an automated financial and corporate ERP system compliant with EU regulations'),
            ('🤖 Autonomous AI Agents', 'Engineering an autonomous AI agents network and automated customer workflows'),
            ('📱 Mobile & Cloud Platform', 'Architecting a high-performance cross-platform mobile app and secure cloud ecosystem')
        ],
        'est_title': 'Architectural Scope & Timeline Estimate',
        'est_query_label': 'Analyzed Concept:',
        'est_lbl_class': 'Architectural Tier',
        'est_val_class': 'Next-Gen Cloud & Enterprise Architecture',
        'est_lbl_timeline': 'Deployment Timeline',
        'est_val_timeline': '3 - 5 Weeks',
        'est_lbl_budget': 'Estimated Investment 💳',
        'curr_all': 'All',
        'curr_eur': 'EUR €',
        'curr_sar': 'SAR',
        'est_lbl_roi': 'Projected Annual ROI 📈',
        'est_val_roi': '+240% Operating Efficiency & Cost Savings',
        'est_lbl_compliance': 'Compliance & Security',
        'est_val_compliance': 'GDPR + 21% BTW Compliance',
        'est_lbl_stack': 'Recommended Stack',
        'est_phases_label': 'Sovereign Deployment Phases:',
        'phase1': 'Core Engine & Data Modeling',
        'phase2': 'Interfaces & API Gateways',
        'phase3': 'Hardening & Production Go-Live',
        'btn_pdf': '📄 Export Architecture Blueprint (PDF)',
        'btn_wa': 'Consult via WhatsApp 💬',
        'btn_consult': '👔 Book Executive Consultation',
        'btn_demo': '⚡ Explore Cloud Sandbox',
        'text_align': 'left'
    },
    'nl': {
        'lang': 'nl',
        'dir': 'ltr',
        'nav_more_label': '06+ / Meer',
        'store_label': '06 Winkel',
        'faq_label': '07 Veelgestelde vragen',
        'blog_label': '08 Inzichten',
        'api_label': '09 API Documentatie',
        'hero_cta_modal': '✨ Plan met AI-Architectuur',
        'modal_badge': '✨ S&R CoreSync Soevereine AI-Architectuur',
        'modal_title': 'Zet uw visie om in soevereine bedrijfsrealiteit',
        'modal_subtitle': 'Beschrijf uw project of gebruik spraakdictaat. Onze AI-architectuurmotor berekent direct de technische reikwijdte, de aanbevolen stack en de lanceringsroadmap.',
        'modal_placeholder': 'Typ hier uw projectidee (bijv. Luxe E-Commerce, Cloud ERP, Soevereine AI-Agents)...',
        'modal_voice_title': 'Spreek uw projectidee in met interactieve stem',
        'modal_submit': '✨ Analyseer mijn project direct met AI',
        'prompts_label': 'Snelle conceptinspiratie:',
        'prompt_chips': [
            ('🛒 Luxe E-Commerce Platform', 'Ik wil een enterprise luxe e-commerce platform bouwen met geautomatiseerde betalingen'),
            ('🏢 Enterprise Cloud ERP', 'Implementatie van een geautomatiseerd financieel en bedrijfs-ERP-systeem conform EU-regels'),
            ('🤖 Autonome AI-Agents', 'Ontwikkeling van een netwerk van autonome AI-agents en geautomatiseerde workflows'),
            ('📱 Mobiele & Cloud App', 'Architectuur van een high-performance mobiele app en veilig cloud-ecosysteem')
        ],
        'est_title': 'Architectonische scope & tijdslijnraming',
        'est_query_label': 'Geanalyseerd concept:',
        'est_lbl_class': 'Architectonische classificatie',
        'est_val_class': 'Next-Gen Cloud & Enterprise Architectuur',
        'est_lbl_timeline': 'Tijdslijn voor lancering',
        'est_val_timeline': '3 - 5 Weken',
        'est_lbl_budget': 'Geschatte investering 💳',
        'curr_all': 'Alles',
        'curr_eur': 'EUR €',
        'curr_sar': 'SAR',
        'est_lbl_roi': 'Verwachte jaarlijkse ROI 📈',
        'est_val_roi': '+240% Operationele efficiëntie & besparingen',
        'est_lbl_compliance': 'Naleving & Beveiliging',
        'est_val_compliance': 'GDPR + 21% BTW Naleving',
        'est_lbl_stack': 'Aanbevolen architectuur',
        'est_phases_label': 'Soevereine implementatiefasen:',
        'phase1': 'Kernmotor & Gegevensmodellering',
        'phase2': 'Interfaces & API-Gateways',
        'phase3': 'Auditing & Livegang',
        'btn_pdf': '📄 Exporteer projectblauwdruk (PDF)',
        'btn_wa': 'Overleg via WhatsApp 💬',
        'btn_consult': '👔 Boek een executive adviesgesprek',
        'btn_demo': '⚡ Ervaar het cloudsysteem',
        'text_align': 'left'
    },
    'de': {
        'lang': 'de',
        'dir': 'ltr',
        'nav_more_label': '06+ / Mehr',
        'store_label': '06 Software-Hub',
        'faq_label': '07 FAQ',
        'blog_label': '08 Einblicke',
        'api_label': '09 API-Dokumentation',
        'hero_cta_modal': '✨ Mit KI-Architektur planen',
        'modal_badge': '✨ S&R CoreSync Souveräne KI-Architektur',
        'modal_title': 'Verwandeln Sie Ihre Vision in souveräne Unternehmensrealität',
        'modal_subtitle': 'Beschreiben Sie Ihr Projekt oder nutzen Sie die Spracheingabe. Unsere KI-Architektur-Engine berechnet sofort den technischen Umfang, den empfohlenen Stack und die Einführungs-Roadmap.',
        'modal_placeholder': 'Geben Sie hier Ihre Projektidee ein (z. B. Luxus-E-Commerce, Cloud-ERP, souveräne KI-Agenten)...',
        'modal_voice_title': 'Sprechen Sie Ihre Projektidee interaktiv ein',
        'modal_submit': '✨ Mein Projekt jetzt sofort mit KI analysieren',
        'prompts_label': 'Schnelle Konzept-Inspiration:',
        'prompt_chips': [
            ('🛒 Luxus E-Commerce Plattform', 'Ich möchte eine hochperformante Luxus-E-Commerce-Plattform mit automatisiertem Checkout aufbauen'),
            ('🏢 Enterprise Cloud ERP', 'Einführung eines automatisierten Finanz- und Unternehmens-ERP-Systems nach EU-Standards'),
            ('🤖 Autonome KI-Agenten', 'Entwicklung eines Netzwerks autonomer KI-Agenten und automatisierter Workflows'),
            ('📱 Mobile & Cloud Plattform', 'Architektur einer hochleistungsfähigen mobilen App und sicheren Cloud-Plattform')
        ],
        'est_title': 'Architektonischer Umfang & Zeitplan-Schätzung',
        'est_query_label': 'Analysiertes Konzept:',
        'est_lbl_class': 'Architektur-Klassifizierung',
        'est_val_class': 'Next-Gen Cloud- & Enterprise-Architektur',
        'est_lbl_timeline': 'Einführungs-Zeitplan',
        'est_val_timeline': '3 - 5 Wochen',
        'est_lbl_budget': 'Geschätztes Budget 💳',
        'curr_all': 'Alle',
        'curr_eur': 'EUR €',
        'curr_sar': 'SAR',
        'est_lbl_roi': 'Erwarteter jährlicher ROI 📈',
        'est_val_roi': '+240% Betriebseffizienz & Kosteneinsparung',
        'est_lbl_compliance': 'Compliance & Sicherheit',
        'est_val_compliance': 'DSGVO + 21% BTW Compliance',
        'est_lbl_stack': 'Empfohlene Architektur',
        'est_phases_label': 'Souveräne Einführungsphasen:',
        'phase1': 'Kern-Engine & Datenmodellierung',
        'phase2': 'Schnittstellen & API-Gateways',
        'phase3': 'Sicherheitsaudit & Go-Live',
        'btn_pdf': '📄 Projekt-Blaupause exportieren (PDF)',
        'btn_wa': 'Über WhatsApp beraten 💬',
        'btn_consult': '👔 Exklusives Beratungsgespräch buchen',
        'btn_demo': '⚡ Cloud-Sandbox testen',
        'text_align': 'left'
    }
}

def generate_modal_html(cfg):
    chips_html = '\n'.join([
        f'                <button type="button" class="sr-idea-prompt-chip" onclick="setAndSubmitPrompt(\'{prompt}\')">{label}</button>'
        for label, prompt in cfg['prompt_chips']
    ])
    
    align_dir = 'ltr' if cfg['dir'] == 'ltr' else 'rtl'
    align_text = cfg['text_align']
    close_pos = 'right: 18px;' if align_dir == 'ltr' else 'left: 18px;'
    mic_pos = 'right: 12px;' if align_dir == 'ltr' else 'right: 12px;'
    input_pad = 'padding: 16px 52px 16px 16px;' if align_dir == 'ltr' else 'padding: 16px 52px 16px 16px;'

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
                <span class="sr-query-label">{cfg['est_query_label']}</span>
                <p class="sr-query-text" id="srEstQueryText">"..."</p>
            </div>

            <div class="sr-estimate-grid">
                <div class="sr-est-metric-card">
                    <span class="sr-est-lbl">{cfg['est_lbl_class']}</span>
                    <strong class="sr-est-val" id="srEstClassification">{cfg['est_val_class']}</strong>
                </div>
                <div class="sr-est-metric-card">
                    <span class="sr-est-lbl">{cfg['est_lbl_timeline']}</span>
                    <strong class="sr-est-val sr-val-gold" id="srEstTimeline">{cfg['est_val_timeline']}</strong>
                </div>
                <div class="sr-est-metric-card sr-est-metric-gold-box" style="border-color: rgba(var(--sr-gold-rgb, 212, 175, 55), 0.55); background: rgba(var(--sr-gold-rgb, 212, 175, 55), 0.08); box-shadow: 0 0 20px rgba(var(--sr-gold-rgb, 212, 175, 55), 0.12);">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:4px;">
                        <span class="sr-est-lbl" style="color: #fce0ad;">{cfg['est_lbl_budget']}</span>
                        <div class="sr-est-currency-toggles" style="display:flex; gap:4px;" aria-label="Currency View Toggle">
                            <button type="button" class="sr-curr-btn active" onclick="switchEstimateCurrency('all', this)" style="padding:2px 7px; font-size:0.68rem; border-radius:5px; border:1px solid rgba(var(--sr-gold-rgb, 212, 175, 55),0.4); background:rgba(var(--sr-gold-rgb, 212, 175, 55),0.25); color:#fff; cursor:pointer; font-weight:700;">{cfg['curr_all']}</button>
                            <button type="button" class="sr-curr-btn" onclick="switchEstimateCurrency('eur', this)" style="padding:2px 7px; font-size:0.68rem; border-radius:5px; border:1px solid rgba(255,255,255,0.15); background:transparent; color:#f3dfba; cursor:pointer; font-weight:700;">{cfg['curr_eur']}</button>
                            <button type="button" class="sr-curr-btn" onclick="switchEstimateCurrency('sar', this)" style="padding:2px 7px; font-size:0.68rem; border-radius:5px; border:1px solid rgba(255,255,255,0.15); background:transparent; color:#f3dfba; cursor:pointer; font-weight:700;">{cfg['curr_sar']}</button>
                        </div>
                    </div>
                    <strong class="sr-est-val sr-val-gold font-num" id="srEstBudget">€4,500 - €8,900  |  18,000 - 35,600 SAR</strong>
                </div>
                <div class="sr-est-metric-card sr-est-metric-roi-box" style="border-color: rgba(16, 185, 129, 0.4); background: rgba(16, 185, 129, 0.08);">
                    <span class="sr-est-lbl" style="color: #a7f3d0;">{cfg['est_lbl_roi']}</span>
                    <strong class="sr-est-val sr-val-emerald font-num" id="srEstRoi">{cfg['est_val_roi']}</strong>
                </div>
                <div class="sr-est-metric-card">
                    <span class="sr-est-lbl">{cfg['est_lbl_compliance']}</span>
                    <strong class="sr-est-val sr-val-emerald" id="srEstCompliance">{cfg['est_val_compliance']}</strong>
                </div>
                <div class="sr-est-metric-card">
                    <span class="sr-est-lbl">{cfg['est_lbl_stack']}</span>
                    <strong class="sr-est-val" id="srEstStack">Next.js + CoreSync Cloud</strong>
                </div>
            </div>

            <div class="sr-estimate-phases">
                <span class="sr-phases-label">{cfg['est_phases_label']}</span>
                <div class="sr-phase-steps">
                    <div class="sr-phase-step"><span class="step-num">1</span><span>{cfg['phase1']}</span></div>
                    <div class="sr-phase-sep">→</div>
                    <div class="sr-phase-step"><span class="step-num">2</span><span>{cfg['phase2']}</span></div>
                    <div class="sr-phase-sep">→</div>
                    <div class="sr-phase-step"><span class="step-num">3</span><span>{cfg['phase3']}</span></div>
                </div>
            </div>

            <div class="sr-estimate-actions">
                <button type="button" class="sr-peek-btn-pdf" id="srBtnExportPdf" onclick="exportAiEstimatePdf()">{cfg['btn_pdf']}</button>
                <button type="button" class="sr-peek-btn-wa" id="srBtnEstimateWhatsApp" onclick="sendEstimateViaWhatsApp()" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color:#ffffff; border:1px solid #34d399; font-weight:800; padding:11px 18px; border-radius:12px; cursor:pointer; display:inline-flex; align-items:center; gap:6px; box-shadow:0 4px 15px rgba(16,185,129,0.35); font-size:0.86rem; transition:transform 0.2s ease;">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M20.52 3.48A11.93 11.93 0 0 0 12.06 0C5.45 0 .09 5.36.09 11.97c0 2.11.55 4.17 1.6 5.98L0 24l6.23-1.63a11.9 11.9 0 0 0 5.83 1.51h.01c6.6 0 11.96-5.36 11.96-11.97 0-3.2-1.25-6.21-3.51-8.43zm-8.46 18.42h-.01a9.92 9.92 0 0 1-5.06-1.39l-.36-.22-3.76.99 1-3.66-.24-.38a9.9 9.9 0 0 1-1.52-5.27c0-5.48 4.46-9.94 9.95-9.94 2.65 0 5.15 1.03 7.02 2.91 1.88 1.88 2.91 4.38 2.91 7.03 0 5.48-4.46 9.93-9.93 9.93zm5.45-7.44c-.3-.15-1.77-.87-2.04-.97-.28-.1-.48-.15-.68.15-.2.3-.78.97-.95 1.17-.18.2-.35.23-.65.08-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.18-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.18.2-.3.3-.5.1-.2.05-.38-.03-.53-.07-.15-.68-1.63-.93-2.24-.24-.59-.49-.51-.68-.52h-.58c-.2 0-.53.08-.8.38-.28.3-1.05 1.03-1.05 2.51s1.08 2.91 1.23 3.11c.15.2 2.12 3.24 5.14 4.54.72.31 1.28.5 1.72.64.72.23 1.38.2 1.9.12.58-.09 1.77-.72 2.02-1.42.25-.7.25-1.3.18-1.42-.08-.12-.28-.2-.58-.35z"/></svg>
                    <span>{cfg['btn_wa']}</span>
                </button>
                <button type="button" class="sr-peek-btn-go" onclick="closeAiEstimateModal(); window.location.href='#services';">{cfg['btn_consult']}</button>
                <a href="demo.html" class="sr-peek-btn-secondary" onclick="closeAiEstimateModal()">{cfg['btn_demo']}</a>
            </div>
        </div>
    </div>

    <!-- AI Idea Analyzer Royal Modal -->
    <div id="srIdeaPromptModal" role="dialog" aria-modal="true" aria-labelledby="srIdeaModalTitle" onclick="if(event.target===this)closeIdeaModal()">
        <div class="sr-idea-modal-card" style="direction:{align_dir}; text-align:{align_text};">
            <button type="button" class="sr-idea-modal-close" style="{close_pos}" onclick="closeIdeaModal()" aria-label="Close">✕</button>
            <div class="sr-idea-modal-badge">{cfg['modal_badge']}</div>
            <h2 class="sr-idea-modal-title" id="srIdeaModalTitle">{cfg['modal_title']}</h2>
            <p class="sr-idea-modal-subtitle">{cfg['modal_subtitle']}</p>

            <div class="sr-idea-input-wrapper">
                <input type="text" id="userIdeaInput" class="sr-idea-input-field" style="direction:{align_dir}; text-align:{align_text}; {input_pad}" placeholder="{cfg['modal_placeholder']}" onkeydown="if(event.key==='Enter'){{submitIdeaAnalysis();}}" />
                <button type="button" id="srVoiceDictateBtn" onclick="toggleHeroVoiceDictation()" class="sr-idea-mic-btn" style="{mic_pos}" title="{cfg['modal_voice_title']}" aria-label="Voice Dictate">🎙️</button>
            </div>

            <div class="sr-idea-modal-actions">
                <button type="button" onclick="submitIdeaAnalysis()" class="sr-idea-submit-btn">
                    <span>{cfg['modal_submit']}</span>
                </button>
            </div>

            <div class="sr-idea-quick-prompts">
                <span class="sr-idea-quick-prompts-label">{cfg['prompts_label']}</span>
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

CSS_MODAL = '''
        /* AI Idea Analyzer Royal Modal Styles */
        #srIdeaPromptModal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(3, 8, 6, 0.85);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            z-index: 100000;
            align-items: center;
            justify-content: center;
            padding: 20px;
            box-sizing: border-box;
            opacity: 0;
            transition: opacity 0.28s ease;
        }
        #srIdeaPromptModal.is-active {
            display: flex;
            opacity: 1;
        }
        .sr-idea-modal-card {
            background: linear-gradient(145deg, rgba(14, 24, 20, 0.98), rgba(8, 14, 11, 0.98));
            border: 1px solid rgba(var(--sr-gold-rgb, 212, 175, 55), 0.45);
            border-radius: 20px;
            max-width: 680px;
            width: 100%;
            padding: 32px 30px;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.8), 0 0 40px rgba(var(--sr-gold-rgb, 212, 175, 55), 0.15);
            position: relative;
            box-sizing: border-box;
            transform: scale(0.96) translateY(10px);
            transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1);
        }
        #srIdeaPromptModal.is-active .sr-idea-modal-card {
            transform: scale(1) translateY(0);
        }
        .sr-idea-modal-close {
            position: absolute;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: #f3dfba;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 1.1rem;
            transition: all 0.2s ease;
            z-index: 2;
        }
        .sr-idea-modal-close:hover {
            background: rgba(239, 68, 68, 0.25);
            border-color: #ef4444;
            color: #ffffff;
            transform: rotate(90deg);
        }
        .sr-idea-modal-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(var(--sr-gold-rgb, 212, 175, 55), 0.12);
            border: 1px solid rgba(var(--sr-gold-rgb, 212, 175, 55), 0.35);
            color: #d4af37;
            font-size: 0.76rem;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: 999px;
            margin-bottom: 12px;
        }
        .sr-idea-modal-title {
            font-size: 1.55rem;
            font-weight: 800;
            color: #ffffff;
            margin: 0 0 8px 0;
            line-height: 1.3;
        }
        .sr-idea-modal-subtitle {
            font-size: 0.92rem;
            color: rgba(255, 255, 255, 0.7);
            margin: 0 0 24px 0;
            line-height: 1.6;
        }
        .sr-idea-input-wrapper {
            position: relative;
            display: flex;
            align-items: center;
            margin-bottom: 16px;
        }
        .sr-idea-input-field {
            width: 100%;
            background: rgba(3, 8, 6, 0.85);
            border: 1.5px solid rgba(var(--sr-gold-rgb, 212, 175, 55), 0.35);
            border-radius: 12px;
            font-size: 0.95rem;
            color: #ffffff;
            font-family: inherit;
            box-sizing: border-box;
            transition: all 0.22s ease;
        }
        .sr-idea-input-field:focus {
            outline: none;
            border-color: #d4af37;
            box-shadow: 0 0 0 3px rgba(var(--sr-gold-rgb, 212, 175, 55), 0.25);
            background: rgba(3, 8, 6, 0.95);
        }
        .sr-idea-mic-btn {
            position: absolute;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1.25rem;
            padding: 4px;
            color: #d4af37;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s ease;
            z-index: 2;
        }
        .sr-idea-mic-btn:hover {
            transform: scale(1.15);
        }
        .sr-idea-modal-actions {
            display: flex;
            gap: 12px;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        .sr-idea-submit-btn {
            flex: 1 1 200px;
            padding: 14px 24px;
            background: linear-gradient(135deg, #fce0ad 0%, #e8bf7a 50%, #d4af37 100%);
            color: #070e0b;
            border: 1px solid rgba(255, 243, 214, 0.85);
            border-radius: 12px;
            font-weight: 800;
            font-size: 0.95rem;
            cursor: pointer;
            box-shadow: 0 8px 22px rgba(232, 191, 122, 0.4);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.25s ease;
        }
        .sr-idea-submit-btn:hover {
            background: linear-gradient(135deg, #ffffff 0%, #fae6bd 50%, #dab471 100%);
            box-shadow: 0 12px 28px rgba(232, 191, 122, 0.65);
            transform: translateY(-2px);
        }
        .sr-idea-quick-prompts {
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
            padding-top: 14px;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }
        .sr-idea-quick-prompts-label {
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.55);
            font-weight: 600;
        }
        .sr-idea-prompt-chip {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(var(--sr-gold-rgb, 212, 175, 55), 0.22);
            color: rgba(243, 223, 186, 0.9);
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .sr-idea-prompt-chip:hover {
            background: rgba(var(--sr-gold-rgb, 212, 175, 55), 0.15);
            border-color: #d4af37;
            color: #ffffff;
            transform: translateY(-1px);
        }

        /* Royal Clean Nav More Dropdown Styles */
        .tf-header-menu .nav-item-has-submenu {
            position: relative;
        }
        .tf-header-menu .nav-submenu {
            display: none;
            position: absolute;
            top: calc(100% + 8px);
            left: 0;
            min-width: 190px;
            background: rgba(14, 24, 20, 0.96);
            border: 1px solid rgba(var(--sr-gold-rgb, 212, 175, 55), 0.35);
            border-radius: 12px;
            padding: 8px 6px;
            box-shadow: 0 16px 36px rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(12px);
            z-index: 9999;
            list-style: none;
            margin: 0;
        }
        .tf-header-menu .nav-submenu.open {
            display: block;
        }
        .tf-header-menu .nav-submenu li {
            margin: 2px 0;
        }
        .tf-header-menu .nav-submenu a {
            display: block;
            padding: 7px 12px;
            font-size: 0.86rem;
            color: rgba(243, 223, 186, 0.9);
            border-radius: 8px;
            transition: all 0.2s ease;
            text-decoration: none;
        }
        .tf-header-menu .nav-submenu a:hover {
            background: rgba(var(--sr-gold-rgb, 212, 175, 55), 0.15);
            color: #ffffff;
        }
'''

def sync_locale(lang):
    cfg = CONFIGS.get(lang)
    if not cfg:
        print(f"Skipping {lang} (no config)")
        return
    
    file_path = os.path.join(ROOT, lang, 'index.html')
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Inject CSS if missing
    if '/* AI Idea Analyzer Royal Modal Styles */' not in html:
        style_close_idx = html.find('</style>')
        if style_close_idx != -1:
            html = html[:style_close_idx] + CSS_MODAL + html[style_close_idx:]
            print(f"[{lang}] Injected Royal Modal & Nav CSS.")

    # 2. Inject Royal Clean Nav More Dropdown in header if missing
    if 'id="navMoreBtn"' not in html:
        # Locate the navigation list in header
        nav_pattern = r'(<li[^>]*>\s*<a[^>]*href="#roi"[^>]*>[\s\S]*?</li>)'
        m = re.search(nav_pattern, html)
        if m:
            roi_item = m.group(0)
            dropdown_html = f'''
                    <li class="nav-item-has-submenu">
                        <button type="button" class="nav-more-btn" id="navMoreBtn" onclick="toggleNavMore(event)" aria-expanded="false" aria-haspopup="true" style="background:none; border:none; color:inherit; font:inherit; cursor:pointer; display:inline-flex; align-items:center; gap:4px; padding:6px 10px;">
                            <span>{cfg['nav_more_label']}</span>
                        </button>
                        <ul class="nav-submenu" id="navMoreSubmenu" role="menu">
                            <li role="none"><a role="menuitem" href="#software-hub">{cfg['store_label']}</a></li>
                            <li role="none"><a role="menuitem" href="#faq">{cfg['faq_label']}</a></li>
                            <li role="none"><a role="menuitem" href="#insights">{cfg['blog_label']}</a></li>
                            <li role="none"><a role="menuitem" href="#api-docs">{cfg['api_label']}</a></li>
                        </ul>
                    </li>'''
            html = html.replace(roi_item, roi_item + dropdown_html, 1)
            print(f"[{lang}] Injected Royal Clean Nav Dropdown.")

    # 3. Inject Modals and script controls before </body>
    if 'id="srIdeaPromptModal"' not in html:
        body_close_idx = html.rfind('</body>')
        if body_close_idx != -1:
            modal_content = generate_modal_html(cfg)
            html = html[:body_close_idx] + '\n' + modal_content + '\n' + html[body_close_idx:]
            print(f"[{lang}] Injected srIdeaPromptModal and srAiEstimateModal.")

    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        f.write(html)
    print(f"[{lang}] Synchronized successfully.")

def main():
    patch_index_auto_detect()
    for lang in ['en', 'nl', 'de']:
        sync_locale(lang)

if __name__ == '__main__':
    main()
