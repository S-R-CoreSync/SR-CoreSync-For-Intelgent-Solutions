"""Remove font files that neither sheet references any more."""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
GF = os.path.join(ROOT, 'assets', 'fonts', 'gf')

refs = set()
for sheet in ('fonts.css', 'mono.css'):
    p = os.path.join(GF, sheet)
    if os.path.exists(p):
        refs |= set(re.findall(r'url\(\./([^)]+\.woff2)\)', open(p, encoding='utf-8').read()))

removed, freed = [], 0
for name in sorted(os.listdir(GF)):
    if name.endswith('.woff2') and name not in refs:
        size = os.path.getsize(os.path.join(GF, name))
        os.remove(os.path.join(GF, name))
        removed.append(name)
        freed += size

print('removed %d unreferenced files, %.1f KB freed' % (len(removed), freed / 1024))
print('kept:', len([n for n in os.listdir(GF) if n.endswith('.woff2')]), 'files')
