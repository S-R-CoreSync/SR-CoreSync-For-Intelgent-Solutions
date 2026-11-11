"""Prepare the estimator + booking-modal port (session 1, read-only).

Pulls the two blocks out of the master, lists every translatable string they
contain, and writes an empty locale skeleton so the next step is a data fill
rather than surgery on 27 pages.
"""
import json, pathlib, re
from lxml import html as LH

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "_extract"
OUT.mkdir(parents=True, exist_ok=True)

src = (ROOT / "index.html").read_text(encoding="utf-8", errors="replace")
doc = LH.fromstring(src)

blocks = {
    "estimator": doc.xpath("//*[contains(@class,'cost-estimator-controls')]"),
    "booking": doc.xpath("//*[@id='executiveBookingModal']"),
}

strings = {}
for name, nodes in blocks.items():
    if not nodes:
        print("missing block:", name)
        continue
    node = nodes[0]
    html = LH.tostring(node, encoding="utf-8").decode("utf-8")
    (OUT / f"{name}.html").write_text(html, encoding="utf-8")

    found = []
    for el in node.iter():
        if not isinstance(el.tag, str):
            continue
        if el.text and el.text.strip():
            found.append(re.sub(r"\s+", " ", el.text).strip())
        for attr in ("alt", "title", "placeholder", "aria-label", "data-title", "data-days"):
            v = el.get(attr)
            if v and v.strip():
                found.append(re.sub(r"\s+", " ", v).strip())
    uniq = sorted(set(found))
    strings[name] = uniq
    print(f"{name}: {len(html):,} chars, {len(uniq)} strings")

json.dump(strings, (OUT / "port-strings.json").open("w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

skeleton = {"__note__": "fill one language at a time; keys are the Arabic strings",
            "de": {}}
for name, items in strings.items():
    for s in items:
        skeleton["de"][s] = ""
pathlib.Path(ROOT / "scripts" / "portal_estimator_locales.json").write_text(
    json.dumps(skeleton, ensure_ascii=False, indent=1), encoding="utf-8")

print("strings total:", sum(len(v) for v in strings.values()))
print("skeleton:", ROOT / "scripts" / "portal_estimator_locales.json")
