#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_header_logo_syntax.py
Fixes broken img tags in headers (stray `/` and duplicated height="64" lines).
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCLUDE_DIRS = {'.git', '.venv', 'node_modules', '_site', '.system_generated'}

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Pattern 1:
    # height="64" / loading="lazy" decoding="async">
    # height="64" loading="lazy" decoding="async">
    content = re.sub(
        r'height="64"\s*/\s*loading="lazy"\s*decoding="async">\s*height="64"\s*loading="lazy"\s*decoding="async">',
        'height="64" loading="lazy" decoding="async">',
        content
    )

    # Pattern 2:
    # height="64" / loading="lazy" decoding="async">
    content = re.sub(
        r'height="64"\s*/\s*loading="lazy"\s*decoding="async">',
        'height="64" loading="lazy" decoding="async">',
        content
    )

    # Pattern 3:
    # Any standalone duplicate height="64" line right after an img closing
    content = re.sub(
        r'(<img[^>]+height="64"[^>]*>)\s*height="64"\s*loading="lazy"\s*decoding="async">',
        r'\1',
        content
    )

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    fixed = 0
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f.endswith('.html'):
                fp = os.path.join(root, f)
                if fix_file(fp):
                    fixed += 1
                    rel = os.path.relpath(fp, ROOT)
                    print(f"Fixed header logo in: {rel}")
    print(f"Total files fixed: {fixed}")

if __name__ == '__main__':
    main()
