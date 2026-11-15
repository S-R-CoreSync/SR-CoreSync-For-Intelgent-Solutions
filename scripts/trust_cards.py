import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
pages = [('index.html', 'ar')]
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        pages.append((n + '/index.html', n))

counts = []
for rel, _ in pages:
    s = open(os.path.join(ROOT, rel), encoding='utf-8', newline='').read()
    counts.append(len(re.findall(r'class="trust-card"', s)))
print('trust-card per page:', sorted(set(counts)), '· pages:', len(pages))

s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='').read()
i = s.find('class="trust-card"')
print()
print(re.sub(r'\s+', ' ', s[i - 60:i + 700])[:660])
