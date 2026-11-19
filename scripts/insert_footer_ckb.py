#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""البند 23 — أداة إدراج فوتر srf السوراني في ckb/index.html (idempotent).

تصيّر الكتلة عبر sync_footer.render(model, 'ckb', '../') وتُدرجها في الموضع
المرجعي الموحد: سطر مستقل مباشرة بعد آخر سكربت أساسي (نفس معادلة
unify_footer_position: h[:cle] + footer + '\\n' + h[cle:]) — فتقررها
unify --check بحالة ALREADY لا DRIFT.

الاستخدام:
    python scripts/insert_footer_ckb.py            # تطبيق + إثباتات
    python scripts/insert_footer_ckb.py --check    # فحص فقط
"""
import sys, os, json, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import sync_footer as SF

PAGE = os.path.join(ROOT, 'ckb', 'index.html')
MODEL = os.path.join(ROOT, 'i18n', 'footer.calibrated.json')
FTAG, FEND = '<footer class="srf"', '</footer>'
CORE = re.compile(
    r'<script src="\.\./js/sr-(command|lang-hint|sound|print-guard|consent)\.js[^"]*"[^>]*></script>')


def core_line_end(h):
    cores = list(CORE.finditer(h))
    if not cores:
        return None
    last_end = h.find('</script>', cores[-1].start()) + len('</script>')
    le = h.find('\n', last_end)
    return len(h) if le < 0 else le + 1


def render_ckb():
    model = json.load(open(MODEL, encoding='utf-8'))
    return SF.render(model, 'ckb', '../')


def main():
    check_only = '--check' in sys.argv
    h = open(PAGE, encoding='utf-8', newline='').read()
    footer = render_ckb()
    n_srf = h.count('id="srf-footer"')

    if n_srf == 1 and footer in h:
        # idempotent: موجود — يكفي أن يطابق التصيير الحرفي وأنه في الموضع المرجعي
        cle = core_line_end(h)
        pos_ok = cle is not None and h[:cle].count('id="srf-footer"') == 0 \
            and h[cle:h.find(FEND, cle) + len(FEND) + 1].strip('\n') == footer
        print('CHECK OK — الفوتر موجود مطابقاً للتصيير، الموضع المرجعي:', pos_ok)
        sys.exit(0)
    if check_only:
        print('CHECK FAIL — لا فوتر سوراني مطابق (عدد srf=%d)' % n_srf)
        sys.exit(1)
    if n_srf:
        raise SystemExit('فوتر موجود غير مطابق للتصيير — تدخل يدوي')

    cle = core_line_end(h)
    if cle is None:
        raise SystemExit('لا سكربتات أساسية في ckb — غير متوقع')
    # الضمانات قبل الكتابة
    before_text = re.sub(r'<[^>]+>', ' ', h)
    h2 = h[:cle] + footer + '\n' + h[cle:]
    # (أ) الإدراج صرف: حذف الكتلة المدرجة يعيد الأصل بايت-ببايت
    assert h2.replace(footer + '\n', '', 1) == h, 'الإدراج ليس صرفاً'
    # (ب) لا فوتر آخر (بلوكات footer عامة قد توجد — نعدّ الوسوم)
    assert h2.count(FTAG) - h.count(FTAG) == 1, 'فوتر واحد مدرج'
    # (ج) توازن الوسوم: validate سيُشغَّل لاحقاً — فحص سريع هنا
    assert h2.count('<footer') == h.count('<footer') + 1
    assert h2.count('</footer>') == h.count('</footer>') + 1

    open(PAGE, 'w', encoding='utf-8', newline='').write(h2)
    print('أُدرج فوتر ckb (%d بايت) بعد آخر سكربت أساسي' % len(footer))
    print('مطابقة التصيير الحرفي:', footer in open(PAGE, encoding='utf-8', newline='').read())
    print('idempotency: جولة --check التالية تثبت')


if __name__ == '__main__':
    main()
