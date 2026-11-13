import re, os
ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
pat = re.compile(r"(setProperty\(\s*['\"]order|\.style\.order\s*=|['\"]order['\"]\s*[,:])", re.I)
hits = 0
for dirpath, dirnames, files in os.walk(ROOT):
    if any(x in dirpath for x in ('_site', 'node_modules', '.git', 'partials')):
        continue
    for f in files:
        if not f.endswith(('.js', '.html', '.mjs')):
            continue
        p = os.path.join(dirpath, f)
        try:
            s = open(p, encoding='utf-8', errors='ignore').read()
        except Exception:
            continue
        for m in pat.finditer(s):
            line = s.count('\n', 0, m.start()) + 1
            ctx = s[max(0, m.start() - 90):m.start() + 110].replace('\n', ' ')
            print('%-28s %5d  %s' % (os.path.relpath(p, ROOT), line, ctx[:190]))
            hits += 1
            if hits > 14:
                raise SystemExit
print('total', hits)
