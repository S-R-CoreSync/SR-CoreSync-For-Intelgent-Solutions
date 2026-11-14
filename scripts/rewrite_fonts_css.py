"""Rewrite fonts.css: Plus Jakarta faces out, Figtree faces in.

The files stay on disk - deleting them broke mono.css last time because the
previous cleanup only read one of the two sheets.
"""
import os, re, shutil

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
GF = os.path.join(ROOT, 'assets', 'fonts', 'gf')
SRC = os.path.join(ROOT, 'docs', 'font-compare')

for name in os.listdir(SRC):
    if name.endswith('.woff2'):
        dst = os.path.join(GF, name)
        if not os.path.exists(dst):
            shutil.copyfile(os.path.join(SRC, name), dst)
            print('copied', name)

fig_css = open(os.path.join(SRC, 'figtree.css'), encoding='utf-8').read()
fig_blocks = re.findall(r'@font-face\s*\{[^}]*\}', fig_css)

p = os.path.join(GF, 'fonts.css')
css = open(p, encoding='utf-8').read()
pj = [b for b in re.findall(r'@font-face\s*\{[^}]*\}', css) if 'Plus Jakarta' in b]
for b in pj:
    css = css.replace(b, '')
print('plus jakarta faces removed:', len(pj))

if 'Figtree' not in css:
    css = css.rstrip() + '\n\n/* Figtree - the Latin face, paired with Alexandria for Arabic. */\n' \
          + '\n'.join(fig_blocks) + '\n'

open(p, 'w', encoding='utf-8', newline='\n').write(css)
print('fonts.css: %.1f KB - figtree blocks: %d' % (os.path.getsize(p) / 1024, len(fig_blocks)))

refs = set(re.findall(r'url\(\./([^)]+\.woff2)\)', css))
have = set(f for f in os.listdir(GF) if f.endswith('.woff2'))
print('missing files:', len(refs - have))
