import re
P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\partials\en\22-pricing.html'
s = open(P, encoding='utf-8', newline='').read()
starts = [m.start() for m in re.finditer(r'class="wg-plan"', s)]
end = starts[1] if len(starts) > 1 else len(s)
block = s[starts[0]:end]
i = block.find('pricing-card-actions')
seg = re.sub(r'\s+', ' ', block[i:i + 600])
seg = re.sub(r'href="[^"]{30,}"', 'href="…"', seg)
print(seg[:560])
