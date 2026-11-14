import os, re
ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='').read()

def kb(x): return len(x.encode('utf-8')) / 1024

def span_of(marker, open_tag=r'<div'):
    i = s.find(marker)
    if i < 0:
        return None
    i = s.rfind(open_tag, 0, i + len(marker))
    depth = 0
    for t in re.finditer(r'<div\b|</div>', s[i:], re.I):
        if t.group(0).startswith('</'):
            depth -= 1
            if depth == 0:
                return i, i + t.end()
        else:
            depth += 1
    return None

total_hidden = 0
print('%-34s %8s' % ('block', 'size'))
for label, marker in [
    ('pane-dev (visible)', 'id="pricing-pane-dev"'),
    ('pane-erp (hidden)', 'id="pricing-pane-erp"'),
    ('pane-care (hidden)', 'id="pricing-pane-care"'),
    ('pane-creative (hidden)', 'id="pricing-pane-creative"'),
    ('tier matrix (Enterprise)', 'id="tier-matrix"'),
]:
    sp = span_of(marker)
    if not sp:
        print('%-34s %8s' % (label, 'n/a')); continue
    size = kb(s[sp[0]:sp[1]])
    if 'hidden' in label or 'matrix' in label:
        total_hidden += size
    print('%-34s %7.1f KB' % (label, size))

print('\nhidden blocks total: %.1f KB of the 116.6 KB pricing section' % total_hidden)
print('page total: %.1f KB' % kb(s))
print('as share of the page: %.1f%%' % (total_hidden / kb(s) * 100))

# do the panes get shown by clicking a tab?
tabs = re.findall(r'data-(?:pane|target)="([^"]+)"', s)
print('\ntab controls that switch panes:', len(tabs), tabs[:6])
