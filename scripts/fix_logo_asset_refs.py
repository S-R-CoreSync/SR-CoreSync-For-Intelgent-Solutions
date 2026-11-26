# -*- coding: utf-8 -*-
"""
Repair the official-logo reference wave (2026-11-26).

The bulk replacement that introduced `assets/logo-official.jpg` wrote
`./assets/...` into language pages (404 under /de/, /en/insights/, ...),
collapsed every responsive `srcset` to a single URL, and declared the JPEG
as `type="image/webp"`.

This tool is idempotent and limited to logo references:
  * rewrites the path prefix to the page's real depth (`./`, `../`, `../../`)
  * rebuilds `srcset` from the generated WebP derivatives (192/384/1024)
  * fixes the MIME type when a `.jpg` is still declared as webp
  * leaves every other byte of the file untouched

Usage:
  python scripts/fix_logo_asset_refs.py --check
  python scripts/fix_logo_asset_refs.py --apply
"""
import argparse
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SRCSET_RE = re.compile(
    r'srcset="(?:(\.\./|\./|/)assets/logo-official\.jpg)(?:\?[^"]*)?"')
SRC_RE = re.compile(
    r'(src|href)="(?:(\.\./|\./|/)assets/logo-official\.jpg)(?:\?[^"]*)?"')
JS_RE = re.compile(
    r"(['\"])(?:\.\./|\./|/)assets/logo-official\.jpg(['\"])")
TYPE_RE = re.compile(r'type="image/webp"')


def tracked_html():
    out = subprocess.run(['git', 'ls-files', '*.html'], cwd=ROOT,
                         capture_output=True, text=True, encoding='utf-8')
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def prefix_for(rel_path):
    """Path prefix for the page each file ends up in.

    A fragment under `partials/<locale>/` is rendered into `<locale>/index.html`
    (depth 1); a fragment directly under `partials/` lands in the root page.
    `docs/` snapshots are not published and are skipped by the caller.
    """
    parts = rel_path.split('/')
    if parts[0] == 'partials':
        return '../' if len(parts) > 2 else './'
    depth = len(parts) - 1
    return './' if depth == 0 else '../' * depth


def fix_text(text, prefix):
    srcset = ('srcset="%sassets/logo-official-192.webp 192w, '
              '%sassets/logo-official-384.webp 384w, '
              '%sassets/logo-official-1024.webp 1024w"'
              % (prefix, prefix, prefix))
    text = SRCSET_RE.sub(srcset, text)
    text = SRC_RE.sub(lambda m: '%s="%sassets/logo-official.jpg"'
                      % (m.group(1), prefix), text)
    text = JS_RE.sub(lambda m: '%s%sassets/logo-official.jpg%s'
                     % (m.group(1), prefix, m.group(2)), text)

    # A JPEG declared as WebP in the same tag: fix the declaration.
    out_lines = []
    for line in text.split('\n'):
        if 'logo-official.jpg' in line and TYPE_RE.search(line):
            line = TYPE_RE.sub('type="image/jpeg"', line)
        out_lines.append(line)
    return '\n'.join(out_lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    if not (args.apply or args.check):
        ap.error('pass --apply or --check')

    changed, checked = [], 0
    for rel in tracked_html():
        if rel.startswith('docs/'):
            continue  # unpublished snapshots, not part of the site
        path = os.path.join(ROOT, rel.replace('/', os.sep))
        if not os.path.exists(path):
            continue
        checked += 1
        with open(path, encoding='utf-8', newline='') as fh:
            original = fh.read()
        fixed = fix_text(original, prefix_for(rel))
        if fixed != original:
            changed.append(rel)
            if args.apply:
                with open(path, 'w', encoding='utf-8', newline='') as fh:
                    fh.write(fixed)

    mode = 'APPLIED' if args.apply else 'DRIFT'
    print('logo refs: %d pages checked, %d %s' % (checked, len(changed), mode))
    for rel in changed[:60]:
        print('  %s %s' % ('~' if args.apply else 'X', rel))
    return 0 if args.apply or not changed else 1


if __name__ == '__main__':
    sys.exit(main())
