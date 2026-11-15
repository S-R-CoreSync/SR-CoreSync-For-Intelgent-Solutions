#!/usr/bin/env python
"""Fail when a published page carries a company identifier that is not canonical.

The site grew four identities before anyone noticed: the About ribbon announced
KVK 95084285 / NL005128080B13, the invoice issuer announced 84920194 /
NL849201942B01, a UBL sample carried NL862145890B01, and the invoice form
defaulted to NL853123456B01. A regex sweep found 11 VAT values and 8 KVK values
across the public HTML.

Two things are wrong with that, and only the first is fixable in code:
  · code: forty copies of a number drift apart; a copy edits a number and the
    others keep the old one.
  · truth: which number is correct is a registry question, not a code question.

This check fixes the code half. `data/company-identity.json` is the single
source; every page must agree with it. The mismatches that already exist are
listed in `data/company-identity-baseline.json` so the gate can land without a
forty-file rewrite: a baselined mismatch is reported but tolerated, and any NEW
one fails the build. Regenerate the baseline with --write-baseline once the real
number is confirmed and the pages are aligned.

Usage:
    python scripts/check_company_identity.py
    python scripts/check_company_identity.py --write-baseline
    python scripts/check_company_identity.py --list

Exit codes: 0 ok · 1 new mismatch · 2 configuration missing or unreadable.
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, 'data', 'company-identity.json')
BASELINE = os.path.join(ROOT, 'data', 'company-identity-baseline.json')

SKIP_DIRS = {'.git', '_site', '_site.next', '_site.prev', 'node_modules', 'build',
             'dist', 'temp_chrome_print_dir', 'temp_chrome_print_dir2', '__pycache__'}

KVK_RE = re.compile(r'KVK[^0-9]{0,6}([0-9]{8})')
VAT_RE = re.compile(r'\b(NL[0-9]{9}B[0-9]{2})\b')


def load_json(path):
    try:
        with io.open(path, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, ValueError) as exc:
        sys.stderr.write('FAILED: cannot read %s (%s)\n' % (path, exc))
        sys.exit(2)


def html_files():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
        for name in files:
            if name.endswith('.html'):
                yield os.path.join(base, name)


def findings(canonical):
    """Every (relative path, kind, value) whose value is not canonical."""
    kvk_ok = str(canonical.get('kvk', '')).strip()
    vat_ok = str(canonical.get('vat', '')).strip().upper()
    out = []
    for path in html_files():
        try:
            with io.open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                text = fh.read()
        except OSError:
            continue
        rel = os.path.relpath(path, ROOT).replace('\\', '/')
        for value in KVK_RE.findall(text):
            if value != kvk_ok:
                out.append((rel, 'kvk', value))
        for value in VAT_RE.findall(text):
            if value.upper() != vat_ok:
                out.append((rel, 'vat', value))
    return out


def key(item):
    return '%s|%s|%s' % item


def main(argv):
    canonical = load_json(CONFIG)
    if not canonical.get('kvk') or not canonical.get('vat'):
        sys.stderr.write('FAILED: %s must define kvk and vat.\n' % CONFIG)
        return 2

    found = sorted(set(findings(canonical)), key=key)

    if '--write-baseline' in argv:
        payload = {
            '_comment': 'Known mismatches tolerated until the canonical identifiers are '
                        'confirmed and the pages are aligned. Regenerate after cleanup.',
            'canonical_at_write': {'kvk': canonical['kvk'], 'vat': canonical['vat']},
            'tolerated': [key(item) for item in found],
        }
        with io.open(BASELINE, 'w', encoding='utf-8') as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        print('Baseline written: %d tolerated mismatch(es) -> %s' % (len(found), BASELINE))
        return 0

    baseline = set()
    if os.path.exists(BASELINE):
        baseline = set(load_json(BASELINE).get('tolerated', []))

    new = [item for item in found if key(item) not in baseline]

    if '--list' in argv:
        for rel, kind, value in found:
            state = 'baselined' if key((rel, kind, value)) in baseline else 'NEW'
            print('%-9s %-4s %-14s %s' % (state, kind.upper(), value, rel))
        print('')
        print('canonical: kvk=%s vat=%s' % (canonical['kvk'], canonical['vat']))

    if new:
        sys.stderr.write('FAILED: %d identifier(s) differ from the canonical pair and are '
                         'not in the baseline.\n' % len(new))
        for rel, kind, value in new[:30]:
            sys.stderr.write('  - %s: %s %s\n' % (rel, kind.upper(), value))
        if len(new) > 30:
            sys.stderr.write('  ... and %d more\n' % (len(new) - 30))
        sys.stderr.write('Either fix the page to %s / %s, or (if the number is a deliberate '
                         'sample) move it out of the published set.\n'
                         % (canonical['kvk'], canonical['vat']))
        return 1

    print('PASSED: no new identifier drift. %d known mismatch(es) remain baselined; '
          'canonical kvk=%s vat=%s.' % (len(found), canonical['kvk'], canonical['vat']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
