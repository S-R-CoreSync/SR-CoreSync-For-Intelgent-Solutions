import re
P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\partials\en\22-pricing.html'
s = open(P, encoding='utf-8', newline='').read()
starts = [m.start() for m in re.finditer(r'class="wg-plan"', s)]
print('plans:', len(starts))
end = starts[1] if len(starts) > 1 else len(s)
block = s[starts[0]:end]
print('block chars:', len(block))
seg = re.sub(r'\s+', ' ', block)
seg = re.sub(r'href="[^"]{25,}"', 'href="…"', seg)
print(seg[-700:])
