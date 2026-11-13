# -*- coding: utf-8 -*-
"""
Guard: every data-sr-args attribute must be valid JSON.

This is the class of failure that showed up as a black portrait: a payload
carrying a raw newline or a stray quote made JSON.parse throw, the handler
died before doing its work, and nothing in the UI said why.

    python scripts/check_sr_args.py            # scan every page
    python scripts/check_sr_args.py --page en  # scan one
"""
import re, os, sys, json, html, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'scripts', 'i18n', 'css', 'js', 'docs', 'assets', 'templates', 'node_modules', '_site', '_site.next'}
ATTR = re.compile(r"data-sr-args\s*=\s*(['\"])(.*?)\1", re.S)


def pages(only=None):
    if only:
        p = os.path.join(ROOT, only, 'index.html') if os.path.isdir(os.path.join(ROOT, only)) else os.path.join(ROOT, 'index.html')
        return [p]
    out = [os.path.join(ROOT, 'index.html')]
    for d in sorted(os.listdir(ROOT)):
        if d in SKIP or not os.path.isdir(os.path.join(ROOT, d)):
            continue
        p = os.path.join(ROOT, d, 'index.html')
        if os.path.exists(p):
            out.append(p)
    return out


def check(path):
    src = open(path, encoding='utf-8', newline='').read()
    bad = []
    for m in ATTR.finditer(src):
        raw = html.unescape(m.group(2))
        try:
            json.loads(raw)
        except Exception as e:
            line = src.count('\n', 0, m.start()) + 1
            call = ''
            seg = src[max(0, m.start() - 220):m.start()]
            cm = re.search(r'data-sr-call="([^"]+)"', seg)
            if cm:
                call = cm.group(1)
            bad.append((line, call, str(e), raw[:70]))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--page')
    a = ap.parse_args()

    total, failures = 0, 0
    for p in pages(a.page):
        bad = check(p)
        total += 1
        if not bad:
            continue
        failures += 1
        rel = os.path.relpath(p, ROOT)
        print('FAIL', rel)
        for line, call, err, sample in bad[:6]:
            print('   line %-6d %-28s %s' % (line, call or '(no call)', err))
            print('      %s' % sample)
    print('\n%d page(s) scanned, %d with invalid payloads' % (total, failures))
    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
