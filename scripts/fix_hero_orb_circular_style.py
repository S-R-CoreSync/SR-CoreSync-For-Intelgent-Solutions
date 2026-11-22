#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_hero_orb_circular_style.py
Ensures .c3-core-orb has overflow: hidden and border-radius: 50%,
and .c3-orb-img has border-radius: 50%, object-fit: cover, and snug dimensions.
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_FILE = os.path.join(ROOT, "css", "hero-declutter.css")

def fix_css():
    with open(CSS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # In .c3-core-orb declarations: ensure overflow: hidden !important;
    def orb_sub(m):
        block = m.group(1)
        if "overflow:" not in block:
            block = block + "\n    overflow: hidden !important;"
        if "border-radius:" not in block:
            block = block + "\n    border-radius: 50% !important;"
        return f".c3-core-orb {{{block}\n}}"

    content = re.sub(r'\.c3-core-orb\s*\{([^}]+)\}', orb_sub, content)

    # In .c3-orb-img declarations: ensure border-radius: 50% !important; and object-fit: cover !important;
    # and increase size to fit the circle snugly
    def img_sub(m):
        block = m.group(1)
        if "border-radius:" not in block:
            block = block + "\n    border-radius: 50% !important;"
        if "object-fit:" not in block:
            block = block + "\n    object-fit: cover !important;"
        # adjust 96px to 132px if present
        block = re.sub(r'width:\s*96px\s*!important;', 'width: 132px !important;', block)
        block = re.sub(r'height:\s*96px\s*!important;', 'height: 132px !important;', block)
        block = re.sub(r'width:\s*82px\s*;', 'width: 132px !important;', block)
        block = re.sub(r'height:\s*82px\s*;', 'height: 132px !important;', block)
        return f".c3-orb-img {{{block}\n}}"

    content = re.sub(r'\.c3-orb-img\s*\{([^}]+)\}', img_sub, content)

    if content != original:
        with open(CSS_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print("Updated css/hero-declutter.css for perfect circular orb fitting!")
        return True
    return False

if __name__ == "__main__":
    fix_css()
