import re
P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\partials\en\22-pricing.html'
s = open(P, encoding='utf-8', newline='').read()
for cls in ('pricing-card-btn-wa', 'pricing-card-btn-gold', 'pricing-card-btn-pdf'):
    print('%-22s %d' % (cls, len(re.findall(re.escape(cls), s))))
print()
# every element carrying a button class, with its visible span text
for m in re.finditer(r'<(a|button)[^>]*class="(pricing-card-btn-[a-z0-9-]+)"[^>]*>(.{0,160})', s, re.S):
    txt = re.sub(r'<[^>]+>', ' ', m.group(3))
    txt = re.sub(r'\s+', ' ', txt).strip()
    print('  %-7s %-24s %s' % (m.group(1), m.group(2), txt[:46]))
