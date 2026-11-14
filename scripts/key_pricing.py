# -*- coding: utf-8 -*-
"""Phase 1, section one: give the four pricing cards stable, meaningful keys.

The key says what the text is, not where it sits in the tree:
    data-i18n="pricing.plan1.desc"
so moving the card, wrapping it, or adding a div above it cannot break the link.
Only attributes are added - not one character of text changes.
"""
import os, re, sys

ROOT = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project'
LANGS = ['index.html']
for n in sorted(os.listdir(ROOT)):
    if n.startswith(('.', '_')) or n in {'build', 'node_modules', 'docs', 'partials', 'scripts', 'assets', 'css', 'js', 'i18n', 'workers'}:
        continue
    if os.path.isfile(os.path.join(ROOT, n, 'index.html')):
        LANGS.append(n + '/index.html')

PLAN = re.compile(r'class="wg-plan"')

PERIOD = re.compile(r'(<span class="text-body-2 fw-normal[^"]*")>')
DESC = re.compile(r'(<p class="plan-desc[^"]*")>')
CTA = re.compile(r'(<a[^>]+class="pricing-card-btn-wa"[^>]*>\s*<span)>')

dry = '--dry' in sys.argv
touched = notes = 0

for rel in LANGS:
    p = os.path.join(ROOT, rel)
    s = open(p, encoding='utf-8', newline='').read()
    if 'data-i18n="pricing.plan1' in s:
        continue

    starts = [m.start() for m in PLAN.finditer(s)]
    if len(starts) != 4:
        print('%-16s %d plans (expected 4) - skipped' % (rel, len(starts)))
        continue

    out, cursor = [], 0
    ok = True
    for idx, st in enumerate(starts, 1):
        end = starts[idx] if idx < len(starts) else len(s)
        block = s[st:end]

        for rx, suffix in ((PERIOD, 'period'), (DESC, 'desc'), (CTA, 'cta')):
            m = rx.search(block)
            if not m:
                ok = False
                break
            key = 'pricing.plan%d.%s' % (idx, suffix)
            block = block[:m.start()] + m.group(1) + ' data-i18n="%s"' % key + block[m.end() - 1:]
            notes += 1
        if not ok:
            break
        out.append(s[cursor:st] + block)
        cursor = end

    if not ok:
        print('%-16s a plan is missing a slot - skipped' % rel)
        continue

    out.append(s[cursor:])
    s2 = ''.join(out)
    if not dry:
        open(p, 'w', encoding='utf-8', newline='').write(s2)
    touched += 1
    print('%-16s 12 keys' % rel)

print('\npages keyed: %d · attributes added: %d' % (touched, notes))
