import os, re, gzip

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='').read()

def kb(x):
    return len(x.encode('utf-8')) / 1024

data_uris = re.findall(r'data:[a-z/+]+;base64,[A-Za-z0-9+/=]+', s)
print('base64 data URIs: %d files, %.1f KB' % (len(data_uris), sum(kb(x) for x in data_uris)))
for x in sorted(data_uris, key=kb, reverse=True)[:5]:
    print('   %6.1f KB  %s…' % (kb(x), x[:48]))

svgs = re.findall(r'<svg\b.*?</svg>', s, re.S | re.I)
print('\ninline <svg>: %d blocks, %.1f KB' % (len(svgs), sum(kb(x) for x in svgs)))
for x in sorted(svgs, key=kb, reverse=True)[:4]:
    print('   %6.1f KB  %s…' % (kb(x), re.sub(r'\s+', ' ', x[:60])))

# how much markup is inside the four big modal/overlay containers?
for marker in ('appleMacosLaunchpad', 'srStudioI18nModal', 'projectModal', 'sr-exec-modal'):
    i = s.find(marker)
    print('%-22s %s' % (marker, 'found' if i > 0 else '—'))

# rough duplication probe: longest repeated line runs
lines = [l for l in s.split('\n') if len(l) > 400]
print('\nlines longer than 400 chars: %d, total %.1f KB' % (len(lines), sum(kb(l) for l in lines)))
longest = max(lines, key=kb) if lines else ''
print('longest line %.1f KB' % kb(longest))

# count of repeated identical long chunks
from collections import Counter
c = Counter(lines)
dup = [(v, k) for k, v in c.items() if v > 1]
print('repeated long lines: %d (total wasted %.1f KB)' % (len(dup), sum((v - 1) * kb(k) for v, k in dup)))
for v, k in sorted(dup, key=lambda t: -(t[0] * kb(t[1])))[:3]:
    print('   x%d %.1f KB each: %s…' % (v, kb(k), k[:60]))
