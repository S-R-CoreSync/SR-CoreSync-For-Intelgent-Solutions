"""Install Figtree properly: local files + @font-face, and retire Plus Jakarta Sans.

Order matters: the face has to exist before any rule asks for it, otherwise the
20 existing references simply fall back again - which is the bug we are fixing.
"""
import hashlib, os, re, shutil, urllib.request

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
GF = os.path.join(ROOT, 'assets', 'fonts', 'gf')
SRC = os.path.join(ROOT, 'docs', 'font-compare')

# 1 · copy the woff2 files next to the other local faces
moved = []
for name in os.listdir(SRC):
    if name.endswith('.woff2'):
        shutil.copyfile(os.path.join(SRC, name), os.path.join(GF, name))
        moved.append(name)
print('figtree files in place:', len(moved))

# 2 · build the @font-face block, paths relative to assets/fonts/gf/
fig_css = open(os.path.join(SRC, 'figtree.css'), encoding='utf-8').read()
fig_css = re.sub(r'url\(\./([^)]+)\)', r'url(./\1)', fig_css)
fig_blocks = re.findall(r'@font-face\s*\{[^}]*\}', fig_css)

fonts_path = os.path.join(GF, 'fonts.css')
css = open(fonts_path, encoding='utf-8').read()

# 3 · drop the Plus Jakarta faces, keep Alexandria
pj_blocks = [b for b in re.findall(r'@font-face\s*\{[^}]*\}', css) if 'Plus Jakarta' in b]
for b in pj_blocks:
    css = css.replace(b, '')
print('plus jakarta faces removed:', len(pj_blocks))

if 'Figtree' not in css:
    css = css.rstrip() + '\n\n/* Figtree — the Latin face, paired with Alexandria for Arabic. */\n' \
          + '\n'.join(fig_blocks) + '\n'
    print('figtree faces added:', len(fig_blocks))

open(fonts_path, 'w', encoding='utf-8', newline='\n').write(css)
print('fonts.css now: %.1f KB' % (os.path.getsize(fonts_path) / 1024))

# 4 · delete the Plus Jakarta files that nothing will reference any more
keep = set(re.findall(r'url\(\./([^)]+\.woff2)\)', css))
removed = 0
for name in os.listdir(GF):
    if name.endswith('.woff2') and name not in keep:
        os.remove(os.path.join(GF, name))
        removed += 1
print('unreferenced woff2 removed:', removed)
