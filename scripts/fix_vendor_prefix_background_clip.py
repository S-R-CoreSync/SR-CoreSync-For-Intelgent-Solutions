#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_vendor_prefix_background_clip.py
Ensures standard property 'background-clip: text' is defined alongside '-webkit-background-clip: text'.
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXCLUDE_DIRS = {'.git', '.venv', 'node_modules', '_site', '.system_generated'}

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    # Pattern 1: -webkit-background-clip: text; (not followed by background-clip: text)
    # Match: -webkit-background-clip: text; -webkit-text-fill-color:
    content = re.sub(
        r'-webkit-background-clip:\s*text;\s*(?!background-clip:\s*text;)\s*-webkit-text-fill-color:',
        r'-webkit-background-clip: text; background-clip: text; -webkit-text-fill-color:',
        content
    )
    # Pattern 2: -webkit-background-clip:text; (no space)
    content = re.sub(
        r'-webkit-background-clip:text;\s*(?!background-clip:text;)\s*-webkit-text-fill-color:',
        r'-webkit-background-clip: text; background-clip: text; -webkit-text-fill-color:',
        content
    )

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    modified_count = 0
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f.endswith('.html') or f.endswith('.css'):
                fp = os.path.join(root, f)
                if fix_file(fp):
                    modified_count += 1
                    rel = os.path.relpath(fp, ROOT)
                    print(f"Fixed background-clip in: {rel}")

    print(f"Total files updated: {modified_count}")

if __name__ == '__main__':
    main()
