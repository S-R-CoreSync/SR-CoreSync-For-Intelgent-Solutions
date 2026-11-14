# -*- coding: utf-8 -*-
"""
Phase 2: Full Section Localization for Turkish (tr/index.html).
Translates all residual English text in Services, Pricing, Software-Hub, FAQ, and ROI into pure idiomatic Turkish.
"""
import os, re

p = os.path.join('tr', 'index.html')
content = open(p, encoding='utf-8').read()

REPLACEMENTS = [
    # Services Header & Controls
    ('Signature Creative &amp; Digital Solutions', 'İmza Nitelikli Yaratıcı &amp; Dijital Çözümler'),
    ('Signature Creative & Digital Solutions', 'İmza Nitelikli Yaratıcı & Dijital Çözümler'),
    ('💱 Active Para Birimi:', '💱 Aktif Para Birimi:'),
    ('Select Currency & Tax Calculation:', 'Para Birimi Seçimi & Vergi Hesaplama:'),
    ('Select Currency &amp; Tax Calculation:', 'Para Birimi Seçimi &amp; Vergi Hesaplama:'),

    # Card 01 - Visual Identity
    ('>Visual Identity<', '>Görsel Kimlik<'),
    ('>Transparent Price:<', '>Şeffaf Fiyat:<'),
    ('>Direct Savings<', '>Doğrudan Tasarruf<'),
    ('>Book Session 📅<', '>Görüşme Planla 📅<'),
    ('>Order via WhatsApp<', '>WhatsApp ile Sipariş Ver<'),

    # Card 02 - Web Design
    ('>Website Design &amp; Optimization<', '>Web Tasarımı &amp; Optimizasyonu<'),
    ('>Website Design & Optimization<', '>Web Tasarımı & Optimizasyonu<'),
    ('>Most Popular<', '>En Çok Tercih Edilen<'),

    # Card 03 - E-Commerce
    ('>E-Commerce Store<', '>E-Ticaret Mağazası<'),
    ('Clear, intuitive online stores that turn visitors into seamless buyers.', 'Ziyaretçileri sorunsuz alıcılara dönüştüren sezgisel, modern e-ticaret mağazaları.'),
    ('>Full ERP Bridge<', '>Tam ERP Köprüsü<'),

    # Cards 04-09 Titles & Tags
    ('>Custom Cloud Software<', '>Özel Bulut Yazılımları<'),
    ('>Autonomous AI Architectures<', '>Otonom Yapay Zekâ Mimarileri<'),
    ('>FinTech &amp; Payment Systems<', '>FinTech &amp; Ödeme Sistemleri<'),
    ('>FinTech & Payment Systems<', '>FinTech & Ödeme Sistemleri<'),
    ('>Global Logistics &amp; ERP<', '>Küresel Lojistik &amp; ERP<'),
    ('>Global Logistics & ERP<', '>Küresel Lojistik & ERP<'),
    ('>Interactive 3D Platforms<', '>Etkileşimli 3D Platformlar<'),
    ('>Cybersecurity &amp; Code Audit<', '>Siber Güvenlik &amp; Kod Denetimi<'),
    ('>Cybersecurity & Code Audit<', '>Siber Güvenlik & Code Audit<'),

    # Pricing Section Packages & Titles
    ('>Creative &amp; E-Commerce<', '>Yaratıcı &amp; E-Ticaret<'),
    ('>Creative & E-Commerce<', '>Yaratıcı & E-Ticaret<'),
    ('>Cloud ERP &amp; Financial Bridges<', '>Bulut ERP &amp; Finansal Köprüler<'),
    ('>Cloud ERP & Financial Bridges<', '>Bulut ERP & Finansal Köprüler<'),
    ('>CoreCare ve Sürekli Optimizasyon<', '>CoreCare &amp; Kesintisiz Optimizasyon<'),
    ('>Core Starter<', '>Core Başlangıç Paketi<'),
    ('>Select Package<', '>Paketi Seç<'),
    ('>Included<', '>Dahil Olanlar<'),
    ('Ideal for launching a dedicated cloud platform or initial core product.', 'Özel bir bulut platformu veya başlangıç çekirdek ürününü yayına almak için idealdir.'),
    ('Cloud platform up to 5 business modules', '5 iş modülüne kadar kapsamlı bulut platformu'),
    ('/ project', '/ proje bazlı'),
    ('/ month', '/ aylık'),
    ('/ complete audit', '/ tam denetim'),

    # Growth Bundle & Other Cards
    ('All-in-One Digital Growth Bundle (Identity + Website + Store)', 'Hepsi Bir Arada Dijital Büyüme Paketi (Kurumsal Kimlik + Web Sitesi + Mağaza)'),
    ('Digital Documentation Suite', 'Eksiksiz Dijital Dokümantasyon Paketi'),
    ('Dedicated Solutions Architect', 'Özel Atanmış Çözüm Mimarı'),
    ('Basic Digital Invoicing', 'Temel Dijital Faturalama'),
    ('Financial &amp; Tax Solutions', 'Finans &amp; Vergi Çözümleri'),
    ('Financial & Tax Solutions', 'Finans & Vergi Çözümleri'),
    ('3 Solutions', '3 Kapsamlı Çözüm'),
    ('Official XML tax returns &amp; audit reports', 'Resmi XML vergi beyannameleri &amp; denetim raporları'),

    # White-Label Platforms & Software Hub
    ('Universal White-Label Platforms', 'Genel Lisanslanabilir White-Label Platformlar'),
    ('>Universal White-Label Platforms<', '>Genel Lisanslanabilir White-Label Platformlar<'),

    # FAQ Section
    ('Frequently Asked Questions', 'Sıkça Sorulan Sorular'),
    ('>Frequently Asked Questions<', '>Sıkça Sorulan Sorular<'),

    # Founders Showcase Tabs
    ('Interactive Auto Slider', 'Etkileşimli Otomatik Sunum'),
    ('Interactive Auto Slider 🔄', 'Etkileşimli Otomatik Sunum 🔄')
]

count = 0
for old, new in REPLACEMENTS:
    if old in content:
        content = content.replace(old, new)
        count += 1

open(p, 'w', encoding='utf-8').write(content)
print(f'Successfully applied {count} localization replacements to tr/index.html')
