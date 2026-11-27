# -*- coding: utf-8 -*-
"""Finish the badge migration: every remaining reference to the old lockup.

Covers the social metas, the icon link, the download links inside the logo
modal, the AI card generator defaults and the JS fallbacks. Text-only edits,
idempotent.
"""
import argparse
import io
import os
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAIRS = [
    # social cards: square badge reads better at 1200x630 centre crops
    ('https://sr-coresync.com/assets/logo-official.jpg',
     'https://sr-coresync.com/assets/sr-badge-official.png'),
    # icon
    ('<link rel="icon" type="image/png" href="./assets/logo-official.jpg">',
     '<link rel="icon" type="image/png" href="./assets/sr-badge-official.png">'),
    # download links inside the logo modal
    ('download="SR-CoreSync-Official-Emblem.png"',
     'download="SR-CoreSync-Official-Badge.png"'),
]

# any remaining href/src to the old file becomes the badge png
RAW = 'logo-official.jpg'


def tracked_html():
    out = subprocess.run(['git', 'ls-files', '*.html'], cwd=ROOT,
                         capture_output=True, text=True, encoding='utf-8')
    return [l.strip() for l in out.stdout.splitlines() if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    if not (a.apply or a.check):
        ap.error('pass --apply or --check')

    changed, checked = [], 0
    for rel in tracked_html():
        if rel.startswith('docs/'):
            continue
        p = os.path.join(ROOT, rel.replace('/', os.sep))
        if not os.path.exists(p):
            continue
        checked += 1
        t = io.open(p, encoding='utf-8', newline='').read()
        o = t
        for old, new in PAIRS:
            t = t.replace(old, new)
        if RAW in t:
            depth = rel.count('/')
            prefix = './' if depth == 0 else '../' * depth
            t = t.replace('assets/' + RAW, 'assets/sr-badge-official.png')
            # card.html uses a bare relative path
            t = t.replace("'./assets/sr-badge-official.png'", "'%sassets/sr-badge-official.png'" % prefix)
        if t != o:
            changed.append(rel)
            if a.apply:
                io.open(p, 'w', encoding='utf-8', newline='').write(t)

    print('leftovers: %d pages, %d changed %s'
          % (checked, len(changed), '(applied)' if a.apply else ''))
    for rel in changed[:8]:
        print('  ', rel)
    return 0 if a.apply or not changed else 1


if __name__ == '__main__':
    sys.exit(main())
