#!/usr/bin/env python3
"""Suggestion #15 (approved 2026-11-18): give the ar root hero the same 2x2
action matrix every portal carries.

Live measurement first (scripts/measure_hero_connect.mjs): on every portal the
matrix lives inside the legacy #hero .content-wrap block, which the site CSS
hides (#hero .content-wrap{display:none !important} - hv2 cockpit is the
visible hero everywhere). The root alone lacks the matrix even in the DOM.
This tool inserts the identical wrapper chain (content-wrap > container-hero-
luxury > hero-reference__grid > hero-reference__copy > hero-reference__actions
hero-actions-2x2) as the last child of the root's section#hero:

- row 1: demo + VIP buttons, Arabic texts taken verbatim from the root's own
  canonical buttons;
- row 2: Developer/Partner portal anchors, labels+titles from the
  PORTAL_LOCALIZATIONS['ar'] single-source dictionary, hrefs same-folder
  (developer-portal.html / partner-portal.html) - the root has no ../.

Rendering stays untouched: the block is hidden by the same CSS rule that hides
it on the 28 portals, so the visible cockpit is byte-for-byte the same hero
the owner approved. Idempotent: a second run produces zero diff.

Guard 10 (check_hero_row2_localization.py) locks the root row 2 to the
dictionary verbatim (same-folder hrefs).
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sync_2x2_all_languages import PORTAL_LOCALIZATIONS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, 'index.html')

# Row 1 texts are the root's own canonical button wording (demo gold button +
# private-consultation booking button), kept in one place here.
ROW1 = {
    'demo_label': 'تجربة النظام المؤسسي ديمو ⚡',
    'demo_title': 'تجربة نظام ERP المالي الحي',
    'vip_label': 'حجز استشارة خاصة 👔',
    'vip_title': 'حجز استشارة تنفيذية VIP',
}


def build_root_matrix(loc, r1):
    return f"""                <div class="content-wrap">
                    <div class="container container-hero-luxury">
                        <div class="hero-reference__grid">
                            <div class="hero-reference__copy">
                                <div class="hero-reference__actions hero-actions-2x2">
                                    <!-- Row 1: Gold Luxury Pair (Live Demo & VIP Executive Consultation) -->
                                    <div class="hero-actions-row">
                                        <a href="demo.html" class="tf-btn hero-reference__action hero-btn-gold-pair hero-btn-demo hero-btn-primary-highlight hero-btn-quiet" title="{r1['demo_title']}">
                                            <span>{r1['demo_label']}</span>
                                        </a>
                                        <button type="button" class="tf-btn hero-reference__action hero-btn-gold-pair hero-btn-vip hero-btn-primary-highlight" data-sr-call="openExecutiveBookingModal" title="{r1['vip_title']}">
                                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                                            <span>{r1['vip_label']}</span>
                                        </button>
                                    </div>

                                    <!-- Row 2: Dark Emerald Portal Pair (Developer Portal & Partner Portal) -->
                                    <div class="hero-actions-row">
                                        <a href="developer-portal.html" class="tf-btn hero-reference__action hero-btn-portal-pair hero-btn-dev-portal" title="{loc['dev_title']}">
                                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M16 18l6-6-6-6"/><path d="M8 6l-6 6 6 6"/></svg>
                                            <span>{loc['dev_label']}</span>
                                        </a>
                                        <a href="partner-portal.html" class="tf-btn hero-reference__action hero-btn-portal-pair hero-btn-partner-portal" title="{loc['partner_title']}">
                                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
                                            <span>{loc['partner_label']}</span>
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>"""


def main():
    with open(PATH, encoding='utf-8') as f:
        content = f.read()

    hero_open = content.find('<section id="hero"')
    if hero_open < 0:
        sys.exit('FAIL: section#hero not found in root index.html')
    hero_close = content.find('</section>', hero_open)
    if hero_close < 0:
        sys.exit('FAIL: section#hero not closed in root index.html')

    hero_seg = content[hero_open:hero_close]
    if 'hero-actions-2x2' in hero_seg:
        print('root hero matrix: already present (zero diff)')
        return

    block = build_root_matrix(PORTAL_LOCALIZATIONS['ar'], ROW1)
    content = content[:hero_close] + block + '\n' + content[hero_close:]
    with open(PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print('root hero matrix: inserted (hidden legacy chain, same-folder hrefs)')


if __name__ == '__main__':
    main()
