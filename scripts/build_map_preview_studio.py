# -*- coding: utf-8 -*-
"""
build_map_preview_studio.py
Generates an interactive laboratory page demonstrating the 3 proposed options
for the Language, Corporate Entities, and Sovereign Golden Line Map.
"""

import json
import re

with open('js/sr-lang-map.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Extract WORLD_PATH
m = re.search(r'var WORLD_PATH\s*=\s*"([^"]+)"', code)
if not m:
    raise Exception("Could not find WORLD_PATH in js/sr-lang-map.js")
world_path = m.group(1)

html_template = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>معمل معاينة خيارات خريطة اللغات والشركات والخط الذهبي — S&amp;R CoreSync</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Alexandria:wght@300;400;600;700;800;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --sr-gold: #d4af37;
            --sr-gold-light: #f7df94;
            --sr-gold-glow: rgba(212, 175, 55, 0.45);
            --sr-emerald: #10b981;
            --sr-emerald-glow: rgba(16, 185, 129, 0.35);
            --sr-dark-bg: #030b08;
            --sr-card-bg: rgba(6, 18, 14, 0.92);
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Alexandria', sans-serif;
        }}
        body {{
            background: var(--sr-dark-bg);
            color: #e2e8f0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }}
        /* Top Switcher Bar */
        .studio-top-bar {{
            background: rgba(10, 22, 18, 0.95);
            border-bottom: 1px solid rgba(212, 175, 55, 0.25);
            backdrop-filter: blur(16px);
            padding: 14px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
            position: sticky;
            top: 0;
            z-index: 1000;
        }}
        .studio-brand {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .studio-brand-emblem {{
            width: 38px;
            height: 38px;
            border-radius: 10px;
            background: linear-gradient(135deg, rgba(212,175,55,0.25), rgba(16,185,129,0.15));
            border: 1px solid var(--sr-gold);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            color: var(--sr-gold);
            box-shadow: 0 0 15px var(--sr-gold-glow);
        }}
        .studio-brand-titles h1 {{
            font-size: 1.05rem;
            font-weight: 800;
            color: #fff;
            letter-spacing: -0.3px;
        }}
        .studio-brand-titles p {{
            font-size: 0.72rem;
            color: #94a3b8;
        }}
        .studio-options-tabs {{
            display: flex;
            gap: 8px;
            background: rgba(0, 0, 0, 0.4);
            padding: 5px;
            border-radius: 999px;
            border: 1px solid rgba(212, 175, 55, 0.2);
        }}
        .opt-btn {{
            background: transparent;
            border: 1px solid transparent;
            color: #94a3b8;
            font-size: 0.8rem;
            font-weight: 700;
            padding: 8px 18px;
            border-radius: 999px;
            cursor: pointer;
            transition: all 0.25s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .opt-btn:hover {{
            color: #fff;
            background: rgba(255, 255, 255, 0.05);
        }}
        .opt-btn.is-active {{
            background: linear-gradient(135deg, rgba(212, 175, 55, 0.35), rgba(16, 185, 129, 0.35));
            border-color: var(--sr-gold);
            color: #ffffff;
            box-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
        }}
        /* Main Workspace Area */
        .studio-stage {{
            flex: 1;
            position: relative;
            display: flex;
            flex-direction: column;
            background: radial-gradient(ellipse at 50% 20%, rgba(212, 175, 55, 0.07), transparent 70%), #030a08;
            padding: 20px 24px;
        }}
        /* Info Banner */
        .option-explainer-banner {{
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 14px;
            padding: 12px 20px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }}
        .option-explainer-banner h3 {{
            font-size: 0.92rem;
            color: #a7f3d0;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .option-explainer-banner p {{
            font-size: 0.78rem;
            color: #cbd5e1;
            margin-top: 3px;
        }}
        /* Map Container Frame */
        .map-viewport {{
            position: relative;
            width: 100%;
            height: 640px;
            border: 1px solid rgba(212, 175, 55, 0.3);
            border-radius: 20px;
            background: radial-gradient(circle at 45% 35%, rgba(14, 34, 26, 0.8), rgba(2, 8, 6, 0.98));
            box-shadow: 0 20px 50px rgba(0,0,0,0.85), inset 0 0 30px rgba(0,0,0,0.6);
            overflow: hidden;
        }}
        .map-svg {{
            width: 100%;
            height: 100%;
            display: block;
        }}
        .map-land {{
            fill: rgba(212, 175, 55, 0.05);
            stroke: rgba(212, 175, 55, 0.3);
            stroke-width: 0.45;
            stroke-linejoin: round;
        }}
        /* Golden Arc Animation */
        .sr-gold-glow {{
            fill: none;
            stroke: rgba(247, 223, 148, 0.38);
            stroke-width: 6;
            stroke-linecap: round;
            filter: blur(4px);
            pointer-events: none;
        }}
        .sr-gold-arc {{
            fill: none;
            stroke: #f7df94;
            stroke-width: 2.2;
            stroke-linecap: round;
            stroke-dasharray: 8 6;
            animation: srGoldDash 1.2s linear infinite;
            filter: drop-shadow(0 0 8px rgba(247, 223, 148, 0.95)) drop-shadow(0 0 16px rgba(212, 175, 55, 0.8));
            pointer-events: none;
        }}
        @keyframes srGoldDash {{
            to {{ stroke-dashoffset: -28; }}
        }}
        /* Amsterdam HQ Star */
        .sr-hq-star {{
            fill: #f7df94;
            stroke: #8a6a12;
            stroke-width: 0.8;
            filter: drop-shadow(0 0 8px rgba(247, 223, 148, 1));
            cursor: pointer;
        }}
        .sr-hq-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 8px;
            font-weight: 700;
            fill: #f3dfba;
            paint-order: stroke;
            stroke: rgba(2, 10, 7, 0.95);
            stroke-width: 2.5;
            pointer-events: none;
        }}
        /* Country Pins */
        .country-pin {{
            fill: #d4af37;
            cursor: pointer;
            transition: all 0.25s ease;
        }}
        .country-pin:hover, .country-pin.is-active {{
            fill: #ffffff;
            filter: drop-shadow(0 0 10px #f7df94) drop-shadow(0 0 20px #10b981);
        }}
        .country-halo {{
            fill: rgba(212, 175, 55, 0.18);
            pointer-events: none;
            transition: all 0.3s ease;
        }}
        .country-pin:hover + .country-halo,
        .country-pin.is-active + .country-halo {{
            fill: rgba(16, 185, 129, 0.4);
            transform: scale(1.6);
            transform-origin: center;
        }}
        /* Floating HUD Card for Option 1 & 2 */
        .floating-hud-card {{
            position: absolute;
            top: 20px;
            left: 20px;
            width: 360px;
            max-width: calc(100% - 40px);
            background: linear-gradient(145deg, rgba(8, 24, 18, 0.96), rgba(3, 12, 9, 0.98));
            border: 1px solid rgba(212, 175, 55, 0.4);
            border-radius: 18px;
            padding: 18px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8), 0 0 25px rgba(212, 175, 55, 0.18);
            backdrop-filter: blur(20px);
            z-index: 100;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            color: #dfe9f4;
        }}
        .floating-hud-card.is-hidden {{
            opacity: 0;
            transform: translateY(-10px) scale(0.96);
            pointer-events: none;
        }}
        .hud-card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid rgba(212, 175, 55, 0.2);
            padding-bottom: 12px;
            margin-bottom: 12px;
        }}
        .hud-card-title {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .hud-flag {{
            font-size: 1.6rem;
        }}
        .hud-titles h4 {{
            font-size: 0.98rem;
            color: #f3dfba;
            font-weight: 800;
        }}
        .hud-titles span {{
            font-size: 0.72rem;
            color: #94a3b8;
        }}
        .hud-hq-badge {{
            background: rgba(212, 175, 55, 0.12);
            border: 1px solid var(--sr-gold);
            color: var(--sr-gold-light);
            font-size: 0.65rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 999px;
            font-family: 'JetBrains Mono', monospace;
        }}
        .hud-info-grid {{
            display: grid;
            gap: 8px;
            font-size: 0.77rem;
            margin-bottom: 14px;
        }}
        .hud-info-row {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 8px;
        }}
        .hud-info-row span {{
            color: #94a3b8;
        }}
        .hud-info-row strong {{
            color: #e2e8f0;
            font-weight: 700;
            text-align: left;
            direction: ltr;
        }}
        /* Entity Types Chips */
        .entity-chips-box {{
            background: rgba(16, 185, 129, 0.06);
            border: 1px dashed rgba(16, 185, 129, 0.35);
            border-radius: 12px;
            padding: 10px;
            margin-bottom: 12px;
        }}
        .entity-chips-box label {{
            display: block;
            font-size: 0.7rem;
            font-weight: 700;
            color: #6ee7b7;
            margin-bottom: 6px;
        }}
        .entity-chips-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
        }}
        .entity-chip {{
            background: rgba(212, 175, 55, 0.12);
            border: 1px solid rgba(212, 175, 55, 0.4);
            color: #f7df94;
            font-size: 0.68rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
        }}
        /* Option 1 Auto-switch Toast */
        .instant-switch-toast {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.95), rgba(5, 150, 105, 0.98));
            color: #fff;
            border-radius: 10px;
            padding: 10px 14px;
            font-size: 0.8rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
            animation: pulseGlow 1.5s infinite alternate;
        }}
        @keyframes pulseGlow {{
            from {{ filter: drop-shadow(0 0 2px #10b981); }}
            to {{ filter: drop-shadow(0 0 10px #10b981); }}
        }}
        /* Option 3 Bottom Dock Strip */
        .bottom-hud-strip {{
            position: absolute;
            bottom: 16px;
            left: 16px;
            right: 16px;
            background: linear-gradient(180deg, rgba(8, 22, 16, 0.95), rgba(4, 14, 10, 0.98));
            border: 1px solid rgba(212, 175, 55, 0.35);
            border-radius: 16px;
            padding: 12px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.85), 0 0 20px rgba(212, 175, 55, 0.15);
            backdrop-filter: blur(16px);
            z-index: 90;
            transition: all 0.3s ease;
        }}
        .bottom-hud-strip.is-hidden {{
            opacity: 0;
            transform: translateY(20px);
            pointer-events: none;
        }}
        .bottom-hud-main {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .bottom-hud-entities {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .quick-switch-action-btn {{
            background: linear-gradient(135deg, var(--sr-gold), #b89628);
            border: none;
            color: #030a08;
            font-size: 0.82rem;
            font-weight: 800;
            padding: 8px 18px;
            border-radius: 999px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.25s ease;
            white-space: nowrap;
        }}
        .quick-switch-action-btn:hover {{
            filter: brightness(1.15);
            transform: scale(1.03);
            box-shadow: 0 0 15px rgba(212, 175, 55, 0.5);
        }}
        /* Quick Country Picker Bar */
        .quick-picker-scroll {{
            display: flex;
            gap: 8px;
            overflow-x: auto;
            padding: 14px 4px 4px 4px;
            scrollbar-width: thin;
            scrollbar-color: rgba(212, 175, 55, 0.4) transparent;
        }}
        .picker-chip {{
            background: rgba(14, 28, 22, 0.7);
            border: 1px solid rgba(212, 175, 55, 0.25);
            color: #cbd5e1;
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .picker-chip:hover, .picker-chip.is-active {{
            background: rgba(212, 175, 55, 0.2);
            border-color: var(--sr-gold);
            color: #fff;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(212, 175, 55, 0.25);
        }}
    </style>
</head>
<body>

    <!-- Header & Option Selector -->
    <header class="studio-top-bar">
        <div class="studio-brand">
            <div class="studio-brand-emblem">✦</div>
            <div class="studio-brand-titles">
                <h1>معمل تجربة خريطة اللغات والشركات والخط الذهبي (S&amp;R CoreSync)</h1>
                <p>المقر السيادي: أمستردام (AMS HQ) · 29 لغة · شبكة الكيانات القانونية</p>
            </div>
        </div>

        <div class="studio-options-tabs">
            <button class="opt-btn is-active" id="btnOpt1" onclick="setStudioOption(1)">
                <span>⚡</span>
                <span>الخيار 1: التحويل التلقائي بلمسة واحدة</span>
            </button>
            <button class="opt-btn" id="btnOpt2" onclick="setStudioOption(2)">
                <span>🔍</span>
                <span>الخيار 2: المعاينة الذكية بالمرور (Hover HUD)</span>
            </button>
            <button class="opt-btn" id="btnOpt3" onclick="setStudioOption(3)">
                <span>📊</span>
                <span>الخيار 3: الشريط الزجاجي السفلي العائم</span>
            </button>
        </div>
    </header>

    <!-- Stage Content -->
    <main class="studio-stage">
        <!-- Dynamic Explainer Banner -->
        <div class="option-explainer-banner" id="explainerBanner">
            <div>
                <h3 id="optTitle">⚡ الخيار الأول: التحويل التلقائي بلمسة واحدة (Single Click Instant Switch)</h3>
                <p id="optDesc">الخريطة بكامل الشاشة (تم حذف الشريط الأيمن وزر التحويل كلياً). انقر على أي دولة لتنطلق شعلة الخط الذهبي من أمستردام وتظهر بطاقة الشركات فوراً مع إتمام التحويل بسلاسة.</p>
            </div>
            <div style="font-size: 0.75rem; color: #f7df94; background: rgba(212,175,55,0.1); padding: 6px 12px; border-radius: 8px; border: 1px solid rgba(212,175,55,0.3);">
                ✦ اضغط أي دولة على الخريطة أو من شريط الاختيار السريع أدناه
            </div>
        </div>

        <!-- Map Viewport Frame -->
        <div class="map-viewport" id="mapViewport">
            <svg class="map-svg" id="mainMapSvg" viewBox="416.7 65.9 263.9 247" preserveAspectRatio="xMidYMid meet">
                <!-- Coastlines -->
                <path class="map-land" d="{world_path}"></path>
                
                <!-- Golden Layer Group (Arcs + HQ Star) -->
                <g id="goldArcLayer"></g>

                <!-- Pins Group -->
                <g id="pinsLayer"></g>
            </svg>

            <!-- Floating HUD Card (Used in Option 1 & 2) -->
            <div class="floating-hud-card" id="floatingHudCard">
                <div class="hud-card-header">
                    <div class="hud-card-title">
                        <span class="hud-flag" id="hudFlag">🇮🇶</span>
                        <div class="hud-titles">
                            <h4 id="hudName">جمهورية العراق</h4>
                            <span id="hudCity">بغداد</span>
                        </div>
                    </div>
                    <span class="hud-hq-badge" id="hudHqBadge">HQ Linked</span>
                </div>

                <div class="hud-info-grid">
                    <div class="hud-info-row">
                        <span>اللغة الرسمية:</span>
                        <strong id="hudLang">العربية (الأم والرسمية الأولى) · ar</strong>
                    </div>
                    <div class="hud-info-row">
                        <span>ضريبة القيمة المضافة:</span>
                        <strong id="hudVat">لا VAT شامل (مبيعات/جمركية)</strong>
                    </div>
                    <div class="hud-info-row">
                        <span>العملة الرسمية:</span>
                        <strong id="hudCur">IQD (دينار عراقي)</strong>
                    </div>
                    <div class="hud-info-row">
                        <span>قاعدة الفوترة مع أمستردام:</span>
                        <strong id="hudBilling">Non-EU Export / معفاة</strong>
                    </div>
                </div>

                <!-- Entity Types Box -->
                <div class="entity-chips-box">
                    <label>🏢 أنواع الشركات والكيانات القانونية المعتمدة:</label>
                    <div class="entity-chips-list" id="hudEntitiesList">
                        <span class="entity-chip">ش.م.م (LLC)</span>
                        <span class="entity-chip">ش.م.خ (JSC)</span>
                        <span class="entity-chip">مشروع فردي (SPC)</span>
                        <span class="entity-chip">فرع أجنبي</span>
                    </div>
                </div>

                <!-- Action / Toast depending on Option -->
                <div id="hudActionContainer">
                    <div class="instant-switch-toast">
                        <span>🚀 جاري التبديل المباشر إلى بوابة العربية…</span>
                        <span style="font-family:'JetBrains Mono'; font-size:0.75rem;">1.0s</span>
                    </div>
                </div>
            </div>

            <!-- Bottom HUD Strip (Used in Option 3) -->
            <div class="bottom-hud-strip is-hidden" id="bottomHudStrip">
                <div class="bottom-hud-main">
                    <span class="hud-flag" id="bHudFlag" style="font-size:1.8rem;">🇮🇶</span>
                    <div>
                        <h4 id="bHudName" style="color:#f3dfba; font-size:0.95rem; font-weight:800;">جمهورية العراق — بغداد</h4>
                        <p id="bHudMeta" style="font-size:0.75rem; color:#94a3b8; margin-top:2px;">اللغة: العربية (الأم والرسمية) · العملة: IQD · الفوترة: Non-EU</p>
                    </div>
                </div>

                <div class="bottom-hud-entities" id="bHudEntities">
                    <span style="font-size:0.75rem; color:#6ee7b7; font-weight:700;">الكيانات:</span>
                    <span class="entity-chip">ش.م.م (LLC)</span>
                    <span class="entity-chip">ش.م.خ (JSC)</span>
                    <span class="entity-chip">فرع أجنبي</span>
                </div>

                <button type="button" class="quick-switch-action-btn" onclick="simulateSwitch()">
                    <span>التحويل التلقائي للغة ➔</span>
                </button>
            </div>
        </div>

        <!-- Quick Country Bar -->
        <div class="quick-picker-scroll" id="quickPickerBar">
            <!-- Populated dynamically via JS -->
        </div>
    </main>

    <script>
        // Sovereign Markets Data with Geopolitical & Corporate Entities Precision
        const MARKETS = [
            {{
                id: 'nl',
                name: 'هولندا (المقر الرئيسي)',
                city: 'أمستردام',
                flag: '🇳🇱',
                code: 'nl',
                lang: 'Nederlands',
                cur: 'EUR',
                vat: '21% BTW',
                lat: 52.37,
                lon: 4.90,
                billing: 'المقر السيادي (KvK / BTW-nummer)',
                types: ['B.V. (ذ.م.م هولندية)', 'N.V. (مساهمة عامة)', 'V.O.F (شراكة تجارية)', 'Eenmanszaak (مؤسسة فردية)']
            }},
            {{
                id: 'iq',
                name: 'جمهورية العراق',
                city: 'بغداد',
                flag: '🇮🇶',
                code: 'ar',
                lang: 'العربية (اللغة الأم والرسمية الأولى)',
                cur: 'IQD (دينار عراقي)',
                vat: 'لا VAT شامل (ضرائب مبيعات وجمركية)',
                lat: 33.31,
                lon: 44.36,
                billing: 'Non-EU Direct Sovereign Invoice',
                types: ['ش.م.م (شركة ذات مسؤولية محدودة)', 'ش.م.خ (شركة مساهمة خاصة)', 'مشروع فردي (SPC)', 'فرع شركة أجنبية مسجل']
            }},
            {{
                id: 'ckb',
                name: 'إقليم كردستان العراق',
                city: 'أربيل (Hewlêr)',
                flag: '☀️',
                code: 'ckb',
                lang: 'کوردیی ناوەندی (السورانية - ckb)',
                cur: 'IQD (دينار عراقي)',
                vat: '0% معفاة إقليمياً',
                lat: 36.19,
                lon: 44.01,
                billing: 'KRG Registered Sovereign Invoicing',
                types: ['KRG LLC (کۆمپانیای سنووردار)', 'KRG JSC (کۆمپانیای پشکدار)', 'فرع إقليم كردستان (KRG Branch)']
            }},
            {{
                id: 'ku',
                name: 'اللغة الكردية (الكرمانجية)',
                city: 'القامشلي / دياربكر',
                flag: '🌐',
                code: 'ku',
                lang: 'Kurmancî (بالحرف اللاتيني - ku)',
                cur: 'SYP / TRY',
                vat: '0% معفاة',
                lat: 37.05,
                lon: 41.22,
                billing: 'Regional Cross-Border Sovereign Support',
                types: ['SARL (شمال شرق سوريا)', 'Ltd. Şti. (جنوب شرق تركيا)', 'LLC (دهوك)']
            }},
            {{
                id: 'de',
                name: 'ألمانيا',
                city: 'برلين',
                flag: '🇩🇪',
                code: 'de',
                lang: 'Deutsch',
                cur: 'EUR',
                vat: '19% MwSt',
                lat: 52.52,
                lon: 13.40,
                billing: 'EU B2B Reverse Charge',
                types: ['GmbH (ذ.م.م ألمانية)', 'AG (مساهمة كبرى)', 'UG (ريادة أعمال)']
            }},
            {{
                id: 'fr',
                name: 'فرنسا',
                city: 'باريس',
                flag: '🇫🇷',
                code: 'fr',
                lang: 'Français',
                cur: 'EUR',
                vat: '20% TVA',
                lat: 48.85,
                lon: 2.35,
                billing: 'EU B2B Reverse Charge',
                types: ['SAS (مساهمة مبسطة)', 'SARL (ذ.م.م فرنسية)', 'SA (مساهمة عامة)']
            }},
            {{
                id: 'sa',
                name: 'المملكة العربية السعودية',
                city: 'الرياض',
                flag: '🇸🇦',
                code: 'ar',
                lang: 'العربية (السعودية)',
                cur: 'SAR',
                vat: '15% VAT',
                lat: 24.71,
                lon: 46.67,
                billing: 'Non-EU Direct Sovereign Invoice',
                types: ['شركة ذات مسؤولية محدودة (LLC)', 'شركة مساهمة مقفلة (JSC)', 'شركة الشخص الواحد']
            }},
            {{
                id: 'ae',
                name: 'الإمارات العربية المتحدة',
                city: 'دبي',
                flag: '🇦🇪',
                code: 'ar',
                lang: 'العربية (الإمارات)',
                cur: 'AED',
                vat: '5% VAT',
                lat: 25.20,
                lon: 55.27,
                billing: 'Non-EU Direct Sovereign Invoice',
                types: ['LLC (ذ.م.م)', 'FZCO (منطقة حرة)', 'Holding (قابضة)']
            }},
            {{
                id: 'tr',
                name: 'تركيا',
                city: 'إسطنبول',
                flag: '🇹🇷',
                code: 'tr',
                lang: 'Türkçe',
                cur: 'TRY',
                vat: '20% KDV',
                lat: 41.01,
                lon: 28.98,
                billing: 'Non-EU Export Invoicing',
                types: ['Ltd. Şti. (شركة محدودة)', 'A.Ş. (شركة مساهمة)']
            }},
            {{
                id: 'es',
                name: 'إسبانيا',
                city: 'مدريد',
                flag: '🇪🇸',
                code: 'es',
                lang: 'Español',
                cur: 'EUR',
                vat: '21% IVA',
                lat: 40.41,
                lon: -3.70,
                billing: 'EU B2B Reverse Charge',
                types: ['S.L. (ذ.م.م إسبانية)', 'S.A. (شركة مساهمة)']
            }},
            {{
                id: 'it',
                name: 'إيطاليا',
                city: 'روما',
                flag: '🇮🇹',
                code: 'it',
                lang: 'Italiano',
                cur: 'EUR',
                vat: '22% IVA',
                lat: 41.90,
                lon: 12.49,
                billing: 'EU B2B Reverse Charge',
                types: ['S.r.l. (ذ.م.م إيطالية)', 'S.p.A. (مساهمة)']
            }},
            {{
                id: 'gb',
                name: 'المملكة المتحدة',
                city: 'لندن',
                flag: '🇬🇧',
                code: 'en',
                lang: 'English (UK)',
                cur: 'GBP',
                vat: '20% VAT',
                lat: 51.50,
                lon: -0.12,
                billing: 'UK Post-Brexit Invoicing',
                types: ['Ltd (Private Limited)', 'PLC (Public Limited)', 'LLP (شراكة محدودة)']
            }}
        ];

        let activeOption = 1;
        let selectedMarket = MARKETS[1]; // Default to Iraq
        const AMS_COORDS = {{ lat: 52.37, lon: 4.90 }};
        const VB_W = 1000, VB_H = 560, LAT_TOP = 78, LAT_BOTTOM = -58;

        function proj(lat, lon) {{
            return {{
                x: (lon + 180) / 360 * VB_W,
                y: (LAT_TOP - lat) / (LAT_TOP - LAT_BOTTOM) * VB_H
            }};
        }}

        // Render Map Pins and Amsterdam Star
        function initMap() {{
            const pinsLayer = document.getElementById('pinsLayer');
            const amsPt = proj(AMS_COORDS.lat, AMS_COORDS.lon);
            let pinsHtml = '';

            // AMS HQ Star
            pinsHtml += `
                <circle class="sr-hq-star" cx="${{amsPt.x.toFixed(1)}}" cy="${{amsPt.y.toFixed(1)}}" r="5" onclick="selectMarket('nl')"></circle>
                <text class="sr-hq-label" x="${{(amsPt.x + 8).toFixed(1)}}" y="${{(amsPt.y - 6).toFixed(1)}}">AMS HQ (S&R CoreSync)</text>
            `;

            MARKETS.forEach(m => {{
                if (m.id === 'nl') return;
                const pt = proj(m.lat, m.lon);
                pinsHtml += `
                    <circle class="country-halo" cx="${{pt.x.toFixed(1)}}" cy="${{pt.y.toFixed(1)}}" r="11"></circle>
                    <circle class="country-pin" id="pin-${{m.id}}" data-id="${{m.id}}" 
                        cx="${{pt.x.toFixed(1)}}" cy="${{pt.y.toFixed(1)}}" r="4.6"
                        onmouseenter="handlePinHover('${{m.id}}')"
                        onclick="handlePinClick('${{m.id}}')">
                        <title>${{m.name}} — ${{m.city}}</title>
                    </circle>
                `;
            }});

            pinsLayer.innerHTML = pinsHtml;

            // Render Quick Picker
            const picker = document.getElementById('quickPickerBar');
            picker.innerHTML = MARKETS.map(m => `
                <div class="picker-chip ${{m.id === selectedMarket.id ? 'is-active' : ''}}" id="chip-${{m.id}}" onclick="handlePinClick('${{m.id}}')">
                    <span>${{m.flag}}</span>
                    <span>${{m.name}}</span>
                </div>
            `).join('');
        }}

        // Draw Golden Arc from Amsterdam HQ to Target
        function drawGoldenArc(targetMarket) {{
            const layer = document.getElementById('goldArcLayer');
            const a = proj(AMS_COORDS.lat, AMS_COORDS.lon);
            const b = proj(targetMarket.lat, targetMarket.lon);

            const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
            const dx = b.x - a.x, dy = b.y - a.y;
            const len = Math.sqrt(dx * dx + dy * dy) || 1;
            const lift = Math.min(80, len * 0.22);
            const cx = mx + (-dy / len) * lift, cy = my + (dx / len) * lift;

            const path = `M${{a.x.toFixed(1)}} ${{a.y.toFixed(1)}} Q${{cx.toFixed(1)}} ${{cy.toFixed(1)}} ${{b.x.toFixed(1)}} ${{b.y.toFixed(1)}}`;

            layer.innerHTML = `
                <path class="sr-gold-glow" d="${{path}}"></path>
                <path class="sr-gold-arc" d="${{path}}"></path>
                <circle cx="${{b.x.toFixed(1)}}" cy="${{b.y.toFixed(1)}}" r="8" fill="none" stroke="#f7df94" stroke-width="1.4" opacity="0.9"></circle>
                <circle cx="${{b.x.toFixed(1)}}" cy="${{b.y.toFixed(1)}}" r="3.6" fill="#fff3c4"></circle>
            `;
        }}

        // Update Details across HUDs
        function updateDetails(m) {{
            selectedMarket = m;

            // Update Floating HUD (Option 1 & 2)
            document.getElementById('hudFlag').textContent = m.flag;
            document.getElementById('hudName').textContent = m.name;
            document.getElementById('hudCity').textContent = m.city;
            document.getElementById('hudLang').textContent = m.lang;
            document.getElementById('hudVat').textContent = m.vat;
            document.getElementById('hudCur').textContent = m.cur;
            document.getElementById('hudBilling').textContent = m.billing;

            const entitiesList = document.getElementById('hudEntitiesList');
            entitiesList.innerHTML = m.types.map(t => `<span class="entity-chip">${{t}}</span>`).join('');

            // Update Bottom HUD (Option 3)
            document.getElementById('bHudFlag').textContent = m.flag;
            document.getElementById('bHudName').textContent = `${{m.name}} — ${{m.city}}`;
            document.getElementById('bHudMeta').textContent = `اللغة: ${{m.lang}} · العملة: ${{m.cur}} · الفوترة: ${{m.billing}}`;
            document.getElementById('bHudEntities').innerHTML = `<span style="font-size:0.75rem; color:#6ee7b7; font-weight:700;">الكيانات:</span>` +
                m.types.map(t => `<span class="entity-chip">${{t}}</span>`).join('');

            // Highlight chip in scrollbar
            document.querySelectorAll('.picker-chip').forEach(c => c.classList.remove('is-active'));
            const c = document.getElementById(`chip-${{m.id}}`);
            if (c) c.classList.add('is-active');

            // Draw golden line
            drawGoldenArc(m);
        }}

        // Switcher logic
        function setStudioOption(opt) {{
            activeOption = opt;
            document.querySelectorAll('.opt-btn').forEach((b, i) => b.classList.toggle('is-active', (i + 1) === opt));

            const bannerTitle = document.getElementById('optTitle');
            const bannerDesc = document.getElementById('optDesc');
            const floatingCard = document.getElementById('floatingHudCard');
            const bottomStrip = document.getElementById('bottomHudStrip');
            const actionContainer = document.getElementById('hudActionContainer');

            if (opt === 1) {{
                bannerTitle.innerHTML = '⚡ الخيار الأول: التحويل التلقائي بلمسة واحدة (Single Click Instant Switch)';
                bannerDesc.innerHTML = 'الخريطة بكامل الشاشة (تم حذف الشريط الأيمن وزر التحويل كلياً). انقر على أي دولة لتنطلق شعلة الخط الذهبي من أمستردام وتظهر بطاقة الشركات فوراً مع إتمام التحويل بسلاسة.';
                floatingCard.classList.remove('is-hidden');
                bottomStrip.classList.add('is-hidden');
                actionContainer.innerHTML = `
                    <div class="instant-switch-toast">
                        <span>🚀 جاري التبديل المباشر إلى بوابة ${{selectedMarket.lang}}…</span>
                        <span style="font-family:'JetBrains Mono'; font-size:0.75rem;">1.0s</span>
                    </div>
                `;
            }} else if (opt === 2) {{
                bannerTitle.innerHTML = '🔍 الخيار الثاني: المعاينة الذكية بالمرور (Hover HUD Mode)';
                bannerDesc.innerHTML = 'بمجرد تمرير مؤشر الفأرة (Hover) فوق أي دولة ينطلق الخط الذهبي من أمستردام وتظهر بطاقة الشركات والكيانات القانونية، والضغط بأي مكان داخل البطاقة ينقلك فوراً للغة.';
                floatingCard.classList.remove('is-hidden');
                bottomStrip.classList.add('is-hidden');
                actionContainer.innerHTML = `
                    <button type="button" class="quick-switch-action-btn" style="width:100%; justify-content:center; padding:10px;" onclick="simulateSwitch()">
                        <span>التحويل المباشر إلى ${{selectedMarket.lang}} ➔</span>
                    </button>
                `;
            }} else if (opt === 3) {{
                bannerTitle.innerHTML = '📊 الخيار الثالث: الشريط الزجاجي السفلي العائم (Bottom HUD Strip)';
                bannerDesc.innerHTML = 'الخريطة في الأعلى بعرض كامل، وتفاصيل الشركات والضرائب تظهر كشريط زجاجي عائم أنيق في أسفل الخريطة بدلاً من الشريط الجانبي الأيمن القديم.';
                floatingCard.classList.add('is-hidden');
                bottomStrip.classList.remove('is-hidden');
            }}
            updateDetails(selectedMarket);
        }}

        function handlePinHover(id) {{
            if (activeOption === 2) {{
                const m = MARKETS.find(x => x.id === id);
                if (m) updateDetails(m);
            }}
        }}

        function handlePinClick(id) {{
            const m = MARKETS.find(x => x.id === id);
            if (!m) return;
            updateDetails(m);

            if (activeOption === 1) {{
                const actionContainer = document.getElementById('hudActionContainer');
                actionContainer.innerHTML = `
                    <div class="instant-switch-toast" style="background:linear-gradient(135deg,#d4af37,#10b981);">
                        <span>⚡ تم التبديل الفوري بنجاح إلى [${{m.name}} — ${{m.lang}}]</span>
                        <span>✓</span>
                    </div>
                `;
                setTimeout(() => {{
                    setStudioOption(1);
                }}, 1800);
            }}
        }}

        function simulateSwitch() {{
            alert(`[محاكاة التحويل السلس]: تم التبديل الفوري إلى بوابة ${{selectedMarket.name}} (${{selectedMarket.lang}}) مع تطبيق ضريبة ${{selectedMarket.vat}} وعملة ${{selectedMarket.cur}} بنجاح.`);
        }}

        // Initialize on load
        window.addEventListener('DOMContentLoaded', () => {{
            initMap();
            setStudioOption(1);
            // Default select Iraq
            handlePinClick('iq');
        }});
    </script>
</body>
</html>
'''

with open('map-options-preview-studio.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("Generated map-options-preview-studio.html successfully!")
