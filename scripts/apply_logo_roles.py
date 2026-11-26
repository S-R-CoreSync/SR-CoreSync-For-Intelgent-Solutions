# -*- coding: utf-8 -*-
"""
Give each logo placement the asset that fits its rendered size.

`assets/logo-official.jpg` is a 1024x1024 opaque brand lockup: monogram +
"S & R CORESYNC" wordmark + tagline. At 42-100 px (headers, footers, orbs)
the wordmark and tagline collapse into an unreadable smudge and the black
background reads as a tile. The transparent emblem
(`sr-core-emblem-official.webp`, 37 KB, RGBA) is the asset designed for
those slots; the lockup stays where it is shown large (hero, lightbox,
showcase cards, covers).

The rule is size-based, not file-based:
  * a placement whose declared box is <= 120 px, or whose class is one of
    the known small brand slots, gets the emblem + its 192w/384w srcset;
  * everything else keeps the lockup.

Usage:
  python scripts/apply_logo_roles.py --check
  python scripts/apply_logo_roles.py --apply
"""
import argparse
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IMG_RE = re.compile(r'<img\b[^>]*logo-official[^>]*>', re.S)
SRC_RE = re.compile(r'src="(?:\.\./|\./|/)*assets/logo-official\.jpg(?:\?[^"]*)?"')
SRCSET_RE = re.compile(r'srcset="[^"]*"')
ANY_RE = re.compile(r'(?:\.\./|\./|/)*assets/logo-official\.jpg')

SMALL_CLASSES = {
    'brand-emblem-img', 'brand-emblem-img-sm', 'c3-orb-img', 'sr-footer-emblem',
    'roi-pdf-emblem-img', 'roi-cert-emblem', 'ds-u27', 'ds-u66', 'emblem',
    'srp-auth__emblem', 'company-logo-img', 'logo-img', 'portal-brand-emblem',
    'dev-emblem', 'partner-emblem', 'corp-emblem-img', 'brand-emblem',
}


def tracked_html():
    out = subprocess.run(['git', 'ls-files', '*.html'], cwd=ROOT,
                         capture_output=True, text=True, encoding='utf-8')
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def prefix_for(rel_path):
    parts = rel_path.split('/')
    if parts[0] == 'partials':
        return '../' if len(parts) > 2 else './'
    depth = len(parts) - 1
    return './' if depth == 0 else '../' * depth


def is_small(tag):
    cls = re.search(r'class="([^"]*)"', tag)
    names = set(cls.group(1).split()) if cls else set()
    if names & SMALL_CLASSES:
        return True
    w = re.search(r'width="(\d+)"', tag)
    h = re.search(r'height="(\d+)"', tag)
    if w and h:
        return max(int(w.group(1)), int(h.group(1))) <= 120
    return False


def emblem_markup(tag, prefix):
    src = '%sassets/sr-core-emblem-official.webp' % prefix
    srcset = ('srcset="%sassets/sr-core-emblem-official-192w.webp 192w, '
              '%sassets/sr-core-emblem-official-384w.webp 384w, '
              '%sassets/sr-core-emblem-official.webp 384w"'
              % (prefix, prefix, prefix))
    tag = SRC_RE.sub('src="%s"' % src, tag)
    if SRCSET_RE.search(tag):
        tag = SRCSET_RE.sub(srcset, tag)
    else:
        tag = tag.replace('src="%s"' % src, 'src="%s"\n                                        %s'
                          % (src, srcset), 1)
    return ANY_RE.sub(src, tag)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    if not (args.apply or args.check):
        ap.error('pass --apply or --check')

    changed, checked, small_total = [], 0, 0
    for rel in tracked_html():
        if rel.startswith('docs/'):
            continue
        path = os.path.join(ROOT, rel.replace('/', os.sep))
        if not os.path.exists(path):
            continue
        checked += 1
        with open(path, encoding='utf-8', newline='') as fh:
            original = fh.read()
        prefix = prefix_for(rel)

        def repl(m):
            nonlocal small_total
            tag = m.group(0)
            if not is_small(tag):
                return tag
            small_total += 1
            return emblem_markup(tag, prefix)

        fixed = IMG_RE.sub(repl, original)
        if fixed != original:
            changed.append(rel)
            if args.apply:
                with open(path, 'w', encoding='utf-8', newline='') as fh:
                    fh.write(fixed)

    mode = 'APPLIED' if args.apply else 'DRIFT'
    print('logo roles: %d pages, %d small placements, %d file(s) %s'
          % (checked, small_total, len(changed), mode))
    for rel in changed[:20]:
        print('  %s %s' % ('~' if args.apply else 'X', rel))
    return 0 if args.apply or not changed else 1


if __name__ == '__main__':
    sys.exit(main())
