# -*- coding: utf-8 -*-
import os

with open('partials/20-hero.html', 'r', encoding='utf-8') as f:
    c = f.read()

old_orb = '''                <div class="c3-core-orb" id="heroOrbCore" data-sr-call="openLogoLightbox" data-sr-event="1" title="S&amp;R CoreSync Sovereign Intelligent Core">
                    <img src="./assets/sr-core-emblem-official.webp" alt="S&amp;R CoreSync Sovereign Intelligent Core" width="100" height="100" class="c3-orb-img" loading="eager" decoding="async">
                </div>'''

new_showcase = '''                <div class="c3-centerpiece-showcase" id="heroOrbCore" data-sr-call="openLogoLightbox" data-sr-event="1" title="S&amp;R CoreSync — منظومة المدار ثلاثي الأبعاد مع السحابة والدرع (الخيار 3)">
                    <img src="./assets/branding/hero-emblem-orbital-cloud-ecosystem.webp" alt="S&amp;R CoreSync Sovereign 3D Cloud Ecosystem" width="580" height="380" class="c3-centerpiece-img" loading="eager" decoding="async">
                </div>'''

if old_orb in c:
    c = c.replace(old_orb, new_showcase)
    with open('partials/20-hero.html', 'w', encoding='utf-8') as f:
        f.write(c)
    print("SUCCESS: Updated partials/20-hero.html with Option 3 centerpiece")
else:
    print("Warning: old_orb not found in partials/20-hero.html")

# Also update index.html
with open('index.html', 'r', encoding='utf-8') as f:
    idx_c = f.read()

if old_orb in idx_c:
    idx_c = idx_c.replace(old_orb, new_showcase)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(idx_c)
    print("SUCCESS: Updated index.html with Option 3 centerpiece")
else:
    print("Notice: old_orb in index.html status checked")
