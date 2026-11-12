# خطة ترحيل بوابة 101 إلى الهيكل المشترك (المهمة 108-ب)

**التاريخ:** الخميس، 12 نوفمبر 2026
**النطاق:** `autonomous-tax-audit.html` (المهمة 101) وحدها.
**الحالة:** مرحّلة بخطة مكتوبة، ولم تُنفَّذ في المرحلة 175 عن قصد — الأسباب أدناه.

---

## 1. لماذا 101 وحدها؟

| البوابة | الهيكل الحالي | العلاقة بجناح المهام |
|---|---|---|
| `smart-escrow-milestone.html` (107-2) | `header > .nav-container` + `.hero-banner` + `.kpi-grid` + `.panel-card` | مطابق تماماً، يحمّل `css/sovereign-mission-suite.css` |
| `sovereign-arbitration-hub.html` (104) | نفسه | مطابق تماماً |
| `sovereign-gold-rwa-treasury.html` (102) | نفس الهيكل والكلاسات، لكن التنسيق **مضمّن في الصفحة** | مطابق في الماركب، منفصل في التنسيق |
| `autonomous-cyber-range.html` (103) | نفس حالة 102 | مطابق في الماركب، منفصل في التنسيق |
| `autonomous-tax-audit.html` (101) | `.topbar` / `.shell` / `.hero` / `.metrics` / `.panel` / `.panel-heading` | **مفردات مختلفة بالكامل** |

لذلك: 102 و103 تحتاجان توحيد التنسيق فقط (وقد قياسه يمنع الدمج — البند 4)، أما 101 فتحتاج إعادة صياغة الماركب نفسه.

---

## 2. خريطة المفردات (Class Mapping)

| 101 اليوم | البديل في جناح المهام |
|---|---|
| `.topbar` + `.topbar-inner` + `.shell` | `header` + `.nav-container` |
| `.brand` (img + strong + small) | `.brand-section` + `.brand-logo` + `.brand-title` + `.brand-sub` |
| `.nav` + `.inv-link` | `.nav-links` + `.nav-link` |
| `.hero` + `.eyebrow` + `.hero p` | `.hero-banner` + `.badge-row` + `.pill-badge` + `.hero-title` + `.hero-desc` |
| `.metrics` + `.metric` + `.metric-label` + `.metric-value` | `.kpi-grid` + `.kpi-card` + `.kpi-label` + `.kpi-value` + `.kpi-foot` |
| `.workspace` + `.panel` | `.workspace-grid` + `.panel-card` |
| `.panel-heading` (+ `h2`/`p`) | `.panel-header` + `.panel-title` (+ `.sub-title`) |
| `.controls` + `.field` + `.field label` | `.form-grid` + `.form-field` |
| `.actions` | `.btn-row` + `.btn-action` / `.btn-secondary` |
| `.table-wrap` + جدول | `.data-table` داخل `.panel-card` |
| `.finding-list` / `.finding` / `.rules` / `.rule-card` | تبقى خاصة بالصفحة (لا مقابل في الجناح) |
| `.status` / `.empty` / `.disclaimer` | تبقى خاصة، مع إعادة تلوين من متغيّرات الجناح |

---

## 3. خطوات التنفيذ

1. **تثبيت المرجع البصري:** لقطة شاشة كاملة لـ 101 الحالية (Pixel) قبل أي تعديل، وحفظها كمرجع مقارنة.
2. **الماركب:** استبدال `<header>` و`<main>` الخارجي بالهيكل النمطي، مع نقل محتوى 101 كما هو داخل البطاقات الجديدة.
3. **التنسيق:** تحميل `css/sovereign-mission-suite.css` قبل تنسيق الصفحة الخاص، وقلّم `style` الداخلي إلى القواعد الخاصة فقط (`.finding*`, `.rules`, `.rule-card`, `.status`, `.empty`, `.disclaimer`).
4. **السكربت:** `js/autonomous-tax-audit.js` (المحرك) و`js/autonomous-tax-audit-advisor.js` (ربط جلسة المستشار) يبقيان كما هما؛ يجب التأكد من أن كل `id` يستعلم عنه المحرك ما زال موجوداً بعد إعادة الماركب.
5. **القياس:** `node scripts/validate.js`، `python scripts/check_site_links.py`، `python scripts/build_csp.py --check`، ثم مقارنة بصرية مع اللقطة المرجعية.
6. **النشر:** إدراج الصفحة في لقطة مقارنة قبل/بعد داخل `walkthrough.md`.

---

## 4. قرار موثّق: لا استبدال لتنسيقات 102 و103

قياس آلي (`scripts` مؤقت، مقارنة قاعدة بقاعدة مع `css/sovereign-mission-suite.css`):

| الصفحة | قواعد | مطابقة حرفياً للمشترك | مختلفة فعلياً | خاصة بالصفحة |
|---|---|---|---|---|
| `sovereign-gold-rwa-treasury.html` | 63 | 15 | **27** | 21 |
| `autonomous-cyber-range.html` | 51 | 18 | **23** | 10 |

الاختلاف ليس تنسيقاً شكلياً: `:root` في 102 يستخدم لوحة ألوان زمردية (`#040907`, `#081510`) لا الأوبسيديان، و`header` و`.nav-container` و`.nav-links` لها قيم مختلفة. استبدال التنسيق المضمّن بالملف المشترك كان **سيغيّر مظهر البوابتين فعلياً**، وهو ما لا يجوز تمريره تحت اسم «توحيد».

**البديل المقترح لاحقاً:** توحيد المتغيّرات (`:root`) أولاً في ملف مشترك واحد مع سمات (`theme-emerald` موجودة أصلاً في `body`)، ثم تقليم القواعد المكرّرة على ثلاث مراحل مع لقطة مقارنة لكل مرحلة.

---

## 5. معايير القبول للبند 108-ب

- [ ] `h1` واحد، و`0` معرّفات مكرّرة في 101.
- [ ] كل `id` يستعلم عنه `js/autonomous-tax-audit.js` موجود.
- [ ] `node scripts/validate.js` و`check_site_links.py` و`build_csp.py --check` خضراء.
- [ ] مقارنة بصرية موثّقة (لقطة قبل/بعد) بلا فقدان أي كتلة وظيفية (المطابقة الضريبية، الاستثناءات، القواعد، زر التصدير).
