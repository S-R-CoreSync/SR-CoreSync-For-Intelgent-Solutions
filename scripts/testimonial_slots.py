import re
P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()
for cls in ('testimonial-v01', 'tes-text', 'tes-author', 'author_info', 'author-name', 'author-role', 'tes-rating'):
    print('%-18s %d' % (cls, len(re.findall(re.escape(cls), s))))
# what follows the author block
i = s.find('class="tes-author"')
print()
print(re.sub(r'\s+', ' ', s[i:i + 500])[:480])
