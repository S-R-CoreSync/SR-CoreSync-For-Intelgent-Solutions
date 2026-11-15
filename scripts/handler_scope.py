# -*- coding: utf-8 -*-
"""Who loads the shell script, who calls the handlers it defines, and what is truly missing."""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
pages = [('index.html', 'ar')]
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        pages.append((n + '/index.html', n))

print('%-6s %-22s %s' % ('lang', 'loads sr-master-shell', 'calls'))
for rel, lang in pages:
    s = open(os.path.join(ROOT, rel), encoding='utf-8', newline='').read()
    loads = 'yes' if 'sr-master-shell.js' in s else 'NO'
    calls = len(re.findall(r'data-sr-call="(?:closeAiEstimateModal|toggleHeroVoiceDictation|exportAiEstimatePdf|sendEstimateViaWhatsApp|switchEstimateCurrency|srPromptPwaInstall)"', s))
    print('%-6s %-22s %d' % (lang, loads, calls))

# where is srPromptPwaInstall defined?
print('\n--- definitions ---')
for name in ('srPromptPwaInstall', 'closeAiEstimateModal', 'toggleHeroVoiceDictation'):
    found = []
    for base, _, files in os.walk(ROOT):
        if any(x in base for x in ('_site', 'node_modules', '.git', 'docs')):
            continue
        for f in files:
            if not f.endswith(('.js', '.html')):
                continue
            p = os.path.join(base, f)
            try:
                c = open(p, encoding='utf-8', errors='ignore').read()
            except Exception:
                continue
            if re.search(r'function\s+%s\b|%s\s*=\s*function|window\.%s\s*=' % (name, name, name), c):
                found.append(os.path.relpath(p, ROOT))
    print('%-24s %s' % (name, ', '.join(sorted(set(found))[:3]) or 'NOT DEFINED'))
