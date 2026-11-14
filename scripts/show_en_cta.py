import re
s = open(r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\en\index.html', encoding='utf-8', newline='').read()
i = s.find('pricing-card-actions')
seg = s[i:i + 1100]
seg = re.sub(r'href="[^"]{40,}"', 'href="…"', seg)
seg = re.sub(r'\s+', ' ', seg)
print(seg[:800])
