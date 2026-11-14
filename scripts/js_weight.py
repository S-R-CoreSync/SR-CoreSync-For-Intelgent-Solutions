import gzip, os, re
ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
os.chdir(ROOT)
for f in ['js/sr-lang-map.js', 'js/sr-software-apps.js', 'js/enterprise-suite.min.js',
          'js/sr-inline-13eaa28e.js', 'js/sr-master-shell.js', 'css/dananajmah-bundle.min.css']:
    d = open(f, 'rb').read()
    print('%-34s %7.1f KB raw  %6.1f KB gz' % (f, len(d) / 1024, len(gzip.compress(d, 9)) / 1024))

print('\n--- sr-lang-map.js head ---')
s = open('js/sr-lang-map.js', encoding='utf-8', errors='replace').read()
print(re.sub(r'\s+', ' ', s[:300]))
print('language codes found:', len(re.findall(r'"[a-z]{2}"\s*:', s)))
print('looks like a dictionary of:', 'translations' if '{"' in s[:200] else 'mapping')
