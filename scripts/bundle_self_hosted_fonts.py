#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bundle_self_hosted_fonts.py
===========================
1. Merges Tajawal, Cinzel, Cairo and Alexandria into assets/fonts/gf/fonts.css.
2. Removes all external Google Fonts <link> tags across all HTML files and replaces
   them with the local self-hosted fonts.css.
3. Removes Google Fonts @import from JS/CSS bundles.
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GF_DIR = os.path.join(ROOT, "assets", "fonts", "gf")

def bundle_css():
    print("-> Bundling local font stylesheets into assets/fonts/gf/fonts.css...")
    base_css_file = os.path.join(GF_DIR, "fonts.css")
    with open(base_css_file, "r", encoding="utf-8") as f:
        base_css = f.read()
    
    # Read tajawal, cinzel, cairo
    extra_css = ""
    for extra in ["tajawal.css", "cinzel.css", "cairo.css"]:
        p = os.path.join(GF_DIR, extra)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as ef:
                extra_css += f"\n/* --- {extra} --- */\n" + ef.read()

    # Aliases for Plus Jakarta Sans, Playfair Display, Outfit to Alexandria / Figtree / Cinzel
    aliases = """
/* --- Typography Aliases & Fallbacks --- */
@font-face {
  font-family: 'Plus Jakarta Sans';
  font-style: normal;
  font-weight: 300 900;
  font-display: swap;
  src: url(./figtree-3c512d8e38.woff2) format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153;
}
@font-face {
  font-family: 'Playfair Display';
  font-style: normal;
  font-weight: 600 900;
  font-display: swap;
  src: url(./cinzel-00.woff2) format('woff2');
}
@font-face {
  font-family: 'Outfit';
  font-style: normal;
  font-weight: 300 900;
  font-display: swap;
  src: url(./figtree-3c512d8e38.woff2) format('woff2');
}
@font-face {
  font-family: 'IBM Plex Sans Arabic';
  font-style: normal;
  font-weight: 300 900;
  font-display: swap;
  src: url(./tajawal-00.woff2) format('woff2');
}
"""
    combined = base_css + extra_css + aliases
    with open(base_css_file, "w", encoding="utf-8") as f:
        f.write(combined)
    print(f"Updated {base_css_file} ({len(combined)} bytes)")

def update_html_and_js_files():
    print("-> Replacing external Google Fonts references across all files...")
    count = 0
    
    for dirpath, dirs, files in os.walk(ROOT):
        if any(x in dirpath for x in ['_site', '.venv', 'node_modules', '.git', 'scratch']):
            continue
        for fname in files:
            p = os.path.join(dirpath, fname)
            rel_dir = os.path.relpath(dirpath, ROOT)
            
            # Compute relative path to assets/fonts/gf/fonts.css
            if rel_dir == ".":
                css_href = "./assets/fonts/gf/fonts.css?v=20261122"
            else:
                depth = len(rel_dir.replace("\\", "/").split("/"))
                css_href = ("../" * depth) + "assets/fonts/gf/fonts.css?v=20261122"

            if fname.endswith(".html"):
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                # Check if it has google fonts links
                if "fonts.googleapis.com" in content or "fonts.gstatic.com" in content:
                    # Remove preconnect to fonts.googleapis.com & fonts.gstatic.com
                    new_content = re.sub(r'<link\s+rel=["\']preconnect["\']\s+href=["\']https://fonts\.googleapis\.com["\'][^>]*>\s*', '', content)
                    new_content = re.sub(r'<link\s+rel=["\']preconnect["\']\s+href=["\']https://fonts\.gstatic\.com["\'][^>]*>\s*', '', new_content)
                    
                    # Replace Google Fonts stylesheet link with local stylesheet
                    # E.g. <link href="https://fonts.googleapis.com/css2?..." rel="stylesheet">
                    def repl_link(m):
                        return f'<link rel="stylesheet" href="{css_href}">'
                    
                    new_content = re.sub(r'<link\s+href=["\']https://fonts\.googleapis\.com/css2\?[^"\']+["\']\s+rel=["\']stylesheet["\']\s*/?>', repl_link, new_content)
                    new_content = re.sub(r'<link\s+rel=["\']stylesheet["\']\s+href=["\']https://fonts\.googleapis\.com/css2\?[^"\']+["\']\s*/?>', repl_link, new_content)

                    # Deduplicate if duplicate fonts.css links were created
                    # Keep one
                    if new_content != content:
                        with open(p, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        count += 1

            elif fname.endswith((".js", ".css")):
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if "fonts.googleapis.com" in content:
                    # Remove @import url('https://fonts.googleapis.com/css2?...');
                    new_content = re.sub(r'@import\s+url\([\'"]?https://fonts\.googleapis\.com/css2\?[^\'"\)]+[\'"]?\);\s*', '', content)
                    if new_content != content:
                        with open(p, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        count += 1

    print(f"[SUCCESS] Cleaned and localized Google Fonts across {count} files!")

if __name__ == "__main__":
    bundle_css()
    update_html_and_js_files()
