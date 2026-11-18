#!/usr/bin/env python3
"""توحيد موضع فوتر الموقع srf في بوابات اللغات على الترتيب المرجعي للجذر.

المرجع (index.html الجذر العربي): السكربتات الأساسية (sr-command, sr-lang-hint,
sr-sound, sr-print-guard, sr-consent) ثم الفوتر. في بوابات اللغات الفوتر مدمج
داخل أسطر سكربتات/أنماط قبل الكتلة — يُستأصل هنا بايت-ببايت ويُدرج سطراً مستقلاً
بعد آخر سكربت أساسي، فتعود أسطر السكربتات ملتصقة كما كانت قبل حقن الفوتر.

تحديد العنصر = منهجية docs/audit_structure_vs_master.py الرسمي: تحليل lxml
وأخذ footer[@id="srf-footer"] الوحيد، ثم تحويل موقعه إلى بايتات داخل السطر.

الضمانات لكل صفحة (أي إخلال = لا كتابة):
  1. الاستئصال من منتصف السطر يترك البادئة واللاحقة متلاصقتين بايت-ببايت.
  2. بايتات وسم الفوتر نفسه لا تتغير إطلاقاً (يُدرج كما هو).
  3. المستند كله ما عدا وسم الفوتر المنقول متطابق بالبايت قبل وبعد.
  4. عدد عناصر footer المحللة وعدد السكربتات الأساسية ثابتان.
  5. idempotent: الفوتر سطراً مستقلاً بعد آخر سكربت أساسي = لا تغيير.

الاستخدام: python scripts/unify_footer_position.py [--check]
"""
import re
import sys
import os
from lxml import etree

LOCALES = ["ckb","cs","da","de","el","en","es","et","fi","fr","ga","hr","hu","it","ku",
           "lt","lv","mt","nl","no","pl","pt","ro","sk","sl","sv","tr"]
CORE = re.compile(
    r'<script src="\.\./js/sr-(command|lang-hint|sound|print-guard|consent)\.js[^"]*"[^>]*></script>')
FTAG, FEND = '<footer class="srf"', "</footer>"

def parsed_counts(h):
    root = etree.fromstring(h.encode("utf-8"), etree.HTMLParser(recover=True))
    return len(root.xpath("//footer")), len(root.xpath('//footer[@id="srf-footer"]'))

def core_line_end(h):
    cores = list(CORE.finditer(h))
    if not cores:
        return None
    last_end = h.find("</script>", cores[-1].start()) + len("</script>")
    le = h.find("\n", last_end)
    return (len(h) if le < 0 else le + 1, cores[-1].group(1), len(cores))

def process(path, check_only):
    with open(path, encoding="utf-8", newline="") as f:
        h = f.read()
    n_footer, n_srf = parsed_counts(h)
    if n_srf == 0:
        return ("NO-FOOTER", "لا فوتر srf — بند منفصل (ckb)")
    if n_srf != 1:
        return ("ERR", f"عدد فوترات srf = {n_srf} — غير متوقع")
    ce = core_line_end(h)
    if not ce:
        return ("NO-CORE", "لا سكربتات أساسية — غير متوقع")
    core_le, core_name, n_core_re = ce
    # موقع السطر الحاوي للفوتر: sourceline أولاً مع تحقق، وإلا فحص نصي
    lines = h.splitlines(keepends=True)
    li = None
    root = etree.fromstring(h.encode("utf-8"), etree.HTMLParser(recover=True))
    el = root.xpath('//footer[@id="srf-footer"]')[0]
    sl = getattr(el, "sourceline", None)
    if sl and 1 <= sl <= len(lines) and FTAG in lines[sl - 1]:
        li = sl - 1
    else:
        for i, ln in enumerate(lines):
            if FTAG in ln:
                li = i
                break
    if li is None:
        return ("ERR", "لم يُوجد سطر الوسم")
    line = lines[li]
    s = line.find(FTAG)
    e = line.find(FEND, s)
    if s < 0 or e < 0:
        return ("ERR", "الوسم غير مكتمل في السطر")
    e += len(FEND)
    if FTAG in line[e:] or line[s:e].count("<footer") != 1:
        return ("ERR", "وسوم footer متداخلة في السطر")
    footer_bytes = line[s:e]
    # idempotent: الفوتر وحده في سطره بعد آخر سكربت أساسي (فراغات بينهما فقط)
    byte_pos = sum(len(x) for x in lines[:li])
    alone = line[:s].strip() == "" and line[e:].strip() == ""
    if alone and byte_pos + s >= core_le and h[core_le:byte_pos + s].strip() == "":
        return ("ALREADY", "الفوتر بالترتيب المرجعي أصلاً")
    if check_only:
        return ("DRIFT", f"الفوتر مدمج قبل آخر سكربت أساسي ({core_name})")
    # الاستئصال: السطر يفقد وسم الفوتر فقط — البادئة واللاحقة تتلاصق
    new_line = line[:s] + line[e:]
    h2_lines = lines[:li] + [new_line] + lines[li + 1:]
    rest = "".join(h2_lines)
    cle2 = core_line_end(rest)[0] if core_line_end(rest) else None
    if cle2 is None:
        return ("ERR", "فقدان السكربتات بعد الاستئصال")
    h2 = rest[:cle2] + footer_bytes + "\n" + rest[cle2:]
    # الضمانات
    nf2, nsrf2 = parsed_counts(h2)
    if (nf2, nsrf2) != (n_footer, n_srf):
        return ("ERR", "عدد الفوترات المحللة تغير — إلغاء")
    if len(CORE.findall(h2)) != n_core_re:
        return ("ERR", "عدد السكربتات الأساسية تغير — إلغاء")
    if h2.replace(footer_bytes + "\n", "", 1) != rest:
        return ("ERR", "المستند خارج الفوتر تغيّر — إلغاء")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(h2)
    return ("FIXED", f"استُأصل من سطر {li+1} وأُدرج بعد سكربت {core_name} (سطر {h2[:cle2].count(chr(10))+1})")

def main():
    check_only = "--check" in sys.argv
    fixed = already = errs = drift = 0
    for loc in LOCALES:
        p = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", loc, "index.html"))
        status, msg = process(p, check_only)
        mark = {"FIXED": "✅", "ALREADY": "·", "DRIFT": "⚠", "NO-FOOTER": "✗", "NO-CORE": "✗", "ERR": "⛔"}[status]
        print(f"{mark} {loc:4} {status:8} {msg}")
        if status == "FIXED": fixed += 1
        elif status == "ALREADY": already += 1
        elif status == "DRIFT": drift += 1
        else: errs += 1
    print(f"\nالملخص: نُقل {fixed} · سليم {already} · انحراف {drift} · مشكلات {errs}")
    if check_only and (drift or errs or fixed):
        sys.exit(1)

if __name__ == "__main__":
    main()
