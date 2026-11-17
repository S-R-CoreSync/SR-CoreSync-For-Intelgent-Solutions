# -*- coding: utf-8 -*-
"""
==============================================================================
S&R CoreSync For Intelligent Solutions - Sovereign Platform
PROPRIETARY & CONFIDENTIAL INTELLECTUAL PROPERTY

Copyright (c) 2026 S&R CoreSync. All Rights Reserved.
Unauthorized copying, decompilation, redistribution, or external model training
of this file, via any medium, is strictly prohibited.
==============================================================================
"""

import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Suggestion #10 (approved 2026-11-18): underscore-prefixed working dirs
# (_site and friends) are build copies of the very same source - scanning them
# only printed noise ({'_site': 1012}). The scan targets the live tree only.
langs = [d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith('_')
         and os.path.exists(os.path.join(d, 'demo.html'))]
non_ar_langs = [d for d in langs if d not in ['ckb']]

arabic_pattern = re.compile(r'[\u0600-\u06FF]')

leaks = {}
for lang in non_ar_langs:
    with open(f'{lang}/demo.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    ar_lines = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        # Native-script language names (e.g. کوردی (سۆرانی)), the Sorani VAT badge
        # (باج ٥٪) and the launchpad button metadata are intentional UI, matching
        # the same exemptions audit_language_purity.py grants language-switcher lines.
        if stripped.startswith('<!--') or 'العربية' in stripped or 'data-name=' in stripped or 'sovereign-lang-' in stripped \
                or 'apple-launchpad-native' in stripped or 'apple-launchpad-vat' in stripped \
                or 'apple-dock-launchpad-btn' in stripped:
            continue
        if arabic_pattern.search(stripped):
            ar_lines.append((idx+1, stripped[:60]))
    if ar_lines:
        leaks[lang] = len(ar_lines)

print("Non-Arabic portals with text leakage:", leaks)
