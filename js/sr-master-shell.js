/**
 * S&R CoreSync For Intelligent Solutions - Sovereign Master Shell Engine (MSE)
 * Governs Global Navigation, Universal Drawer (31+ Studios), Typography Resizer & Layout Inheritance
 * Version: 2026.11-MasterSovereign
 */

(function () {
    'use strict';

    // 1. Directory of all Official S&R CoreSync Platforms, Studios & Portals
    const SR_PLATFORM_REGISTRY = [
        { id: 'home', title: 'الرئيسية والمنظومة الأم', num: '01 /', url: './index.html', tag: 'الرئيسية 🏠' },
        { id: 'demo', title: 'النظام التجريبي السحابي', num: '02 /', url: './demo.html', tag: 'تجريبي ⚡' },
        { id: 'software', title: 'سوق البرمجيات والأنظمة', num: '03 /', url: './software.html', tag: 'سوق 💻' },
        { id: 'api_docs', title: 'توثيق الـ API السيادي (OpenAPI 3.1)', num: '04 /', url: './api-docs.html', tag: 'توثيق 📖' },
        { id: 'brand_studio', title: 'استوديو الهوية البصرية والمطابقة', num: '05 /', url: './brand-identity-studio.html', tag: 'هوية 🎨' },
        { id: 'web_showcase', title: 'معرض واجهات الويب والمتاجر الفاخرة', num: '06 /', url: './web-showcase-studio.html', tag: 'معرض 🌐' },
        { id: 'device_simulator', title: 'استوديو محاكاة الأجهزة 3D', num: '07 /', url: './device-simulator-studio.html', tag: 'محاكاة 📱' },
        { id: 'invoice_engine', title: 'محرك الفوترة الرقمية ZATCA', num: '08 /', url: './invoice-engine.html', tag: 'فوترة 🧾' },
        { id: 'smart_proposal', title: 'بوابة العروض والتعاقد الذكي المباشر', num: '09 /', url: './smart-proposal-portal.html', tag: 'عقود 🤝' },
        { id: 'crm_dashboard', title: 'لوحة CRM والتحليلات الحية', num: '10 /', url: './crm-dashboard.html', tag: 'تحليلات 📊' },
        { id: 'payment_gateway', title: 'بوابة المدفوعات الدولية الموحدة', num: '11 /', url: './payment-gateway.html', tag: 'دفع 💳' },
        { id: 'ecommerce_launchpad', title: 'استوديو توليد المتاجر الفورية', num: '12 /', url: './ecommerce-launchpad.html', tag: 'متاجر 🛍️' },
        { id: 'landing_builder', title: 'مولّد صفحات الهبوط فائقة التحويل', num: '13 /', url: './landing-page-builder.html', tag: 'هبوط 🚀' },
        { id: 'webhook_hub', title: 'مركز أتمتة الـ Webhooks والربط السحابي', num: '14 /', url: './webhook-integration-hub.html', tag: 'سحابي ⚡' },
        { id: 'security_center', title: 'مركز الأمان وشارات التوثيق', num: '15 /', url: './security-trust-center.html', tag: 'أمان 🛡️' },
        { id: 'social_ads', title: 'استوديو أصول التواصل 8K', num: '16 /', url: './social-ads-studio.html', tag: 'إعلانات 🎨' },
        { id: 'badge_3d', title: 'محرك الشارات والأيقونات 3D', num: '17 /', url: './icon-badge-3d-generator.html', tag: 'شارات 3D ✨' },
        { id: 'api_playground', title: 'بيئة اختبار واجهات البرمجة (Playground)', num: '18 /', url: './api-playground.html', tag: 'API 🌐' },
        { id: 'financial_charts', title: 'استوديو الرسوم البيانية المالية', num: '19 /', url: './financial-charts-studio.html', tag: 'مخططات 📈' },
        { id: 'ip_nda', title: 'محرك عقود الملكية الفكرية وNDA', num: '20 /', url: './ip-nda-smart-contract.html', tag: 'عقود 📜' },
        { id: 'executive_id', title: 'استوديو الهويات الرقمية التنفيذية 3D', num: '21 /', url: './executive-digital-id.html', tag: 'هويات 🪪' },
        { id: '3d_configurator', title: 'محرك تخصيص المنتجات الفاخرة 3D', num: '22 /', url: './3d-product-configurator.html', tag: 'منتجات 3D 💎' },
        { id: 'dynamic_qr', title: 'استوديو أكواد QR الديناميكية المشفرة', num: '23 /', url: './dynamic-qr-studio.html', tag: 'QR ذكي 📲' }
    ];

    // 2. Universal Typography Scale Controller (A+ / A- Persistent Engine)
    const SR_FONT_SCALE_KEY = 'sr_unified_font_scale';
    let currentScalePercent = parseInt(localStorage.getItem(SR_FONT_SCALE_KEY), 10) || 100;

    function applyFontScale(percent) {
        currentScalePercent = Math.max(85, Math.min(130, percent));
        localStorage.setItem(SR_FONT_SCALE_KEY, currentScalePercent);
        document.documentElement.style.setProperty('--sr-font-scale', `${currentScalePercent}%`);
        
        // Update all indicators on page
        document.querySelectorAll('.sr-resizer-val, [data-sr-resizer-val]').forEach(el => {
            el.textContent = `${currentScalePercent}%`;
        });
    }

    window.srAdjustFontSize = function (delta) {
        applyFontScale(currentScalePercent + (delta * 5));
    };

    window.srResetFontSize = function () {
        applyFontScale(100);
    };

    // Apply scale on boot
    applyFontScale(currentScalePercent);

    // 3. Universal Offcanvas Drawer Generator & Controller
    function createMasterDrawer() {
        if (document.getElementById('srMasterDrawer')) return;

        const currentPath = window.location.pathname.split('/').pop() || 'index.html';

        const backdrop = document.createElement('div');
        backdrop.id = 'srMasterDrawerBackdrop';
        backdrop.className = 'sr-master-drawer-backdrop';
        backdrop.onclick = closeMasterDrawer;

        const drawer = document.createElement('aside');
        drawer.id = 'srMasterDrawer';
        drawer.className = 'sr-master-drawer';
        drawer.setAttribute('aria-label', 'خريطة المنصة السيادية الموحدة');

        let itemsHtml = '';
        SR_PLATFORM_REGISTRY.forEach(item => {
            const isActive = currentPath === item.url.replace('./', '');
            itemsHtml += `
                <li class="sr-drawer-item">
                    <a href="${item.url}" class="${isActive ? 'active' : ''}">
                        <span>${item.title}</span>
                        <span class="sr-drawer-item-num">${item.num}</span>
                    </a>
                </li>
            `;
        });

        drawer.innerHTML = `
            <div class="sr-drawer-header">
                <div style="display:flex; align-items:center; gap:10px;">
                    <img src="./assets/sr-core-emblem.svg" alt="S&R Emblem" width="30" height="30">
                    <span style="font-weight:900; color:var(--sr-gold-light); font-size:0.95rem;">خريطة المنظومة الموحدة</span>
                </div>
                <button type="button" onclick="srCloseMasterDrawer()" style="background:none; border:none; color:#cbd5e1; font-size:1.4rem; cursor:pointer; line-height:1;">✕</button>
            </div>
            <div style="padding: 12px 24px; border-bottom: 1px solid var(--sr-border-subtle); display:flex; align-items:center; justify-content:space-between;">
                <span style="font-size:0.78rem; color:var(--sr-text-muted);">حجم الخط والقراءة:</span>
                <div class="sr-text-resizer-widget">
                    <button type="button" class="sr-resizer-btn" onclick="srAdjustFontSize(-1)" title="تصغير الخط (A-)">A-</button>
                    <button type="button" class="sr-resizer-indicator" onclick="srResetFontSize()" title="إعادة الضبط (100%)">
                        <span class="sr-resizer-val">${currentScalePercent}%</span>
                    </button>
                    <button type="button" class="sr-resizer-btn" onclick="srAdjustFontSize(1)" title="تكبير الخط (A+)">A+</button>
                </div>
            </div>
            <div class="sr-drawer-body">
                <ul class="sr-drawer-list">
                    ${itemsHtml}
                </ul>
            </div>
            <div style="padding:16px 24px; border-top:1px solid var(--sr-border-subtle); font-size:0.75rem; color:var(--sr-text-muted); text-align:center;">
                S&R CoreSync For Intelligent Solutions • 2026
            </div>
        `;

        document.body.appendChild(backdrop);
        document.body.appendChild(drawer);
    }

    window.srOpenMasterDrawer = function () {
        createMasterDrawer();
        document.getElementById('srMasterDrawer').classList.add('open');
        document.getElementById('srMasterDrawerBackdrop').classList.add('open');
        document.body.style.overflow = 'hidden';
    };

    window.srCloseMasterDrawer = function () {
        const drawer = document.getElementById('srMasterDrawer');
        const backdrop = document.getElementById('srMasterDrawerBackdrop');
        if (drawer) drawer.classList.remove('open');
        if (backdrop) backdrop.classList.remove('open');
        document.body.style.overflow = '';
    };

    function closeMasterDrawer() {
        window.srCloseMasterDrawer();
    }

    // Escape Key Listener for Accessibility
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            window.srCloseMasterDrawer();
        }
    });

    // 4. Auto-Enhance Existing Navbars Across Studio Pages
    function autoEnhanceNavbar() {
        const nav = document.querySelector('.navbar, .nav, .sr-master-navbar');
        if (!nav) return;

        // Ensure master class
        nav.classList.add('sr-master-navbar');

        // Check if hamburger button exists; if not, append one
        let toggleBtn = nav.querySelector('.sr-master-menu-toggle, [data-sr-call="toggleMobileMenu"]');
        if (!toggleBtn) {
            const actionsBox = document.createElement('div');
            actionsBox.className = 'sr-master-nav-actions';
            actionsBox.innerHTML = `
                <div class="sr-text-resizer-widget" style="display:none; @media(min-width:768px){display:inline-flex;}">
                    <button type="button" class="sr-resizer-btn" onclick="srAdjustFontSize(-1)" title="تصغير الخط">A-</button>
                    <button type="button" class="sr-resizer-indicator" onclick="srResetFontSize()" title="إعادة ضبط">
                        <span class="sr-resizer-val">${currentScalePercent}%</span>
                    </button>
                    <button type="button" class="sr-resizer-btn" onclick="srAdjustFontSize(1)" title="تكبير الخط">A+</button>
                </div>
                <button type="button" class="sr-master-menu-toggle" onclick="srOpenMasterDrawer()">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
                    <span>القائمة الشاملة</span>
                </button>
            `;
            nav.appendChild(actionsBox);
        }
    }

    // 5. Universal AI Idea Analyzer & Dispatcher
    // 5. Universal AI Idea Analyzer & Dispatcher (S&R CoreSync User Specification)
    window.setPrompt = function (text) {
        const input = document.getElementById('userIdeaInput') || document.getElementById('heroAiIdeaInput');
        const input = document.getElementById('userIdeaInput');
        if (input) {
            input.value = text;
            input.focus();
            input.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    };

    window.analyzeIdea = function () {
        const input = document.getElementById('userIdeaInput') || document.getElementById('heroAiIdeaInput');
        const query = (input ? input.value : '').trim();

        if (!query) {
            if (input) {
                input.focus();
                input.style.boxShadow = '0 0 15px rgba(239, 68, 68, 0.8)';
                setTimeout(() => { input.style.boxShadow = ''; }, 1500);
            }
            alert('يرجى كتابة فكرة مشروعك أولاً ليقوم الذكاء الاصطناعي بتحليلها.');
        const input = document.getElementById('userIdeaInput');
        const idea = (input ? input.value : '').toLowerCase();
        
        if (!idea.trim()) {
            alert('الرجاء كتابة فكرة المشروع أولاً.');
            if (input) input.focus();
            return;
        }

        // Semantic Analysis & Routing Logic
        let recommendation = {
            category: 'منظومة برمجيات سحابية سيادية مخصصة',
            system: 'S&R CoreSync Enterprise Suite',
            description: 'تحليل الفكرة أظهر الحاجة إلى معمارية متقدمة وتكامل سحابي فوري وإدارة عمليات.',
            url: './demo.html',
            urlText: 'بدء المعاينة والتجربة الفورية ⚡',
            badge: 'حلول مؤسسية مخصصة'
        };

        const q = query.toLowerCase();

        if (q.includes('متجر') || q.includes('تجارة') || q.includes('بيع') || q.includes('منتجات') || q.includes('سلة') || q.includes('ecommerce')) {
            recommendation = {
                category: 'متاجر إلكترونية فاخرة وحلول التجارة الرقمية',
                system: 'S&R Automated E-Commerce Launchpad',
                description: 'بناء متجر إلكتروني فاخر فائق السرعة متوافق مع بوابات الدفع الدولية iDEAL و Stripe و Apple Pay مع الفوترة والربط السحابي.',
                url: './ecommerce-launchpad.html',
                urlText: 'فتح استوديو المتاجر الفورية 🛍️',
                badge: 'التجارة الإلكترونية'
            };
        } else if (q.includes('مبيعات') || q.includes('crm') || q.includes('عملاء') || q.includes('إدارة') || q.includes('زبائن')) {
            recommendation = {
                category: 'إدارة علاقات العملاء وتحليلات الأداء الحي',
                system: 'S&R Sovereign CRM & Live Analytics Engine',
                description: 'لوحة تحكم تنفيذية لمتابعة الصفقات، تدفقات المبيعات، ومؤشرات الأداء المالي والربط الفوري مع الفواتير.',
                url: './crm-dashboard.html',
                urlText: 'استعراض لوحة الـ CRM والبيانات 📊',
                badge: 'إدارة المبيعات والـ CRM'
            };
        } else if (q.includes('تعليم') || q.includes('منصة') || q.includes('أكاديمية') || q.includes('دورات') || q.includes('كورسات') || q.includes('تدريب')) {
            recommendation = {
                category: 'المنصات التعليمية والأنظمة التفاعلية LMS',
                system: 'S&R Sovereign Educational & Knowledge Platform',
                description: 'هندسة منصة تعليمية وبوابات اشتراكات ذكية مع فصول افتراضية وحماية المحتوى الرقمي والملكية الفكرية.',
                url: './software.html',
                urlText: 'استعراض سوق الأنظمة والبرمجيات 💻',
                badge: 'المنصات التعليمية LMS'
            };
        } else if (q.includes('دفع') || q.includes('بوابة') || q.includes('تحويل') || q.includes('فيزا') || q.includes('stripe') || q.includes('ideal')) {
            recommendation = {
                category: 'بوابات المدفوعات والحلول المالية FinTech',
                system: 'S&R Sovereign Unified Payment Gateway',
                description: 'تكامل بوابات الدفع الدولية متعددة العملات مع امتثال PSD2 الأوروبي وإيصالات الدفع المشفرة.',
                url: './payment-gateway.html',
                urlText: 'فتح بوابة المدفوعات الموحدة 💳',
                badge: 'المدفوعات الدولية FinTech'
            };
        } else if (q.includes('فاتورة') || q.includes('ضرائب') || q.includes('zatca') || q.includes('peppol') || q.includes('فوترة')) {
            recommendation = {
                category: 'الفوترة الإلكترونية والامتثال الضريبي',
                system: 'S&R Digital Invoice & Tax Compliance Engine',
                description: 'محرك الفوترة الرقمية المعتمد المتوافق مع هيئة الزكاة والضريبة والجمارك ZATCA والأنظمة الأوروبية Peppol.',
                url: './invoice-engine.html',
                urlText: 'تشغيل محرك الفوترة الرقمية 🧾',
                badge: 'الفوترة والامتثال ZATCA'
            };
        } else if (q.includes('هبوط') || q.includes('تسويق') || q.includes('إعلان') || q.includes('landing') || q.includes('صفحة')) {
            recommendation = {
                category: 'صفحات الهبوط والحملات التسويقية عالية التحويل',
                system: 'S&R High-Converting Landing Page Builder',
                description: 'تصميم وإطلاق صفحات هبوط متجاوبة مع حاسبة العائد الاستثماري ونموذج حجز فوري ومربوطة بـ WhatsApp.',
                url: './landing-page-builder.html',
                urlText: 'فتح مولّد صفحات الهبوط 🚀',
                badge: 'صفحات الهبوط والتحويل'
            };
        } else if (q.includes('عقد') || q.includes('اتفاقية') || q.includes('ملكية') || q.includes('توقيع') || q.includes('nda')) {
            recommendation = {
                category: 'العقود الذكية وحماية الملكية الفكرية والشيفرات',
                system: 'S&R IP & NDA Smart Contract Engine',
                description: 'صياغة اتفاقيات عدم الإفصاح وتراخيص السوفتوير مع التوقيع الإلكتروني وتوثيق بصمة SHA-256 المشفرة.',
                url: './ip-nda-smart-contract.html',
                urlText: 'فتح محرك عقود الملكية الفكرية 📜',
                badge: 'العقود والملكية الفكرية'
            };
        } else if (q.includes('شعار') || q.includes('هوية') || q.includes('براند') || q.includes('ألوان') || q.includes('تصميم')) {
            recommendation = {
                category: 'الهويات البصرية والأصول السيادية 3D',
                system: 'S&R Sovereign Brand Identity Studio',
                description: 'بناء وتخصيص الهوية البصرية المتكاملة للمؤسسات وتصدير حزم الأصول الرقمية بدقة 8K فائقة.',
                url: './brand-identity-studio.html',
                urlText: 'فتح استوديو الهوية البصرية 🎨',
                badge: 'الهوية البصرية والتصميم'
            };
        } else if (q.includes('qr') || q.includes('باركود') || q.includes('رمز')) {
            recommendation = {
                category: 'أكواد QR المشفرة والربط الديناميكي',
                system: 'S&R Dynamic QR Studio & Scanner',
                description: 'توليد وتخصيص وفحص أكواد QR للمواقع والمنتجات وفواتير ZATCA مع دمج الشعار والتحليل اللحظي.',
                url: './dynamic-qr-studio.html',
                urlText: 'فتح استوديو أكواد QR المشفرة 📲',
                badge: 'أكواد QR الذكية'
            };
        // منطق التحليل الذكي والتوجيه البسيط
        if (idea.includes('متجر') || idea.includes('بيع') || idea.includes('منتج')) {
            alert('تحليل الذكاء الاصطناعي: فكرتك تميل نحو التجارة الإلكترونية. جاري تحويلك إلى المتجر والخدمات المرتبطة...');
            const storeEl = document.getElementById('store-section') || document.getElementById('software-hub');
            if (storeEl) {
                storeEl.scrollIntoView({ behavior: 'smooth' });
                window.location.hash = 'store-section';
            } else {
                window.location.href = './index.html#store-section';
            }
        } else if (idea.includes('سعر') || idea.includes('تكلفة') || idea.includes('باقة')) {
            alert('تحليل الذكاء الاصطناعي: تم تصنيف مشروعك، جاري عرض خطط الأسعار المناسبة لك...');
            const pricingEl = document.getElementById('pricing-section') || document.getElementById('pricing');
            if (pricingEl) {
                pricingEl.scrollIntoView({ behavior: 'smooth' });
                window.location.hash = 'pricing-section';
            } else {
                window.location.href = './index.html#pricing-section';
            }
        } else {
            alert('تحليل الذكاء الاصطناعي: فكرة واعدة! جاري تحويلك إلى فرع القيادة والخدمات للاستشارة الشاملة...');
            const servicesEl = document.getElementById('services-section') || document.getElementById('services');
            if (servicesEl) {
                servicesEl.scrollIntoView({ behavior: 'smooth' });
                window.location.hash = 'services-section';
            } else {
                window.location.href = './index.html#services-section';
            }
        }

        // Render AI Analysis Modal
        let modal = document.getElementById('srAiAnalysisModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'srAiAnalysisModal';
            modal.className = 'sr-ai-modal-overlay';
            document.body.appendChild(modal);
        }

        const encodedWa = encodeURIComponent(`مرحباً S&R CoreSync، قمت بتحليل فكرة مشروعي عبر الذكاء الاصطناعي في المنصة:\n\n*الفكرة:* "${query}"\n*التصنيف المقترح:* ${recommendation.category}\n*النظام:* ${recommendation.system}\n\nأود مناقشة التنفيذ والبدء المباشر معكم.`);

        modal.innerHTML = `
            <div class="sr-ai-modal-content">
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:18px; border-bottom:1px solid var(--sr-border); padding-bottom:14px;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="font-size:1.6rem;">✨</span>
                        <div>
                            <h3 style="margin:0; font-size:1.25rem; color:var(--sr-gold-light);">نتيجة تحليل الفكرة بالذكاء الاصطناعي</h3>
                            <span style="font-size:0.76rem; color:var(--sr-text-muted);">S&R CoreSync Sovereign Intelligent Analyzer</span>
                        </div>
                    </div>
                    <button type="button" onclick="document.getElementById('srAiAnalysisModal').classList.remove('open')" style="background:none; border:none; color:#cbd5e1; font-size:1.5rem; cursor:pointer; line-height:1;">✕</button>
                </div>

                <div style="margin-bottom:16px;">
                    <span style="font-size:0.75rem; color:var(--sr-gold); font-weight:700;">فكرتك المسجلة:</span>
                    <p style="background:rgba(255,255,255,0.04); padding:10px 14px; border-radius:10px; font-weight:700; color:#fff; border:1px solid rgba(255,255,255,0.08); margin-top:4px;">"${query}"</p>
                </div>

                <div style="background:rgba(197,168,128,0.08); border:1px solid var(--sr-border); border-radius:14px; padding:18px; margin-bottom:22px;">
                    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
                        <span style="font-size:0.8rem; font-weight:800; color:var(--sr-emerald);">القطاع الموصى به:</span>
                        <span style="background:rgba(16,185,129,0.15); color:var(--sr-emerald); padding:3px 10px; border-radius:6px; font-size:0.72rem; font-weight:700;">${recommendation.badge}</span>
                    </div>
                    <h4 style="color:#ffffff; font-size:1.05rem; margin-bottom:6px;">${recommendation.system}</h4>
                    <p style="font-size:0.88rem; color:var(--sr-text-secondary); margin:0;">${recommendation.description}</p>
                </div>

                <div style="display:flex; gap:10px; flex-wrap:wrap;">
                    <a href="${recommendation.url}" class="sr-unified-btn-primary" style="flex:1; justify-content:center; text-decoration:none;">
                        ${recommendation.urlText}
                    </a>
                    <a href="https://wa.me/31687766555?text=${encodedWa}" target="_blank" class="sr-unified-btn-secondary" style="background:rgba(16,185,129,0.15); border-color:rgba(16,185,129,0.4); color:var(--sr-emerald); text-decoration:none;">
                        <span>محادثة المستشار عبر WhatsApp 💬</span>
                    </a>
                </div>
            </div>
        `;

        modal.classList.add('open');
    };

    // Close modal on escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const modal = document.getElementById('srAiAnalysisModal');
            if (modal) modal.classList.remove('open');
        }
    });

    // Boot on DOMContentLoaded or immediately if ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            createMasterDrawer();
            autoEnhanceNavbar();
        });
    } else {
        createMasterDrawer();
        autoEnhanceNavbar();
    }

})();

