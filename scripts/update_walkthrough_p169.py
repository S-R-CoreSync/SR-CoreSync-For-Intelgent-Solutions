with open('walkthrough.md', 'r', encoding='utf-8') as f:
    text = f.read()

target = '<div dir="rtl">\n\n## 🌟 المرحلة 168'
replacement = '''<div dir="rtl">

## 🌟 المرحلة 169: إضافة الميزانية التقديرية الفورية (EUR/SAR) والعائد الاستثماري (ROI) لبطاقة تحليل الأفكار وتصدير الـ PDF (100% Completed)
- **التاريخ:** الأحد، 08 نوفمبر 2026 — الساعة 04:13 صباحاً (+01:00).
- **المنجزات المنفذة والمحسومة بنسبة 100%:**
  1. **إضافة الميزانية التقديرية الفورية (EUR / SAR):**
     - تم تحديث دالة `openAiEstimatorModal` في `js/sr-master-shell.js` لتوليد نطاق ميزانية تقديرية فوري باليورو والريال السعودي بحسب تصنيف المشروع المكتشف بالذكاء الاصطناعي.
     - إضافة بطاقة مذهبة بارزة `#srEstBudget` داخل شبكة مقاييس البطاقة.
  2. **إضافة العائد الاستثماري المتوقع (ROI %):**
     - إضافة بطاقة `#srEstRoi` ذات مؤشرات نمو زمردية توضح معدل توفير التكاليف ونمو المبيعات المحسوب بدقة.
  3. **تحديث وثيقة التصدير التنفيذي للـ PDF:**
     - إدراج بنود الميزانية والـ ROI تلقائياً في جدول المصفوفة المعمارية المطبوعة رسمياً عبر `exportAiEstimatePdf()`.
  4. **الفحص والجودة والاعتماد:**
     - اجتياز `node scripts/validate.js` و `node scripts/check_inline_scripts.mjs` و `node --check` بنسبة 100%، وتحديث لقطات المعاينة الحية.

---

## 🌟 المرحلة 168'''

new_text = text.replace(target, replacement, 1)
with open('walkthrough_tmp.md', 'w', encoding='utf-8') as f:
    f.write(new_text)
print("SUCCESS_REPLACE")
