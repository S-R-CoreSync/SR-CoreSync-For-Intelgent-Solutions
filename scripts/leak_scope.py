# -*- coding: utf-8 -*-
"""Which languages actually carry the English block, and how much of it."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translations_batch import DE

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
LANGS = ['bg','ckb','cs','da','de','el','en','es','et','fi','fr','ga','hr','hu','it','ku',
         'lt','lv','mt','nl','no','pl','pt','ro','sk','sl','sv','tr']

keys = list(DE.keys())
print('%-4s %s' % ('lang', 'matched of 33'))
scope = []
for lang in LANGS:
    p = os.path.join(ROOT, lang, 'index.html')
    s = open(p, encoding='utf-8', newline='').read()
    hits = sum(1 for k in keys if k in s)
    scope.append((lang, hits))
    print('%-4s %d' % (lang, hits))

need = [l for l, h in scope if h >= 5]
print('\nlanguages that need work (>=5 leaked lines):', ' '.join(need))
print('total pages:', len(need))
