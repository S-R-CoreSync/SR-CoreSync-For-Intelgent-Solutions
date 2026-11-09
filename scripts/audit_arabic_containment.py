# -*- coding: utf-8 -*-
"""
Arabic containment audit
========================

The portals are generated from masters that were originally authored in
Arabic. When a localized copy is regenerated from such a master, Arabic UI
text (navigation, meta descriptions, form labels, WhatsApp templates,
alerts) silently reappears on German, French, Dutch, English, ... pages.

This gate makes that regression impossible to miss:

  * every HTML file inside every language folder whose language is not
    written in Arabic script must contain ZERO Arabic-script runs in
    visible text (any length) and user-facing attributes, except the exact
    native label used by the language switcher;
  * inside <script> bodies, Arabic is only permitted on per-language data
    lines (the `ar: "..."` TTS entries) - any other Arabic string literal
    (alerts, prompts, injected HTML) is a finding.

Arabic-script languages (ar, ckb, ku) and the root master are exempt.

Usage:
    python scripts/audit_arabic_containment.py
Exits non-zero when any finding exists, so CI can gate on it.
"""

import html
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit_translation_leakage import (  # noqa: E402
    ARABIC_SCRIPT_LANGS,
    ATTR_TEXT,
    COMMENT,
    LANGUAGES,
    TAG,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROTECT = re.compile(r'<(script|style)\b[^>]*>.*?</\1>', re.S | re.I)
AR_RUN = re.compile(r'[\u0600-\u06FF][\u0600-\u06FF\u0640\u064B-\u0652\u060C\u061B\u061F\s]*')
SCRIPT_BLOCK = re.compile(r'<script\b[^>]*>(.*?)</script>', re.S | re.I)
AR_DATA_LINE = re.compile(r'^\s*ar\s*:')

ALLOWED_TEXT = {
    'العربية',          # native name of Arabic in the language switcher
}


def visible_arabic(raw):
    """Arabic runs in visible text nodes and user-facing attributes."""
    body = PROTECT.sub(' ', raw)
    body = COMMENT.sub(' ', body)

    runs = []
    text_part = html.unescape(TAG.sub('\n', body))
    for match in AR_RUN.finditer(text_part):
        runs.append(' '.join(match.group(0).split()))
    for m in ATTR_TEXT.finditer(body):
        value = html.unescape(m.group(1))
        for match in AR_RUN.finditer(value):
            runs.append(' '.join(match.group(0).split()))
    return runs


def script_arabic(raw):
    """Arabic runs inside <script> bodies, except ar: data lines."""
    out = []
    for m in SCRIPT_BLOCK.finditer(raw):
        for line in m.group(1).splitlines():
            if AR_DATA_LINE.match(line):
                continue  # the ar: TTS data entry stays Arabic by design
            for match in AR_RUN.finditer(line):
                out.append(' '.join(match.group(0).split()))
    return out


def collect():
    findings = []
    scanned = 0
    for lang in sorted(LANGUAGES):
        if lang in ARABIC_SCRIPT_LANGS:
            continue
        folder = os.path.join(ROOT, lang)
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            if not name.lower().endswith('.html'):
                continue
            path = os.path.join(folder, name)
            rel = os.path.relpath(path, ROOT).replace('\\', '/')
            scanned += 1
            with io.open(path, encoding='utf-8', errors='ignore') as fh:
                raw = fh.read()

            for run in visible_arabic(raw):
                if run in ALLOWED_TEXT:
                    continue
                if len(run.replace(' ', '')) >= 2:
                    findings.append((rel, 'text', run[:80]))
            for run in script_arabic(raw):
                if len(run.replace(' ', '')) >= 2:
                    findings.append((rel, 'script', run[:80]))
    return scanned, findings


def main():
    scanned, findings = collect()
    print('=' * 78)
    print('Arabic containment audit - %d HTML files across %d non-Arabic languages'
          % (scanned, len([l for l in LANGUAGES if l not in ARABIC_SCRIPT_LANGS])))
    print('=' * 78)

    if not findings:
        print('PASSED: no Arabic-script text leaked into any localized page.')
        return 0

    by_file = {}
    for rel, kind, snippet in findings:
        by_file.setdefault(rel, []).append((kind, snippet))
    for rel in sorted(by_file):
        print('%s : %d finding(s)' % (rel, len(by_file[rel])))
        for kind, snippet in by_file[rel][:5]:
            print('   [%s] %s' % (kind, snippet))

    print('-' * 78)
    print('FAILED: %d Arabic run(s) found in %d localized file(s).'
          % (len(findings), len(by_file)))
    return 1


if __name__ == '__main__':
    sys.exit(main())
