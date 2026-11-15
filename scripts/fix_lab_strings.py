# -*- coding: utf-8 -*-
"""Two strings slipped: the badge (entity-encoded apostrophe) and the long paragraph (not in the map)."""
import os, re

P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\partials\23-store.html'
s = open(P, encoding='utf-8', newline='').read()

badge = re.compile(r'🚀\s*FOUNDER[^<]{0,60}COMMERCIAL DISTRIBUTION PORTAL', re.I)
s, n1 = badge.subn('🚀 مختبر المؤسس وبوابة التوزيع التجاري', s, count=1)

longp = re.compile(r'S&amp;R CoreSync For Intelligent Solutions delivers an enterprise-grade commercialization.*?European enterprise compliance\.', re.S)
if not longp.search(s):
    longp = re.compile(r'S&R CoreSync For Intelligent Solutions delivers an enterprise-grade commercialization.*?European enterprise compliance\.', re.S)

AR = ('تُقدّم S&amp;R CoreSync For Intelligent Solutions بنية تحتية للتوزيع التجاري بمستوى المؤسسات، '
      'مصمّمة لمهندسي البرمجيات وكبار المصممين. انشر أدواتك المكتبية المستقلة وواجهاتك البرمجية '
      'ومشاريعك السحابية داخل إطارنا القانوني الموثّق: مفاتيح ترخيص مشفّرة، وفوترة آلية عبر SEPA وiDEAL، '
      'وامتثال أوروبي كامل.')
s, n2 = longp.subn(AR, s, count=1)

open(P, 'w', encoding='utf-8', newline='').write(s)
print('badge replaced:', n1, '· paragraph replaced:', n2)

# verify with a real parser
import lxml.html
i = s.find('id="softwareArchitectLab"')
start = s.rfind('<div', 0, i)
depth = 0
for m in re.finditer(r'<div\b|</div>', s[start:], re.I):
    depth += -1 if m.group(0).startswith('</') else 1
    if depth == 0:
        block = s[start:start + m.end()]
        break
doc = lxml.html.fromstring(block)
left = [re.sub(r'\s+', ' ', (c or '').strip()) for el in doc.iter() if isinstance(el.tag, str)
        for c in (el.text, el.tail) if c and len(c.strip()) > 8 and re.search(r'[A-Za-z]{4,}', c)
        and not re.search(r'[\u0600-\u06FF]', c)]
print('latin text left in the block:', left if left else 'none')
