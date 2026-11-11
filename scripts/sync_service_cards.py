"""Upgrade the six service cards in a language page to the master's card shell.

Master redesigned the card header (number, title, badge, icon on one bar). The
localized pages kept the old shell, so the same six services render differently.
This copies the master's shell and keeps the language's own words and its
working action buttons - no handler is added that the page does not ship.

  python scripts/sync_service_cards.py --lang de [--dry-run]
"""
import argparse, pathlib, re, sys
from lxml import html as LH

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOKEN = re.compile(r'<!--.*?-->|<script\b.*?</script>|<div\b|</div\s*>', re.S | re.I)
CARD_OPEN = re.compile(r'<div class="wg-tech-v2"')
BADGES = {"de": "Am gefragtesten", "nl": "Meest gevraagd",
          "fr": "Le plus demandé", "es": "El más solicitado"}


def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def span_of(html, open_index):
    depth = 0
    for tok in TOKEN.finditer(html, open_index):
        raw = tok.group(0).lower()
        if raw.startswith("<div"):
            depth += 1
        elif raw.startswith("</div"):
            depth -= 1
        if depth == 0:
            return tok.end()
    raise SystemExit("unbalanced card")


def build_card(master_card, target_card, badge_text):
    # master comments are Arabic; they would fail the LTR purity gate
    master_card = re.sub(r'<!--.*?-->', '', master_card, flags=re.S)
    node = LH.fragment_fromstring(master_card)

    t_title = target_card.xpath(".//*[contains(@class,'tech-name')]")
    t_desc = target_card.xpath(".//*[contains(@class,'tech-desc')]")
    t_metric = target_card.xpath(".//*[contains(@class,'tech-metric-tag')]")
    t_img = target_card.xpath(".//img")
    t_footer = target_card.xpath(".//*[contains(@class,'tech-card-footer-actions')]")

    title = node.xpath(".//*[contains(@class,'tech-name')]")
    if title and t_title:
        title[0].text = norm(t_title[0].text_content())

    desc = node.xpath(".//*[contains(@class,'tech-desc')]")
    if desc and t_desc:
        # master prose can carry inline tags whose tails are Arabic: drop them
        for child in list(desc[0]):
            desc[0].remove(child)
        desc[0].text = norm(t_desc[0].text_content())
        if t_desc[0].get("data-short"):
            desc[0].set("data-short", norm(t_desc[0].get("data-short")))

    metric = node.xpath(".//*[contains(@class,'metric-text')]")
    if metric:
        for child in list(metric[0]):
            metric[0].remove(child)
    if metric and t_metric:
        inner = t_metric[0]
        text = norm(" ".join(inner.itertext()))
        text = re.sub(r"^[^\wÀ-ÿ]+", "", text).strip()
        metric[0].text = text

    img = node.xpath(".//img")
    if img and t_img:
        src = t_img[0].get("src") or ""
        img[0].set("src", src.replace("./", "../", 1) if src.startswith("./") else src)
        if t_img[0].get("alt"):
            img[0].set("alt", t_img[0].get("alt"))

    badge = node.xpath(".//*[contains(@class,'dana-price-badge-saving')]")
    if badge:
        if badge_text:
            badge[0].text = badge_text
        else:
            badge[0].getparent().remove(badge[0])

    footer = node.xpath(".//*[contains(@class,'tech-card-footer-actions')]")
    if footer and t_footer:
        footer[0].getparent().replace(footer[0], LH.fromstring(LH.tostring(t_footer[0], encoding="unicode")))

    return LH.tostring(node, encoding="unicode")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    lang = args.lang

    master_doc = LH.fromstring((ROOT / "index.html").read_text(encoding="utf-8", errors="replace"))
    master_cards = master_doc.xpath("//*[contains(@class,'wg-tech-v2')]")
    page = ROOT / lang / "index.html"
    html = page.read_text(encoding="utf-8", errors="replace")

    if html.count("tech-card-top-bar") >= 6:
        print(f"{lang}: cards already carry the master shell")
        return 0

    target_doc = LH.fromstring(html)
    target_cards = target_doc.xpath("//*[contains(@class,'wg-tech-v2')]")
    if len(target_cards) != len(master_cards):
        print(f"{lang}: card count {len(target_cards)} != master {len(master_cards)}")
        return 2

    badge = BADGES.get(lang)
    new_markup = [build_card(LH.tostring(m, encoding="unicode"), t, badge)
                  for m, t in zip(master_cards, target_cards)]

    # replace from the last card backwards so earlier offsets stay valid
    spans = []
    pos = 0
    for _ in range(len(master_cards)):
        m = CARD_OPEN.search(html, pos)
        if not m:
            print(f"{lang}: card markup not found in raw html")
            return 3
        end = span_of(html, m.start())
        spans.append((m.start(), end))
        pos = end

    for (start, end), markup in zip(reversed(spans), reversed(new_markup)):
        html = html[:start] + markup + html[end:]

    print(f"{lang}: {len(new_markup)} cards upgraded ({len(html):,} bytes)")
    if args.dry_run:
        print("dry run - nothing written")
        return 0
    page.write_text(html, encoding="utf-8", newline="")
    print(f"wrote {page}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
