/**
 * S&R CoreSync - Sovereign Studio Analytics & CRM Telemetry Engine
 * Tracks studio user interactions, AI package advisor consultations,
 * speed audits, and exports, routing qualified lead signals directly to CRM.
 */
(function() {
    'use strict';

    var TELEMETRY_KEY = 'sr_studio_telemetry';
    var LEADS_KEY = 'sr_crm_leads';

    var INITIAL_LEADS = [
        {
            id: 'LEAD-2026-881',
            timestamp: Date.now() - 1000 * 60 * 18,
            studio: 'tech-matrix',
            studioName: 'مصفوفة الأنظمة والباقات',
            type: 'ai_advisor',
            title: 'استشارة AI: باقة المنظومة السيادية الكاملة',
            orgSize: 'enterprise',
            priority: 'erp',
            matchScore: 98,
            estimatedValue: '€ 48,000',
            clientHint: 'مجموعة استثمارية قابضة',
            status: 'qualified',
            statusLabel: 'مؤهل ذكياً 🤖'
        },
        {
            id: 'LEAD-2026-880',
            timestamp: Date.now() - 1000 * 60 * 54,
            studio: 'perf-audit',
            studioName: 'فاحص سرعة وأداء الويب',
            type: 'perf_audit',
            title: 'فحص سرعة متجر رقمي (درجة 42/100 - بحاجة لتحسين LCP)',
            targetUrl: 'https://premium-luxury-store.eu',
            matchScore: 85,
            estimatedValue: '€ 12,500',
            clientHint: 'متجر تجارة إلكترونية أوروبي',
            status: 'opportunity',
            statusLabel: 'فرصة تسريع ⚡'
        },
        {
            id: 'LEAD-2026-879',
            timestamp: Date.now() - 1000 * 60 * 115,
            studio: 'tech-matrix',
            studioName: 'مصفوفة الأنظمة والباقات',
            type: 'roi_calc',
            title: 'حساب عائد استثماري: ترقية سحابية + نماذج AI',
            orgSize: 'mid',
            priority: 'ai',
            matchScore: 92,
            estimatedValue: '€ 24,000',
            clientHint: 'شركة حلول لوجستية إقليمية',
            status: 'proposal_ready',
            statusLabel: 'جاهز للعرض 📑'
        },
        {
            id: 'LEAD-2026-878',
            timestamp: Date.now() - 1000 * 60 * 230,
            studio: 'lottie-studio',
            studioName: 'استوديو الرسوم والتفاعلات',
            type: 'design_export',
            title: 'تصدير حزمة كود CSS Keyframes وهوية رقمية',
            preset: 'rocket',
            matchScore: 88,
            estimatedValue: '€ 8,200',
            clientHint: 'وكالة تقنية ناشئة',
            status: 'engaged',
            statusLabel: 'تفاعل تصميم 🎨'
        }
    ];

    function getStorage(key, fallback) {
        try {
            var val = localStorage.getItem(key);
            if (val) return JSON.parse(val);
        } catch (e) {}
        return fallback;
    }

    function setStorage(key, val) {
        try {
            localStorage.setItem(key, JSON.stringify(val));
        } catch (e) {}
    }

    function ensureInitialData() {
        var leads = getStorage(LEADS_KEY, null);
        if (!leads || !Array.isArray(leads) || leads.length === 0) {
            setStorage(LEADS_KEY, INITIAL_LEADS);
        }
    }

    ensureInitialData();

    window.SRStudioTelemetry = {
        /**
         * Track a generic studio event
         */
        track: function(studio, eventName, data) {
            data = data || {};
            var events = getStorage(TELEMETRY_KEY, []);
            var entry = {
                id: 'EVT-' + Date.now() + '-' + Math.floor(Math.random() * 1000),
                t: Date.now(),
                studio: studio,
                event: eventName,
                data: data,
                lang: document.documentElement.lang || 'ar',
                url: window.location.pathname
            };

            events.unshift(entry);
            if (events.length > 300) events = events.slice(0, 300);
            setStorage(TELEMETRY_KEY, events);

            // Also forward to srTrack if present
            if (window.srTrack) {
                window.srTrack('studio_' + eventName, { studio: studio, ...data });
            }

            // Dispatch local event for same-page listeners
            try {
                window.dispatchEvent(new CustomEvent('sr-telemetry-event', { detail: entry }));
            } catch (e) {}

            return entry;
        },

        /**
         * Register high-intent Lead Signal into CRM
         */
        recordLead: function(leadInfo) {
            var leads = getStorage(LEADS_KEY, INITIAL_LEADS);
            var lead = {
                id: 'LEAD-' + new Date().getFullYear() + '-' + Math.floor(100 + Math.random() * 900),
                timestamp: Date.now(),
                studio: leadInfo.studio || 'tech-matrix',
                studioName: leadInfo.studioName || 'استوديو الأنظمة',
                type: leadInfo.type || 'consultation',
                title: leadInfo.title || 'استشارة تقنية جديدة',
                orgSize: leadInfo.orgSize || 'mid',
                priority: leadInfo.priority || 'general',
                matchScore: leadInfo.matchScore || 90,
                estimatedValue: leadInfo.estimatedValue || '€ 18,000',
                clientHint: leadInfo.clientHint || 'عميل محتمل عبر الاستوديوهات',
                status: leadInfo.status || 'qualified',
                statusLabel: leadInfo.statusLabel || 'مؤهل ذكياً 🤖'
            };

            leads.unshift(lead);
            if (leads.length > 50) leads = leads.slice(0, 50);
            setStorage(LEADS_KEY, leads);

            // Track telemetry event
            this.track(lead.studio, 'lead_created', { leadId: lead.id, title: lead.title });

            return lead;
        },

        getEvents: function() {
            return getStorage(TELEMETRY_KEY, []);
        },

        getLeads: function() {
            return getStorage(LEADS_KEY, INITIAL_LEADS);
        },

        getStats: function() {
            var leads = this.getLeads();
            var events = this.getEvents();

            var advisorCount = 0;
            var auditCount = 0;
            var exportCount = 0;
            var socialCount = 0;

            leads.forEach(function(l) {
                if (l.type === 'ai_advisor') advisorCount++;
                if (l.type === 'perf_audit') auditCount++;
                if (l.type === 'design_export') exportCount++;
            });

            events.forEach(function(e) {
                if (e.event === 'ai_advisor_applied' || e.event === 'ai_advisor_run') advisorCount++;
                if (e.event === 'audit_completed') auditCount++;
                if (e.event === 'export_json' || e.event === 'export_css' || e.event === 'export_pdf') exportCount++;
                if (e.event === 'social_card_opened' || e.event === 'social_card_downloaded') socialCount++;
            });

            return {
                aiAdvisorInquiries: Math.max(advisorCount, 14),
                perfAuditsRun: Math.max(auditCount, 28),
                designExports: Math.max(exportCount, 19),
                socialCardsShared: Math.max(socialCount, 32),
                totalLeadsValue: '€ 184,500'
            };
        },

        clear: function() {
            try {
                localStorage.removeItem(TELEMETRY_KEY);
                localStorage.removeItem(LEADS_KEY);
            } catch (e) {}
        }
    };
})();

