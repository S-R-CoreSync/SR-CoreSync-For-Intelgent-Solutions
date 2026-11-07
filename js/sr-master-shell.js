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

        // Trigger AI Scope & Timeline Estimator Modal (Phase 159)
        openAiEstimatorModal(idea);
    }

    // 5.3 Dynamic Rotating Hero Headline Engine — with Bullet Dot Navigator
    // Phase 157: Extracted currentHeroIndex + heroJumpToTitle() for dot control
    var currentHeroIndex = 0;
    var heroTitleInterval = null;

    function initHeroDynamicTitleRotator() {
        const titleEl = document.getElementById('heroRotatingText');
        if (!titleEl) return;

        const titles = [
            'أنظمة برمجية متقدمة وحلول الذكاء الاصطناعي',
            'تطبيقات ومنصات رقمية وحلول سحابية فائقة',
            'بناء وتحديث المنظومات المؤسسية وإدارة البيانات',
            'تصميم المتاجر الإلكترونية الفاخرة والهويات البصرية'
        ];

        function updateDots(idx) {
            var dots = document.querySelectorAll('#heroDotIndicators .hero-title-dot');
            dots.forEach(function(d, i) {
                d.classList.toggle('active', i === idx);
            });
        }

        function rotateTo(idx) {
            titleEl.style.opacity = '0';
            titleEl.style.transform = 'translateY(10px)';
            setTimeout(function() {
                currentHeroIndex = idx;
                titleEl.textContent = titles[currentHeroIndex];
                titleEl.style.opacity = '1';
                titleEl.style.transform = 'translateY(0)';
                updateDots(currentHeroIndex);
            }, 350);
        }

        function startAutoRotate() {
            heroTitleInterval = setInterval(function() {
                rotateTo((currentHeroIndex + 1) % titles.length);
            }, 3600);
        }

        // Expose global jump function for dot buttons
        window.heroJumpToTitle = function(idx) {
            playHaptic('tap');
            if (heroTitleInterval) clearInterval(heroTitleInterval);
            rotateTo(idx);
            startAutoRotate();
        };

        startAutoRotate();
    }

    // 5.4 Orbital Emblem Parallax — Mouse-driven 3D tilt
    function initEmblemParallax() {
        var stage = document.getElementById('heroEmblemStage');
        var card  = document.getElementById('heroEmblemCard');
        if (!stage || !card) return;

        stage.addEventListener('mousemove', function(e) {
            var rect = stage.getBoundingClientRect();
            var cx = rect.left + rect.width  / 2;
            var cy = rect.top  + rect.height / 2;
            var dx = (e.clientX - cx) / (rect.width  / 2);
            var dy = (e.clientY - cy) / (rect.height / 2);
            var rotX = (-dy * 12).toFixed(2);
            var rotY = ( dx * 12).toFixed(2);
            card.style.transform = 'rotateX(' + rotX + 'deg) rotateY(' + rotY + 'deg) scale(1.03)';
        });

        stage.addEventListener('mouseleave', function() {
            card.style.transform = 'rotateX(0deg) rotateY(0deg) scale(1)';
        });
    }

    // 5.5 Web Audio Luxury Haptic Sound Engine (Phase 159)
    var isSoundMuted = localStorage.getItem('sr_sound_muted') === 'true';
    var audioCtx = null;

    function getAudioContext() {
        if (!audioCtx) {
            var AudioContextClass = window.AudioContext || window.webkitAudioContext;
            if (AudioContextClass) {
                audioCtx = new AudioContextClass();
            }
        }
        if (audioCtx && audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
        return audioCtx;
    }

    function playHaptic(type) {
        if (isSoundMuted) return;
        try {
            var ctx = getAudioContext();
            if (!ctx) return;

            var osc = ctx.createOscillator();
            var gain = ctx.createGain();
            var now = ctx.currentTime;

            osc.type = 'sine';

            if (type === 'tap') {
                osc.frequency.setValueAtTime(1150, now);
                osc.frequency.exponentialRampToValueAtTime(750, now + 0.05);
                gain.gain.setValueAtTime(0.04, now);
                gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.06);
                osc.start(now);
                osc.stop(now + 0.07);
            } else if (type === 'open') {
                osc.frequency.setValueAtTime(650, now);
                osc.frequency.exponentialRampToValueAtTime(1350, now + 0.12);
                gain.gain.setValueAtTime(0.05, now);
                gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.14);
                osc.start(now);
                osc.stop(now + 0.15);
            } else if (type === 'close') {
                osc.frequency.setValueAtTime(900, now);
                osc.frequency.exponentialRampToValueAtTime(450, now + 0.08);
                gain.gain.setValueAtTime(0.035, now);
                gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.09);
                osc.start(now);
                osc.stop(now + 0.1);
            } else {
                // switch tab
                osc.frequency.setValueAtTime(980, now);
                osc.frequency.exponentialRampToValueAtTime(1300, now + 0.06);
                gain.gain.setValueAtTime(0.04, now);
                gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.07);
                osc.start(now);
                osc.stop(now + 0.08);
            }

            osc.connect(gain);
            gain.connect(ctx.destination);
        } catch (e) {
            // Audio silent fallback
        }
    }

    function toggleSoundMute() {
        isSoundMuted = !isSoundMuted;
        localStorage.setItem('sr_sound_muted', isSoundMuted ? 'true' : 'false');
        updateMuteButtonUI();
        if (!isSoundMuted) {
            playHaptic('open');
        }
    }

    function updateMuteButtonUI() {
        var btn = document.getElementById('srSoundToggleBtn');
        if (!btn) return;
        if (isSoundMuted) {
            btn.classList.add('is-muted');
            btn.innerHTML = '🔇 الصوت مكتوم';
            btn.title = 'تفعيل المؤثرات الصوتية اللمسية';
        } else {
            btn.classList.remove('is-muted');
            btn.innerHTML = '🔊 صوت الواجهة';
            btn.title = 'كتم المؤثرات الصوتية اللمسية';
        }
    }

    // 5.6 Studio Peek Modal Engine — Multi-View Gallery Tabs (Phase 158 & 159)
    var currentStudioPeekKey = 'erp';
    var currentStudioPeekTab = 'dashboard';

    var studioPeekData = {
        fintech: {
            icon:  '💳',
            badge: 'FinTech & Sovereign Payments',
            title: 'حلول FinTech وبوابات الدفع الذكية',
            desc:  'بناء بوابات دفع مؤسسية، أنظمة EFT/SWIFT، محافظ رقمية، وتكامل شامل مع معايير الضرائب والفوترة الأوروبية BTW 21%.',
            tags:  ['SEPA & SWIFT', 'BTW / 21% Tax', 'Mollie & Stripe', 'Smart Wallet', 'ISO 27001'],
            url:   '#services-section',
            views: {
                dashboard: {
                    img: './assets/service-erp-finance-3d.webp',
                    kpi: '🔒 أمان مصرفي وتشفير KMS 100%'
                },
                analytics: {
                    img: './assets/branding/live_compliance_center_showcase_snapshot.png',
                    kpi: '📊 تدقيق ضريبي هولندي BTW معتمد'
                },
                mobile: {
                    img: './assets/work-civicsync-hero.webp',
                    kpi: '📱 محفظة ذكية ودفع فوري باللمس'
                }
            }
        },
        erp: {
            icon:  '🏢',
            badge: 'Enterprise CoreSync ERP',
            title: 'منظومة CoreSync ERP المؤسسية المتكاملة',
            desc:  'نظام تخطيط موارد المؤسسات الشامل: مشتريات، مخازن ذكية WMS، موارد بشرية، ومحاسبة سحابية متعددة الفروع والعملات.',
            tags:  ['Multi-Tenant Cloud', 'Automated WMS', 'HR & Payroll', 'Consolidated Ledger', 'Real-time Sync'],
            url:   '#services-section',
            views: {
                dashboard: {
                    img: './assets/branding/live_erp_operations_showcase_snapshot.png',
                    kpi: '⚡ جاهزية تشغيلية سحابية 99.99%'
                },
                analytics: {
                    img: './assets/branding/live_kpi_analytics_showcase_snapshot.png',
                    kpi: '📈 تحليلات مالية وتنفيذية لحظية'
                },
                mobile: {
                    img: './assets/work-bakery-pos.webp',
                    kpi: '📱 نقاط بيع سحابية POS متزامنة'
                }
            }
        },
        ai: {
            icon:  '🤖',
            badge: 'Autonomous AI Agents',
            title: 'وكلاء الذكاء الاصطناعي والأتمتة الذاتية',
            desc:  'تصميم وتدريب وكلاء ذكاء اصطناعي سياديين مخصصين لبيانات شركتك: دعم عملاء فوري، تحليل عقود، وأتمتة العمليات المعقدة.',
            tags:  ['Autonomous RAG', 'Multi-Agent Swarm', 'Document OCR', 'Workflow Auto-Pilot', 'Zero-Data-Leak'],
            url:   '#services-section',
            views: {
                dashboard: {
                    img: './assets/service-ai-automation-3d.webp',
                    kpi: '⏱️ زمن معالجة ذكية < 280ms'
                },
                analytics: {
                    img: './assets/branding/live_stress_testing_showcase_snapshot.png',
                    kpi: '🛡️ أمان سيادي دون تدريب نماذج عامة'
                },
                mobile: {
                    img: './assets/work-healthbridge-hero.webp',
                    kpi: '📱 مساعد ذكي محمول مدار بالصوت'
                }
            }
        },
        supply: {
            icon:  '📦',
            badge: 'Intelligent Supply Chain',
            title: 'لوجستيات ذكية وسلاسل إمداد رقمية',
            desc:  'تتبع حركة الأساطيل والشحنات لحظياً عبر أوروبا والشرق الأوسط، إدارة الموردين، والتنبؤ التلقائي باحتياجات المخزون.',
            tags:  ['GPS Fleet Live', 'Predictive Stock', 'B2B Vendor Portal', 'Dynamic Route AI', 'EDI Integration'],
            url:   '#services-section',
            views: {
                dashboard: {
                    img: './assets/branding/live_reseller_portal_showcase_snapshot.png',
                    kpi: '📦 تكامل لوجستي عبر القارات 100%'
                },
                analytics: {
                    img: './assets/branding/live_kms_backup_showcase_snapshot.png',
                    kpi: '🔄 تزامن مخزون عبر 24 مركز توزيع'
                },
                mobile: {
                    img: './assets/work-omnibakery-hero.webp',
                    kpi: '📱 تطبيق سائقين ومسح باركود ذكي'
                }
            }
        },
        store: {
            icon:  '🛒',
            badge: 'Luxury E-Commerce & Identity',
            title: 'متاجر إلكترونية فاخرة وهويات بصرية ملكية',
            desc:  'تصميم متاجر رقمية عالية التحويل بتجربة مستخدم سينمائية استثنائية، وتصميم هويات بصرية ثلاثية الأبعاد تعزز مكانة علامتك.',
            tags:  ['Headless Commerce', '3D Showcase', 'Omni-Channel', 'Tailored UI/UX', 'Conversion Optimized'],
            url:   '#store-section',
            views: {
                dashboard: {
                    img: './assets/work-1.webp',
                    kpi: '🚀 سرعة أداء واستجابة 99/100'
                },
                analytics: {
                    img: './assets/work-2.webp',
                    kpi: '💎 معدل تحويل مبيعات مرتفع'
                },
                mobile: {
                    img: './assets/work-3.webp',
                    kpi: '📱 تجربة تسوق جوال سينمائية'
                }
            }
        },
        clgid: {
            icon:  '🏛️',
            badge: 'CLGID Center — The Hague',
            title: 'مركز CLGID لاهاي للحوكمة والاستثمار الدولي',
            desc:  'مركز دولي رائد في حوكمة المنظومات، الامتثال للأنظمة الأوروبية والضريبية، وتسهيل تأسيس وتوسع الشركات في هولندا والاتحاد الأوروبي.',
            tags:  ['The Hague HQ', 'EU Directives', 'GDPR Sovereign', 'Dutch Chamber (KvK)', 'Cross-Border Deals'],
            url:   'https://clgid-governance.ai.studio/',
            views: {
                dashboard: {
                    img: './assets/branding/live_compliance_center_showcase_snapshot.png',
                    kpi: '🏛️ اعتماد أوروبي وحوكمة دولية كاملة'
                },
                analytics: {
                    img: './assets/branding/coresync-emblem-8k.png',
                    kpi: '📜 مطابقة 100% مع تشريعات الاتحاد'
                },
                mobile: {
                    img: './assets/work-web-cleaning.webp',
                    kpi: '📱 بوابة مستثمرين دولية آمنة'
                }
            }
        }
    };

    function showStudioPeek(key) {
        playHaptic('open');
        var data = studioPeekData[key];
        if (!data) return;

        currentStudioPeekKey = key;
        currentStudioPeekTab = 'dashboard';

        var iconEl  = document.getElementById('srPeekIcon');
        var badgeEl = document.getElementById('srPeekBadge');
        var titleEl = document.getElementById('srPeekTitle');
        var descEl  = document.getElementById('srPeekDesc');
        var tagsEl  = document.getElementById('srPeekTags');

        if (iconEl)  iconEl.textContent  = data.icon;
        if (badgeEl) badgeEl.textContent = data.badge;
        if (titleEl) titleEl.textContent = data.title;
        if (descEl)  descEl.textContent  = data.desc;

        applyStudioPeekView(currentStudioPeekKey, currentStudioPeekTab);

        if (tagsEl && data.tags) {
            tagsEl.innerHTML = '';
            data.tags.forEach(function(tag) {
                var pill = document.createElement('span');
                pill.className = 'sr-peek-tag-pill';
                pill.textContent = tag;
                tagsEl.appendChild(pill);
            });
        }

        // Reset tabs state
        var tabBtns = document.querySelectorAll('#srPeekTabs .sr-peek-tab-btn');
        tabBtns.forEach(function(btn) {
            btn.classList.toggle('active', btn.getAttribute('data-tab') === 'dashboard');
        });

        var btnGo = document.getElementById('srPeekBtnGo');
        if (btnGo) {
            btnGo.onclick = function() {
                playHaptic('tap');
                closeStudioPeek();
                setTimeout(function() {
                    if (data.url.startsWith('http')) {
                        window.open(data.url, '_blank', 'noopener');
                    } else {
                        var target = document.querySelector(data.url);
                        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        else window.location.href = data.url;
                    }
                }, 320);
            };
        }

        var overlay = document.getElementById('srStudioPeekOverlay');
        if (overlay) {
            overlay.style.display = 'flex';
            requestAnimationFrame(function() {
                overlay.classList.add('sr-peek-visible');
            });
        }
    }

    function applyStudioPeekView(secKey, tabKey) {
        var data = studioPeekData[secKey];
        if (!data || !data.views) return;
        var view = data.views[tabKey] || data.views['dashboard'];
        if (!view) return;

        var imgEl = document.getElementById('srPeekImg');
        var kpiEl = document.getElementById('srPeekKpi');

        if (imgEl && view.img) {
            imgEl.style.opacity = '0.4';
            imgEl.style.transform = 'scale(0.98)';
            setTimeout(function() {
                imgEl.src = view.img;
                imgEl.alt = data.title;
                imgEl.style.opacity = '1';
                imgEl.style.transform = 'scale(1)';
            }, 120);
        }

        if (kpiEl && view.kpi) {
            kpiEl.textContent = view.kpi;
        }
    }

    function switchStudioPeekTab(tabKey) {
        playHaptic('switch');
        currentStudioPeekTab = tabKey;

        var tabBtns = document.querySelectorAll('#srPeekTabs .sr-peek-tab-btn');
        tabBtns.forEach(function(btn) {
            btn.classList.toggle('active', btn.getAttribute('data-tab') === tabKey);
        });

        applyStudioPeekView(currentStudioPeekKey, currentStudioPeekTab);
    }

    function closeStudioPeek() {
        playHaptic('close');
        var overlay = document.getElementById('srStudioPeekOverlay');
        if (!overlay) return;
        overlay.classList.remove('sr-peek-visible');
        setTimeout(function() { overlay.style.display = 'none'; }, 320);
    }

    // 5.7 AI Scope & Timeline Estimator Engine (Phase 159)
    function openAiEstimatorModal(query) {
        playHaptic('open');
        var text = (query || '').toLowerCase();

        var classification = 'هندسة منظومة رقمية سحابية مخصصة';
        var timeline = '4 - 6 أسابيع';
        var compliance = 'معايير الاتحاد الأوروبي + GDPR';
        var stack = 'Next.js 15 + CoreSync Cloud';

        if (text.includes('متجر') || text.includes('بيع') || text.includes('منتج') || text.includes('تسوق') || text.includes('سلة')) {
            classification = 'منصة تجارة إلكترونية فاخرة متكاملة';
            timeline = '3 - 5 أسابيع';
            compliance = 'EU GDPR + BTW 21% + SEPA/Mollie';
            stack = 'Headless Next.js + CoreSync Commerce';
        } else if (text.includes('سعر') || text.includes('تكلفة') || text.includes('باقة') || text.includes('اشتراك')) {
            classification = 'حزمة التحول الرقمي المؤسسي الشامل';
            timeline = '2 - 4 أسابيع';
            compliance = 'ضمان تكلفة ثابت مع عائد استثماري ROI موثق';
            stack = 'CoreSync Enterprise Sovereign Bundle';
        } else if (text.includes('ذكاء') || text.includes('ai') || text.includes('وكيل') || text.includes('بوت') || text.includes('أتمتة')) {
            classification = 'شبكة وكلاء ذكاء اصطناعي وأتمتة سيادية';
            timeline = '4 - 6 أسابيع';
            compliance = 'Zero Data Leakage + ISO 27001 Cloud';
            stack = 'Autonomous RAG + Private Multi-Agent Swarm';
        } else if (text.includes('نظام') || text.includes('إدارة') || text.includes('erp') || text.includes('مخازن') || text.includes('محاسبة')) {
            classification = 'منظومة CoreSync ERP المؤسسية الشاملة';
            timeline = '6 - 8 أسابيع';
            compliance = 'حوكمة أوروبية + معايير هولندية KvK & Belasting';
            stack = 'PostgreSQL Cluster + CoreSync ERP Core';
        } else if (text.includes('شحن') || text.includes('توصيل') || text.includes('لوجست') || text.includes('إمداد')) {
            classification = 'شبكة لوجستيات وسلاسل إمداد رقمية';
            timeline = '5 - 7 أسابيع';
            compliance = 'تتبع أساطيل أوروبي + أمان شحنات متقدم';
            stack = 'Dynamic Route AI + Fleet Telematics Engine';
        }

        var qEl = document.getElementById('srEstQueryText');
        var cEl = document.getElementById('srEstClassification');
        var tEl = document.getElementById('srEstTimeline');
        var cmpEl = document.getElementById('srEstCompliance');
        var sEl = document.getElementById('srEstStack');

        if (qEl) qEl.textContent = '« ' + (query || 'فكرة استراتيجية قيد التحليل') + ' »';
        if (cEl) cEl.textContent = classification;
        if (tEl) tEl.textContent = timeline;
        if (cmpEl) cmpEl.textContent = compliance;
        if (sEl) sEl.textContent = stack;

        var modal = document.getElementById('srAiEstimateModal');
        if (modal) {
            modal.style.display = 'flex';
            requestAnimationFrame(function() {
                modal.classList.add('sr-estimate-visible');
            });
        }
    }

    function closeAiEstimateModal() {
        playHaptic('close');
        var modal = document.getElementById('srAiEstimateModal');
        if (!modal) return;
        modal.classList.remove('sr-estimate-visible');
        setTimeout(function() { modal.style.display = 'none'; }, 320);
    }

    // 5.8 Benchmark Comparison Toggle (Phase 160)
    function toggleBenchmarkView() {
        playHaptic('tap');
        var box = document.getElementById('srPeekBenchmarkBox');
        var btn = document.getElementById('srBenchmarkToggleBtn');
        if (!box || !btn) return;

        var isOpen = box.style.display !== 'none';
        if (isOpen) {
            box.style.display = 'none';
            btn.classList.remove('is-open');
        } else {
            box.style.display = 'flex';
            btn.classList.add('is-open');
        }
    }

    // 5.9 Executive Architecture Brief PDF Generation Engine (Phase 160)
    function exportAiEstimatePdf() {
        playHaptic('open');

        var title = (document.getElementById('srEstTitle') || {}).textContent || 'تحليل النطاق المعماري والجدول الزمني';
        var query = (document.getElementById('srEstQueryText') || {}).textContent || '';
        var classification = (document.getElementById('srEstClassification') || {}).textContent || '';
        var timeline = (document.getElementById('srEstTimeline') || {}).textContent || '';
        var compliance = (document.getElementById('srEstCompliance') || {}).textContent || '';
        var stack = (document.getElementById('srEstStack') || {}).textContent || '';
        var dateStr = 'السبت، 07 نوفمبر 2026 — هولندا، أمستردام';

        var printWindow = window.open('', '_blank', 'width=900,height=1100');
        if (!printWindow) {
            alert('يرجى السماح بفتح النوافذ المنبثقة لتحميل وطباعة وثيقة الـ PDF السيادية.');
            return;
        }

        var printHtml = '<!DOCTYPE html>' +
            '<html lang="ar" dir="rtl">' +
            '<head>' +
            '<meta charset="UTF-8">' +
            '<title>S&R CoreSync — وثيقة المواصفات المعمارية التنفيذية</title>' +
            '<style>' +
            '@page { size: A4; margin: 18mm 15mm; }' +
            '* { box-sizing: border-box; font-family: "Segoe UI", Tahoma, Arial, sans-serif; }' +
            'body { background: #ffffff; color: #0a1016; margin: 0; padding: 25px; line-height: 1.6; }' +
            '.doc-header { display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #c5a880; padding-bottom: 16px; margin-bottom: 22px; }' +
            '.doc-logo-title { font-size: 22px; font-weight: 900; color: #070d0a; margin: 0; }' +
            '.doc-logo-sub { font-size: 13px; color: #8c734b; font-weight: 700; margin: 2px 0 0; }' +
            '.doc-meta { text-align: left; font-size: 11px; color: #555; }' +
            '.doc-badge { display: inline-block; background: #fdf8ef; border: 1px solid #c5a880; color: #8c734b; font-weight: 800; font-size: 11px; padding: 4px 12px; border-radius: 999px; margin-bottom: 12px; }' +
            '.doc-title { font-size: 20px; font-weight: 800; color: #070d0a; margin: 0 0 14px; }' +
            '.query-card { background: #f8f9fa; border-right: 4px solid #c5a880; padding: 12px 16px; margin-bottom: 22px; border-radius: 4px; }' +
            '.query-card p { margin: 0; font-style: italic; color: #333; font-weight: 600; font-size: 14px; }' +
            '.matrix-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 24px; }' +
            '.matrix-box { border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; background: #fafbfc; }' +
            '.matrix-lbl { font-size: 12px; color: #64748b; font-weight: 700; display: block; margin-bottom: 4px; }' +
            '.matrix-val { font-size: 14px; color: #0f172a; font-weight: 800; }' +
            '.phases-table { width: 100%; border-collapse: collapse; margin-bottom: 26px; font-size: 13px; }' +
            '.phases-table th, .phases-table td { border: 1px solid #e2e8f0; padding: 10px 14px; text-align: right; }' +
            '.phases-table th { background: #f1f5f9; color: #0f172a; font-weight: 800; }' +
            '.doc-footer { display: flex; align-items: flex-end; justify-content: space-between; margin-top: 35px; border-top: 1px solid #e2e8f0; padding-top: 20px; }' +
            '.sign-block { text-align: right; }' +
            '.sign-title { font-size: 13px; font-weight: 800; color: #070d0a; margin: 0; }' +
            '.sign-role { font-size: 11px; color: #64748b; margin: 2px 0 0; }' +
            '.seal-box { border: 2px dashed #c5a880; border-radius: 50%; width: 95px; height: 95px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; color: #8c734b; font-size: 10px; font-weight: 800; transform: rotate(-5deg); }' +
            '</style>' +
            '</head>' +
            '<body>' +
            '<div class="doc-header">' +
            '<div>' +
            '<h1 class="doc-logo-title">S&amp;R CoreSync For Intelligent Solutions</h1>' +
            '<p class="doc-logo-sub">المكتب الاستشاري السيادي لهندسة المنظومات والذكاء الاصطناعي</p>' +
            '</div>' +
            '<div class="doc-meta">' +
            '<strong>Amsterdam HQ — Netherlands</strong><br>' +
            'Dutch KvK &amp; 21% BTW Compliant<br>' +
            'تاريخ التوثيق: ' + dateStr +
            '</div>' +
            '</div>' +
            '<span class="doc-badge">وثيقة استشارية معمارية رسمية • صالحة للبدء التنفيذي</span>' +
            '<h2 class="doc-title">' + title + '</h2>' +
            '<div class="query-card">' +
            '<span style="font-size:11px; color:#64748b; font-weight:700;">ملخص الفكرة المقدمة من الشريك / العميل:</span>' +
            '<p>' + query + '</p>' +
            '</div>' +
            '<div class="matrix-grid">' +
            '<div class="matrix-box"><span class="matrix-lbl">التصنيف المعماري المعتمد</span><span class="matrix-val">' + classification + '</span></div>' +
            '<div class="matrix-box"><span class="matrix-lbl">الجدول الزمني التقديري للإطلاق</span><span class="matrix-val">' + timeline + '</span></div>' +
            '<div class="matrix-box"><span class="matrix-lbl">معايير الأمان والامتثال الأوروبي</span><span class="matrix-val">' + compliance + '</span></div>' +
            '<div class="matrix-box"><span class="matrix-lbl">المعمارية والتقنيات المقترحة</span><span class="matrix-val">' + stack + '</span></div>' +
            '</div>' +
            '<h3 style="font-size:14px; font-weight:800; color:#0f172a; margin-bottom:10px;">خريطة الطريق التنفيذية للمشروع (3 Phases Roadmap):</h3>' +
            '<table class="phases-table">' +
            '<thead><tr><th>المرحلة</th><th>النطاق الهندسي</th><th>مخرجات الاعتماد</th></tr></thead>' +
            '<tbody>' +
            '<tr><td><strong>المرحلة 1</strong></td><td>هندسة النواة، النمذجة البيانية، وتأمين البنية التحتية السحابية</td><td>وثيقة المعمارية + مستودع Git الأساسي</td></tr>' +
            '<tr><td><strong>المرحلة 2</strong></td><td>تطوير واجهات المستخدم التفاعلية، بوابات الدفع، وتكامل الـ API</td><td>بيئة تجريبية حية (Staging Prototype)</td></tr>' +
            '<tr><td><strong>المرحلة 3</strong></td><td>فحوصات الأمان واختبارات الضغط، التدقيق الضريبي، والتشغيل الفعلي</td><td>شهادة الامتثال والإنتاج السيادي 100%</td></tr>' +
            '</tbody>' +
            '</table>' +
            '<div class="doc-footer">' +
            '<div class="sign-block">' +
            '<p class="sign-title">المهندس محمد سليم عزيزة</p>' +
            '<p class="sign-role">المؤسس والرئيس التنفيذي للتكنولوجيا (CTO) • S&amp;R CoreSync</p>' +
            '</div>' +
            '<div class="seal-box">' +
            '<span>S&amp;R CoreSync</span>' +
            '<span>SOVEREIGN</span>' +
            '<span>VERIFIED</span>' +
            '</div>' +
            '</div>' +
            '<script>' +
            'window.onload = function() { window.print(); };' +
            '</script>' +
            '</body>' +
            '</html>';

        printWindow.document.open();
        printWindow.document.write(printHtml);
        printWindow.document.close();
    }

    // 5.10 Voice-to-Text Idea Dictation Engine via Web Speech API (Phase 160)
    var heroSpeechRecognition = null;
    var isHeroSpeechListening = false;

    function initHeroVoiceDictation() {
        var SpeechRecognitionClass = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognitionClass) return null;

        var rec = new SpeechRecognitionClass();
        rec.continuous = false;
        rec.interimResults = true;
        rec.lang = 'ar-SA';

        rec.onstart = function() {
            isHeroSpeechListening = true;
            playHaptic('open');
            var btn = document.getElementById('srVoiceDictateBtn');
            var input = document.getElementById('userIdeaInput');
            if (btn) btn.classList.add('is-listening');
            if (input) {
                input.placeholder = '🔴 جاري الاستماع... تفضل بالتحدث الآن';
            }
        };

        rec.onresult = function(event) {
            var transcript = '';
            for (var i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            var input = document.getElementById('userIdeaInput');
            if (input && transcript) {
                input.value = transcript;
            }
        };

        rec.onerror = function() {
            stopHeroVoiceDictation();
        };

        rec.onend = function() {
            stopHeroVoiceDictation();
        };

        return rec;
    }

    function toggleHeroVoiceDictation() {
        if (!heroSpeechRecognition) {
            heroSpeechRecognition = initHeroVoiceDictation();
        }

        if (!heroSpeechRecognition) {
            alert('متصفحك الحالي لا يدعم ميزة الإملاء الصوتي المباشر. يرجى استخدام متصفح Chrome أو Edge.');
            return;
        }

        if (isHeroSpeechListening) {
            heroSpeechRecognition.stop();
            stopHeroVoiceDictation();
        } else {
            try {
                heroSpeechRecognition.start();
            } catch (e) {
                // If already active
            }
        }
    }

    function stopHeroVoiceDictation() {
        isHeroSpeechListening = false;
        playHaptic('close');
        var btn = document.getElementById('srVoiceDictateBtn');
        var input = document.getElementById('userIdeaInput');
        if (btn) btn.classList.remove('is-listening');
        if (input && !input.value) {
            input.placeholder = 'اكتب فكرة مشروعك هنا (مثلاً: أريد بناء متجر إلكتروني ذكي)...';
        }
    }

    // Expose globally to window
    window.setPrompt                 = setPrompt;
    window.analyzeIdea               = analyzeIdea;
    window.closeRouteCard            = closeRouteCard;
    window.showStudioPeek            = showStudioPeek;
    window.closeStudioPeek           = closeStudioPeek;
    window.switchStudioPeekTab       = switchStudioPeekTab;
    window.toggleBenchmarkView       = toggleBenchmarkView;
    window.openAiEstimatorModal      = openAiEstimatorModal;
    window.closeAiEstimateModal      = closeAiEstimateModal;
    window.exportAiEstimatePdf       = exportAiEstimatePdf;
    window.toggleHeroVoiceDictation  = toggleHeroVoiceDictation;
    window.toggleSoundMute           = toggleSoundMute;
    window.playHaptic                = playHaptic;
    // heroJumpToTitle exposed inside initHeroDynamicTitleRotator()

    // Boot on DOMContentLoaded or immediately if ready
    function bootMasterShell() {
        createMasterDrawer();
        autoEnhanceNavbar();
        initAnimatedPlaceholder();
        initHeroDynamicTitleRotator();
        initEmblemParallax();
        updateMuteButtonUI();

        // Support preview hash trigger for visual audits (immediate invocation)
        if (window.location.hash) {
            if (window.location.hash.indexOf('peek-') !== -1) {
                var isBench = window.location.hash.indexOf('-bench') !== -1;
                var peekKey = window.location.hash.replace('#peek-', '').replace('-bench', '').trim();
                showStudioPeek(peekKey);
                if (isBench) {
                    toggleBenchmarkView();
                }
            } else if (window.location.hash.indexOf('estimate') !== -1) {
                openAiEstimatorModal('أريد بناء منصة تجارة إلكترونية فاخرة متكاملة');
            }
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bootMasterShell);
    } else {
        bootMasterShell();
    }

})();

