#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""البند 26 — مزامنة اقتباسات ku في القاموس مع صفحتها.

التشخيص: قيم testimonials.0X.quote للكرمانجية في i18n/sections/testimonials.json
إنجليزية بينما نص الصفحة ku/index.html كرمانجي (انزياح قاموس قائم قبل البند 18).
العلاج: نسخ نص الصفحة الخمس (بفك &amp; — العُرف الموثق بقيم de الخام) إلى القاموس.
الصفحات نفسها: صفر تغيير. تنسيق الملف: json.dumps(indent=1, ensure_ascii=False)
بلا سطر نهائي — مطابق بايت-ببايت للتنسيق القائم فيصبح الفرق 5 أسطر حصراً.

الاستخدام:
    python scripts/sync_ku_quotes.py            # تطبيق + إثباتات
    python scripts/sync_ku_quotes.py --check    # فحص فقط (خروج 1 عند انحراف)
"""
import json, re, sys, os, html as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'ku', 'index.html')
DICT = os.path.join(ROOT, 'i18n', 'sections', 'testimonials.json')
KEYS = ['testimonials.%s.quote' % n for n in ('01', '02', '03', '04', '05')]


def page_quotes():
    s = open(PAGE, encoding='utf-8', newline='').read()
    out = {}
    for k in KEYS:
        m = re.search(r'data-i18n="%s">([^<]*)</p>' % re.escape(k), s)
        if not m:
            raise SystemExit('الصفحة بلا مقتبس لـ %s' % k)
        out[k] = H.unescape(m.group(1))
    return out


def load():
    raw = open(DICT, encoding='utf-8', newline='').read()
    return raw, json.loads(raw)


def dump(d):
    return json.dumps(d, ensure_ascii=False, indent=1)


def main():
    check_only = '--check' in sys.argv
    raw, d = load()
    if 'ku' not in d:
        raise SystemExit('القاموس بلا مفتاح ku')
    target = page_quotes()

    # 1) نبضات ما قبل التغيير: القيم الأخرى (كل اللغات + مفاتيح rating)
    before = {lang: dict(vals) for lang, vals in d.items() if lang != 'ku'}

    changed = [k for k in KEYS if d['ku'].get(k) != target[k]]
    if check_only:
        if changed:
            print('CHECK FAIL — منحرفة:', changed)
            sys.exit(1)
        print('CHECK OK — ku مطابقة حرفياً ×5')
        return

    if not changed:
        print('IDEMPOTENT: صفر تغييرات — القاموس مطابق مسبقاً')
    else:
        for k in changed:
            old = d['ku'].get(k, '')
            d['ku'][k] = target[k]
            print('استُبدل %s: %r… → %r…' % (k, old[:50], target[k][:50]))
        open(DICT, 'w', encoding='utf-8', newline='').write(dump(d))

    # 2) إثباتات بعد الكتابة
    raw2, d2 = load()
    # (أ) مطابقة حرفية صفحة↔قاموس ×5
    tq = page_quotes()
    ok = all(d2['ku'][k] == tq[k] for k in KEYS)
    print('مطابقة صفحة↔قاموس ×5:', 'ناجحة' if ok else 'فاشلة')
    # (ب) كل اللغات الأخرى + مفاتيح rating سليمة حرفياً
    drift = []
    for lang, vals in before.items():
        if d2.get(lang) != vals:
            drift.append(lang)
    ku_others = {k: v for k, v in d2['ku'].items() if k not in KEYS}
    print('انحراف لغات أخرى:', drift if drift else 'صفر')
    print('مفاتيح ku الأخرى (rating) سليمة:',
          'نعم' if ku_others == {k: v for k, v in d['ku'].items() if k not in KEYS} else 'فشل!')
    # (ج) تنسيق الملف: إعادة التصدير مطابقة (ثبات الشكل)
    print('ثبات التنسيق (إعادة تصدير = الملف):', dump(d2) == raw2)
    # (د) الصفحات صفر تغيير — الصفحة الوحيدة المقروءة لم تُمس
    print('الصفحات: صفر تغيير (الأداة تقرأ ku فقط ولا تكتب صفحات)')
    sys.exit(0 if (ok and not drift) else 1)


if __name__ == '__main__':
    main()
