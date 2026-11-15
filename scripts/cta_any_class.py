# -*- coding: utf-8 -*-
"""Count every pricing button whatever its class, so a rename is not mistaken for a gap."""
import os, re

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
pages = [('index.html', 'ar')]
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts',
                                         'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        pages.append((n + '/index.html', n))

print('%-4s %-9s %-10s %s' % ('lang', 'actions', 'buttons', 'classes'))
for rel, lang in pages:
    s = open(os.path.join(ROOT, rel), encoding='utf-8', newline='').read()
    actions = len(re.findall(r'pricing-card-actions', s))
    btns = re.findall(r'<(?:a|button)[^>]*class="(pricing-card-btn[^"]*)"', s)
    kinds = {}
    for b in btns:
        kinds[b] = kinds.get(b, 0) + 1
    print('%-4s %-9d %-10d %s' % (lang, actions, len(btns),
                                  ', '.join('%s=%d' % (k.replace('pricing-card-btn-', ''), v) for k, v in sorted(kinds.items()))))
