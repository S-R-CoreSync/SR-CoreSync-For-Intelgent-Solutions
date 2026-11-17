#!/usr/bin/env python3
"""Find every visible text node that is still English on a localized page.

Manual patching misses blocks because nobody knows how many there are. This
scans the DOM and reports them by section, so the work becomes a list instead of
a hunt.

  python scripts/i18n_scan_english.py --lang de [--csv out.csv]
"""
import argparse, csv, json, pathlib, re, sys
from lxml import html as LH

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = {"script", "style", "svg", "path", "rect", "line", "polyline", "circle"}

BRANDS = ["S&R CoreSync For Intelligent Solutions", "S&R CORESYNC FOR INTELLIGENT SOLUTIONS",
          "S&R CORESYNC", "For Intelligent Solutions", "Official Corporate Emblem",
          "Brand Emblem", "S&R TaxSync Desktop", "S&R CloudPOS Connector",
          "S&R FlowScan AI Mobile", "S&R Financial AI SDK", "S&R SecureVault B2B",
          "S&R Cloud Terminal Agent", "S&R CivicSync", "S&R HealthBridge",
          "S&R OmniBakery"]


def is_brand_only(text):
    """A line that carries nothing but the brand, a product name or an emblem label."""
    rest = text
    for brand in BRANDS:
        rest = re.sub(re.escape(brand), " ", rest, flags=re.I)
    rest = re.sub(r"[^A-Za-z\u00C0-\u024F]+", " ", rest)
    words = [w for w in rest.split() if len(w) > 2]
    return len(words) < 4

EN = re.compile(r"\b(the|and|your|with|from|this|that|our|we|are|is|will|can|you|for|of|to|"
                r"all|new|more|best|ready|solutions|systems|software|services)\b", re.I)

# English-detector words that are ALSO valid words of the page language, so
# they are not evidence of English prose: "for"/"at"/"to" in Danish, "is" is
# the Estonian inessive suffix (AWS-is, Azure'is) and the ice-word in da/no/sv.
SHARED_EN = {
    'da': {'for', 'at', 'to', 'is'},
    'no': {'for', 'to', 'is'},
    'sv': {'for', 'to', 'is'},
    'et': {'is'},
    'nl': {'is'},
}

