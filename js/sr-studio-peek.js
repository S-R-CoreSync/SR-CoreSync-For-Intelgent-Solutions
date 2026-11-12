/*
 * S&R CoreSync For Intelligent Solutions - Studio Peek Modal Engine
 * PROPRIETARY & CONFIDENTIAL INTELLECTUAL PROPERTY
 * Copyright (c) 2026 S&R CoreSync. All Rights Reserved.
 * Unauthorized copying, decompilation, redistribution, or external model training is prohibited.
 *
 * The sector chips in the hero of every localized homepage call
 * showStudioPeek('fintech') and friends. Only the Arabic master loaded the
 * master shell that defined it and carried the overlay, so on 28 localized
 * homepages the twelve chips were dead buttons: markup without a controller,
 * the exact failure mode the CI dock-handler check exists to catch.
 *
 * This module is the controller on its own: it defines the three entry points,
 * builds the overlay when the page has none, resolves asset paths one level up
 * from a language directory, and never overwrites the master shell's copy
 * (it returns early when showStudioPeek already exists).
 *
 * External (non-inline) script: no CSP hash needed, no inline handler in the
 * markup it injects - every listener is bound in JavaScript.
 */
(function (global) {
    'use strict';

    if (typeof global.showStudioPeek === 'function') {
        return;
    }

    var doc = global.document;

    /* ------------------------------------------------------------------
     * Asset base: './' on the site root, '../' inside /de/, /ckb/, ...
     * ------------------------------------------------------------------ */
    function basePrefix() {
        var path = global.location.pathname.replace(/\/[^\/]*$/, '');
        var parts = path.split('/').filter(function (part) { return part.length > 0; });
        if (!parts.length) { return './'; }
        var prefix = '';
        for (var i = 0; i < parts.length; i++) { prefix += '../'; }
        return prefix;
    }

    var BASE = basePrefix();

    function asset(path) {
        return path.indexOf('./') === 0 ? BASE + path.slice(2) : path;
    }

    function haptic(kind) {
        if (typeof global.playHaptic === 'function') {
            global.playHaptic(kind);
        }
    }

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

    var currentStudioPeekKey = 'erp';
    var currentStudioPeekTab = 'dashboard';
    var overlayBuilt = false;

    /* ------------------------------------------------------------------
     * Overlay construction (only when the page carries none)
     * ------------------------------------------------------------------ */
    function el(tag, className, id) {
        var node = doc.createElement(tag);
        if (className) { node.className = className; }
        if (id) { node.id = id; }
        return node;
    }

    var BENCHMARK_ROWS = [
        ['3.8 ثوانٍ (تقليدي)', '⚡ السرعة:', '< 280ms (CoreSync)'],
        ['تكاليف باهظة ومجزأة', '💰 التكلفة:', 'توفير 60% مع بنية موحدة'],
        ['يدوي ومعرض للغرامات', '🛡️ الامتثال:', 'مؤتمت 100% BTW & GDPR'],
        ['تعطل متكرر وصيانة معقدة', '☁️ الجاهزية:', 'سحابي موزع 99.9%']
    ];

    function buildOverlay() {
        if (doc.getElementById('srStudioPeekOverlay')) { return; }

        var overlay = el('div', '', 'srStudioPeekOverlay');
        overlay.setAttribute('role', 'dialog');
        overlay.setAttribute('aria-modal', 'true');
        overlay.setAttribute('aria-label', 'معاينة الاستوديو التفاعلية');

        var card = el('div', 'sr-studio-peek-card', 'srStudioPeekCard');

        var topBar = el('div', 'sr-peek-top-bar');
        var brand = el('div', 'd-flex align-items-center gap-2');
        var icon = el('span', 'sr-peek-icon', 'srPeekIcon');
        icon.textContent = '💡';
        var badge = el('span', 'sr-peek-badge', 'srPeekBadge');
        badge.textContent = 'استوديو S&R CoreSync';
        brand.appendChild(icon);
        brand.appendChild(badge);

        var closeCorner = el('button', 'sr-peek-close-corner');
        closeCorner.type = 'button';
        closeCorner.setAttribute('aria-label', 'إغلاق النافذة');
        closeCorner.textContent = '✕';
        closeCorner.addEventListener('click', function () { closeStudioPeek(); });

        topBar.appendChild(brand);
        topBar.appendChild(closeCorner);

        var tabs = el('div', 'sr-peek-tabs-row', 'srPeekTabs');
        tabs.setAttribute('role', 'tablist');
        tabs.setAttribute('aria-label', 'أوضاع المعاينة للمنظومة');
        [['dashboard', '🖥️ لوحة الإدارة'], ['analytics', '📊 التقارير والامتثال'], ['mobile', '📱 تطبيق الجوال']]
            .forEach(function (pair) {
                var tab = el('button', 'sr-peek-tab-btn' + (pair[0] === 'dashboard' ? ' active' : ''));
                tab.type = 'button';
                tab.dataset.tab = pair[0];
                tab.setAttribute('role', 'tab');
                tab.textContent = pair[1];
                tab.addEventListener('click', function () { switchStudioPeekTab(pair[0]); });
                tabs.appendChild(tab);
            });

        var visual = el('div', 'sr-peek-visual-box', 'srPeekVisualBox');
        var img = el('img', 'sr-peek-thumb-img', 'srPeekImg');
        img.src = asset('./assets/service-erp-finance-3d.webp');
        img.alt = 'معاينة المنصة';
        img.loading = 'lazy';
        var kpi = el('span', 'sr-peek-kpi-badge', 'srPeekKpi');
        kpi.textContent = '⚡ مؤشر الأداء: 99.9%';
        visual.appendChild(img);
        visual.appendChild(el('div', 'sr-peek-visual-overlay'));
        visual.appendChild(kpi);

        var title = el('h2', 'sr-peek-title', 'srPeekTitle');
        title.textContent = 'عنوان الخدمة';
        var desc = el('p', 'sr-peek-desc', 'srPeekDesc');
        desc.textContent = 'وصف الخدمة';
        var tags = el('div', 'sr-peek-tags-row', 'srPeekTags');
        tags.setAttribute('aria-label', 'التقنيات المستخدمة');

        var benchmark = el('div', 'sr-peek-benchmark-section');
        var benchBtn = el('button', 'sr-peek-benchmark-toggle-btn', 'srBenchmarkToggleBtn');
        benchBtn.type = 'button';
        var benchLabel = el('span');
        benchLabel.textContent = '⚖️ مقارنة الأداء: الأنظمة القديمة vs CoreSync';
        var benchArrow = el('span', 'sr-toggle-arrow', 'srBenchmarkArrow');
        benchArrow.textContent = '▾';
        benchBtn.appendChild(benchLabel);
        benchBtn.appendChild(benchArrow);
        benchBtn.addEventListener('click', function () { toggleBenchmarkView(); });

        var benchBox = el('div', 'sr-peek-benchmark-box', 'srPeekBenchmarkBox');
        benchBox.style.display = 'none';
        BENCHMARK_ROWS.forEach(function (row) {
            var line = el('div', 'sr-benchmark-row');
            var legacy = el('span', 'sr-bm-item legacy');
            legacy.textContent = row[0];
            var vs = el('span', 'sr-bm-vs');
            vs.textContent = row[1];
            var modern = el('span', 'sr-bm-item coresync');
            modern.textContent = row[2];
            line.appendChild(legacy);
            line.appendChild(vs);
            line.appendChild(modern);
            benchBox.appendChild(line);
        });

        benchmark.appendChild(benchBtn);
        benchmark.appendChild(benchBox);

        var actions = el('div', 'sr-peek-actions');
        var goBtn = el('button', 'sr-peek-btn-go', 'srPeekBtnGo');
        goBtn.type = 'button';
        goBtn.textContent = '🚀 استعراض الاستوديو بالكامل';
        var closeBtn = el('button', 'sr-peek-btn-close');
        closeBtn.type = 'button';
        closeBtn.textContent = 'إغلاق';
        closeBtn.addEventListener('click', function () { closeStudioPeek(); });
        actions.appendChild(goBtn);
        actions.appendChild(closeBtn);

        card.appendChild(topBar);
        card.appendChild(tabs);
        card.appendChild(visual);
        card.appendChild(title);
        card.appendChild(desc);
        card.appendChild(tags);
        card.appendChild(benchmark);
        card.appendChild(actions);
        overlay.appendChild(card);

        overlay.addEventListener('click', function (event) {
            if (event.target === overlay) { closeStudioPeek(); }
        });

        doc.body.appendChild(overlay);
        overlayBuilt = true;

        doc.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') { closeStudioPeek(); }
        });
    }

    /* ------------------------------------------------------------------
     * Behaviour - mirrors the master shell's engine
     * ------------------------------------------------------------------ */
    function applyStudioPeekView(sectionKey, tabKey) {
        var data = studioPeekData[sectionKey];
        if (!data || !data.views) { return; }
        var view = data.views[tabKey] || data.views.dashboard;
        if (!view) { return; }

        var imgEl = doc.getElementById('srPeekImg');
        var kpiEl = doc.getElementById('srPeekKpi');

        if (imgEl && view.img) {
            imgEl.style.opacity = '0.4';
            imgEl.style.transform = 'scale(0.98)';
            global.setTimeout(function () {
                imgEl.src = asset(view.img);
                imgEl.alt = data.title;
                imgEl.style.opacity = '1';
                imgEl.style.transform = 'scale(1)';
            }, 120);
        }

        if (kpiEl && view.kpi) { kpiEl.textContent = view.kpi; }
    }

    function goTo(url) {
        if (!url) { return; }
        if (url.indexOf('http') === 0) {
            global.open(url, '_blank', 'noopener');
            return;
        }
        var target = doc.querySelector(url);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            global.location.href = url;
        }
    }

    function showStudioPeek(key) {
        var data = studioPeekData[key];
        if (!data) { return; }
        haptic('open');

        buildOverlay();

        currentStudioPeekKey = key;
        currentStudioPeekTab = 'dashboard';

        var iconEl = doc.getElementById('srPeekIcon');
        var badgeEl = doc.getElementById('srPeekBadge');
        var titleEl = doc.getElementById('srPeekTitle');
        var descEl = doc.getElementById('srPeekDesc');
        var tagsEl = doc.getElementById('srPeekTags');

        if (iconEl) { iconEl.textContent = data.icon; }
        if (badgeEl) { badgeEl.textContent = data.badge; }
        if (titleEl) { titleEl.textContent = data.title; }
        if (descEl) { descEl.textContent = data.desc; }

        applyStudioPeekView(currentStudioPeekKey, currentStudioPeekTab);

        if (tagsEl && data.tags) {
            tagsEl.textContent = '';
            data.tags.forEach(function (tag) {
                var pill = el('span', 'sr-peek-tag-pill');
                pill.textContent = tag;
                tagsEl.appendChild(pill);
            });
        }

        var tabBtns = doc.querySelectorAll('#srPeekTabs .sr-peek-tab-btn');
        Array.prototype.forEach.call(tabBtns, function (btn) {
            btn.classList.toggle('active', btn.getAttribute('data-tab') === 'dashboard');
        });

        var goBtn = doc.getElementById('srPeekBtnGo');
        if (goBtn) {
            goBtn.onclick = function () {
                haptic('tap');
                closeStudioPeek();
                global.setTimeout(function () { goTo(data.url); }, 320);
            };
        }

        var overlay = doc.getElementById('srStudioPeekOverlay');
        if (overlay) {
            overlay.style.display = 'flex';
            global.requestAnimationFrame(function () {
                overlay.classList.add('sr-peek-visible');
            });
        }
    }

    function closeStudioPeek() {
        haptic('close');
        var overlay = doc.getElementById('srStudioPeekOverlay');
        if (!overlay) { return; }
        overlay.classList.remove('sr-peek-visible');
        global.setTimeout(function () { overlay.style.display = 'none'; }, 320);
    }

    function switchStudioPeekTab(tabKey) {
        haptic('switch');
        currentStudioPeekTab = tabKey;
        var tabBtns = doc.querySelectorAll('#srPeekTabs .sr-peek-tab-btn');
        Array.prototype.forEach.call(tabBtns, function (btn) {
            btn.classList.toggle('active', btn.getAttribute('data-tab') === tabKey);
        });
        applyStudioPeekView(currentStudioPeekKey, currentStudioPeekTab);
    }

    function toggleBenchmarkView() {
        haptic('tap');
        var box = doc.getElementById('srPeekBenchmarkBox');
        var btn = doc.getElementById('srBenchmarkToggleBtn');
        if (!box || !btn) { return; }
        var isOpen = box.style.display !== 'none';
        if (isOpen) {
            box.style.display = 'none';
            btn.classList.remove('is-open');
        } else {
            box.style.display = 'flex';
            btn.classList.add('is-open');
        }
    }

    global.showStudioPeek = showStudioPeek;
    global.closeStudioPeek = closeStudioPeek;
    global.switchStudioPeekTab = switchStudioPeekTab;
    global.toggleBenchmarkView = toggleBenchmarkView;
})(window);
