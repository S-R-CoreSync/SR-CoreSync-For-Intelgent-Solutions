import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
P = os.path.join(ROOT, 'index.html')
s = open(P, encoding='utf-8', newline='').read()

i = s.find('Legally binding European regulatory certifications')
start = s.rfind('<', 0, i)
print('context:', re.sub(r'\s+', ' ', s[max(0, i - 400):i + 80])[-460:])
print()
for cls in ('trust-card', 'compliance-card', 'cert-card', 'shield-card', 'ribbon-item'):
    print('%-18s %d' % (cls, len(re.findall(re.escape(cls), s))))
