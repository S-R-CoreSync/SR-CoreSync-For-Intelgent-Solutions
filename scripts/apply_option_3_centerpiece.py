# -*- coding: utf-8 -*-
import os

with open('partials/20-hero.html', 'r', encoding='utf-8') as f:
    c = f.read()

bad_showcase = '''                <div class="c3-centerpiece-showcase" id="heroOrbCore" data-sr-call="openLogoLightbox" data-sr-event="1" title="S&amp;R CoreSync — منظومة المدار ثلاثي الأبعاد مع السحابة والدرع (الخيار 3)">
                    <img src="./assets/branding/hero-emblem-orbital-cloud-ecosystem.webp" alt="S&amp;R CoreSync Sovereign 3D Cloud Ecosystem" width="580" height="380" class="c3-centerpiece-img" loading="eager" decoding="async">
                </div>'''

clean_showcase = '''                <div class="c3-centerpiece-showcase" id="heroOrbCore" data-sr-call="openLogoLightbox" data-sr-event="1" title="S&amp;R CoreSync Sovereign 3D Cloud Ecosystem">
                    <img src="./assets/branding/hero-emblem-orbital-cloud-ecosystem.webp" alt="S&amp;R CoreSync Sovereign 3D Cloud Ecosystem" width="580" height="380" class="c3-centerpiece-img" loading="eager" decoding="async">
                </div>'''

if bad_showcase in c:
    c = c.replace(bad_showcase, clean_showcase)
    with open('partials/20-hero.html', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Cleaned partials/20-hero.html")

with open('index.html', 'r', encoding='utf-8') as f:
    idx_c = f.read()

if bad_showcase in idx_c:
    idx_c = idx_c.replace(bad_showcase, clean_showcase)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(idx_c)
    print("Cleaned index.html")
