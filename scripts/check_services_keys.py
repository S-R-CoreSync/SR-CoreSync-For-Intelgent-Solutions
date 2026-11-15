import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
pages = [('index.html', 'ar')]
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        pages.append((n + '/index.html', n))

bad = []
for rel, lang in pages:
    s = open(os.path.join(ROOT, rel), encoding='utf-8', newline='').read()
    c = len(re.findall(r'data-i18n="services\.', s))
    if c != 6:
        bad.append((lang, c))
print('pages:', len(pages), '· with != 6 services keys:', bad if bad else 'none')
