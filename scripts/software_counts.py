import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
pages = [('index.html', 'ar')]
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        pages.append((n + '/index.html', n))

for cls in ('software-card-desc', 'software-card-title', 'software-card-badge'):
    counts = []
    for rel, _ in pages:
        s = open(os.path.join(ROOT, rel), encoding='utf-8', newline='').read()
        counts.append(len(re.findall(re.escape(cls), s)))
    print('%-22s min=%d max=%d distinct=%s' % (cls, min(counts), max(counts), sorted(set(counts))))
