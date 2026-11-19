#!/usr/bin/env python
"""One-time normalization for the script-tag sync gate (2026-11-17).

Aligns every drifted script reference to its canonical (newest) version. The
versions are pure cache keys - the file contents never change - so this is a
safe mechanical sweep across all html pages and partials. The gate
(scripts/check_script_tags.py) then keeps it from ever drifting again.
"""
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# script filename (escaped for regex) -> canonical version tag
CANONICAL = {
    'enterprise-suite.min.js': '20261102-p0-matrix',
    'sr-dock-merge.js': '20261113f',
    'sr-estimator.js': '20261112',
    'sr-inline-13eaa28e.js': '20261102-p0-matrix',
    'sr-lang-hint.js': '20261114-ring',
    'sr-quick-dock.js': '20261117',
}

PATTERNS = [
    # (script, old-version-or-empty, canonical)
    ('sr-dock-merge.js', '20261113b', '20261113f'),
    ('sr-estimator.js', '20261111', '20261112'),
    ('enterprise-suite.min.js', '', '20261102-p0-matrix'),
    ('sr-inline-13eaa28e.js', '', '20261102-p0-matrix'),
    ('sr-lang-hint.js', '', '20261114-ring'),
    ('sr-quick-dock.js', '', '20261117'),
]

changed = 0
files = set(glob.glob(os.path.join(ROOT, '*.html')))
files |= set(glob.glob(os.path.join(ROOT, '*', '*.html')))
files |= set(glob.glob(os.path.join(ROOT, '*', '*', '*.html')))
files |= set(glob.glob(os.path.join(ROOT, '*', '*', '*', '*.html')))
for path in sorted(files):
    if os.sep + '_site' + os.sep in path:
        continue
    with open(path, encoding='utf-8', errors='replace') as fh:
        text = fh.read()
    original = text
    for script, old, new in PATTERNS:
        if old:
            text = text.replace('%s?v=%s' % (script, old), '%s?v=%s' % (script, new))
        else:
            # add the version to bare references: src="./js/x.js" -> src="./js/x.js?v=..."
            for prefix in ('"', "'"):
                text = text.replace(script + prefix, '%s?v=%s%s' % (script, new, prefix))
    if text != original:
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(text)
        changed += 1
        print('fixed', os.path.relpath(path, ROOT))

print('done - %d file(s) normalized' % changed)
