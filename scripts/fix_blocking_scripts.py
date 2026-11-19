#!/usr/bin/env python3
"""
fix_blocking_scripts.py
يضيف defer إلى سكريبتات JS التي تُوقف تحميل الصفحة (blocking scripts)
في جميع صفحات اللغات + الصفحة الرئيسية
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# الملفات التي يجب إضافة defer إليها (بدون defer حالياً)
BLOCKING_SCRIPTS = [
    "sr-lead-dispatcher.js",
    "sr-live-feed.js",
    "enterprise-suite.min.js",
    "sr-software-apps.js",
    "sr-studio-peek.js",
]

# جمع كل ملفات index.html في المشروع
HTML_FILES = []

# الصفحة الرئيسية
root_index = os.path.join(ROOT, "index.html")
if os.path.exists(root_index):
    HTML_FILES.append(root_index)

# مجلدات اللغات
LOCALES = [
    "ar","en","nl","de","fr","tr","sv","no","es","it",
    "ku","ckb","pl","pt","da","fi","cs","el","ro","hu",
    "bg","sk","hr","lt","sl","lv","et","ga","mt"
]
for loc in LOCALES:
    p = os.path.join(ROOT, loc, "index.html")
    if os.path.exists(p):
        HTML_FILES.append(p)

total_changes = 0

for html_path in HTML_FILES:
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    changes = 0

    for script_name in BLOCKING_SCRIPTS:
        # تطابق script tag يحمل هذا الملف بدون defer أو async
        pattern = r'(<script\b(?![^>]*\bdefer\b)(?![^>]*\basync\b)[^>]*\bsrc="[^"]*' + re.escape(script_name) + r'[^"]*"[^>]*)>'
        
        def add_defer(m):
            tag = m.group(1)
            # لا تضف defer إذا كانت موجودة
            if 'defer' not in tag:
                return tag + ' defer>'
            return m.group(0)
        
        new_content = re.sub(pattern, add_defer, content)
        if new_content != content:
            changes += 1
            content = new_content

    if content != original:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)
        rel = os.path.relpath(html_path, ROOT)
        print(f"  ✅ {rel} — {changes} سكريبت معدَّل")
        total_changes += changes
    else:
        rel = os.path.relpath(html_path, ROOT)
        print(f"  — {rel} (لا تغيير)")

print(f"\n✅ الإجمالي: {total_changes} تعديل على {len(HTML_FILES)} ملف HTML")
