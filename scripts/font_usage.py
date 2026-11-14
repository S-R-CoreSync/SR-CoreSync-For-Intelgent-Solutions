import os, re
from collections import Counter

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
files = []
for base, _, names in os.walk(os.path.join(ROOT, 'css')):
    for n in names:
        if n.endswith('.css'):
            files.append(os.path.join(base, n))
files.append(os.path.join(ROOT, 'index.html'))

fam = Counter()
stacks = Counter()
for f in files:
    try:
        s = open(f, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    for m in re.finditer(r'font-family\s*:\s*([^;}]+)', s, re.I):
        val = re.sub(r'\s+', ' ', m.group(1)).strip().lower()
        stacks[val] += 1
        for name in ('alexandria', 'plus jakarta sans', 'figtree', 'jetbrains mono', 'cairo', 'ibm plex sans arabic'):
            if name in val:
                fam[name] += 1

print('font-family declarations mentioning each family:')
for k, v in fam.most_common():
    print('  %-22s %d' % (k, v))

print('\nmost common stacks:')
for stack, n in stacks.most_common(6):
    print('  %-3d  %s' % (n, stack[:110]))

# what the body actually asks for, per language
for rel in ('index.html', 'en/index.html', 'de/index.html'):
    s = open(os.path.join(ROOT, rel), encoding='utf-8', newline='').read()
    m = re.search(r'html\[lang="ar"\]\s*body[^{]*\{[^}]*font-family\s*:\s*([^;}]+)', s, re.I)
    m2 = re.search(r'(?:^|})\s*body\s*\{[^}]*font-family\s*:\s*([^;}]+)', s, re.I)
    print('\n%-16s arabic-body: %s' % (rel, (m.group(1)[:90] if m else '—')))
    print('%-16s body:        %s' % ('', (m2.group(1)[:90] if m2 else '—')))
