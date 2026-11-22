#!/usr/bin/env python3
"""البند 18: تطبيع نمط الاقتباس المشوّه في tes-rating (aria-label/data-i18n).

العطل (الالتزام 3796d5cb، 2026-11-15): في 28 صفحة نشر + مرآة partials/en
القيمة القاموسية للتصنيف فقدت موضعها داخل الوسم بشكلين:
  A) aria-label=" data-i18n="testimonials.0X.rating"">          (27 لغة — القيمة ضائعة)
  B) aria-label=" data-i18n="testimonials.0X.rating""VALUE">    (en + المرآة — القيمة مزاحة)
والشكل المرجعي النظيف (الجذر العربي وبطاقة en الأولى):
  aria-label="<القيمة القاموسية>" data-i18n="testimonials.0X.rating">

الأوضاع:
  --apply  : إصلاح كل موقع من القاموس الموحد (dict-exact) مع الضمانات:
             ثبات النص المرئي حرفياً، ثبات عدد بطاقات tes-rating،
             ولا كتابة إن لم يتغير شيء (idempotent ببنية الملف نفسها).
  --check  : وضع الحارس (الثالث عشر في السنتينل):
             (1) صفر نمط مشوّه على مجموعة النشر + المرآة
             (2) كل وسم tes-rating: aria-label يطابق القاموس حرفياً + الشكل القانوني
             (3) اختبار سلبي ذاتي: النمطان A/B الاصطناعيان يجب أن يُكتشفا ويُصلحا
خروج غير صفري = فشل.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from publish_set import iter_publish_files  # noqa: E402

CARDS = ("01", "02", "03", "04", "05")
MIRROR = "partials/en/99-tail.html"
# نمط الوسم المشوّه (يغطي الشكلين A وB): كل ما بين aria-label=" المعطوب وإغلاق الوسم
BROKEN = re.compile(
    r'aria-label=" data-i18n="(testimonials\.0[1-5]\.rating)"[^>]*>')
TAG = re.compile(r'<p class="tes-rating"[^>]*>', re.DOTALL)
CLEAN_TAG = re.compile(
    r'^<p\s+class="tes-rating"\s+role="img"\s+aria-label="([^"]*)"\s+'
    r'data-i18n="(testimonials\.0[1-5]\.rating)">$', re.DOTALL)
VISIBLE_STRIP = re.compile(r"<[^>]+>")

def load_dict():
    import json
    return json.loads((ROOT / "i18n" / "sections" / "testimonials.json")
                      .read_text(encoding="utf-8"))

def lang_of(rel):
    if rel == "index.html":
        return "ar"
    if rel.startswith("partials/"):
        return "en"
    return rel.split("/", 1)[0]

def visible_text(h):
    return VISIBLE_STRIP.sub("", re.sub(r"<(script|style)\b.*?</\1>", "", h, flags=re.S))

def fix_text(h, lang, dic):
    """أعد كل وسم tes-rating إلى الشكل القانوني بقيمة القاموس. يعيد (نص، عدد الإصلاحات)."""
    fixes = 0
    def repl(m):
        nonlocal fixes
        key = m.group(1)
        val = dic.get(lang, {}).get(key)
        if val is None:
            raise SystemExit(f"⛔ مفتاح القاموس مفقود: {lang}.{key} — ممنوع الابتكار")
        fixes += 1
        return f'aria-label="{val}" data-i18n="{key}">'
    return BROKEN.sub(repl, h), fixes

def targets():
    for rel in iter_publish_files(ROOT):
        if rel.lower().endswith(".html"):
            yield rel
    yield MIRROR

def apply_mode(dic):
    total_files = total_fixes = 0
    for rel in targets():
        p = ROOT / rel
        with open(p, encoding="utf-8", newline="") as f:
            h = f.read()
        n_tags = len(TAG.findall(h))
        vtext = visible_text(h)
        h2, n = fix_text(h, lang_of(rel), dic)
        if not n:
            continue
        # الضمانات: النص المرئي ثابت + عدد البطاقات ثابت
        assert visible_text(h2) == vtext, f"{rel}: النص المرئي تغير — إلغاء"
        assert len(TAG.findall(h2)) == n_tags, f"{rel}: عدد البطاقات تغير — إلغاء"
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(h2)
        total_files += 1
        total_fixes += n
        print(f"✅ {rel}: {n} موضعاً")
    print(f"الملخص: {total_fixes} موضعاً في {total_files} ملفاً")
    return 0

def check_mode(dic):
    bad = []
    # (1) صفر نمط مشوّه + (2) مطابقة القاموس حرفياً بالشكل القانوني
    for rel in targets():
        with open(ROOT / rel, encoding="utf-8", newline="") as f:
            h = f.read()
        lang = lang_of(rel)
        if BROKEN.search(h):
            bad.append(f"{rel}: نمط مشوّه باقٍ ({len(BROKEN.findall(h))})")
        for m in TAG.finditer(h):
            tag = m.group(0)
            cm = CLEAN_TAG.match(tag)
            if not cm:
                bad.append(f"{rel}: وسم خارج الشكل القانوني: {tag[:90]}")
                continue
            val, key = cm.groups()
            expected = dic.get(lang, {}).get(key)
            if val != expected:
                bad.append(f"{rel}: {key} القيمة لا تطابق القاموس: {val!r} ≠ {expected!r}")
    # (3) الاختبار السلبي الذاتي: النمطان يجب أن يُكتشفا ويُصلحا، والنظيف يبقى كما هو
    samples = [
        'aria-label=" data-i18n="testimonials.01.rating"">',                       # A
        'aria-label=" data-i18n="testimonials.05.rating""Rating 5 out of 5">',     # B
        'aria-label="التقييم 5 من 5" data-i18n="testimonials.01.rating">',         # نظيف
    ]
    synthetic = f'<p class="tes-rating" role="img" {samples[0]}' + "\n" \
        + f'<p class="tes-rating" role="img" {samples[1]}' + "\n" \
        + f'<p class="tes-rating" role="img" {samples[2]}'
    fixed, n = fix_text(synthetic, "en", dic)
    if n != 2 or 'aria-label="Rating 5 out of 5" data-i18n="testimonials.01.rating">' not in fixed \
            or f'aria-label="{dic["en"]["testimonials.05.rating"]}"' not in fixed \
            or samples[2] not in fixed:
        bad.append("الاختبار السلبي فشل: الكشف/الإصلاح لا يعمل كما يجب")
    if bad:
        print("TES-RATING GUARD RED:")
        for b in bad:
            print("  ⛔", b)
        return 1
    print("TES-RATING GUARD GREEN: صفر مواضع مشوهة، كل القيم مطابقة للقاموس حرفياً، "
          "والاختبار السلبي يثبت كاشفاً فعّالاً.")
    return 0

def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--apply", action="store_true")
    g.add_argument("--check", action="store_true")
    args = ap.parse_args()
    dic = load_dict()
    return apply_mode(dic) if args.apply else check_mode(dic)

if __name__ == "__main__":
    sys.exit(main())
