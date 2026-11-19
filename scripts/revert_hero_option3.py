"""
revert_hero_option3.py
======================
تراجع كامل عن الخيار الثالث (Option 3) وعودة للهيرو الأصلي:
  - c3-core-orb   +   sr-core-emblem-official.webp
"""

import os
import re
import pathlib

ROOT = pathlib.Path(r"d:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project")

# ─── 1. النص القديم والجديد في HTML ─────────────────────────────────────────
OLD_DIV = (
    '<div class="c3-centerpiece-showcase" id="heroOrbCore" '
    'data-sr-call="openLogoLightbox" data-sr-event="1" '
    'title="S&amp;R CoreSync Sovereign 3D Cloud Ecosystem">\n'
    '                    <img src="./assets/branding/hero-emblem-orbital-cloud-ecosystem.webp" '
    'alt="S&amp;R CoreSync Sovereign 3D Cloud Ecosystem" '
    'width="580" height="380" class="c3-centerpiece-img" loading="eager" decoding="async">\n'
    '                </div>'
)
NEW_DIV = (
    '<div class="c3-core-orb" id="heroOrbCore" '
    'data-sr-call="openLogoLightbox" data-sr-event="1" '
    'title="S&amp;R CoreSync Sovereign Intelligent Core">\n'
    '                    <img src="./assets/sr-core-emblem-official.webp" '
    'alt="S&amp;R CoreSync Sovereign Intelligent Core" '
    'width="100" height="100" class="c3-orb-img" loading="eager" decoding="async">\n'
    '                </div>'
)

# بالنسبة للمسار النسبي في الـ en/ partition (./assets → ثابت نفسه)
OLD_DIV_EN = OLD_DIV  # نفس الصياغة
NEW_DIV_EN = NEW_DIV  # نفس الصياغة

# ─── 2. ملفات HTML التي تحتاج تعديل ─────────────────────────────────────────
SKIP_DIRS = {".git", "_site", "SR-CoreSync-For-Intelgent-Solutions", "node_modules"}

html_files = []
for path in ROOT.rglob("index.html"):
    if any(s in path.parts for s in SKIP_DIRS):
        continue
    html_files.append(path)

# ─── 3. تطبيق التبديل على HTML ───────────────────────────────────────────────
replaced_html = []
skipped_html = []

for f in html_files:
    text = f.read_text(encoding="utf-8")
    if "c3-centerpiece-showcase" in text:
        new_text = text.replace(OLD_DIV, NEW_DIV, 1)
        if new_text == text:
            # محاولة regex بديلة للتعامل مع اختلافات المسافات
            new_text = re.sub(
                r'<div class="c3-centerpiece-showcase"[^>]*>.*?</div>',
                NEW_DIV,
                text,
                count=1,
                flags=re.DOTALL
            )
        f.write_text(new_text, encoding="utf-8")
        replaced_html.append(str(f.relative_to(ROOT)))
    else:
        skipped_html.append(str(f.relative_to(ROOT)))

# ─── 4. ملفات الـ partials ────────────────────────────────────────────────────
for pf in [ROOT / "partials" / "20-hero.html", ROOT / "partials" / "en" / "20-hero.html"]:
    if pf.exists():
        text = pf.read_text(encoding="utf-8")
        if "c3-centerpiece-showcase" in text:
            new_text = text.replace(OLD_DIV, NEW_DIV, 1)
            if new_text == text:
                new_text = re.sub(
                    r'<div class="c3-centerpiece-showcase"[^>]*>.*?</div>',
                    NEW_DIV,
                    text,
                    count=1,
                    flags=re.DOTALL
                )
            pf.write_text(new_text, encoding="utf-8")
            replaced_html.append(str(pf.relative_to(ROOT)))

# ─── 5. إزالة كتلة CSS الخاصة بـ Option 3 من hero-declutter.css ──────────────
css_path = ROOT / "css" / "hero-declutter.css"
css_text = css_path.read_text(encoding="utf-8")

# حذف الكتلة كاملة من التعليق حتى نهاية الملف (أو حتى نهاية آخر قاعدة)
css_block_pattern = re.compile(
    r"/\* ={10,}\s*\n\s*Option 3 Sovereign 3D Centerpiece.*",
    re.DOTALL
)
new_css = css_block_pattern.sub("", css_text).rstrip() + "\n"
css_path.write_text(new_css, encoding="utf-8")

# ─── 6. استعادة حركات الحلقات (rotateCockpitRing) إن كانت مشطوبة ─────────────
# الملف يحتوي بالفعل على تعريفات الـ keyframes لكن animation مشطوب
# نتحقق: إن كانت animation مفقودة نضيفها
css_text2 = css_path.read_text(encoding="utf-8")

# قائمة بالـ rules التي تحتاج animation
ring_fixes = [
    (".c3-orb-ring-outer", "animation: rotateCockpitRing 25s infinite linear;"),
    (".c3-orb-ring-inner", "animation: rotateCockpitRingReverse 18s infinite linear;"),
]

for selector, anim_rule in ring_fixes:
    # البحث عن الكتلة
    block_match = re.search(
        re.escape(selector) + r"\s*\{([^}]*)\}",
        css_text2,
        flags=re.DOTALL
    )
    if block_match:
        block_body = block_match.group(1)
        if "animation:" not in block_body:
            new_body = block_body.rstrip() + f"\n    {anim_rule}\n"
            css_text2 = css_text2[:block_match.start(1)] + new_body + css_text2[block_match.end(1):]

css_path.write_text(css_text2, encoding="utf-8")

# ─── 7. التقرير ───────────────────────────────────────────────────────────────
print("=" * 60)
print("✅ تراجع الهيرو - تقرير الإنجاز")
print("=" * 60)
print(f"📄 HTML ملفات تم تعديلها  : {len(replaced_html)}")
for f in replaced_html:
    print(f"   ✓ {f}")
print(f"⏭️  HTML ملفات تم تجاوزها : {len(skipped_html)}")
print(f"🎨 CSS تم تنظيف كتلة Option 3 من: css/hero-declutter.css")
print(f"⚙️  تم استعادة animation للحلقات في hero-declutter.css")
print("=" * 60)
print("الخطوة التالية: تشغيل preflight.py")
