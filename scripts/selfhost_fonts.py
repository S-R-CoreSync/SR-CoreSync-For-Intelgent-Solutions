"""Download the exact woff2 files Google is already serving us, and serve them locally.

The page asks Google for two families. Self-hosting them removes two third-party
origins from every visit while keeping the same glyphs, because the files are the
same files - not re-subset ones.
"""
import hashlib
import os
import re
import urllib.request

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
OUT_DIR = os.path.join(ROOT, 'assets', 'fonts', 'gf')
CSS_PATH = os.path.join(OUT_DIR, 'fonts.css')

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

SRC_CSS = ('https://fonts.googleapis.com/css2?'
           'family=Alexandria:wght@200;300;400;500;600;700;800;900'
           '&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap')


def fetch(url, binary=False):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return data if binary else data.decode('utf-8')


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    css = fetch(SRC_CSS)
    blocks = re.findall(r'@font-face\s*\{[^}]*\}', css)
    print('font-face blocks from Google:', len(blocks))

    total = 0
    seen = {}
    out_blocks = []

    for block in blocks:
        m = re.search(r'url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)', block)
        if not m:
            continue
        url = m.group(1)
        if url not in seen:
            data = fetch(url, binary=True)
            name = hashlib.sha1(url.encode()).hexdigest()[:16] + '.woff2'
            with open(os.path.join(OUT_DIR, name), 'wb') as f:
                f.write(data)
            seen[url] = name
            total += len(data)
        name = seen[url]
        out_blocks.append(block.replace(m.group(0), 'url(./%s)' % name))

    header = ('/* Alexandria + Plus Jakarta Sans, served from this domain.\n'
              '   The files and the unicode-range sets are the ones Google was already\n'
              '   sending, so rendering is unchanged; only the origin is gone. */\n')
    with open(CSS_PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write(header + '\n'.join(out_blocks) + '\n')

    print('unique woff2 downloaded:', len(seen))
    print('total bytes: %.1f KB' % (total / 1024))
    print('css written: %.1f KB' % (os.path.getsize(CSS_PATH) / 1024))


if __name__ == '__main__':
    main()
