"""Verify that every English block still on a locale page is covered by its dictionary.

The runtime layer (js/sr-content-i18n.js) matches text exactly first, then falls
back to a punctuation-insensitive "core" form. This checker mirrors that: a row
from `i18n_scan_english.py --csv` is covered when either form is a key.

Usage:  python scripts/check_dict_coverage.py --lang el [--csv docs/i18n-en/el.csv]
Exit code 1 when any block is uncovered.
"""
import argparse
import csv
import json
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def core(value):
    value = re.sub(r'[^\w\s]', ' ', value or '', flags=re.UNICODE)
    return re.sub(r'\s+', ' ', value).strip().lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lang', required=True)
    ap.add_argument('--csv')
    ap.add_argument('--root', default=ROOT)
    args = ap.parse_args()

    csv_path = args.csv or os.path.join(args.root, 'docs', 'i18n-en', args.lang + '.csv')
    if not os.path.exists(csv_path):
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        subprocess.run([sys.executable, os.path.join(args.root, 'scripts', 'i18n_scan_english.py'),
                        '--lang', args.lang, '--csv', csv_path], check=False,
                       cwd=args.root, stdout=subprocess.DEVNULL)

    dict_path = os.path.join(args.root, 'js', 'sr-content-%s.json' % args.lang)
    data = {}
    if os.path.exists(dict_path):
        with open(dict_path, encoding='utf-8') as fh:
            data = json.load(fh)

    keys = set(data)
    cores = {core(k) for k in data}

    rows = []
    with open(csv_path, encoding='utf-8-sig', newline='') as fh:
        for row in csv.DictReader(fh):
            text = (row.get('text') or '').strip()
            if text:
                rows.append(text)

    missing = [t for t in rows if t not in keys and core(t) not in cores]

    print('=' * 66)
    print(' content dictionary coverage — %s' % args.lang)
    print('=' * 66)
    print(' dictionary entries : %d' % len(data))
    print(' english blocks     : %d' % len(rows))
    print(' uncovered          : %d' % len(missing))
    for text in missing[:12]:
        print('   - ' + text[:96])
    if missing:
        print('RESULT: FAILED')
        return 1
    print('RESULT: PASSED')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
