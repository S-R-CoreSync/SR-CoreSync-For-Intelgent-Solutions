# -*- coding: utf-8 -*-
import os

with open('map-options-preview-studio.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Add CSS for radar and clock
radar_css = """
        /* AMS HQ Radar Pulse */
        .sr-hq-radar-pulse {
            fill: none;
            stroke: #34d399;
            stroke-width: 1.5;
            opacity: 0.8;
            animation: srRadarPulse 2.4s ease-out infinite;
            transform-origin: center;
            pointer-events: none;
        }
        .sr-hq-radar-pulse.pulse-2 {
            animation-delay: 1.2s;
            stroke: #6ee7b7;
        }
        @keyframes srRadarPulse {
            0% { r: 6px; opacity: 0.9; stroke-width: 2px; }
            50% { opacity: 0.5; }
            100% { r: 24px; opacity: 0; stroke-width: 0.5px; }
        }
        .sr-hq-status-dot {
            fill: #34d399;
            filter: drop-shadow(0 0 5px #34d399);
        }
        .sr-lm__hotkey-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(212,175,55,0.12);
            border: 1px solid rgba(212,175,55,0.35);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            color: #f3dfba;
        }
"""

if '/* AMS HQ Radar Pulse */' not in c:
    c = c.replace('/* Amsterdam HQ Star */', radar_css + '\n        /* Amsterdam HQ Star */')

# 2. Add Hotkey Badge in Top Bar
hotkey_badge = """
        <div class="sr-lm__hotkey-badge">
            <span style="color:#6ee7b7; font-weight:800;">⚡ Global Hotkey:</span>
            <kbd style="background:rgba(255,255,255,0.15); border:1px solid rgba(255,255,255,0.3); border-radius:4px; padding:1px 6px; font-family:monospace; font-weight:800;">M</kbd> أو 
            <kbd style="background:rgba(255,255,255,0.15); border:1px solid rgba(255,255,255,0.3); border-radius:4px; padding:1px 6px; font-family:monospace; font-weight:800;">L</kbd> للفتح السريع · 
            <kbd style="background:rgba(255,255,255,0.15); border:1px solid rgba(255,255,255,0.3); border-radius:4px; padding:1px 6px; font-family:monospace; font-weight:800;">Esc</kbd> للإغلاق
        </div>
"""

if 'class="sr-lm__hotkey-badge"' not in c:
    c = c.replace('</div>\n    </header>', hotkey_badge + '    </div>\n    </header>')

# 3. Add Radar circles to AMS HQ Star in pinsHtml
old_ams_pins = """            // AMS HQ Star
            pinsHtml += `
                <circle class="sr-hq-star" cx="${amsPt.x.toFixed(1)}" cy="${amsPt.y.toFixed(1)}" r="5" onclick="selectMarket('nl')"></circle>
                <text class="sr-hq-label" x="${(amsPt.x + 8).toFixed(1)}" y="${(amsPt.y - 6).toFixed(1)}">AMS HQ (S&R CoreSync)</text>
            `;"""

new_ams_pins = """            // AMS HQ Star & Live Radar Pulse
            pinsHtml += `
                <circle class="sr-hq-radar-pulse pulse-1" cx="${amsPt.x.toFixed(1)}" cy="${amsPt.y.toFixed(1)}" r="10"></circle>
                <circle class="sr-hq-radar-pulse pulse-2" cx="${amsPt.x.toFixed(1)}" cy="${amsPt.y.toFixed(1)}" r="18"></circle>
                <circle class="sr-hq-halo" cx="${amsPt.x.toFixed(1)}" cy="${amsPt.y.toFixed(1)}" r="13"></circle>
                <circle class="sr-hq-star" cx="${amsPt.x.toFixed(1)}" cy="${amsPt.y.toFixed(1)}" r="5" onclick="selectMarket('nl')"></circle>
                <circle class="sr-hq-status-dot" cx="${(amsPt.x + 4.5).toFixed(1)}" cy="${(amsPt.y - 4.5).toFixed(1)}" r="2"></circle>
                <text class="sr-hq-label" x="${(amsPt.x + 8).toFixed(1)}" y="${(amsPt.y - 6).toFixed(1)}">AMS HQ (S&R CoreSync) 🟢 البث السيادي الحي</text>
            `;"""

if 'sr-hq-radar-pulse pulse-1' not in c:
    c = c.replace(old_ams_pins, new_ams_pins)

# 4. Add Live Clocks inside Floating HUD card
clock_html = """
                <!-- Live Capital Clocks Card -->
                <div class="hud-live-clock-card" style="margin-top:12px; padding:8px 12px; background:rgba(6,78,59,0.3); border:1px solid rgba(52,211,153,0.35); border-radius:10px; display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; flex-direction:column; gap:2px;">
                        <span style="font-size:0.7rem; color:#a7f3d0; font-weight:700;">⏱️ التوقيت اللحظي للعاصمة</span>
                        <strong id="hudMarketClock" style="font-size:0.95rem; color:#fef08a; font-family:monospace; font-weight:800; letter-spacing:0.5px;">10:15:20 (أربيل)</strong>
                    </div>
                    <div style="height:24px; width:1px; background:rgba(52,211,153,0.3);"></div>
                    <div style="display:flex; flex-direction:column; gap:2px; text-align:left;">
                        <span style="font-size:0.7rem; color:#a7f3d0; font-weight:700;">🏢 المقر الرئيسي أمستردام</span>
                        <strong id="hudAmsClock" style="font-size:0.95rem; color:#34d399; font-family:monospace; font-weight:800; letter-spacing:0.5px;">08:15:20 (AMS)</strong>
                    </div>
                </div>
"""

if 'hud-live-clock-card' not in c:
    c = c.replace('<div id="hudActionContainer">', clock_html + '\n                <div id="hudActionContainer">')

with open('map-options-preview-studio.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Updated map-options-preview-studio.html successfully!')