# Distinctive words of each locale (none of them are English words). Two or
# more distinct hits mean the block already reads in the page language and is
# not English prose - this zeroes the documented false alarms on da/et/no
# (Scandinavian/Estonian function words tripping the English heuristic).
LANG_WORDS = {
    'da': {'og', 'til', 'som', 'med', 'ikke', 'vores', 'deres', 'hver', 'blir', 'kan',
           'har', 'være', 'det', 'denne', 'dette', 'eller', 'hvor', 'når', 'også'},
    'no': {'og', 'til', 'som', 'med', 'ikke', 'vår', 'våre', 'dere', 'hver', 'blir',
           'kan', 'har', 'være', 'det', 'denne', 'dette', 'eller', 'hvor', 'når', 'også'},
    'sv': {'och', 'till', 'som', 'med', 'inte', 'vår', 'våra', 'eras', 'varje', 'blir',
           'kan', 'har', 'vara', 'det', 'denna', 'detta', 'eller', 'var', 'också'},
    'et': {'ja', 'ei', 'või', 'ning', 'meie', 'teie', 'kõik', 'iga', 'samuti', 'aga',
           'ole', 'olla', 'meid', 'teid', 'kuid'},
    'de': {'der', 'das', 'und', 'nicht', 'mit', 'für', 'unser', 'unsere', 'ihre', 'ist',
           'sind', 'auch', 'bei', 'von', 'dieser', 'diese', 'werden', 'können', 'mehr'},
    'fr': {'les', 'des', 'une', 'nos', 'vos', 'pour', 'est', 'sont', 'dans', 'avec',
           'nous', 'votre', 'vous', 'qui', 'que', 'cette', 'aux', 'sur', 'leur', 'ainsi'},
    'es': {'los', 'las', 'una', 'está', 'están', 'para', 'con', 'sobre', 'más', 'pero',
           'como', 'cuando', 'cada', 'además', 'nuestro', 'nuestra', 'usted', 'sus'},
    'it': {'gli', 'delle', 'degli', 'sono', 'per', 'con', 'più', 'anche', 'nostro',
           'nostra', 'questo', 'questa', 'loro', 'nella', 'nel', 'sul', 'alla', 'tutte'},
    'pt': {'são', 'dos', 'das', 'uma', 'para', 'com', 'mais', 'como', 'também', 'nosso',
           'nossa', 'isso', 'cada', 'sobre', 'pela', 'pelo', 'nas', 'todos', 'todas'},
    'nl': {'het', 'een', 'van', 'niet', 'met', 'voor', 'ons', 'onze', 'zijn', 'wordt',
           'ook', 'als', 'bij', 'deze', 'dit', 'naar', 'dat', 'uw', 'wij', 'hun'},
    'tr': {'bir', 'için', 'olarak', 'daha', 'değil', 'olmak', 'olan', 'bu', 'şu', 'tüm',
           'her', 'ile', 'kadar', 'bizim', 'sizin', 've', 'çok', 'yok'},
    'pl': {'oraz', 'jest', 'są', 'dla', 'że', 'nie', 'jak', 'który', 'która', 'które',
           'nasze', 'naszych', 'także', 'przez', 'może', 'każdy', 'wszystkie', 'się'},
    'cs': {'jsou', 'pro', 'které', 'který', 'nám', 'vaše', 'naše', 'není', 'jako',
           'podle', 'mezi', 'tím', 'této', 'toto', 'vše', 'každý', 'jsme', 'své'},
    'sk': {'sú', 'pre', 'ktoré', 'ktorý', 'naše', 'vaše', 'nie', 'ako', 'medzi',
           'týmto', 'tejto', 'všetky', 'každý', 'sme', 'svoje'},
    'hu': {'és', 'egy', 'nem', 'minden', 'vagy', 'van', 'vannak', 'hogy', 'mely', 'önt',
           'csak', 'nincs', 'az'},
    'ro': {'și', 'este', 'sunt', 'pentru', 'fiecare', 'nostru', 'noastră', 'care', 'nu',
           'mai', 'cele', 'ale', 'prin', 'fără'},
    'bg': {'за', 'на', 'от', 'че', 'са', 'всяка', 'всеки', 'нашите', 'вашите', 'които',
           'към', 'при', 'или', 'всички'},
    'el': {'και', 'για', 'με', 'τα', 'τις', 'μας', 'σας', 'είναι', 'κάθε', 'όλες',
           'όλα', 'που', 'στο', 'στη'},
    'hr': {'su', 'se', 'za', 'koje', 'koja', 'naša', 'naše', 'vaše', 'nije', 'ali',
           'sve', 'svaka', 'svaki', 'kroz', 'između', 'ili'},
    'sl': {'so', 'se', 'za', 'ki', 'niso', 'vse', 'vsak', 'vsaka', 'naša', 'vaše',
           'ali', 'vseh'},
    'fi': {'ja', 'ovat', 'meidän', 'teidän', 'kaikki', 'joka', 'jokainen', 'myös',
           'mutta', 'tämä', 'nämä', 'eivät', 'ole', 'sekä'},
    'lv': {'un', 'ir', 'nav', 'vai', 'mūsu', 'jūsu', 'visi', 'katrs', 'arī', 'bet',
           'kas', 'pie', 'uz'},
    'lt': {'ir', 'yra', 'nėra', 'arba', 'mūsų', 'jūsų', 'visi', 'kiekvienas', 'kas',
           'iš', 'nuo', 'taip'},
    'ga': {'agus', 'na', 'ar', 'le', 'go', 'bhfuil', 'sé', 'sí', 'muid', 'sibh', 'iad',
           'ár', 'bhur', 'nach', 'gur'},
    'mt': {'ta', 'li', 'fil', 'tal', 'għal', 'fit', 'minn', 'għandna', 'tagħna',
           'tagħkom', 'kollha', 'jew'},
    'ku': {'û', 'bi', 'ji', 'bo', 'ev', 'ne', 'ye', 'hemû', 'her', 'xwe', 'yên'},
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True)
    ap.add_argument("--csv", default="")
    args = ap.parse_args()

    page = ROOT / args.lang / "index.html"
    if not page.exists():
        print("no page", page)
        return 2
    doc = LH.fromstring(page.read_text(encoding="utf-8", errors="replace"))

    rows = []
    for el in doc.iter():
        if not isinstance(el.tag, str) or el.tag in SKIP:
            continue
        text = re.sub(r"\s+", " ", el.text or "").strip()
        if len(text) < 18:
            continue
        # brand and product names are not English prose; strip them first
        probe = text
        for brand in BRANDS:
            probe = re.sub(re.escape(brand), " ", probe, flags=re.I)
        probe = re.sub(r"[•·|/–—-]+", " ", probe)
        raw_hits = EN.findall(probe)
        # English-detector words that double as words of the page language are
        # not evidence (da/no "for", Estonian "-is" suffix, ...)
        hits = [w for w in raw_hits if w.lower() not in SHARED_EN.get(args.lang, ())]
        lang_hits = len({w for w in LANG_WORDS.get(args.lang, ())
                         if re.search(rf"\b{re.escape(w)}\b", probe, re.I)})
        words = len(probe.split())
        if lang_hits >= 2:
            continue  # the block already reads in the page language
        if len(hits) < 2 or words < 4:
            continue
        if is_brand_only(text):
            continue
        # section = nearest ancestor with an id
        node, section = el, ""
        while node is not None:
            if node.get("id"):
                section = node.get("id")
                break
            node = node.getparent()
        rows.append({"section": section or "-", "words": words, "text": text})

    rows.sort(key=lambda r: (-r["words"], r["section"]))
    print(f"{args.lang}: {len(rows)} English blocks, {sum(r['words'] for r in rows):,} words")
    by_section = {}
    for r in rows:
        by_section[r["section"]] = by_section.get(r["section"], 0) + 1
    for name, count in sorted(by_section.items(), key=lambda x: -x[1])[:10]:
        print(f"   {name:28} {count}")
    for r in rows[:5]:
        print(f"   - [{r['section']}] {r['text'][:80]}")

    if args.csv:
        out = pathlib.Path(args.csv)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["section", "words", "text", "translation"])
            w.writeheader()
            for r in rows:
                w.writerow({**r, "translation": ""})
        print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
