import os, re
ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
css = open(os.path.join(ROOT, 'assets', 'fonts', 'gf', 'fonts.css'), encoding='utf-8').read()

for m in re.finditer(r'@font-face\s*\{[^}]*\}', css):
    b = m.group(0)
    fam = re.search(r"font-family:\s*'([^']+)'", b)
    url = re.search(r'url\(\./([^)]+\.woff2)\)', b)
    w = re.search(r'font-weight:\s*([^;]+);', b)
    ur = re.search(r'unicode-range:\s*([^;]+);', b)
    subset = 'arabic' if ur and '0600' in ur.group(1) else ('latin-ext' if ur and '0100' in ur.group(1) else 'latin')
    print('%-10s %-9s %-19s %-9s %s' % (
        fam.group(1) if fam else '?',
        subset,
        w.group(1).strip() if w else '-',
        (url.group(1)[:19] if url else '-'),
        (ur.group(1)[:40] if ur else '-')))
