import re
P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()
i = s.find('class="dana-card"')
seg = s[i - 60:i + 900]
seg = re.sub(r'\s+', ' ', seg)
print(seg[:800])
