import re, os
ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
LANGS = ['en','de','nl','fr','es','it','pl','pt','ro','sv','cs','tr','el','da','no','fi','hu','sk','sl','hr','lt','lv','et','mt','ga','ku','bg']

# read codes and sprite height from the master sprite CSS
master = open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='').read()
positions = dict(re.findall(r'\.apple-dock-flag--([a-z\-]+)\{background-position:0 -(\d+)px\}', master))
if not positions:
    raise SystemExit('no sprite positions found in the master')
H = 19
total = len(positions) * H
print('codes:', len(positions))

rules = ['.apple-dock-flag{display:inline-block;width:28px;height:19px;background-image:url(../assets/flags-sprite.webp);background-repeat:no-repeat;background-size:28px %dpx}' % total]
for code, pos in positions.items():
    rules.append('.apple-dock-flag--%s{background-position:0 -%spx}' % (code, pos))
css = '\n'.join(rules)

done = 0
for lang in LANGS:
    p = os.path.join(ROOT, lang, 'index.html')
    if not os.path.exists(p):
        continue
    s = open(p, encoding='utf-8', newline='').read()
    n = 0
    for code in positions:
        s, k = re.subn(r'<img\s+src="\.\./assets/flags/%s\.png"[^>]*class="apple-dock-flag"[^>]*>' % code,
                       '<span class="apple-dock-flag apple-dock-flag--%s" role="img" aria-label="%s"></span>' % (code, code.upper()),
                       s)
        n += k
    if n == 0:
        print('%-3s no flag images' % lang)
        continue
    if 'id="flags-sprite"' not in s:
        low = s.lower(); h = low.find('</head'); i = s.index('>', h) + 1
        s = s[:i] + '<style id="flags-sprite">\n' + css + '\n</style>\n' + s[i:]
    open(p, 'w', encoding='utf-8', newline='').write(s)
    done += 1
    print('%-3s %d flags -> sprite' % (lang, n))
print('pages updated:', done)
