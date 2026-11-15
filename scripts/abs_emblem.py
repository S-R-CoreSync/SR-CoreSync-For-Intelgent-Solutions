# -*- coding: utf-8 -*-
"""A relative './assets/...' inside a shared script resolves inside /de/ on subpages.

The site is served from the domain root, so the emblem belongs at /assets/.
"""
import os

P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\js\sr-master-shell.js'
s = open(P, encoding='utf-8', newline='').read()
old = 'src="./assets/sr-core-emblem.svg"'
new = 'src="/assets/sr-core-emblem.svg"'
n = s.count(old)
if n:
    open(P, 'w', encoding='utf-8', newline='').write(s.replace(old, new))
print('references made absolute:', n)
