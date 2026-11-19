#!/usr/bin/env python3
"""Reorder ckb's sections into the ar root's canonical order (approved
suggestion #11 - radical structural parity).

ckb-specific repairs handled here:
1. #trust-metrics is NESTED inside #hero on ckb (root has it as a sibling
   right after the hero) - it is cut out of the hero and re-placed as a
   sibling in root position.
2. The single wrapper <div> hosting hero..trust-band on ckb (root hosts
   hero..software-hub) is relocated with its opening tag and closing </div>
   so the wrapped group matches the root exactly.
3. All other 16 sections are reordered to the root's canonical order.

Verifications before writing: top-level order == root order, div/section
balance clean, every section span byte-preserved exactly once.
"""
import re
import sys

from lxml import html as LH

sys.stdout.reconfigure(encoding='utf-8')

PAGE = 'ckb/index.html'
ROOT = 'index.html'


def root_order():
    doc = LH.fromstring(open(ROOT, encoding='utf-8').read())
    return [s.get('id') for s in doc.xpath('//section') if s.get('id')]


def main():
    raw = open(PAGE, encoding='utf-8').read()
    order = root_order()
    print('target order from root:', ' > '.join(order))

    mask = list(raw)
    for m in re.finditer(r'<!--.*?-->|<script\b.*?</script\s*>', raw, re.DOTALL | re.IGNORECASE):
        for i in range(m.start(), m.end()):
            mask[i] = '\x00'
    masked = ''.join(mask)

    events = []
    for m in re.finditer(r'<div\b|</div\s*>|<section\b[^>]*\bid="([a-z-]+)"|</section\s*>', masked):
        t = m.group(0)
        if t.startswith('<div'):
            events.append(('div', None, m.start(), m.end()))
        elif t.startswith('</div'):
            events.append(('/div', None, m.start(), m.end()))
        elif t.startswith('</section'):
            events.append(('/sec', None, m.start(), m.end()))
        else:
            events.append(('sec', m.group(1), m.start(), m.end()))

    # ---- depth-aware section spans (ckb nests #trust-metrics inside #hero) ----
    spans = {}
    sec_stack = []
    for k, sid, s, e in events:
        if k == 'sec':
            sec_stack.append((sid, s))
        elif k == '/sec':
            sid, s = sec_stack.pop()
            spans[sid] = (s, e)
    assert not sec_stack, 'unclosed section'
    sec_ids = list(spans)
    print('ckb sections found:', ' > '.join(sec_ids))
    assert sorted(sec_ids) == sorted(order), 'section sets differ - abort'

    # nesting map: parent = the section whose span contains this span
    nested = {}
    for sid, (s, e) in spans.items():
        for pid, (ps, pe) in spans.items():
            if pid != sid and ps < s and e < pe:
                nested[sid] = pid
    print('nested sections:', nested or 'none')

    # ---- wrapper div: depth-1 ancestor of hero, closing after trust-band ----
    hero_start = spans['hero'][0]
    tb_end = spans['trust-band'][1]
    founders_start = spans['founders-showcase'][0]
    stack, wrapper = [], None
    for k, sid, s, e in events:
        if k == 'div':
            stack.append((s, e))
        elif k == '/div':
            if stack and stack[-1][0] < hero_start and s > tb_end and s < founders_start:
                wrapper = (stack[-1], (s, e))
                break
            stack.pop()
    assert wrapper, 'wrapper not resolved'
    (w_open_s, w_open_e), (w_close_s, w_close_e) = wrapper
    print(f'wrapper open  @{w_open_s}: {raw[w_open_s:w_open_e+60][:140]!r}')
    print(f'wrapper close @{w_close_s}: {raw[w_close_s:w_close_e]!r}')

    # ---- top-level section blocks: interstitial + section span ----
    top_ids = [sid for sid in sec_ids if sid not in nested]
    blocks = {}
    prev = w_open_e
    for sid in top_ids:
        s, e = spans[sid]
        blocks[sid] = raw[prev:e]
        prev = e
    tail = raw[prev:]

    # nested section: cut its span (plus preceding whitespace) out of parent
    for sid, pid in nested.items():
        s, e = spans[sid]
        hole = raw[s:e]
        assert hole in blocks[pid], f'nested {sid} span not inside parent block'
        blocks[pid] = blocks[pid].replace(hole, '', 1)
        # the nested section becomes a standalone sibling block
        blocks[sid] = hole

    # wrapper close currently sits in the interstitial BEFORE founders
    # (founders' block prefix) - remove it there, re-insert after software-hub
    close_txt = raw[w_close_s:w_close_e]
    fb = blocks['founders-showcase']
    rel = fb.find(close_txt)
    assert rel >= 0, 'wrapper close not found in founders block prefix'
    blocks['founders-showcase'] = fb[:rel] + fb[rel + len(close_txt):]

    # ---- rebuild in root order ----
    head_group = order[:5]  # hero trust-metrics services pricing software-hub
    out = [raw[:w_open_s], raw[w_open_s:w_open_e]]
    for sid in head_group:
        out.append(blocks[sid])
    out.append('\n        ' + close_txt)
    for sid in order[5:]:
        out.append(blocks[sid])
    out.append(tail)
    rebuilt = ''.join(out)

    # ---- verifications ----
    top_doc_ids = []
    for el in LH.fromstring(rebuilt).xpath('//section'):
        top_doc_ids.append(el.get('id'))
    assert top_doc_ids == order, f'order mismatch: {top_doc_ids}'
    parents = set(nested.values())
    for sid, (s, e) in spans.items():
        if sid in nested:
            continue  # child spans are re-placed verbatim as sibling blocks
        if sid in parents:
            # parent span is intentionally split by the extracted child:
            # both surrounding slices must survive verbatim
            child = next(c for c, p in nested.items() if p == sid)
            cs, ce = spans[child]
            assert raw[s:cs] in rebuilt, f'{sid} pre-child slice lost!'
            assert raw[ce:e] in rebuilt, f'{sid} post-child slice lost!'
        else:
            assert raw[s:e] in rebuilt, f'section {sid} content lost!'
    mask2 = list(rebuilt)
    for m in re.finditer(r'<!--.*?-->|<script\b.*?</script\s*>', rebuilt, re.DOTALL | re.IGNORECASE):
        for i in range(m.start(), m.end()):
            mask2[i] = '\x00'
    masked2 = ''.join(mask2)
    depth = 0
    for m in re.finditer(r'<div\b|</div\s*>', masked2):
        depth += 1 if m.group(0).startswith('<div') else -1
        assert depth >= 0, 'orphan close introduced'
    assert depth == 0, f'unbalanced: {depth} unclosed'

    open(PAGE, 'w', encoding='utf-8').write(rebuilt)
    print(f'\nOK: {PAGE} rewritten - {len(rebuilt)} chars (was {len(raw)}), '
          f'order == root, nested trust-metrics un-nested, balance clean.')


if __name__ == '__main__':
    main()
