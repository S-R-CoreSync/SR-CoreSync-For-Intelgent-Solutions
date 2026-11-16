@echo off & chcp 65001 >nul & title CoreSync CI Fix - Achievement 164 & python -x "%~f0" || py -3 -x "%~f0" & echo. & pause & exit /b
# -*- coding: utf-8 -*-
"""الملف الواحد — إصلاح CI: تثبيت lxml في ci.yml و deploy-pages.yml ثم الدفع (الإنجاز 164)."""
import os, subprocess, sys, traceback

def out(s):
    print(s, flush=True)

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    out("=" * 62)
    out("  الملف الواحد — إصلاح CI: تثبيت lxml (الإنجاز 164)")
    out("=" * 62)
    try:
        root = os.path.dirname(os.path.abspath(__file__))
        out("جذر المشروع المكتشف: " + root)
        if not os.path.isdir(os.path.join(root, ".git")):
            out("FAIL: لا يوجد مجلد .git في هذا الموضع.")
            out("النقل الصحيح: انسخ هذا الملف إلى جذر المشروع:")
            out(r"  D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project")
            out("ثم نقرة مزدوجة عليه من جديد. إن تكررت الرسالة انسخها وأرسلها للمساعد.")
            return
        wf = os.path.join(root, ".github", "workflows")
        if not os.path.isfile(os.path.join(wf, "ci.yml")):
            out("FAIL: لم أجد .github/workflows/ci.yml في هذا الجذر — تأكد أنك وضعت الملف في جذر المشروع الصحيح.")
            return

        def git(*args):
            env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
            r = subprocess.run(["git"] + list(args), cwd=root, capture_output=True, env=env)
            return (r.returncode,
                    (r.stdout or b"").decode("utf-8", "replace"),
                    (r.stderr or b"").decode("utf-8", "replace"))

        out("[1/5] جلب آخر حالة من GitHub ...")
        rc, so, se = git("fetch", "origin")
        if rc != 0:
            out("FAIL: فشل git fetch — تحقق من الاتصال بالإنترنت ثم أعد تشغيل الملف.")
            out(se.strip())
            return
        _, head, _ = git("rev-parse", "HEAD"); head = head.strip()
        _, om, _ = git("rev-parse", "origin/main"); om = om.strip()
        if head != om:
            out("[2/5] نسخة جهازك متأخرة عن GitHub — تحديث سريع (fast-forward) ...")
            rc, so, se = git("merge", "--ff-only", "origin/main")
            if rc != 0:
                out("FAIL: التعديل المباشر لم يكتمل — نسخة جهازك مختلفة البنية (التزامات محلية أو ملفات غير محفوظة).")
                out("الخطة: شغّل ملف المزامنة (مزامنة_المشروع_مع_GitHub.bat) أولاً ثم أعد تشغيل هذا الملف.")
                out(se.strip())
                return
            out("      تم التحديث إلى أحدث حالة بنجاح")
        else:
            out("[2/5] نسخة جهازك مطابقة لأحدث حالة على GitHub")

        INSTALL = ('      - name: Install Python dependencies (lxml)\n'
                   '        run: |\n'
                   '          python -m pip install --upgrade pip\n'
                   '          python -m pip install "lxml>=5.0"\n')
        targets = [
            (os.path.join(wf, "ci.yml"), "      - name: Verify HTML & CSS Syntax Integrity\n"),
            (os.path.join(wf, "deploy-pages.yml"), "      - name: Build the pages from their parts\n"),
        ]
        changed = 0
        for path, anchor_lf in targets:
            name = os.path.basename(path)
            with open(path, "r", encoding="utf-8", newline="") as f:
                txt = f.read()
            if "Install Python dependencies (lxml)" in txt:
                out("[3/5] " + name + ": الإصلاح مطبّق مسبقاً — تخطي")
                continue
            eol = "\r\n" if "\r\n" in txt else "\n"
            anchor = anchor_lf.replace("\n", eol)
            install = INSTALL.replace("\n", eol)
            c = txt.count(anchor)
            if c != 1:
                out("FAIL: في " + name + " لم أجد نقطة الإدراج الفريدة (عدد المطابقات: " + str(c) + ").")
                out("المحتوى اختلف عن المتوقع — انسخ هذه الرسالة كاملة وأرسلها للمساعد دون أي تعديل.")
                return
            txt2 = txt.replace(anchor, install + anchor)
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(txt2)
            changed += 1
            out("[3/5] " + name + ": أُدرجت خطوة التثبيت بنجاح (+" + str(len(txt2) - len(txt)) + " بايت)")
        if changed == 0:
            out("[4/5] لا جديد للرفع — الإصلاح مطبّق بالكامل مسبقاً.")
            out("PASS: لا شيء مطلوب — إذا كانت Actions ما زالت حمراء فالسبب تشغيل قديم؛ افتح أحدث تشغيل.")
            out("=" * 62)
            return

        out("[4/5] الحفظ في git والرفع إلى GitHub ...")
        rc, so, se = git("add", ".github/workflows/ci.yml", ".github/workflows/deploy-pages.yml")
        rc, so, se = git("commit", "-m", "fix(ci): install lxml for the blocking content-parity gate (achievement 164)")
        if rc != 0:
            out("FAIL: فشل git commit — انسخ الرسالة التالية كاملة وأرسلها لي:")
            out((se or so).strip())
            return
        rc, so, se = git("push", "origin", "main")
        if rc != 0:
            out("FAIL: فشل git push — انسخ الرسالة التالية كاملة وأرسلها لي دون تعديل:")
            out((se or so).strip())
            return
        out("[5/5] تم الرفع إلى GitHub بنجاح")
        out("=" * 62)
        out("PASS: الإصلاح مرفوع — CI سيعاد تشغيله تلقائياً الآن.")
        out("الخطوة الأخيرة: افتح تبويب Actions في المستودع بعد 2-3 دقائق،")
        out("انتظر علامة الأخضر على أحدث تشغيل، ثم اكتب لي في المحادثة كلمة: أخضر")
        out("=" * 62)
    except Exception:
        out("FAIL: استثناء غير متوقع — انسخ كل هذه الرسالة وأرسلها للمساعد:")
        out(traceback.format_exc())

main()
sys.exit(0)
