import re, os
from PIL import Image

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
P = os.path.join(ROOT, 'index.html')
s = open(P, encoding='utf-8', newline='').read()

pat = re.compile(r'<img\s+src="\./assets/flags/([a-z\-]+)\.png"[^>]*class="apple-dock-flag"[^>]*>')
codes = list(dict.fromkeys(pat.findall(s)))
print('flags found:', len(codes))

W, H = 28, 19
sprite = Image.new('RGBA', (W, H * len(codes)), (0, 0, 0, 0))
for i, code in enumerate(codes):
    p = os.path.join(ROOT, 'assets', 'flags', code + '.png')
    im = Image.open(p).convert('RGBA').resize((W, H), Image.LANCZOS)
    sprite.paste(im, (0, i * H), im)

out = os.path.join(ROOT, 'assets', 'flags-sprite.webp')
sprite.save(out, 'WEBP', quality=90, method=6, lossless=False)
print('sprite: %dx%d  %.1f KB' % (sprite.size[0], sprite.size[1], os.path.getsize(out) / 1024))

# CSS
rules = ['.apple-dock-flag{display:inline-block;width:%dpx;height:%dpx;background-image:url(./assets/flags-sprite.webp);background-repeat:no-repeat;background-size:%dpx %dpx}' % (W, H, W, H * len(codes))]
for i, code in enumerate(codes):
    rules.append('.apple-dock-flag--%s{background-position:0 -%dpx}' % (code, i * H))
css = '\n'.join(rules)

# replace tags with spans
for code in codes:
    s = re.sub(r'<img\s+src="\./assets/flags/%s\.png"[^>]*class="apple-dock-flag"[^>]*>' % code,
               '<span class="apple-dock-flag apple-dock-flag--%s" role="img" aria-label="%s"></span>' % (code, code.upper()),
               s)

if 'id="flags-sprite"' not in s:
    i = s.lower().index('</head>')
    s = s[:i] + '<style id="flags-sprite">\n' + css + '\n</style>\n' + s[i:]

open(P, 'w', encoding='utf-8', newline='').write(s)
print('img tags left for flags:', len(pat.findall(s)))
