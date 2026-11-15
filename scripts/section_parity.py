# -*- coding: utf-8 -*-
"""Do all 29 pages carry the same sections?

The keying work assumes the master is a superset. It is not: the founder lab
section exists in all 28 translations and in none... let me show exactly which
ids and which keys each page has, so the divergence is a number and not a hunch.
"""
import os, re, json

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
pages = [('index.html', 'ar')]
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        pages.append((n + '/index.html', n))

MARKERS = {
 'lab section': 'softwareArchitectLab',
 'compliance ribbon (eu)': 'srEuropeanComplianceRibbon',
 'compliance band': 'compliance',
 'estimator compliance': 'srEstCompliance',
 'roi calculator': 'roi-calculator',
 'exec stage': 'execStage',
 'sound control': 'heroSoundLabel',
}

rows = []
for rel, lang in pages:
    s = open(os.path.join(ROOT, rel), encoding='utf-8', newline='').read()
    have = {k: (v in s) for k, v in MARKERS.items()}
    keys = len(set(re.findall(r'data-i18n="([^"]+)"', s)))
    rows.append((lang, have, keys))

print('%-4s %s' % ('lang', ' '.join('%-3s' % k.split()[0][:3] for k in MARKERS) + '  keys'))
for lang, have, keys in rows:
    flags = ' '.join('Y  ' if have[k] else '-  ' for k in MARKERS)
    print('%-4s %s %d' % (lang, flags, keys))

print('\nmarker legend:')
for k in MARKERS:
    present = sum(1 for _, h, _ in rows if h[k])
    print('  %-26s in %d of %d pages' % (k, present, len(rows)))

# which pages lack a marker the majority has
print('\npages missing a section the majority carries:')
for k in MARKERS:
    present = [l for l, h, _ in rows if h[k]]
    if 0 < len(present) < len(rows):
        missing = [l for l, h, _ in rows if not h[k]]
        print('  %-26s present in %d · missing in %s' % (k, len(present), ' '.join(missing[:8])))
