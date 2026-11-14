import os, re
ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='').read()

def kb(x): return len(x.encode('utf-8')) / 1024

for kw in ('tab-pane', 'matrix'):
    print('=== %s ===' % kw)
    for m in re.finditer(kw, s, re.I):
        line_start = s.rfind('\n', 0, m.start()) + 1
        snippet = s[line_start:line_start + 220].strip()
        print('  @%d  %s' % (m.start(), re.sub(r'\s+', ' ', snippet)[:170]))
    print()
