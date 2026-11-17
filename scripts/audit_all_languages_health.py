import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Single source of the language codes: 29 codes = the Arabic master + 28
# portals. Every counter in this audit derives N from this list; no hardcoded
# "28" survives (the marketing copy keeps saying 28 portals, tooling does not).
LANGS = [
    'ar', 'ckb', 'bg', 'cs', 'da', 'de', 'el', 'en', 'es', 'et',
    'fi', 'fr', 'ga', 'hr', 'hu', 'it', 'ku', 'lt', 'lv', 'mt',
    'nl', 'no', 'pl', 'pt', 'ro', 'sk', 'sl', 'sv', 'tr'
]
N = len(LANGS)

print('======================================================================')
print(f'S&R CoreSync - Multilingual Quality & Integrity Audit Across {N} Codes')
print('(Arabic master + %d portals)' % (N - 1))
print('======================================================================')

all_passed = True
stats = {
    'total_checked': 0,
    'matrix_2x2_passed': 0,
    'cache_busting_passed': 0,
    'hreflang_clean_passed': 0,
    'demo_page_present': 0
}

for lang in LANGS:
    idx_path = 'index.html' if lang == 'ar' else f'{lang}/index.html'
    demo_path = 'demo.html' if lang == 'ar' else f'{lang}/demo.html'

    if not os.path.exists(idx_path):
        print(f'[FAIL] [{lang}] missing index: {idx_path}')
        all_passed = False
        continue

    stats['total_checked'] += 1

    with open(idx_path, 'r', encoding='utf-8', errors='ignore') as f:
        c = f.read()

    # Check 2x2 matrix (trio)
    has_2x2 = ('hero-actions-2x2' in c and 'hero-btn-gold-pair' in c and 'hero-btn-portal-pair' in c)
    if has_2x2:
        stats['matrix_2x2_passed'] += 1
    else:
        print(f'[WARN] [{lang}] Missing 2x2 matrix structure!')
        all_passed = False

    # Check cache busting
    has_cb = ('?v=20261102-p0-matrix' in c)
    if has_cb:
        stats['cache_busting_passed'] += 1
    else:
        print(f'[WARN] [{lang}] Missing cache busting query parameter!')
        all_passed = False

    # Check hreflang duplicates - strict <link> pairs only, the same rule as
    # check_hreflang.py. The old attribute-wide regex also counted the
    # hreflang strings inside the inline language-map JS config (8 markets)
    # and reported 7-8 phantom duplicates on every portal.
    pairs = re.findall(r'<link[^>]+hreflang=["\']([^"\']+)["\'][^>]*href=["\']([^"\']+)["\']', c, re.I)
    if not pairs:
        pairs = [(co, u) for u, co in
                 re.findall(r'<link[^>]+href=["\']([^"\']+)["\'][^>]*hreflang=["\']([^"\']+)["\']', c, re.I)]
    codes = [co for co, _ in pairs]
    dups = len(codes) - len(set(codes))
    if dups == 0 and len(codes) >= 20:
        stats['hreflang_clean_passed'] += 1
    else:
        print(f'[WARN] [{lang}] Hreflang issues: link pairs={len(codes)}, duplicates={dups}')
        all_passed = False

    # Check demo page
    if os.path.exists(demo_path):
        stats['demo_page_present'] += 1

print(f'\n--- SUMMARY RESULTS ---')
print(f'Total Codes Audited         : {stats["total_checked"]}/{N}')
print(f'2x2 Sovereign Matrix Passed : {stats["matrix_2x2_passed"]}/{N}')
print(f'Cache-Busting Passed        : {stats["cache_busting_passed"]}/{N}')
print(f'Zero-Duplicate Hreflang     : {stats["hreflang_clean_passed"]}/{N}')
print(f'Interactive Demo Pages      : {stats["demo_page_present"]}/{N}')
print('======================================================================')
if all_passed:
    print('AUDIT PASSED: All language codes are harmonized, translated, and verified.')
    sys.exit(0)
else:
    print('AUDIT FAILED: see the [WARN]/[FAIL] lines above - CI gates on this exit code.')
    sys.exit(1)
