import re, pathlib
from lxml import html as LH
def card(path, i=0):
    d = LH.fromstring(pathlib.Path(path).read_text(encoding="utf-8", errors="replace"))
    cards = d.xpath("//*[contains(@class,'wg-tech-v2')]")
    s = LH.tostring(cards[i], encoding="unicode")
    return re.sub(r"\n\s*", "\n", s)
m = card("index.html"); t = card("de/index.html")
print("MASTER len", len(m)); print(m[:2200])
print("="*70)
print("DE len", len(t)); print(t[:1600])
