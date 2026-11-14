P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()
i = s.find('class="wg-plan"')
block = s[i - 80:i + 1500]
print(block)
