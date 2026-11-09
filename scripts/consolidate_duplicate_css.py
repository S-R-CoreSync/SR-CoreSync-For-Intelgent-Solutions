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

"""
Consolidate byte-identical per-language stylesheets
====================================================

`css/inline-<lang>.css` was generated once per language, but 24 of the 29 copies
are byte-for-byte identical (94.4 KB each, 2.27 MB in total). The duplication
costs nothing at request time - a page loads exactly one of them - but it bloats
the repository, the publish artifact and every clone, and it silently invites
drift: a fix applied to `inline-fr.css` would never reach the other 23.

This tool collapses each duplicate group onto one canonical file:

    group of >= 10 identical files -> css/inline-ltr.css  (a stable, honest name)
    smaller group                  -> an existing member   (prefers inline-en.css)

Then every `<link href=".../inline-xx.css">` in the tracked HTML is rewritten to
the canonical name, and the redundant copies are removed.

Guarantees:
  * Only files that are byte-for-byte identical are merged.
  * A rewrite only happens where the exact basename is referenced.
  * Relative asset URLs inside the CSS are unaffected: every file lives in
    `css/`, so `../assets/...` resolves identically from the canonical file.
  * Dry run by default; `--apply` is required to touch the tree.

Usage:
    python scripts/consolidate_duplicate_css.py
    python scripts/consolidate_duplicate_css.py --apply
"""
import argparse
import collections
import hashlib
import io
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSS_DIR = 'css'
PATTERN = re.compile(r'^inline-[a-z]{2,3}\.css$')

# Names that must never be rewritten or removed by this tool.
PROTECTED = {'inline-core.css'}

LINK_RE = re.compile(r'(?P<pre>(?:href|src)\s*=\s*["\'])(?P<path>[^"\']*?)(?P<name>inline-[a-z]{2,3}\.css)(?P<query>\?[^"\']*)?(?P<post>["\'])')


def tracked(pattern):
    out = subprocess.run(['git', 'ls-files', pattern], cwd=ROOT, capture_output=True, text=True)
    return [l.strip() for l in out.stdout.splitlines() if l.strip()]


def digest(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    css_files = [f for f in os.listdir(os.path.join(ROOT, CSS_DIR)) if PATTERN.match(f)]
    css_files = [f for f in css_files if f not in PROTECTED]

    groups = collections.defaultdict(list)
    for name in sorted(css_files):
        groups[digest(os.path.join(ROOT, CSS_DIR, name))].append(name)

    plan = {}          # old basename -> canonical basename
    to_delete = []     # basenames to remove
    to_write = []      # (canonical basename, source basename)

    for members in groups.values():
        if len(members) < 2:
            continue
        if len(members) >= 10:
            canonical = 'inline-ltr.css'
            to_write.append((canonical, members[0]))
        else:
            canonical = 'inline-en.css' if 'inline-en.css' in members else members[0]
        for name in members:
            if name != canonical:
                plan[name] = canonical
                if name not in to_delete:
                    to_delete.append(name)

    if not plan and not to_write:
        print('nothing to consolidate: every inline-*.css is already unique')
        return 0

    print('groups merged:')
    by_target = collections.defaultdict(list)
    for old, new in plan.items():
        by_target[new].append(old)
    for target, olds in sorted(by_target.items()):
        print('  %-18s <- %d file(s): %s' % (target, len(olds), ', '.join(sorted(olds))))
    saved = sum(os.path.getsize(os.path.join(ROOT, CSS_DIR, n)) for n in to_delete)
    if to_write:
        saved -= os.path.getsize(os.path.join(ROOT, CSS_DIR, to_write[0][1]))
    print('  saved: %.1f KB' % (saved / 1024))

    # ---------------------------------------------------------------- rewrite
    html_files = [f for f in tracked('*.html')]
    touched = 0
    for rel in html_files:
        path = os.path.join(ROOT, rel.replace('/', os.sep))
        if not os.path.isfile(path):
            continue
        with io.open(path, 'r', encoding='utf-8', newline='') as fh:
            text = fh.read()
        original = text

        def repl(match):
            name = match.group('name')
            if name not in plan:
                return match.group(0)
            return (match.group('pre') + match.group('path') + plan[name]
                    + (match.group('query') or '') + match.group('post'))

        text = LINK_RE.sub(repl, text)
        if text != original:
            touched += 1
            print('  rewrite %s' % rel)
            if args.apply:
                with io.open(path, 'w', encoding='utf-8', newline='') as fh:
                    fh.write(text)

    # ------------------------------------------------------------------ write
    for canonical, source in to_write:
        target = os.path.join(ROOT, CSS_DIR, canonical)
        if os.path.exists(target):
            continue
        print('  create  css/%s (from %s)' % (canonical, source))
        if args.apply:
            with open(os.path.join(ROOT, CSS_DIR, source), 'rb') as fh:
                data = fh.read()
            with open(target, 'wb') as fh:
                fh.write(data)

    # ----------------------------------------------------------------- delete
    for name in sorted(to_delete):
        print('  delete  css/%s' % name)
        if args.apply:
            os.remove(os.path.join(ROOT, CSS_DIR, name))

    print('-' * 70)
    print('%s: %d html file(s) rewritten, %d css file(s) removed' % (
        'APPLIED' if args.apply else 'DRY RUN', touched, len(to_delete)))
    if not args.apply:
        print('Re-run with --apply to write.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
