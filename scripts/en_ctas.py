import collections, re
P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\partials\en\22-pricing.html'
s = open(P, encoding='utf-8', newline='').read()
pat = re.compile(r'<a[^>]*class="(pricing-card-btn-[a-z0-9-]+)"[^>]*>\s*<span[^>]*>([^<]{0,60})')
found = pat.findall(s)
print('cta anchors found:', len(found))
for cls, text in found:
    print('  %-24s %s' % (cls, text.strip()[:48]))
print()
# how many plans in each pane
print('panes:', len(re.findall(r'id="pricing-pane-', s)))
print('wg-plan:', len(re.findall(r'class="wg-plan"', s)))
