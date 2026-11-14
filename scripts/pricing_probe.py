import os, re, gzip
ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='').read()

def kb(x): return len(x.encode('utf-8')) / 1024

i = s.find('<section')
# find the pricing section
m = re.search(r'<section[^>]*class="[^"]*section-pricing[^"]*"[^>]*>', s)
if not m:
    raise SystemExit('pricing section not found')
start = m.start()
depth = 0
end = None
for t in re.finditer(r'<section\b|</section>', s[start:], re.I):
    if t.group(0).startswith('</'):
        depth -= 1
        if depth == 0:
            end = start + t.end(); break
    else:
        depth += 1
sec = s[start:end]
print('pricing section: %.1f KB' % kb(sec))

# what is inside: list child blocks with sizes
print('\nchildren (first level):')
inner = sec[sec.find('>') + 1:]
depth = 0
children = []
pos = 0
for t in re.finditer(r'<(div|section|table|ul)\b|</(div|section|table|ul)>', inner, re.I):
    if t.group(0).startswith('</'):
        depth -= 1
        if depth == 0:
            children.append(inner[pos:t.end()])
            pos = t.end()
    else:
        if depth == 0:
            pos = t.start()
        depth += 1
for c in sorted(children, key=kb, reverse=True)[:6]:
    cls = re.search(r'class="([^"]{0,60})', c)
    print('   %6.1f KB  %s' % (kb(c), cls.group(1) if cls else c[:50]))

# hidden by default?
for marker in ('data-bs-toggle="tab"', 'hidden', 'display:none', 'aria-hidden="true"', 'tab-pane'):
    print('%-22s %d' % (marker, len(re.findall(re.escape(marker), sec))))

# the matrix specifically
for name in ('matrix', 'compare', 'comparison', 'feature-table', 'pricing-matrix'):
    print('%-22s %d occurrences' % (name, len(re.findall(name, sec, re.I))))
