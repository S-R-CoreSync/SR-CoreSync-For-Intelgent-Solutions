#!/usr/bin/env python3
"""Suggestion #16 (approved 2026-11-18): align the language of ckb's
#trust-metrics strip.

ckb/index.html predates the parity wave: its trust strip is written in Fusha
Arabic ('جاهزية سحابية موثوقة...') with a non-localized aria-label, while the
page itself is Sorani Kurdish. This tool replaces the whole section with the
canonical build_trust_metrics(TRUST_METRICS_LOCALIZATIONS['ckb']) markup - the
exact markup every other portal carries - so ckb's strip becomes Sorani from
the single-source dictionary. Idempotent: a second run produces zero diff.

Guard 11 drops ckb from TM_STRUCTURAL_ONLY once this runs: the strip is then
checked dict-exact like the other 27 portals.
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sync_structure_strips import build_trust_metrics, TRUST_METRICS_LOCALIZATIONS

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'ckb', 'index.html')


def main():
    with open(PATH, encoding='utf-8') as f:
        content = f.read()

    start = content.find('<section id="trust-metrics"')
    if start < 0:
        sys.exit('FAIL: no #trust-metrics section in ckb/index.html')
    end = content.find('</section>', start)
    if end < 0:
        sys.exit('FAIL: #trust-metrics section not closed in ckb/index.html')
    end += len('</section>')

    canonical = build_trust_metrics(TRUST_METRICS_LOCALIZATIONS['ckb'])
    if content[start:end] == canonical:
        print('ckb trust strip: already canonical (zero diff)')
        return

    content = content[:start] + canonical + content[end:]
    with open(PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print('ckb trust strip: replaced with the Sorani dictionary build')


if __name__ == '__main__':
    main()
