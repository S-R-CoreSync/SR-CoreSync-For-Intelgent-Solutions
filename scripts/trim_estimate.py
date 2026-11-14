import os, re, gzip
ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='').read()

def kb(x): return len(x.encode('utf-8')) / 1024

comments = re.findall(r'<!--.*?-->', s, re.S)
print('HTML comments: %d blocks, %.1f KB' % (len(comments), sum(kb(c) for c in comments)))

svgs = re.findall(r'<svg\b.*?</svg>', s, re.S | re.I)
uniq = {}
for x in svgs:
    key = hashlib_key = __import__('hashlib').sha1(x.encode()).hexdigest()
    uniq.setdefault(key, []).append(x)
dup_bytes = sum((len(v) - 1) * kb(v[0]) for v in uniq.values() if len(v) > 1)
print('inline <svg>: %d blocks, %d distinct, %.1f KB' % (len(svgs), len(uniq), sum(kb(x) for x in svgs)))
print('   recoverable by a sprite of the repeats: %.1f KB raw' % dup_bytes)
top = sorted(((len(v), kb(v[0])) for v in uniq.values() if len(v) > 1), reverse=True)[:4]
print('   most repeated:', top)

print('\nprojected effect of each lever on the *gzipped* transfer:')
raw = s.encode()
g0 = len(gzip.compress(raw, 9)) / 1024
def after(remove_text):
    t = s
    for x in remove_text:
        t = t.replace(x, '', 1)
    return len(gzip.compress(t.encode(), 9)) / 1024

print('   now                      %.1f KB gz' % g0)
print('   without html comments    %.1f KB gz' % after(comments))
# whitespace between tags only (safe-ish subset: newline + spaces between > and <)
import re as _re
tight = _re.sub(r'>\s{2,}<', '><', s)
print('   collapsed inter-tag gaps %.1f KB gz' % (len(gzip.compress(tight.encode(), 9)) / 1024))
