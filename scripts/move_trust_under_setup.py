# -*- coding: utf-8 -*-
"""
Move the trust-metrics strip under the System-Setup (AI idea) bar.

Owner request 2026-11-27: in the hero the three bars read
setup -> language dock -> trust metrics. The trust strip must sit right
under the setup bar, so the floating language dock becomes the bottom-most
element again.

The strip is moved inside `.c3-center-stage` (a centred flex column with
gap 18px) immediately before its closing </div>, i.e. directly under the
`hero-ai-idea-form`. The block itself is carried over byte-for-byte, with
the indentation of its new home.

Usage:
  python scripts/move_trust_under_setup.py --check
  python scripts/move_trust_under_setup.py --apply
"""
import argparse
import io
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPEN_RE = re.compile(r'[ \t]*(?:<!--[^\n]*-->\n[ \t]*)?<section\b[^>]*id="trust-metrics"[^>]*>', re.S)


def tracked_html():
    out = subprocess.run(['git', 'ls-files', '*.html'], cwd=ROOT,
                         capture_output=True, text=True, encoding='utf-8')
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def find_block(text):
    m = OPEN_RE.search(text)
    if not m:
        return None
    end = text.find('</section>', m.end())
    if end < 0:
        return None
    end += len('</section>')
    # swallow the newline that follows the block
    while end < len(text) and text[end] in '\r\n':
        end += 1
    return m.start(), end


def insert_point(text):
    """Index just before the </div> that closes .c3-center-stage."""
    anchor = text.find('submitHeroAiIdea')
    if anchor < 0:
        return None
    form_end = text.find('</form>', anchor)
    if form_end < 0:
        return None
    close = text.find('</div>', form_end)
    if close < 0:
        return None
    line_start = text.rfind('\n', 0, close) + 1
    return line_start


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    if not (args.apply or args.check):
        ap.error('pass --apply or --check')

    changed, skipped, checked = [], [], 0
    for rel in tracked_html():
        if rel.startswith('docs/'):
            continue
        path = os.path.join(ROOT, rel.replace('/', os.sep))
        if not os.path.exists(path):
            continue
        with io.open(path, encoding='utf-8', newline='') as fh:
            text = fh.read()
        if 'id="trust-metrics"' not in text:
            continue
        checked += 1

        block = find_block(text)
        if not block:
            skipped.append((rel, 'block not closed'))
            continue
        start, end = block
        form_anchor = text.find('submitHeroAiIdea')
        if form_anchor < 0:
            skipped.append((rel, 'no setup form'))
            continue
        form_end = text.find('</form>', form_anchor)
        form_end = form_end + len('</form>') if form_end >= 0 else -1
        if form_end > 0 and not text[form_end:start].strip():
            skipped.append((rel, 'already under setup'))
            continue

        nl = '\r\n' if '\r\n' in text else '\n'
        piece = text[start:end]
        piece = piece.replace('\r\n', '\n').strip('\n')
        target = insert_point(text)
        if target is None:
            skipped.append((rel, 'no center-stage close'))
            continue
        # indentation of the closing </div> line
        line = text[target:]
        indent = re.match(r'[ \t]*', line).group(0)
        inner = indent + '    '
        # keep the block's internal indentation: shift by the original base indent
        lines = piece.split('\n')
        base = None
        for ln in lines[1:]:
            if ln.strip():
                cur = len(ln) - len(ln.lstrip())
                base = cur if base is None else min(base, cur)
        base = base or 0
        out_lines = [inner + lines[0].lstrip()]
        for ln in lines[1:]:
            out_lines.append(inner + (ln[base:] if ln[:base].strip() == '' else ln.lstrip()))
        moved = nl.join(out_lines)

        body = text[:start] + text[end:]
        target = insert_point(body)
        body = body[:target] + moved + nl + body[target:]

        if body != text:
            changed.append(rel)
            if args.apply:
                with io.open(path, 'w', encoding='utf-8', newline='') as fh:
                    fh.write(body)

    print('trust strip: %d page(s) with the block, %d %s, %d skipped'
          % (checked, len(changed), 'APPLIED' if args.apply else 'DRIFT', len(skipped)))
    for rel, why in skipped[:8]:
        print('  - %s (%s)' % (rel, why))
    return 0 if args.apply or not changed else 1


if __name__ == '__main__':
    sys.exit(main())
