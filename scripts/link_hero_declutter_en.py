#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""البند 22أ — ربط hero-declutter.css بـ en/index.html.

المشخّص (البند 19): en الصفحة الوحيدة الـ28 البقية بلا رابط hero-declutter.css
— قياس قمرة en الـ441px طبيعي بمجموعة أنماط مختلفة وليس نجاح التسوية.
الثابت البنيوي عبر الـ27 صفحة: سطر الرابط يسبق <style id="hv2-port"> مباشرة
(مثبت بالمسح الشامل). العلاج: إدراج السطر النظير في en بنفس الثابت.

الاستخدام:
    python scripts/link_hero_declutter_en.py            # تطبيق + إثباتات
    python scripts/link_hero_declutter_en.py --check    # فحص فقط
"""
import sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'en', 'index.html')
LINK = '<link rel="stylesheet" href="../css/hero-declutter.css?v=20261118-cockpit">'
MARK = '<style id="hv2-port">'


def main():
    check_only = '--check' in sys.argv
    s = open(PAGE, encoding='utf-8', newline='').read()
    already = s.count(LINK)
    if already == 1 and (LINK + '\n' + MARK) in s:
        print('CHECK OK — الرابط موجود في الموضع النظير (قبل hv2-port مباشرة)')
        return
    if check_only:
        print('CHECK FAIL — الرابط غائب أو بموضع خاطئ (عدد=%d)' % already)
        sys.exit(1)
    if already:
        raise SystemExit('الرابط موجود %d مرة بموضع خاطئ — تدخل يدوي' % already)
    pairs = s.count(MARK)
    if pairs != 1:
        raise SystemExit('hv2-port غير فريد (%d) — تدخل يدوي' % pairs)
    # الثابت: الرابط يسبق hv2-port مباشرة (نمط الـ27 الصفحة، بلا مسافات بادئة)
    s2 = s.replace(MARK, LINK + '\n' + MARK, 1)
    open(PAGE, 'w', encoding='utf-8', newline='').write(s2)
    # إثباتات
    s3 = open(PAGE, encoding='utf-8', newline='').read()
    print('عدد الروابط في en:', s3.count('hero-declutter.css'), '(المطلوب 1)')
    print('الموضع: يسبق hv2-port مباشرة:', (LINK + '\n' + MARK) in s3)
    print('صفر تغيير آخر:', s3.replace(LINK + '\n' + MARK, MARK, 1) == s)
    print('idempotency:', 'نعم' if s3.count(LINK) == 1 else 'فشل')
    sys.exit(0)


if __name__ == '__main__':
    main()
