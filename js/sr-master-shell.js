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

    // 5. Universal AI Idea Analyzer, Animated Placeholder & Custom Route Card (S&R CoreSync Specification)
    function setPrompt(text) {
        const ideaInput = document.getElementById('userIdeaInput');
        if (ideaInput) {
            ideaInput.value = text;
            ideaInput.focus();
        }
    }

    // 5.1 Animated Typing Placeholder Engine
    function initAnimatedPlaceholder() {
        const input = document.getElementById('userIdeaInput');
        if (!input) return;

        const prompts = [
            'اكتب فكرة مشروعك هنا (مثلاً: أريد بناء متجر إلكتروني ذكي)...',
            'مثلاً: منصة تعليمية ذكية مع بوابات دفع واشتراكات...',
            'مثلاً: نظام سحابي لإدارة المبيعات والعملاء CRM...',
            'مثلاً: متجر إلكتروني فاخر متعدد العملات والشحن الفوري...',
            'مثلاً: نظام فوترة إلكترونية معتمد لـ ZATCA و Peppol...',
            'مثلاً: استوديو هويات بصرية وعقود حماية ملكية فكرية...'
        ];

        let promptIndex = 0;
        let charIndex = 0;
        let isDeleting = false;
        let isFocused = false;
        let typingTimeout = null;

        input.addEventListener('focus', () => { isFocused = true; });
        input.addEventListener('blur', () => {
            isFocused = false;
            if (!input.value.trim() && !typingTimeout) {
                typeLoop();
            }
        });
        input.addEventListener('input', () => {
            if (input.value.trim().length > 0) {
                isFocused = true;
            }
        });

        function typeLoop() {
            if (isFocused || input.value.trim().length > 0) {
                typingTimeout = setTimeout(typeLoop, 1000);
                return;
            }

            const currentPrompt = prompts[promptIndex];
            if (isDeleting) {
                charIndex--;
                input.setAttribute('placeholder', currentPrompt.substring(0, charIndex));
                if (charIndex <= 0) {
                    isDeleting = false;
                    promptIndex = (promptIndex + 1) % prompts.length;
                    typingTimeout = setTimeout(typeLoop, 500);
                    return;
                }
                typingTimeout = setTimeout(typeLoop, 25);
            } else {
                charIndex++;
                input.setAttribute('placeholder', currentPrompt.substring(0, charIndex));
                if (charIndex >= currentPrompt.length) {
                    isDeleting = true;
                    typingTimeout = setTimeout(typeLoop, 3000); // 3 ثوانٍ كما طلب المستخدم
                    return;
                }
                typingTimeout = setTimeout(typeLoop, 45);
            }
        }

        typeLoop();
    }

    // 5.2 Custom Glassmorphism Route Card Engine
    let routeCountdownInterval = null;
    let routeAutoRedirectTimeout = null;

    function closeRouteCard() {
        if (routeCountdownInterval) clearInterval(routeCountdownInterval);
        if (routeAutoRedirectTimeout) clearTimeout(routeAutoRedirectTimeout);
        const card = document.getElementById('srCustomRouteOverlay');
        if (card) {
            card.classList.remove('active');
            setTimeout(() => { card.style.display = 'none'; }, 300);
        }
    }

    function showCustomRouteCard(config) {
        closeRouteCard();

        let overlay = document.getElementById('srCustomRouteOverlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'srCustomRouteOverlay';
            overlay.style.cssText = `
                position: fixed; inset: 0; z-index: 999999;
                display: flex; align-items: center; justify-content: center;
                background: rgba(1, 9, 7, 0.78); backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px); opacity: 0;
                transition: opacity 0.3s ease; direction: rtl; text-align: right;
                padding: 16px; font-family: 'Alexandria', 'Plus Jakarta Sans', system-ui, sans-serif;
            `;
            document.body.appendChild(overlay);
        }

        let secondsLeft = 3;
        overlay.innerHTML = `
            <div style="
                background: linear-gradient(145deg, rgba(10, 24, 19, 0.98), rgba(2, 11, 8, 0.98));
                border: 1px solid rgba(197, 168, 128, 0.35);
                border-radius: 18px; max-width: 520px; width: 100%;
                padding: 26px; box-shadow: 0 25px 60px rgba(0, 0, 0, 0.65), 0 0 40px rgba(197, 168, 128, 0.15);
                position: relative; overflow: hidden;
            ">
                <div style="position: absolute; top: 0; right: 0; left: 0; height: 3px; background: rgba(255, 255, 255, 0.1);">
                    <div id="srRouteProgressBar" style="width: 100%; height: 100%; background: linear-gradient(90deg, #10b981, #d4af37); transition: width 3s linear;"></div>
                </div>

                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 14px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 2rem;">${config.icon}</span>
                        <div>
                            <span style="font-size: 0.75rem; color: #10b981; font-weight: 800; background: rgba(16, 185, 129, 0.15); padding: 3px 10px; border-radius: 20px;">${config.badge}</span>
                            <h3 style="margin: 4px 0 0; font-size: 1.18rem; color: #f8fafc; font-weight: 800;">${config.title}</h3>
                        </div>
                    </div>
                    <button type="button" onclick="window.closeRouteCard()" style="background: none; border: none; color: #94a3b8; font-size: 1.4rem; cursor: pointer; line-height: 1; padding: 4px;">✕</button>
                </div>

                <p style="font-size: 0.94rem; color: #cbd5e1; line-height: 1.7; margin: 0 0 20px; background: rgba(255, 255, 255, 0.03); padding: 12px 16px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.06);">
                    ${config.description}
                </p>

                <div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap;">
                    <div style="font-size: 0.84rem; color: #d4af37; font-weight: 700; display: flex; align-items: center; gap: 6px;">
                        <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #10b981; animation: srPulseDot 1.5s infinite;"></span>
                        جاري التوجيه التلقائي خلال <span id="srRouteTimer" style="font-weight: 900; font-size: 1rem; color: #10b981;">${secondsLeft}</span> ثوانٍ...
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button type="button" onclick="window.closeRouteCard()" style="padding: 10px 18px; background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); color: #e2e8f0; border-radius: 8px; cursor: pointer; font-size: 0.88rem; font-weight: 700;">تعديل الفكرة</button>
                        <button type="button" id="srRouteConfirmBtn" style="padding: 10px 22px; background: linear-gradient(135deg, #d4af37, #c5a880); border: none; color: #020b08; border-radius: 8px; cursor: pointer; font-size: 0.88rem; font-weight: 900; display: flex; align-items: center; gap: 6px;">انتقال فوري ⚡</button>
                    </div>
                </div>
            </div>
        `;

        overlay.style.display = 'flex';
        requestAnimationFrame(() => {
            overlay.style.opacity = '1';
            const bar = document.getElementById('srRouteProgressBar');
            if (bar) bar.style.width = '0%';
        });

        const executeRedirect = () => {
            closeRouteCard();
            navigateToSection(config.targetId, config.fallbackUrl);
        };

        const confirmBtn = document.getElementById('srRouteConfirmBtn');
        if (confirmBtn) {
            confirmBtn.onclick = executeRedirect;
        }

        routeCountdownInterval = setInterval(() => {
            secondsLeft--;
            const timerEl = document.getElementById('srRouteTimer');
            if (timerEl) timerEl.textContent = secondsLeft;
            if (secondsLeft <= 0) {
                clearInterval(routeCountdownInterval);
            }
        }, 1000);

        routeAutoRedirectTimeout = setTimeout(executeRedirect, 3000);
    }

    function navigateToSection(targetId, fallbackUrl) {
        const el = document.getElementById(targetId) ||
                   (targetId === 'store-section' ? document.getElementById('software-hub') :
                   (targetId === 'pricing-section' ? document.getElementById('pricing') :
                   document.getElementById('services')));

        if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            window.location.hash = targetId;

            // Highlight pulse on target
            el.style.transition = 'outline 0.4s ease, box-shadow 0.4s ease';
            el.style.outline = '2px solid rgba(212, 175, 55, 0.85)';
            el.style.boxShadow = '0 0 35px rgba(212, 175, 55, 0.35)';
            setTimeout(() => {
                el.style.outline = '';
                el.style.boxShadow = '';
            }, 3500);
        } else {
            window.location.href = fallbackUrl;
        }
    }

    function analyzeIdea() {
        const ideaInput = document.getElementById('userIdeaInput');
        const idea = (ideaInput ? ideaInput.value : '').toLowerCase();

        if (!idea.trim()) {
            if (ideaInput) {
                ideaInput.focus();
                ideaInput.style.transition = 'all 0.3s ease';
                ideaInput.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.45)';
                ideaInput.style.borderColor = '#ef4444';
                setTimeout(() => {
                    ideaInput.style.boxShadow = '';
                    ideaInput.style.borderColor = '';
                }, 2000);
            }
            alert('الرجاء كتابة فكرة المشروع أولاً.');
            return;
        }

        let targetId = 'services-section';
        let fallbackUrl = './index.html#services-section';
        let routeTitle = 'فرع القيادة والخدمات المؤسسية الشاملة';
        let routeDesc = 'تحليل الذكاء الاصطناعي: فكرة واعدة واستراتيجية! جاري توجيهك إلى فرع القيادة والخدمات للاستشارة الشاملة وحلول التحول الرقمي.';
        let routeBadge = 'الاستشارات الشاملة';
        let routeIcon = '🏛️';

        if (idea.includes('متجر') || idea.includes('بيع') || idea.includes('منتج')) {
            targetId = 'store-section';
            fallbackUrl = './index.html#store-section';
            routeTitle = 'استوديو المتاجر والتجارة الإلكترونية';
            routeDesc = 'تحليل الذكاء الاصطناعي: فكرتك تميل نحو التجارة الإلكترونية. جاري تحويلك إلى المتجر والخدمات المرتبطة.';
            routeBadge = 'التجارة الإلكترونية';
            routeIcon = '🛍️';
        } else if (idea.includes('سعر') || idea.includes('تكلفة') || idea.includes('باقة')) {
            targetId = 'pricing-section';
            fallbackUrl = './index.html#pricing-section';
            routeTitle = 'خطط الأسعار والباقات المؤسسية';
            routeDesc = 'تحليل الذكاء الاصطناعي: تم تصنيف مشروعك، جاري عرض خطط الأسعار والخيارات المناسبة لك.';
            routeBadge = 'خطط الأسعار';
            routeIcon = '💎';
        }

        showCustomRouteCard({
            badge: routeBadge,
            icon: routeIcon,
            title: routeTitle,
            description: routeDesc,
            targetId: targetId,
            fallbackUrl: fallbackUrl
        });
    }

    // 5.3 Dynamic Rotating Hero Headline Engine (Mohammad Salim Aziza & S&R CoreSync Pillars)
    function initHeroDynamicTitleRotator() {
        const titleEl = document.getElementById('heroRotatingText');
        if (!titleEl) return;

        const titles = [
            'أنظمة برمجية متقدمة وحلول الذكاء الاصطناعي',
            'تطبيقات ومنصات رقمية وحلول سحابية فائقة',
            'بناء وتحديث المنظومات المؤسسية وإدارة البيانات',
            'تصميم المتاجر الإلكترونية الفاخرة والهويات البصرية'
        ];

        let index = 0;
        setInterval(() => {
            titleEl.style.opacity = '0';
            titleEl.style.transform = 'translateY(10px)';
            setTimeout(() => {
                index = (index + 1) % titles.length;
                titleEl.textContent = titles[index];
                titleEl.style.opacity = '1';
                titleEl.style.transform = 'translateY(0)';
            }, 350);
        }, 3600);
    }

    // Expose globally to window
    window.setPrompt = setPrompt;
    window.analyzeIdea = analyzeIdea;
    window.closeRouteCard = closeRouteCard;

    // Boot on DOMContentLoaded or immediately if ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            createMasterDrawer();
            autoEnhanceNavbar();
            initAnimatedPlaceholder();
            initHeroDynamicTitleRotator();
        });
    } else {
        createMasterDrawer();
        autoEnhanceNavbar();
        initAnimatedPlaceholder();
        initHeroDynamicTitleRotator();
    }

})();

