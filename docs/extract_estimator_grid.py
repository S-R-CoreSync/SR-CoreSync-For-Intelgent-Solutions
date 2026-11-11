"""Extract the WHOLE estimator (grid + controls + summary), not only the controls.

  python docs/extract_estimator_grid.py

Writes docs/_extract/estimator-grid.html and estimator-grid-strings.json.
The old estimator.html stopped at the controls, so an install built from it gave
a page the option buttons but no total, no timeline and no call to action.
"""
import json, pathlib, re, sys
from lxml import html as LH

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "_extract"


def block(raw, marker):
    i = raw.find(marker)
    start = raw.rfind("<div", 0, i)
    depth = 0
    for m in re.finditer(r"<div\b|</div>", raw[start:]):
        depth += 1 if m.group(0).startswith("<div") else -1
        if depth == 0:
            return raw[start:start + m.end()]
    raise SystemExit("unbalanced block: " + marker)


raw = (ROOT / "index.html").read_text(encoding="utf-8", errors="replace")
grid = block(raw, "cost-estimator-grid")
node = LH.fragment_fromstring(grid)

strings = set()
for el in node.iter():
    if not isinstance(el.tag, str):
        continue
    if el.text and el.text.strip():
        strings.add(re.sub(r"\s+", " ", el.text).strip())
    for attr in ("alt", "title", "placeholder", "aria-label", "data-title", "data-days"):
        v = el.get(attr)
        if v and v.strip():
            strings.add(re.sub(r"\s+", " ", v).strip())

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "estimator-grid.html").write_text(grid, encoding="utf-8")
(OUT / "estimator-grid-strings.json").write_text(
    json.dumps(sorted(strings), ensure_ascii=False, indent=1), encoding="utf-8")

sys.stdout.reconfigure(encoding="utf-8")
print(f"grid {len(grid):,} chars | {len(strings)} unique strings -> {OUT}")
