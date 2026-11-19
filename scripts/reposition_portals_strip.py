#!/usr/bin/env python3
"""Reposition the localized quick-portals strip outside the shared-section
markers on every portal landing page.

Why: `localize_multilingual_shared_sections.py` owns exactly the
services-compare + tech-pillars block between the shared-index-sections
markers. The structural-parity wave (a20ac6b8) left the per-page localized
`<section id="portals">` strip INSIDE those markers, so --check compares
marker content that includes a section the generator never produces
("generated section content is out of date", first hit: de).

Fix: move the strip verbatim (byte-identical, same DOM position directly
before the marker comment) outside the markers. Rendering, section order,
tag balance and parity guards are untouched. Idempotent: a page already
repaired is skipped unchanged.
"""
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from deploy_sovereign_multilingual import LANGUAGES  # noqa: E402

START = "<!-- shared-index-sections:start -->"
STRIP_RE = re.compile(
    r'<section id="portals" class="section-portals"[^>]*>'
    r'<div class="hero-quick-portals-strip.*?</div></section>\n',
    re.DOTALL,
)


def repair(path: Path) -> str:
    """Return 'moved', 'already-ok' or an error description."""
    content = path.read_text(encoding="utf-8")
    marker_pos = content.find(START)
    if marker_pos == -1:
        return "no shared-index-sections markers"
    after_marker = marker_pos + len(START) + 1  # + newline
    match = STRIP_RE.match(content, after_marker)
    if not match:
        return "already-ok"
    strip = match.group(0)
    before = content[:marker_pos]
    rest = content[match.end():]
    repaired = before + strip + START + "\n" + rest
    path.write_text(repaired, encoding="utf-8", newline="")
    return "moved"


def main() -> int:
    moved = ok = 0
    for language in LANGUAGES:
        code = language["code"]
        if code == "ar":
            continue
        result = repair(BASE_DIR / code / "index.html")
        if result == "moved":
            moved += 1
        elif result == "already-ok":
            ok += 1
        else:
            print(f"FAIL {code}: {result}")
            return 1
    print(f"portals strip repositioned: {moved} moved / {ok} already outside markers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
