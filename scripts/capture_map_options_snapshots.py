# -*- coding: utf-8 -*-
"""
capture_map_options_snapshots.py
Captures headless Chrome screenshots for Options 1, 2, and 3 from map-options-preview-studio.html.
"""

import subprocess
import os
import re

ART_DIR = r'C:\Users\msali\.gemini\antigravity\brain\36a38584-d480-4aa6-b502-4d07f979cd72'
chrome = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
temp_profile = os.path.join(ART_DIR, 'temp_chrome_profile_map')

with open('map-options-preview-studio.html', 'r', encoding='utf-8') as f:
    base_html = f.read()

configs = [
    (1, 'iq', 'map_preview_option_1.png', 'الخيار 1: التحويل التلقائي بلمسة واحدة — جمهورية العراق (بغداد)'),
    (2, 'ckb', 'map_preview_option_2.png', 'الخيار 2: المعاينة الذكية بالمرور — إقليم كردستان (أربيل)'),
    (3, 'ku', 'map_preview_option_3.png', 'الخيار 3: الشريط الزجاجي السفلي — اللغة الكردية الكرمانجية (سوريا وجنوب شرق تركيا)')
]

for opt_num, market_id, out_file, desc in configs:
    out_path = os.path.join(ART_DIR, out_file)
    temp_html_name = f'temp_map_opt_{opt_num}.html'

    new_listener = f"""window.addEventListener('DOMContentLoaded', () => {{
        initMap();
        setStudioOption({opt_num});
        handlePinClick('{market_id}');
    }});"""

    mod_html = re.sub(
        r"window\.addEventListener\('DOMContentLoaded', \(\) => \{.*?\}\);",
        new_listener,
        base_html,
        flags=re.DOTALL
    )

    with open(temp_html_name, 'w', encoding='utf-8') as f:
        f.write(mod_html)

    t_url = 'file:///' + os.path.abspath(temp_html_name).replace('\\', '/')

    cmd = [
        chrome, '--headless=new', '--disable-gpu', '--no-sandbox', '--incognito',
        f'--user-data-dir={temp_profile}',
        f'--screenshot={out_path}',
        '--window-size=1600,980',
        '--virtual-time-budget=2000',
        '--run-all-compositor-stages-before-draw',
        t_url
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    size = os.path.getsize(out_path) if os.path.exists(out_path) else 0
    print(f"Captured {out_file}: exists={os.path.exists(out_path)}, size={size}")

    if os.path.exists(temp_html_name):
        os.remove(temp_html_name)

print("All option snapshots captured successfully!")
