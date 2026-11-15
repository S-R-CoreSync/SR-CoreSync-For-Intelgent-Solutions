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
    q = len(re.findall(r'data-i18n="testimonials\.\d\d\.quote"', s))
    r = len(re.findall(r'data-i18n="testimonials\.\d\d\.rating"', s))
    if q != 5 or r != 5:
        bad.append((lang, q, r))
print('pages:', len(pages), '· wrong counts:', bad if bad else 'none')

# text integrity on the root: removing the new attributes must give the old file
a = open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='').read()
b = open(os.path.join(os.environ['TEMP'], 'idx-t-before.html'), encoding='utf-8', newline='').read()
strip = lambda x: re.sub(r' data-i18n="testimonials\.\d\d\.(?:quote|rating)"', '', x)
print('root text unchanged:', strip(a) == strip(b))
