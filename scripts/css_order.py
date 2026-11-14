import os, re
ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='').read()

def kb(x): return len(x.encode('utf-8')) / 1024

events = []
for m in re.finditer(r'<link[^>]+rel="stylesheet"[^>]*>|<style[^>]*>.*?</style>', s, re.S | re.I):
    tag = m.group(0)
    if tag.startswith('<link'):
        href = re.search(r'href="([^"]+)"', tag)
        events.append(('link', href.group(1) if href else '?', m.start(), 0))
    else:
        sid = re.search(r'id="([^"]+)"', tag[:120])
        body = re.sub(r'^<style[^>]*>|</style>$', '', tag, flags=re.I | re.S)
        events.append(('style', sid.group(1) if sid else '(anonymous)', m.start(), kb(body)))

print('order in the document:')
seq = []
for kind, name, pos, size in events:
    seq.append(kind)
    if kind == 'style':
        print('  %6d  STYLE  %-28s %6.1f KB' % (pos, name[:28], size))
    else:
        print('  %6d  link   %s' % (pos, name[:70]))

# are the style blocks contiguous, or interleaved with links?
pattern = ''.join('S' if k == 'style' else 'L' for k in seq)
print('\nsequence:', pattern)
print('contiguous style runs:', len(re.findall(r'S+', pattern)))
print('style blocks before the first link:', pattern.find('S') < pattern.find('L') if 'L' in pattern else True)
