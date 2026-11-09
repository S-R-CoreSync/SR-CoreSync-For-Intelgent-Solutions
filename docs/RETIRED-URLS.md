<div dir="rtl">

# إزالة الروابط المسحوبة من فهرس Google (Retired URLs)

**آخر تحديث:** الاثنين، 09 نوفمبر 2026 — المرحلة 171

---

## 1) الروابط المسحوبة (تحتاج إزالة في GSC)

| الرابط | الحالة الآن | ملاحظة |
|---|---|---|
| `https://sr-coresync.com/_trash_160/2026-11-08_1704/index.html` | **404** + `noindex` | كانت نسخة مكررة من الصفحة الرئيسية |
| `https://sr-coresync.com/_trash_160/2026-11-08_1704/index_1.html` | **404** + `noindex` | نسخة ثانية من نفس الصفحة |

المجلد كاملًا: `https://sr-coresync.com/_trash_160/` → 404.

**لماذا 404 كافٍ تقنيًا:** خادم GitHub Pages يعيد صفحة `404.html` المخصصة، وهي تحمل
`<meta name="robots" content="noindex, follow">`، أي أن Google يستقبل إشارتَي حذف
معًا (رمز 404 + منع الفهرسة). الحذف النهائي يحدث تلقائيًا خلال أيام إلى أسابيع.
الخطوات التالية تُسرّع العملية فقط.

---

## 2) نتيجة فحص كل الروابط القديمة المرشحة (33 رابطًا)

فُحصت كل الصفحات التطويرية المستثناة (`EXCLUDED_DEV_PAGES`) وكل صفحات HTML المحذوفة من تاريخ Git،
محليًا وعلى الموقع الحيّ، بتاريخ 09 نوفمبر 2026.

### أ) صفحات مستثناة من النشر — كلها 404 ✅

`debug_header.html`، `preview-booking-modal.html`، `preview-checkout.html`،
`preview-client-portal.html`، `preview-comparison.html`، `preview-header.html`،
`preview-invoice-quote.html`، `preview-license-manager.html`، `preview-software-modal.html`،
`preview-welcome-email.html`، `preview_emblem_tuning.html`، `preview_new_official_embel.html`،
`preview_roi_modal.html`.

> 13 رابطًا → **404** جميعها. لا حاجة لأي إجراء إضافي.

### ب) صفحات محذوفة من تاريخ Git — 404 ✅ (باستثناء المشروعة أدناه)

`card_print_preview.html`، `invoice_branded_preview.html`، `presets/index-option1-slider.html`،
`presets/index-option2-split.html`، `preview_mobile_fabs.html`، `preview_mobile_fabs_ready.html`،
`preview_modal_en.html`، `preview_modal_en_ready.html`، `preview_modal_nl.html`،
`preview_modal_nl_ready.html`، `preview_modal_switcher.html`، `preview-work-cleaning.html`،
`test_mobile.html`، `test_rect.html`، `test_switch.html`.

> 15 رابطًا → **404** جميعها.

### ج) صفحات حيّة مشروعة — لا تُحذف ⚠️

| الرابط | الحالة | السبب |
|---|---|---|
| `3d-product-configurator.html` | 200 | مرتبطة من `index.html` و`dynamic-qr-studio.html` — صفحة منتج حقيقية |
| `multi-cbdc-bridge.html` | 200 | مُدرجة في `sitemap.xml` وضمن مجموعة صفحات الحلول السيادية |
| `sovereign-arbitration-hub.html` | 200 | مُدرجة في `sitemap.xml` وضمن مجموعة صفحات الحلول السيادية |
| `zkp-confidential-enclave.html` | 200 | مُدرجة في `sitemap.xml` وضمن مجموعة صفحات الحلول السيادية |

هذه الصفحات ظهرت في تاريخ Git كـ«محذوفة» لأنها حُذفت ثم أُعيدت لاحقًا؛ وهي الآن **متعقَّبة في Git
ومنشورة ومربوطة داخليًا**، لذا تُستثنى من أي قائمة إزالة.

**الخلاصة:** 30 رابطًا مسحوبًا مؤكد بـ404، و4 صفحات حيّة مشروعة. لا توجد روابط مكشوفة تحتاج معالجة.

---

## 3) الإزالة عبر Google Search Console (خطوتان)

> **الحالة:** ✅ نُفِّذ طلب الإزالة المؤقتة للبادئة `https://sr-coresync.com/_trash_160/`
> بتاريخ **09 نوفمبر 2026**، وأُعيد التحقق الحيّ بعده: الرابطان يعيدان **404**.
> يبقى الطلب فعّالًا نحو 6 أشهر، ويكفي لأن الصفحات تعيد 404 نهائيًا. الخطوتان أدناه للمرجع فقط.

### الخيار (أ) — أداة «إزالة المحتوى القديم» (الأسرع)

1. افتح: <https://search.google.com/search-console/remove-outdated-content>
2. سجّل الدخول بالحساب المالك للعقار (Property).
3. الصق الرابط الأول ثم اضغط **طلب الإزالة**.
4. كرّر للرابط الثاني.

> هذه الأداة مخصصة أصلًا للصفحات التي لم تعد موجودة (404)، ولا تحتاج أي تعديل على الموقع.

### الخيار (ب) — «الإزالة المؤقتة» بنطاق بادئة (Prefix)

1. افتح: <https://search.google.com/search-console/removals>
2. اختر العقار `sr-coresync.com`.
3. **طلب جديد** → تبويب **إزالة مؤقتة**.
4. أدخل: `https://sr-coresync.com/_trash_160/`
5. فعّل خيار **إزالة كل الروابط التي تبدأ بهذه البادئة** ثم أرسل.

> الإزالة المؤقتة تستمر نحو 6 أشهر، وهي كافية تمامًا لأن الصفحات تعيد 404 نهائيًا.

---

## 4) التحقق بعد التنفيذ

```powershell
curl.exe -4 -sS -o NUL -w "%{http_code}`n" "https://sr-coresync.com/_trash_160/2026-11-08_1704/index.html"
curl.exe -4 -sS -o NUL -w "%{http_code}`n" "https://sr-coresync.com/_trash_160/2026-11-08_1704/index_1.html"
```

المتوقع: `404` لكليهما.

للتحقق من انتهاء الإزالة في GSC: صفحة **Removals** تعرض الحالة
(قيد الانتظار → تمت الإزالة)، وقد يستغرق ظهورها من ساعات إلى 3 أيام.

---

## 5) ضمان عدم التكرار

- `scripts/publish_set.py` يستثني **أي مجلد يبدأ بشرطة سفلية** (`_trash_*`، `_css_archive_*`، `_site`).
- `.gitignore` يمنع إعادة إضافة هذه المجلدات إلى Git.
- `deploy-pages.yml` يشغّل `validate_publish_set.py` و`check_site_links.py` قبل كل رفع.
- `robots.txt` يعلن `Disallow` لمسارات الأرشيف القديمة.

</div>
