# -*- coding: utf-8 -*-
"""
Which style sources does the master load that English does not?

    python scripts/style_sources.py
"""
import re, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sources(path):
    s = open(path, encoding='utf-8', newline='').read()
    links = re.findall(r'<link\b[^>]*rel="stylesheet"[^>]*href="([^"]+)"', s)
    links += [h for h in re.findall(r'<link\b[^>]*href="([^"]+)"[^>]*rel="stylesheet"', s)]
    styles = re.findall(r'<style\b[^>]*id="([^"]*)"', s)
    return {'links': list(dict.fromkeys(links)), 'inline': list(dict.fromkeys(styles))}


def main():
    a = sources(os.path.join(ROOT, 'index.html'))
    b = sources(os.path.join(ROOT, 'en', 'index.html'))

    na = {os.path.basename(x.split('?')[0]) for x in a['links']}
    nb = {os.path.basename(x.split('?')[0]) for x in b['links']}
    print('stylesheet files — master:', len(na), ' english:', len(nb))
    print('missing in english:', sorted(na - nb))
    print('extra in english  :', sorted(nb - na))
    print()
    print('inline style blocks — master:', len(a['inline']), ' english:', len(b['inline']))
    print('missing in english:', [x for x in a['inline'] if x not in b['inline']][:12])
    print('extra in english  :', [x for x in b['inline'] if x not in a['inline']][:12])


if __name__ == '__main__':
    main()
