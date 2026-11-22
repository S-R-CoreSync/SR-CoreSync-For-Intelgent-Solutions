#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_self_hosted_fonts.py
=============================
Downloads WOFF2 files for Tajawal and Cinzel directly from Google Fonts
and generates self-hosted CSS declarations inside assets/fonts/gf/.
"""

import os
import re
import urllib.request

FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts", "gf")

HEADERS = {
    # Send modern browser user-agent to get WOFF2
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_css(family_url):
    req = urllib.request.Request(family_url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")

def download_and_localize(family_name, css_url):
    print(f"-> Fetching CSS for {family_name}...")
    css_content = fetch_css(css_url)
    
    # Find all url(https://fonts.gstatic.com/s/...)
    urls = re.findall(r'url\((https://fonts\.gstatic\.com/s/[^)]+\.woff2)\)', css_content)
    print(f"Found {len(urls)} woff2 files for {family_name}")
    
    local_css = css_content
    for idx, remote_url in enumerate(urls):
        filename = f"{family_name.lower()}-{idx:02d}.woff2"
        local_path = os.path.join(FONTS_DIR, filename)
        
        if not os.path.exists(local_path):
            print(f"Downloading {filename}...")
            req = urllib.request.Request(remote_url, headers=HEADERS)
            with urllib.request.urlopen(req) as resp, open(local_path, "wb") as fh:
                fh.write(resp.read())
        
        local_css = local_css.replace(remote_url, f"./{filename}")
    
    return local_css

def run():
    os.makedirs(FONTS_DIR, exist_ok=True)
    
    # 1. Tajawal (Arabic & Latin)
    tajawal_url = "https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&display=swap"
    tajawal_css = download_and_localize("tajawal", tajawal_url)
    
    # 2. Cinzel (Latin luxury serif)
    cinzel_url = "https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800;900&display=swap"
    cinzel_css = download_and_localize("cinzel", cinzel_url)
    
    # 3. Cairo (Arabic)
    cairo_url = "https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap"
    cairo_css = download_and_localize("cairo", cairo_url)

    # Save to dedicated self-hosted CSS files
    with open(os.path.join(FONTS_DIR, "tajawal.css"), "w", encoding="utf-8") as f:
        f.write(tajawal_css)
    with open(os.path.join(FONTS_DIR, "cinzel.css"), "w", encoding="utf-8") as f:
        f.write(cinzel_css)
    with open(os.path.join(FONTS_DIR, "cairo.css"), "w", encoding="utf-8") as f:
        f.write(cairo_css)
        
    print("[SUCCESS] All font files and localized CSS generated successfully in assets/fonts/gf/!")

if __name__ == "__main__":
    run()
