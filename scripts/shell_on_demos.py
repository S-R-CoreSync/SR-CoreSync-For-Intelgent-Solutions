# -*- coding: utf-8 -*-
"""The 28 demo pages call the same six handlers; they need the script too."""
import os

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
TAG = '<script src="../js/sr-master-shell.js" defer></script>'

n = 0
for d in sorted(os.listdir(ROOT)):
    p = os.path.join(ROOT, d, 'demo.html')
    if not os.path.isfile(p):
        continue
    s = open(p, encoding='utf-8', newline='').read()
    if 'sr-master-shell.js' in s:
        print('%-6s already' % d)
        continue
    i = s.rfind('</body>')
    if i < 0:
        print('%-6s no </body>' % d)
        continue
    open(p, 'w', encoding='utf-8', newline='').write(s[:i] + TAG + '\r\n' + s[i:])
    n += 1

print('demo pages updated:', n)
