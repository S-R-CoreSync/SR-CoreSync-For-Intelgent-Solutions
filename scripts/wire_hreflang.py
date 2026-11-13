"""Wire the hreflang guard into preflight and into the deploy gate."""
import re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'

# 1 · preflight
p = ROOT + r'\scripts\preflight.py'
s = open(p, encoding='utf-8', newline='').read()
if 'check_hreflang.py' not in s:
    anchor = "    ('event payloads', ['scripts/check_sr_args.py']),"
    assert anchor in s
    s = s.replace(anchor, "    ('hreflang agreement', ['scripts/check_hreflang.py']),\r\n" + anchor, 1)
    open(p, 'w', encoding='utf-8', newline='').write(s)
    print('preflight: guard added')
else:
    print('preflight: already there')

# 2 · deploy workflow
w = ROOT + r'\.github\workflows\deploy-pages.yml'
y = open(w, encoding='utf-8', newline='').read()
if 'check_hreflang.py' not in y:
    anchor = '          python scripts/check_sr_args.py'
    assert anchor in y, 'workflow anchor missing'
    y = y.replace(anchor, '          python scripts/check_hreflang.py\n' + anchor, 1)
    open(w, 'w', encoding='utf-8', newline='').write(y)
    print('workflow: guard added')
else:
    print('workflow: already there')
