import re
P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()
i = s.find('class="testimonial')
seg = re.sub(r'\s+', ' ', s[i - 40:i + 700])
print(seg[:650])
print()
print('count testimonial items:', len(re.findall(r'class="testimonial-item"', s)))
for cls in ('testimonial-text', 'testimonial-name', 'testimonial-role', 'testimonial-company', 'testimonial-quote'):
    print('%-20s %d' % (cls, len(re.findall(re.escape(cls), s))))
