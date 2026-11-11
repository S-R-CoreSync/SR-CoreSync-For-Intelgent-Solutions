import pathlib, re
from lxml import html as LH
p = pathlib.Path("de/index.html")
raw = p.read_text(encoding="utf-8", errors="replace")
doc = LH.fromstring(raw)
# rebuild each tech-desc as plain escaped text, dropping Arabic tails
count = 0
for el in doc.xpath("//*[contains(@class,'tech-desc')]"):
    if len(el):
        for child in list(el):
            el.remove(child)
        count += 1
out = LH.tostring(doc, encoding="unicode", method="html")
print("cleaned desc nodes:", count)
p.write_text(out, encoding="utf-8", newline="")
print("arabic chars now:", len(re.findall(r"[\u0600-\u06FF]", out)))
