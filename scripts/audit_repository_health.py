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
Repository health audit
=======================

Answers three questions with evidence, and changes nothing:

1. Which tracked files are byte-for-byte duplicates of another tracked file?
2. Which tracked assets are never referenced by any page, stylesheet or script?
3. Do the helper programs still parse / run?

Everything here is read-only: it prints a report and never deletes. Deletion is
a separate, reviewed step because a false positive costs a broken page.

Usage:
    python scripts/audit_repository_health.py
    python scripts/audit_repository_health.py --json report.json
"""
import argparse
import collections
import hashlib
import json
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Build output and vendored dependencies are not part of the source tree.
SKIP_DIRS = {'_site', 'dist', 'node_modules', '.git', '__pycache__', 'scratch', '.zwork'}

ASSET_SUFFIXES = ('.jpg', '.jpeg', '.png', '.webp', '.avif', '.svg', '.mp4', '.webm',
                  '.gif', '.ico', '.woff', '.woff2', '.ttf', '.otf', '.pdf', '.zip')

# Text files that can reference an asset.
REF_SUFFIXES = ('.html', '.css', '.js', '.json', '.xml', '.md', '.txt', '.webmanifest', '.py', '.mjs')


def tracked_files():
    out = subprocess.run(['git', 'ls-files'], cwd=ROOT, capture_output=True, text=True)
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def find_duplicates(files):
    by_hash = collections.defaultdict(list)
    for rel in files:
        path = os.path.join(ROOT, rel.replace('/', os.sep))
        if not os.path.isfile(path):
            continue
        try:
            by_hash[sha256(path)].append(rel)
        except OSError:
            continue
    groups = [sorted(v) for v in by_hash.values() if len(v) > 1]
    groups.sort(key=lambda g: -os.path.getsize(os.path.join(ROOT, g[0].replace('/', os.sep))))
    return groups


def build_reference_index(files):
    """Concatenate every text file once and count basename mentions."""
    haystack = []
    for rel in files:
        if not rel.lower().endswith(REF_SUFFIXES):
            continue
        path = os.path.join(ROOT, rel.replace('/', os.sep))
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                haystack.append(fh.read())
        except OSError:
            continue
    return '\n'.join(haystack)


def find_unreferenced_assets(files, index):
    orphans = []
    for rel in files:
        if not rel.lower().endswith(ASSET_SUFFIXES):
            continue
        base = os.path.basename(rel)
        if base not in index and rel not in index:
            size = os.path.getsize(os.path.join(ROOT, rel.replace('/', os.sep)))
            orphans.append((size, rel))
    orphans.sort(reverse=True)
    return orphans


def find_root_clutter(files):
    clutter = collections.defaultdict(list)
    patterns = [
        ('preview/debug harness', re.compile(r'^(preview[-_]|debug_|test-)')),
        ('windows launcher', re.compile(r'\.(bat|ps1|url)$', re.I)),
        ('scratch dump', re.compile(r'(dump|missing|remaining|extracted|all_demo|non_comment).*\.(txt|json)$', re.I)),
    ]
    for rel in files:
        if '/' in rel:
            continue
        for label, pattern in patterns:
            if pattern.search(rel):
                clutter[label].append(rel)
                break
    return clutter


def check_python(files):
    broken = []
    for rel in files:
        if not rel.endswith('.py'):
            continue
        path = os.path.join(ROOT, rel.replace('/', os.sep))
        probe = subprocess.run([sys.executable, '-m', 'py_compile', path],
                               capture_output=True, text=True)
        if probe.returncode != 0:
            broken.append((rel, probe.stderr.strip().splitlines()[-1] if probe.stderr.strip() else 'compile error'))
    return broken


def check_js(files):
    broken = []
    for rel in files:
        if not rel.endswith(('.js', '.mjs')) or rel.endswith('.min.js'):
            continue
        path = os.path.join(ROOT, rel.replace('/', os.sep))
        probe = subprocess.run(['node', '--check', path], capture_output=True, text=True)
        if probe.returncode != 0:
            msg = (probe.stderr or probe.stdout).strip().splitlines()
            broken.append((rel, msg[0] if msg else 'syntax error'))
    return broken


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', default=None)
    args = ap.parse_args()

    files = tracked_files()
    total = sum(os.path.getsize(os.path.join(ROOT, f.replace('/', os.sep)))
                for f in files if os.path.isfile(os.path.join(ROOT, f.replace('/', os.sep))))

    print('=' * 78)
    print('S&R CoreSync - repository health audit')
    print('=' * 78)
    print('tracked files : %d' % len(files))
    print('tracked bytes : %.1f MB' % (total / 1048576))

    duplicates = find_duplicates(files)
    dup_waste = 0
    print('\n-- exact duplicates: %d group(s) --' % len(duplicates))
    for group in duplicates[:25]:
        size = os.path.getsize(os.path.join(ROOT, group[-1].replace('/', os.sep)))
        dup_waste += size * (len(group) - 1)
        print('  %6.1f KB x%d' % (size / 1024, len(group)))
        for rel in group:
            print('      %s' % rel)
    if len(duplicates) > 25:
        print('  ... %d more groups' % (len(duplicates) - 25))
    print('  recoverable if reduced to one copy: %.1f KB' % (dup_waste / 1024))

    index = build_reference_index(files)
    orphans = find_unreferenced_assets(files, index)
    orphan_total = sum(s for s, _ in orphans)
    print('\n-- assets never referenced: %d file(s), %.1f KB --' % (len(orphans), orphan_total / 1024))
    for size, rel in orphans[:30]:
        print('  %6.1f KB  %s' % (size / 1024, rel))

    clutter = find_root_clutter(files)
    print('\n-- root-level clutter --')
    for label, rels in clutter.items():
        print('  %s: %d' % (label, len(rels)))
        for rel in rels[:12]:
            print('      %s' % rel)

    py_broken = check_python(files)
    js_broken = check_js(files)
    print('\n-- helper programs --')
    print('  python files that fail to compile: %d' % len(py_broken))
    for rel, err in py_broken:
        print('      %s -> %s' % (rel, err))
    print('  javascript files that fail to parse: %d' % len(js_broken))
    for rel, err in js_broken:
        print('      %s -> %s' % (rel, err))

    payload = {
        'tracked_files': len(files),
        'duplicate_groups': duplicates,
        'unreferenced_assets': [{'size': s, 'path': p} for s, p in orphans],
        'clutter': clutter,
        'broken_python': py_broken,
        'broken_js': js_broken,
    }
    if args.json:
        with open(args.json, 'w', encoding='utf-8') as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        print('\nreport written to %s' % args.json)
    return 0


if __name__ == '__main__':
    sys.exit(main())
