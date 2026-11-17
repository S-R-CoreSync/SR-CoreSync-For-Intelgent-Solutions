#!/usr/bin/env python3
"""Guard 10: hero matrix row 2 must match PORTAL_LOCALIZATIONS exactly.

The 2x2 hero action matrix's second row (Developer Portal / Partner Portal)
is localized from the single-source dictionary PORTAL_LOCALIZATIONS in
scripts/sync_2x2_all_languages.py. This guard locks every dictionary portal
to its dictionary verbatim (href + label + title), so no English fallback
text can ever come back. Portals with no dictionary entry (ckb - Sorani,
written in Arabic script by design) are checked structurally instead: both
portal buttons must exist and their labels must not be English.
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sync_2x2_all_languages import PORTAL_LOCALIZATIONS  # noqa: E402

from lxml import html as LH  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

EXPECTED_HREFS = {
    'dev': '../developer-portal.html',
    'partner': '../partner-portal.html',
}

# Portals written natively without a dictionary entry (structurally checked).
NO_DICT_PORTALS = ['ckb']


def text_of(el):
    return ' '.join(el.text_content().split())


def check_dict_portal(lang, doc, faults):
    loc = PORTAL_LOCALIZATIONS[lang]
    for key, cls, label_key, title_key in (
            ('dev', 'hero-btn-dev-portal', 'dev_label', 'dev_title'),
            ('partner', 'hero-btn-partner-portal', 'partner_label', 'partner_title')):
        nodes = doc.xpath(
            f'//a[contains(concat(" ", normalize-space(@class), " "), " {cls} ")]')
        if len(nodes) != 1:
            faults.append(f'{lang}: {cls} found {len(nodes)}x (expected 1)')
            continue
        a = nodes[0]
        href, label, title = a.get('href'), text_of(a), (a.get('title') or '').strip()
        if href != EXPECTED_HREFS[key]:
            faults.append(f'{lang}: {cls} href={href!r} (expected {EXPECTED_HREFS[key]!r})')
        if label != loc[label_key]:
            faults.append(f'{lang}: {cls} label={label!r} (expected {loc[label_key]!r})')
        if title != loc[title_key]:
            faults.append(f'{lang}: {cls} title={title!r} (expected {loc[title_key]!r})')


def check_no_dict_portal(lang, doc, faults):
    # Both portal buttons must exist; labels must not be pure English words.
    for cls in ('hero-btn-dev-portal', 'hero-btn-partner-portal'):
        nodes = doc.xpath(
            f'//a[contains(concat(" ", normalize-space(@class), " "), " {cls} ")]')
        if len(nodes) != 1:
            faults.append(f'{lang}: {cls} found {len(nodes)}x (expected 1)')
            continue
        label = text_of(nodes[0])
        ascii_words = re.sub(r'[^\x00-\x7F]+', ' ', label).split()
        meaningful = [w for w in ascii_words if len(w) > 2 and w.lower() not in
                      ('3d', 'api', 'apis', 'vip')]
        if meaningful:
            faults.append(f'{lang}: {cls} label looks English: {label!r}')


def main():
    faults = []
    checked_dict, checked_nodict = [], []
    for lang in sorted(PORTAL_LOCALIZATIONS):
        p = ROOT / lang / 'index.html'
        if not p.exists():
            faults.append(f'{lang}: index.html missing')
            continue
        doc = LH.fromstring(p.read_text(encoding='utf-8', errors='replace'))
        check_dict_portal(lang, doc, faults)
        checked_dict.append(lang)
    for lang in NO_DICT_PORTALS:
        p = ROOT / lang / 'index.html'
        if not p.exists():
            faults.append(f'{lang}: index.html missing')
            continue
        doc = LH.fromstring(p.read_text(encoding='utf-8', errors='replace'))
        check_no_dict_portal(lang, doc, faults)
        checked_nodict.append(lang)

    if faults:
        print('FAIL hero matrix row 2 localization')
        for f in faults:
            print('  -', f)
        sys.exit(1)

    print(f"PASS hero matrix row 2 localization - "
          f"{len(checked_dict)} dict-exact + {len(checked_nodict)} no-dict "
          f"({', '.join(checked_nodict)}) portals")


if __name__ == '__main__':
    main()
