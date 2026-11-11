"""Correct extraction: full estimator (5 groups / 21 options), the social plan
card, and the FAQ items a language is missing by their order number."""
import json, pathlib, re, sys
from lxml import html as LH

ROOT = pathlib.Path(".")
OUT = ROOT / "docs" / "_extract"
OUT.mkdir(parents=True, exist_ok=True)

src = (ROOT / "index.html").read_text(encoding="utf-8", errors="replace")
doc = LH.fromstring(src)


def outer(el):
    return LH.tostring(el, encoding="unicode")


groups = doc.xpath("//*[starts-with(@id,'estimatorGroup')]")
print("groups:", [g.get("id") for g in groups])

anc_sets = []
for g in groups:
    anc_sets.append({a for a in g.iterancestors()})
common = set.intersection(*anc_sets) if anc_sets else set()
# deepest common ancestor = the one furthest from the root
depth = {el: len(list(el.iterancestors())) for el in common}
estimator = max(common, key=lambda e: depth[e]) if common else groups[0]

block = outer(estimator)
print("estimator container:", estimator.tag, estimator.get("id"), estimator.get("class"), len(block), "chars")
print("options inside:", block.count("estimator-option"))

plans = doc.xpath("//*[@class and contains(@class,'wg-plan')]")
social = next(p for p in plans if "8K" in re.sub(r"\s+", " ", p.text_content()))
print("social card:", len(outer(social)), "chars")

(OUT / "estimator.html").write_text(block, encoding="utf-8")
(OUT / "plan-social.html").write_text(outer(social), encoding="utf-8")

# FAQ items missing in a target language, matched by their order number
def faq_map(path):
    d = LH.fromstring(pathlib.Path(path).read_text(encoding="utf-8", errors="replace"))
    out = {}
    for item in d.xpath("//*[contains(@class,'accordion-faq_item')]"):
        order = item.xpath(".//*[contains(@class,'accordion-order')]")
        key = re.sub(r"\s+", "", order[0].text_content()) if order else None
        if key:
            out[key] = item
    return out

master_faq = faq_map("index.html")
target = sys.argv[1] if len(sys.argv) > 1 else "de"
target_faq = faq_map(pathlib.Path(target, "index.html"))
missing = [k for k in master_faq if k not in target_faq]
print(f"{target}: has {sorted(target_faq)}")
print(f"missing in {target}: {missing}")
(OUT / f"faq-missing-{target}.html").write_text(
    "\n".join(outer(master_faq[k]) for k in missing), encoding="utf-8")

strings = set()
for e in estimator.xpath(".//*[contains(@class,'option-title') or contains(@class,'option-badge')]"):
    strings.add(re.sub(r"\s+", " ", e.text_content()).strip())
for e in estimator.xpath(".//button"):
    for attr in ("data-title", "data-days"):
        if e.get(attr):
            strings.add(e.get(attr))
for e in estimator.xpath(".//*[contains(@class,'est-') or contains(@class,'estimator-')]"):
    if e.tag in ("h3", "h4", "h5", "p", "span", "label"):
        t = re.sub(r"\s+", " ", e.text_content()).strip()
        if t:
            strings.add(t)
json.dump(sorted(strings), (OUT / f"estimator-strings.json").open("w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("estimator strings:", len(strings))
for s in sorted(strings)[:40]:
    print("   -", s[:100])
