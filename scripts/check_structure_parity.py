#!/usr/bin/env python3
"""Guard 11: structural parity with the ar root (approved suggestion #12).

The Arabic root page is the normative reference. This guard locks:
1. every portal's ordered section skeleton (21 ids) == root's, with no
   section nested inside another section;
2. #trust-metrics present right after the hero with the 4-metric strip,
   labels verbatim from TRUST_METRICS_LOCALIZATIONS (ckb carries its own
   pre-existing Fusha strip today - structural check only);
3. #portals present before #services-compare with the quick-portals strip,
   links/labels verbatim from PORTALS_STRIP_LOCALIZATIONS (all 28 portals).

Any future section insertion, removal, reorder or strip edit that breaks
parity fails CI before it can reach main.
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sync_structure_strips import (  # noqa: E402
    PORTALS_STRIP_LOCALIZATIONS,
    TRUST_METRICS_LOCALIZATIONS,
)

from lxml import html as LH  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# Portals whose existing #trust-metrics strip predates the parity wave and
# is not yet dictionary-aligned (structural check only).
# ckb was aligned in suggestion #16 (approved 2026-11-18): the Fusha strip is
# now the Sorani dictionary build, so the list is empty today; the mechanism
# stays for any future no-dict portal.
TM_STRUCTURAL_ONLY = []

METRIC_VALUES = ['99.9%', 'EU & BTW', '< 30s', 'Amsterdam HQ']


def text_of(el):
    return ' '.join(el.text_content().split())


def ordered_sections(doc):
    return [s.get('id') for s in doc.xpath('//section') if s.get('id')]


def check_root(doc, faults):
    order = ordered_sections(doc)
    if not order:
        faults.append('root: no sections found')
        return None
    if 'trust-metrics' not in order:
        faults.append('root: #trust-metrics missing')
    if 'portals' not in order:
        faults.append('root: #portals missing')
    tm = doc.xpath('//section[@id="trust-metrics"]')
    if len(tm) == 1 and len(tm[0].xpath('.//*[contains(@class,"trust-metric-item")]')) != 4:
        faults.append('root: #trust-metrics strip is not 4 items')
    ps = doc.xpath('//section[@id="portals"]')
    if len(ps) == 1 and not ps[0].xpath('.//*[contains(@class,"hero-quick-portals-strip")]'):
        faults.append('root: #portals strip missing')
    return order


def check_portal(lang, doc, root_order, faults):
    # 1) ordered skeleton parity, no nesting
    order = ordered_sections(doc)
    if order != root_order:
        faults.append(f'{lang}: section order {order} != root {root_order}')
        return
    for parent in doc.xpath('//section[.//section]'):
        faults.append(f'{lang}: section #{parent.get("id")} contains a nested section')

    # 2) trust-metrics strip
    tm = doc.xpath('//section[@id="trust-metrics"]')
    if len(tm) != 1:
        faults.append(f'{lang}: #trust-metrics found {len(tm)}x (expected 1)')
    else:
        items = tm[0].xpath('.//*[contains(@class,"trust-metric-item")]')
        if len(items) != 4:
            faults.append(f'{lang}: trust strip has {len(items)} items (expected 4)')
        else:
            vals = [text_of(i.xpath('.//*[contains(@class,"metric-val")][1]')[0]) for i in items]
            if vals != METRIC_VALUES:
                faults.append(f'{lang}: metric values {vals} != {METRIC_VALUES}')
        if lang not in TM_STRUCTURAL_ONLY:
            loc = TRUST_METRICS_LOCALIZATIONS[lang]
            labels = [text_of(i.xpath('.//*[contains(@class,"metric-lbl")][1]')[0]) for i in items]
            expected = [loc['l1'], loc['l2'], loc['l3'], loc['l4']]
            if labels != expected:
                faults.append(f'{lang}: trust labels {labels} != {expected}')
            aria_sec = (tm[0].get('aria-label') or '').strip()
            if aria_sec != loc['aria_section']:
                faults.append(f'{lang}: tm aria-label {aria_sec!r} != {loc["aria_section"]!r}')

    # 3) portals quick strip
    ps = doc.xpath('//section[@id="portals"]')
    if len(ps) != 1:
        faults.append(f'{lang}: #portals found {len(ps)}x (expected 1)')
        return
    strip = ps[0].xpath('.//*[contains(@class,"hero-quick-portals-strip")]')
    if len(strip) != 1:
        faults.append(f'{lang}: portals strip missing')
        return
    loc = PORTALS_STRIP_LOCALIZATIONS[lang]
    links = strip[0].xpath('.//a[contains(@class,"hero-quick-portal-link")]')
    if len(links) != 2:
        faults.append(f'{lang}: portals strip has {len(links)} links (expected 2)')
        return
    for a, key, href in ((links[0], 'dev', '../developer-portal.html'),
                         (links[1], 'partner', '../partner-portal.html')):
        if a.get('href') != href:
            faults.append(f'{lang}: strip {key} href={a.get("href")!r} != {href!r}')
        if text_of(a) != loc[key]:
            faults.append(f'{lang}: strip {key} label {text_of(a)!r} != {loc[key]!r}')
    book = strip[0].xpath('.//button[contains(@class,"hero-quick-portal-btn")]')
    if len(book) != 1 or text_of(book[0]) != loc['book']:
        faults.append(f'{lang}: strip booking button mismatch')
    sound = strip[0].xpath('.//button[contains(@class,"hero-sound-toggle-btn")]')
    if len(sound) != 1 or text_of(sound[0]) != loc['sound']:
        faults.append(f'{lang}: strip sound button mismatch')
    elif (sound[0].get('title') or '').strip() != loc['sound_title']:
        faults.append(f'{lang}: strip sound title '
                      f'{(sound[0].get("title") or "").strip()!r} != {loc["sound_title"]!r}')


def main():
    faults = []
    root_doc = LH.fromstring((ROOT / 'index.html').read_text(encoding='utf-8', errors='replace'))
    root_order = check_root(root_doc, faults)
    if root_order is None:
        print('FAIL structural parity - root unreadable')
        for f in faults:
            print('  -', f)
        sys.exit(1)

    checked = []
    for lang in sorted(PORTALS_STRIP_LOCALIZATIONS):
        p = ROOT / lang / 'index.html'
        if not p.exists():
            faults.append(f'{lang}: index.html missing')
            continue
        doc = LH.fromstring(p.read_text(encoding='utf-8', errors='replace'))
        check_portal(lang, doc, root_order, faults)
        checked.append(lang)

    if faults:
        print('FAIL structural parity with ar root')
        for f in faults:
            print('  -', f)
        sys.exit(1)
    print(f'PASS structural parity - root + {len(checked)} portals, '
          f'{len(root_order)} sections, identical ordered skeletons')


if __name__ == '__main__':
    main()
