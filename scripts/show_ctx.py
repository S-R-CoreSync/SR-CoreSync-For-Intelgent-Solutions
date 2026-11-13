P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()
i = s.find('<section id="trust-metrics"')
print('--- 600 chars before ---')
print(s[max(0, i - 600):i])
print('--- 200 chars after ---')
j = s.find('</section>', i) + 10
print(s[j:j + 200])
