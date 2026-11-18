#!/usr/bin/env python3
"""S&R CoreSync - i18n & language-map sentinel (one command, one verdict).

Runs every real language/map guard in one pass and prints a single follow-up
table, so a wave can never ship half-checked again (the language map once
shipped with a dead switcher behind fully green gates).

    python scripts/sentinel_i18n.py            # run everything, exit 1 on any fault
    python scripts/sentinel_i18n.py --quiet    # only failures and the verdict

The monthly GitHub Actions schedule in locale-drift.yml runs this same bank as
the periodic inventory; the dated worklog entry is written by whoever runs it
locally.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The 28 localized portals scanned by the English detector (ar master is the
# source language, en IS English - both are exempt by design).
SCAN_LANGS = [
    'ckb', 'bg', 'cs', 'da', 'de', 'el', 'es', 'et', 'fi', 'fr', 'ga', 'hr',
    'hu', 'it', 'ku', 'lt', 'lv', 'mt', 'nl', 'no', 'pl', 'pt', 'ro', 'sk',
    'sl', 'sv', 'tr'
]

CHECKS = [
    ('HTML/CSS/JS tag balance', ['node', 'scripts/validate.js']),
    ('inline scripts + JSON-LD', ['node', 'scripts/check_inline_scripts.mjs']),
    ('language purity & assets', ['python3', 'scripts/audit_language_purity.py']),
    ('text leakage guard', ['python3', 'scripts/check_leakage_clean.py']),
    ('content depth parity --strict', ['python3', 'scripts/check_content_depth_parity.py', '--strict']),
    ('hero drift vs master', ['python3', 'scripts/sync_locales.py', '--check']),
    ('hero row 2 localization', ['python3', 'scripts/check_hero_row2_localization.py']),
    ('structural parity vs ar root', ['python3', 'scripts/check_structure_parity.py']),
    ('full-site tag balance', ['python3', 'scripts/check_tag_balance_all.py']),
    ('hreflang agreement', ['python3', 'scripts/check_hreflang.py']),
    ('one version per script tag', ['python3', 'scripts/check_script_tags.py']),
    ('languages health (2x2/cache/hreflang)', ['python3', 'scripts/audit_all_languages_health.py']),
    ('tes-rating dict-exact (guard 13)', ['python3', 'scripts/normalize_tes_rating.py', '--check']),
]

TAIL_ON_FAIL = 12


def run(name, cmd, quiet):
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    dt = time.time() - t0
    ok = proc.returncode == 0
    print(f'{"PASS" if ok else "FAIL"}  {name:<40} {dt:5.1f}s')
    if not ok:
        out = (proc.stdout or '') + (proc.stderr or '')
        lines = [ln for ln in out.splitlines() if ln.strip()]
        print('      --- last output ---')
        for ln in lines[-TAIL_ON_FAIL:]:
            print('      ' + ln)
    elif not quiet:
        out = (proc.stdout or '').strip().splitlines()
        for ln in out[-2:]:
            print(f'      {ln}')
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()

    print(f'S&R CoreSync sentinel - {len(CHECKS)} guard suites + '
          f'{len(SCAN_LANGS)} English scans')
    print('=' * 68)

    ok = True
    for name, cmd in CHECKS:
        ok &= run(name, cmd, a.quiet)

    # English residue on every localized portal (one line per language)
    t0 = time.time()
    bad = []
    for lang in SCAN_LANGS:
        proc = subprocess.run(
            ['python3', 'scripts/i18n_scan_english.py', '--lang', lang],
            cwd=ROOT, capture_output=True, text=True)
        first = (proc.stdout or '').strip().splitlines()[:1]
        summary = first[0] if first else f'{lang}: scan error'
        if proc.returncode != 0 or not summary.rstrip().endswith('0 English blocks, 0 words'):
            bad.append(summary)
    dt = time.time() - t0
    if bad:
        ok = False
        print(f'FAIL  English residue on localized portals            {dt:5.1f}s')
        for ln in bad:
            print('      ' + ln)
    else:
        print(f'PASS  English residue on localized portals            {dt:5.1f}s')
        if not a.quiet:
            print(f'      {len(SCAN_LANGS)} portals x 0 English blocks')

    print('=' * 68)
    if ok:
        print('SENTINEL PASSED: languages and maps are fully harmonized.')
        return 0
    print('SENTINEL FAILED: fix the FAIL lines above before shipping.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
