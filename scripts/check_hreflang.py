#!/usr/bin/env python
"""Every page must agree with the other twenty-eight about where each language lives.

Twenty-six pages shipped with a canonical pointing at /en/, which tells Google
that the German, Dutch, French… pages are copies of the English one. This guard
exists so that cannot happen silently again: it checks, for each of the 29
pages, the canonical, the html lang/dir, and the full hreflang set including
x-default.

    python scripts/check_hreflang.py           # report, exit 1 on any fault
    python scripts/check_hreflang.py --quiet   # only failures
"""
import os
import re
import sys

# resolved from this file, so the same guard runs on the runner and on Windows
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://sr-coresync.com'
# Kurmanji (ku) is written in Latin letters, so it is LTR; Sorani (ckb) is not.

RTL = {'ar', 'ckb'}

PAGES = ['ar']
SKIP = {'_site', 'build', 'node_modules', 'scripts', 'docs', 'partials', 'assets', 'i18n', 'js', 'css', 'workers', '.git', '.githooks', '.zwork'}
for name in sorted(os.listdir(ROOT)):
    if name in SKIP or name.startswith(('.', '_')):
        continue
    if os.path.isdir(os.path.join(ROOT, name)) and os.path.exists(os.path.join(ROOT, name, 'index.html')):
        PAGES.append(name)

EXPECTED_CODES = set(PAGES)


def path_of(lang):
    return os.path.join(ROOT, 'index.html') if lang == 'ar' else os.path.join(ROOT, lang, 'index.html')


def url_of(lang):
    base = BASE + '/'
    return base if lang == 'ar' else '%s%s/' % (base, lang)


def check_page(lang):
    html = open(path_of(lang), encoding='utf-8', newline='').read()
    faults = []

    m = re.search(r'<html[^>]*\blang="([^"]*)"', html, re.I)
    if not m:
        faults.append('no lang on <html>')
    elif m.group(1).lower() != lang:
        faults.append('html lang="%s" but the page is %s' % (m.group(1), lang))

    m = re.search(r'<html[^>]*\bdir="([^"]*)"', html, re.I)
    want_dir = 'rtl' if lang in RTL else 'ltr'
    if not m:
        faults.append('no dir on <html>')
    elif m.group(1).lower() != want_dir:
        faults.append('dir="%s" but %s should be %s' % (m.group(1), lang, want_dir))

    canons = re.findall(r'<link[^>]+rel="canonical"[^>]*href="([^"]+)"', html, re.I)
    if len(canons) != 1:
        faults.append('%d canonical links' % len(canons))
    elif canons[0].rstrip('/') != url_of(lang).rstrip('/'):
        faults.append('canonical is %s, should be %s' % (canons[0], url_of(lang)))

    pairs = re.findall(r'<link[^>]+hreflang="([^"]+)"[^>]*href="([^"]+)"', html, re.I)
    if not pairs:
        pairs = [(c, u) for u, c in re.findall(r'<link[^>]+href="([^"]+)"[^>]*hreflang="([^"]+)"', html, re.I)]
    codes = [c for c, _ in pairs]
    if len(codes) != len(set(codes)):
        faults.append('duplicate hreflang: %s' % sorted({c for c in codes if codes.count(c) > 1}))

    missing = EXPECTED_CODES - set(codes)
    extra = set(codes) - EXPECTED_CODES - {'x-default'}
    if missing:
        faults.append('missing hreflang: %s' % ' '.join(sorted(missing)))
    if extra:
        faults.append('unknown hreflang: %s' % ' '.join(sorted(extra)))

    for code, href in pairs:
        want = url_of('ar') if code == 'x-default' else url_of(code)
        if href.rstrip('/') != want.rstrip('/'):
            faults.append('hreflang %s -> %s, expected %s' % (code, href, want))

    return faults


def main():
    quiet = '--quiet' in sys.argv
    broken = 0
    for lang in PAGES:
        faults = check_page(lang)
        if faults:
            broken += 1
            print('%-4s %d fault(s)' % (lang, len(faults)))
            for f in faults:
                print('       - ' + f)
        elif not quiet:
            print('%-4s ok' % lang)

    print('\n%d page(s) checked, %d with faults' % (len(PAGES), broken))
    return 1 if broken else 0


if __name__ == '__main__':
    raise SystemExit(main())
