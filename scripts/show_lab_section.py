import re
P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\partials\en\23-store.html'
s = open(P, encoding='utf-8', newline='').read()
i = s.find('softwareArchitectLab')
start = s.rfind('<section', 0, i)
# find the matching </section>
depth = 0
end = None
for m in re.finditer(r'<section\b|</section>', s[start:], re.I):
    depth += -1 if m.group(0).startswith('</') else 1
    if depth == 0:
        end = start + m.end()
        break
block = s[start:end]
print('section bytes: %.1f KB' % (len(block.encode()) / 1024))
print(re.sub(r'\s+', ' ', block[:900]))
