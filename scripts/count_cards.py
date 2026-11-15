import re
P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()
for pat in ('class="dana-card"', 'dana-card-title"', 'dana-card-desc"', 'dana-card-icon"'):
    print('%-22s %d' % (pat, len(re.findall(re.escape(pat), s))))
m = re.search(r'dana-card-desc[^>]*>([^<]{0,90})', s)
print('desc sample:', (m.group(1).strip() if m else 'none'))
