import re, os
ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
LANGS = ['ar','bg','cs','da','de','el','en','es','et','fi','fr','ga','hr','hu','it','ku',
         'lt','lv','mt','nl','no','pl','pt','ro','sk','sl','sv','tr']

rows = []
for lang in LANGS:
    p = os.path.join(ROOT, 'index.html') if lang == 'ar' else os.path.join(ROOT, lang, 'index.html')
    if not os.path.exists(p):
        rows.append((lang, 'MISSING', '', '', '')); continue
    h = open(p, encoding='utf-8', newline='').read()
    codes = re.findall(r'<link[^>]+hreflang="([^"]+)"', h, re.I)
    canon = re.search(r'<link[^>]+rel="canonical"[^>]*href="([^"]+)"', h, re.I)
    canon = canon.group(1) if canon else '-'
    expect = 'https://sr-coresync.com/' if lang == 'ar' else 'https://sr-coresync.com/%s/' % lang
    ok = 'OK' if canon.rstrip('/') == expect.rstrip('/') else 'WRONG'
    rows.append((lang, len(codes), ','.join(c for c in codes if c == 'x-default' or '-' in c) or '-', canon, ok))

print('%-4s %-6s %-14s %-46s %s' % ('lang', 'tags', 'special', 'canonical', 'verdict'))
bad = 0
for r in rows:
    if r[4] != 'OK':
        bad += 1
    print('%-4s %-6s %-14s %-46s %s' % r)
print('\ncanonical wrong/missing:', bad, 'of', len(rows))

# the full code list of the arabic page, to explain the 30
h = open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='').read()
codes = re.findall(r'<link[^>]+hreflang="([^"]+)"', h, re.I)
print('\nar codes (%d):' % len(codes), ' '.join(codes))
print('duplicates:', [c for c in set(codes) if codes.count(c) > 1])
