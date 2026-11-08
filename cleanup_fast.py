#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""الإنجاز 160 — النسخة السريعة: جرد وتنظيف شامل في دقائق بدل ساعات.

لماذا كانت النسخة الأولى بطيئة؟
  كانت تفحص كل ملف في المشروع (بما فيها node_modules و .git وقد تصل لمئات
  آلاف الملفات) وتحسب بصمة SHA-256 كاملة لكل ملف => ساعات انتظار.
هذه النسخة:
  1) تتخطى المجلدات الثقيلة نهائياً ولا تدخلها أصلاً.
  2) الجرد بدون قراءة أي ملف (stat فقط).
  3) البصمة (أول 512KB) فقط للملفات المرشحة للتكرار، وبحد قراءة أقصى.
  4) لا حذف نهائي إطلاقاً: كل شيء يُنقل إلى مجلدات أرشيف قابلة للاسترجاع.
  5) الافتراضي = تقرير فقط. للتنفيذ الفعلي:  python cleanup_fast.py --go
"""

import os
import sys
import hashlib
import time
import argparse
import shutil
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

T0 = time.time()
ROOT = os.path.dirname(os.path.abspath(__file__))

HEAVY = {
    "node_modules", ".git", ".next", ".vercel", "venv", ".venv", "env",
    "__pycache__", ".cache", "dist", "build", ".idea", ".vscode", ".npm",
    ".yarn", "coverage", ".pytest_cache", ".mypy_cache", "site-packages",
    ".terraform", "vendor", ".svn", ".hg", ".ruff_cache",
    "_trash_160", "_css_archive_160", "_archive",
}

DEAD_EXT = {".bak", ".tmp", ".old", ".orig", ".pyc", ".pyo",
            ".crdownload", ".partial"}
TRASH = "_trash_160"
CSSA = "_css_archive_160"
REPORT = "CLEANUP_REPORT_fast.md"
REF_EXT = {".html", ".htm", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
           ".py", ".json", ".vue", ".svelte"}
REPORT_PREFIX = "CLEANUP_REPORT"


def log(m):
    print(m, flush=True)


def el():
    return f"{time.time() - T0:.1f}ث"


def mb(n):
    return f"{n / 1048576:.1f} ميغابايت"


def scan():
    files = []
    n = 0
    skipped = 0
    t0 = time.time()
    log("[1/4] الجرد السريع — stat فقط بدون قراءة أي ملف ...")
    log("      (تخطي تلقائي: node_modules، .git، venv، dist، build ...)") 
    for dp, dns, fns in os.walk(ROOT):
        heavy_here = [d for d in dns if d.lower() in HEAVY]
        skipped += len(heavy_here)
        dns[:] = [d for d in dns if d.lower() not in HEAVY]
        for f in fns:
            p = os.path.join(dp, f)
            try:
                st = os.stat(p)
                files.append((p, st.st_size))
            except OSError:
                pass
            n += 1
            if n % 5000 == 0:
                log(f"      ... {n} ملف — {time.time() - t0:.1f}ث")
    log(f"      الجرد اكتمل: {n} ملف في {el()} — تخطينا {skipped} مجلد ثقيل")
    return files


def head_hash(p, nbytes=524288):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        h.update(fh.read(nbytes))
    return h.hexdigest()


def find_dead(files):
    out = []
    for p, s in files:
        b = os.path.basename(p).lower()
        e = os.path.splitext(b)[1]
        if (e in DEAD_EXT or b.startswith("~$")
                or " - copy" in b or "copy of " in b
                or " - نسخة" in b or b == "thumbs.db"):
            out.append((p, s))
    return out


def find_dups(files, budget_mb=300):
    by_size = {}
    for p, s in files:
        if s >= 65536:
            by_size.setdefault(s, []).append(p)
    cand = [(sz, ps) for sz, ps in by_size.items() if len(ps) > 1]
    cand.sort(key=lambda kv: -kv[0] * len(kv[1]))
    budget = budget_mb * 1024 * 1024
    hashed = 0
    dups = []
    log(f"[2/4] فحص التكرار — {len(cand)} مجموعة بنفس الحجم (بصمة أول 512KB فقط) ...")
    for sz, ps in cand:
        if hashed >= budget:
            log("      (بلوغ حد القراءة — عرض جزئي، الأكبر أولاً)")
            break
        heads = {}
        for p in ps:
            try:
                heads.setdefault(head_hash(p), []).append(p)
                hashed += min(sz, 524288)
            except OSError:
                pass
        for g in heads.values():
            if len(g) > 1:
                dups.append((sz, g))
    dups.sort(key=lambda d: -d[0] * (len(d[1]) - 1))
    log(f"      التكرارات: {len(dups)} مجموعة في {el()}")
    return dups


def css_plan(files):
    log("[3/4] فحص ملفات CSS ومراجعها في الكود ...")
    css = [(p, s) for p, s in files if p.lower().endswith(".css")]
    used = set()
    scanned = 0
    for p, s in files:
        e = os.path.splitext(p)[1].lower()
        if e not in REF_EXT or s > 2_000_000:
            continue
        if os.path.basename(p).startswith(REPORT_PREFIX):
            continue  # التقارير نفسها ليست مراجع كود
        scanned += s
        if scanned > 80_000_000:
            log("      (بلوغ حد فحص المراجع — نتيجة جزئية)")
            break
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                txt = fh.read()
        except OSError:
            continue
        for cp, _ in css:
            name = os.path.basename(cp)
            if name != os.path.basename(p) and name in txt:
                used.add(cp)
    unused = [(p, s) for p, s in css if p not in used]
    log(f"      CSS: {len(css)} ملف — مُستخدم: {len(css) - len(unused)}"
        f" — غير مُستخدم: {len(unused)}")
    return css, used, unused


def top_dirs(files, k=15):
    agg = {}
    for p, s in files:
        rel = os.path.relpath(p, ROOT)
        top = rel.split(os.sep)[0]
        if top == rel:
            top = "(الجذر)"
        agg[top] = agg.get(top, 0) + s
    return sorted(agg.items(), key=lambda kv: -kv[1])[:k]


def build_report(files, dead, dups, unused, css):
    L = []
    L.append("# الإنجاز 160 — تقرير النسخة السريعة")
    L.append("")
    L.append(f"- التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    L.append(f"- مدة الفحص: {el()}")
    L.append(f"- ملفات مفحوصة بعد تخطي المجلدات الثقيلة: {len(files)}")
    L.append("")
    L.append("## أكبر مجلدات المستوى الأول")
    for d, s in top_dirs(files):
        L.append(f"- {d}: {mb(s)}")
    dead_save = sum(s for _, s in dead)
    dup_save = sum(sz * (len(g) - 1) for sz, g in dups)
    L.append("")
    L.append(f"## أ) ملفات ميتة: {len(dead)} — وفرة {mb(dead_save)}")
    for p, s in dead:
        L.append(f"- {os.path.relpath(p, ROOT)} ({mb(s)})")
    L.append("")
    L.append(f"## ب) نسخ مكررة: {len(dups)} مجموعة — وفرة {mb(dup_save)}")
    L.append("الاحتفاظ بالنسخة الأولى؛ البقية تنتقل إلى _trash_160.")
    for sz, g in dups:
        L.append(f"- {mb(sz)} × {len(g)} نسخ:")
        for i, p in enumerate(g):
            tag = "يُحفظ" if i == 0 else "ينتقل"
            L.append(f"  - [{tag}] {os.path.relpath(p, ROOT)}")
    L.append("")
    L.append(f"## ج) CSS: {len(css)} ملف — غير مُستخدم: {len(unused)}"
             f" (ينتقل إلى _css_archive_160)")
    for p, s in unused:
        L.append(f"- {os.path.relpath(p, ROOT)} ({mb(s)})")
    L.append("")
    L.append("## الخلاصة")
    L.append(f"- الوفرة الإجمالية المحتملة: {mb(dead_save + dup_save)}")
    L.append("- التنفيذ: python cleanup_fast.py --go")
    L.append("- كل النقل قابل للاسترجاع من _trash_160 و _css_archive_160")
    return "\n".join(L), dead_save, dup_save


def execute(dead, dups, unused):
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    tdir = os.path.join(ROOT, TRASH, stamp)
    cdir = os.path.join(ROOT, CSSA, stamp)
    os.makedirs(tdir, exist_ok=True)
    os.makedirs(cdir, exist_ok=True)
    moved = [0]
    errors = [0]

    def mv(p, dst):
        try:
            target = os.path.join(dst, os.path.basename(p))
            base, ext = os.path.splitext(target)
            i = 1
            while os.path.exists(target):
                target = f"{base}_{i}{ext}"
                i += 1
            shutil.move(p, target)
            moved[0] += 1
        except OSError as ex:
            errors[0] += 1
            log(f"      تعذر النقل: {p} — {ex}")

    log("[4/4] التنفيذ — نقل آلي قابل للاسترجاع ...")
    for p, _ in dead:
        mv(p, tdir)
    for _, g in dups:
        for p in g[1:]:
            mv(p, tdir)
    for p, _ in unused:
        mv(p, cdir)
    log(f"      نُقل {moved[0]} ملف — أخطاء: {errors[0]} — المدة {el()}")
    log(f"      للاسترجاع: الملفات في {TRASH}\\{stamp} و {CSSA}\\{stamp}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--go", action="store_true",
                    help="تنفيذ النقل (بدونه: تقرير فقط)")
    a = ap.parse_args()
    log("=== الإنجاز 160 — النسخة السريعة ===")
    log(f"الجذر: {ROOT}")
    files = scan()
    dead = find_dead(files)
    dups = find_dups(files)
    css, used, unused = css_plan(files)
    report, dead_save, dup_save = build_report(files, dead, dups, unused, css)
    with open(os.path.join(ROOT, REPORT), "w", encoding="utf-8") as fh:
        fh.write(report)
    log("")
    log("===== الخلاصة =====")
    log(f"ملفات ميتة: {len(dead)} ({mb(dead_save)})")
    log(f"مجموعات مكررة: {len(dups)} (وفرة {mb(dup_save)})")
    log(f"CSS غير مستخدم: {len(unused)} من {len(css)}")
    log(f"التقرير الكامل: {REPORT}")
    if a.go:
        execute(dead, dups, unused)
        log("اكتمل التنفيذ — كل شيء قابل للاسترجاع من مجلدي الأرشيف.")
    else:
        log("")
        log("وضع التقرير فقط — لم يُنقل أو يُحذف أي شيء.")
        log("للتنفيذ:  python cleanup_fast.py --go")
    log(f"انتهى في {el()}")


if __name__ == "__main__":
    main()
