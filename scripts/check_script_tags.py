#!/usr/bin/env python
"""Script-tag sync gate: one version per script, across every page.

The language map fix (2026-11-17) exposed a silent failure class: the lazy
loader reference is written at the bottom of 60 pages while sync_locales only
regenerates the hero region, so bumping the version in index.html alone left
57 pages pointing at the stale tag. Browsers then kept the old cached script
and the fix never reached them - and nothing failed anywhere, which is exactly
why it needs a gate.

This check groups every versioned local script reference by path and requires
a single version across all pages that mention it. Unversioned references are
ignored, and anything outside the working tree (e.g. _site) is never scanned.

    python scripts/check_script_tags.py            # gate (exit 1 on drift)
"""
import glob
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directories to skip entirely (nested clones, build artefacts, trash, etc.)
SKIP_DIRS = {
    'SR-CoreSync-For-Intelgent-Solutions',
    '_site',
    '_trash_160',
    'node_modules',
    '.git',
}

# js/whatever.js?v=20261117a  -  local scripts with a cache-busting version.
TAG_RE = re.compile(r"""(?:src|href)=["'](?:\.{1,2}/)?(js/[\w.-]+\.(?:m?js))(?:\?v=([\w.-]+))?["']""")


def main():
    versions = defaultdict(set)          # path -> {version}
    offenders = defaultdict(list)        # path -> [(file, version)]
    html_files = []
    seen = set()
    html_files += glob.glob(os.path.join(ROOT, '*.html'))
    html_files += glob.glob(os.path.join(ROOT, '*', 'index.html'))
    html_files += glob.glob(os.path.join(ROOT, '*', '*.html'))
    html_files += glob.glob(os.path.join(ROOT, '*', '*', '*.html'))
    html_files += glob.glob(os.path.join(ROOT, '*', '*', '*', '*.html'))
    for f in html_files:
        real = os.path.realpath(f)
        parts = real.split(os.sep)
        if real in seen or any(p in SKIP_DIRS for p in parts):
            continue
        seen.add(real)
        try:
            with open(f, encoding='utf-8', errors='replace') as fh:
                text = fh.read()
        except OSError:
            continue
        rel = os.path.relpath(f, ROOT)
        for path, tag in TAG_RE.findall(text):
            versions[path].add(tag or '(unversioned)')
            offenders[path].append((rel, tag or '(unversioned)'))

    drift = {path: v for path, v in versions.items() if len(v) > 1}
    if drift:
        print('FAILED - script versions drift across pages:')
        for path, v in sorted(drift.items()):
            print('  %s -> %s' % (path, ', '.join(sorted(v))))
            for rel, tag in sorted(offenders[path]):
                print('     %-28s %s' % (rel, tag))
        return 1
    multi = {p: len(v) for p, v in versions.items() if len(offenders[p]) > 1}
    if multi:
        for path in sorted(multi):
            vs = ', '.join(sorted(versions[path]))
            print('  ok  %-44s %d pages, version %s' % (path, multi[path], vs))
    print('script-tag sync: clean - one version per script across %d pages' % len(seen))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
