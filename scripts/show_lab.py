import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='').read()
i = s.find('softwareArchitectLab')
print('found at', i)
if i > 0:
    print(re.sub(r'\s+', ' ', s[i - 200:i + 900])[:900])
