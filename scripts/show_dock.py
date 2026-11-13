P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\index.html'
s = open(P, encoding='utf-8', newline='').read()
i = s.find('<aside class="apple-macos-dock-wrapper"')
print(s[i:i + 2800])
