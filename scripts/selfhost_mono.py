"""The design-system sheet still imports four families from Google.

Only one of them is used and not already local: JetBrains Mono (code blocks).
IBM Plex Sans Arabic and Space Grotesk appear nowhere but that import line.
So the import becomes a local file holding JetBrains Mono alone.
"""
import hashlib, os, re, urllib.request

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
OUT = os.path.join(ROOT, 'assets', 'fonts', 'gf')
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
URL = 'https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap'


def fetch(u, binary=False):
    req = urllib.request.Request(u, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = r.read()
    return d if binary else d.decode('utf-8')


def main():
    css = fetch(URL)
    blocks = re.findall(r'@font-face\s*\{[^}]*\}', css)
    seen, out = {}, []
    total = 0
    for b in blocks:
        m = re.search(r'url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)', b)
        if not m:
            continue
        u = m.group(1)
        if u not in seen:
            data = fetch(u, binary=True)
            name = 'mono-' + hashlib.sha1(u.encode()).hexdigest()[:12] + '.woff2'
            open(os.path.join(OUT, name), 'wb').write(data)
            seen[u] = name
            total += len(data)
        out.append(b.replace(m.group(0), 'url(./%s)' % seen[u]))

    open(os.path.join(OUT, 'mono.css'), 'w', encoding='utf-8', newline='\n').write(
        '/* JetBrains Mono, served from this domain (code blocks only). */\n' + '\n'.join(out) + '\n')
    print('mono files:', len(seen), 'bytes: %.1f KB' % (total / 1024))

    p = os.path.join(ROOT, 'css', 'sr-unified-design-system.css')
    s = open(p, encoding='utf-8', newline='').read()
    new, n = re.subn(r"@import\s+url\('https://fonts\.googleapis\.com/css2\?[^']+'\);?",
                     "@import url('../assets/fonts/gf/mono.css');", s, count=1)
    if n:
        open(p, 'w', encoding='utf-8', newline='').write(new)
        print('design-system import now local')
    else:
        print('import not found')


if __name__ == '__main__':
    main()
