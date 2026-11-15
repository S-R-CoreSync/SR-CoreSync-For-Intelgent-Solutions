import re
P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()
for cls in ('software-card', 'sw-card', 'software-item', 'app-card', 'product-card'):
    print('%-16s %d' % (cls, len(re.findall(re.escape(cls), s))))
i = s.find('class="software-card')
print()
print(re.sub(r'\s+', ' ', s[i - 40:i + 700])[:650] if i > 0 else 'no software-card')
