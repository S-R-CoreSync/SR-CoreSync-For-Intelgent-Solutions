#!/usr/bin/env python
"""One command before a commit: refresh what is generated, then prove it is fresh.

The site has three generated layers, and each has bitten us in the same way:

  · index.html        is generated from  partials/            (build_site)
  · en/index.html     is generated from  partials/en/         (build_lang)
  · xx/index.html ×26 is generated from  index.html's hero    (sync_locales)

Editing a page and forgetting to regenerate its layer leaves the repo
inconsistent; the deploy then fails at the guard step, after the work is done.
This script regenerates every layer first, then runs the checks, so a commit
can only leave a tree that re-builds byte for byte.

    python scripts/preflight.py          # fix, then check (default)
    python scripts/preflight.py --check  # check only, change nothing
    python scripts/preflight.py --full   # also parity and the perf budget
"""
import argparse
import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FIX = [
    ('parts  <- index.html', ['scripts/build_site.py', '--extract']),
    ('en     <- parts/en', ['scripts/build_lang.py', '--extract', 'en']),
    ('locales <- master', ['scripts/sync_locales.py', '--write']),
]

CHECK = [
    ('index.html rebuilds', ['scripts/build_site.py', '--check']),
    ('en rebuilds', ['scripts/build_lang.py', '--check', 'en']),
    ('locales match master', ['scripts/sync_locales.py', '--check']),
    ('event payloads', ['scripts/check_sr_args.py']),
    ('local links', ['scripts/check_site_links.py']),
]

FULL = [
    ('language parity', ['scripts/check_multilingual_page_parity.py']),
    ('language purity', ['scripts/audit_language_purity.py']),
    ('performance budget', ['scripts/check_perf_budget.py']),
]


def run(label, args, quiet=True):
    proc = subprocess.run([sys.executable] + args, cwd=ROOT,
                          capture_output=True, text=True, encoding='utf-8', errors='replace')
    ok = proc.returncode == 0
    tail = ''
    if not ok:
        lines = [l for l in (proc.stdout + proc.stderr).splitlines() if l.strip()]
        tail = lines[-1] if lines else ''
    print('  %-24s %s%s' % (label, 'ok' if ok else 'FAILED', ('  · ' + tail[:110]) if tail else ''))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='change nothing, only verify')
    ap.add_argument('--full', action='store_true', help='add parity, purity and the budget')
    a = ap.parse_args()

    failed = 0
    if not a.check:
        print('regenerating')
        for label, args in FIX:
            failed += 0 if run(label, args) else 1
        if failed:
            print('\npreflight: a generator failed; fix that before anything else')
            return 1

    print('verifying')
    for label, args in CHECK + (FULL if a.full else []):
        failed += 0 if run(label, args) else 1

    if failed:
        print('\npreflight: %d check(s) failed' % failed)
        return 1
    print('\npreflight: clean - the tree rebuilds itself everywhere')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
