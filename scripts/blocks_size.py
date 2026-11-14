import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='').read()


def kb(x):
    return len(x.encode('utf-8')) / 1024


def block_from(marker_start, tag='div'):
    i = s.find(marker_start)
    if i < 0:
        return None, 0
    depth = 0
    for m in re.finditer(r'<%s\b|</%s>' % (tag, tag), s[i:], re.I):
        if m.group(0).startswith('</'):
            depth -= 1
            if depth == 0:
                return s[i:i + m.end()], kb(s[i:i + m.end()])
        else:
            depth += 1
    return None, 0

for label, start in [
    ('launchpad (29 langs)', '<div class="apple-launchpad'),
    ('project modal', 'id="projectModal"'),
    ('exec modal', 'class="sr-exec-modal'),
    ('pricing matrix', 'id="matrixRoot"'),
    ('consent overlay', 'id="cookieConsent"'),
]:
    b, size = block_from(start)
    print('%-22s %s' % (label, ('%.1f KB' % size) if b else 'not found'))

# every top-level section: name + size
print('\ntop-level sections by size:')
sections = re.findall(r'<section\b[^>]*>.*?</section>', s, re.S | re.I)
sizes = sorted(((kb(x), x) for x in sections), reverse=True)
total = sum(k for k, _ in sizes)
print('  %d sections, %.1f KB total' % (len(sizes), total))
for k, x in sizes[:8]:
    m = re.search(r'(?:id|class)="([^"]{0,48})', x)
    print('   %6.1f KB  %s' % (k, m.group(1) if m else '?'))

# the language launchpad: is it static markup for 29 languages?
i = s.find('apple-launchpad')
if i > 0:
    seg = s[i:i + 4000]
    print('\nlaunchpad sample:', re.sub(r'\s+', ' ', seg[:300]))
    print('launchpad language cards (class count):',
          len(re.findall(r'apple-launchpad-(?:item|lang|card)', s, re.I)))
