import re
P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()
i = s.find('class="tes-author"')
seg = re.sub(r'\s+', ' ', s[i:i + 1400])
seg = re.sub(r'<use[^>]*>', '', seg)
print(seg[:900])
