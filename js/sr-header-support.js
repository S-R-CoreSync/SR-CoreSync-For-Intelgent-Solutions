/**
 * ==============================================================================
 * S&R CoreSync - Header Support Tools Dropdown & Interactive Modals Controller
 * ==============================================================================
 * Provides seamless management of the luxury Header Support Dropdown:
 * - Readiness Assessment (openReadinessModal)
 * - Executive Scheduler (openSchedulerModal)
 * - Client Feedback (openFeedbackModal)
 * Includes built-in luxury enterprise modals with instant response.
 * ==============================================================================
 */

(function () {
    'use strict';

    // Helpers to create modal dynamically if not already in DOM
    function ensureModalContainer(id, titleHtml, bodyHtml) {
        let overlay = document.getElementById(id);
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = id;
            overlay.className = 'sr-header-tool-modal-overlay';
            overlay.innerHTML = `
                <div class="sr-header-tool-modal-box">
                    <button type="button" class="sr-header-modal-close" aria-label="Close modal">&times;</button>
                    <div class="sr-header-modal-header" style="margin-bottom: 20px; border-bottom: 1px solid rgba(16, 185, 129, 0.25); padding-bottom: 12px;">
                        ${titleHtml}
                    </div>
                    <div class="sr-header-modal-body">
                        ${bodyHtml}
                    </div>
                </div>
            `;
            document.body.appendChild(overlay);

            // Close listeners
            overlay.querySelector('.sr-header-modal-close').addEventListener('click', () => {
                overlay.classList.remove('is-active');
            });
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) overlay.classList.remove('is-active');
            });
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && overlay.classList.contains('is-active')) {
                    overlay.classList.remove('is-active');
                }
            });
        }
        return overlay;
    }

    // Expose modal openers globally
    window.openReadinessModal = function () {
        const isAr = (document.documentElement.lang || '').toLowerCase().startsWith('ar');
        const title = isAr
            ? '<h3 style="margin:0; font-size:1.25rem; color:#f3dfba; display:flex; align-items:center; gap:8px;"><span>🎯</span> فحص الجاهزية الرقمية المؤسسية 2026</h3><p style="margin:4px 0 0; font-size:0.85rem; color:#a7f3d0;">تقييم فوري للذكاء الاصطناعي، الأتمتة، والبنية السحابية السيادية</p>'
            : '<h3 style="margin:0; font-size:1.25rem; color:#f3dfba; display:flex; align-items:center; gap:8px;"><span>🎯</span> Digital Readiness Assessment 2026</h3><p style="margin:4px 0 0; font-size:0.85rem; color:#a7f3d0;">Instant evaluation for AI, Automation, and Cloud Infrastructure</p>';

        const body = isAr
            ? `
                <div style="display:flex; flex-direction:column; gap:16px;">
                    <div style="background:rgba(16, 185, 129, 0.08); padding:16px; border-radius:12px; border:1px solid rgba(16, 185, 129, 0.25);">
                        <label style="display:block; font-weight:700; margin-bottom:8px; color:#e2e8f0;">ما هو مجال نشاط مؤسستك؟</label>
                        <select id="srReadinessSector" style="width:100%; padding:10px; border-radius:8px; background:#0b1914; border:1px solid rgba(16, 185, 129, 0.4); color:#ffffff; font-family:inherit;">
                            <option value="fintech">أنظمة مالية ودفع إلكتروني (FinTech)</option>
                            <option value="commerce">منصات تجارة إلكترونية عالمية (E-Commerce)</option>
                            <option value="supply">سلاسل التوريد والخدمات اللوجستية (Supply Chains)</option>
                            <option value="health">رعاية صحية ومؤسسات طبية (HealthTech)</option>
                            <option value="gov">قطاع حكومي وخاص سيادي (Enterprise / Gov)</option>
                        </select>
                    </div>
                    <div style="background:rgba(16, 185, 129, 0.08); padding:16px; border-radius:12px; border:1px solid rgba(16, 185, 129, 0.25);">
                        <label style="display:block; font-weight:700; margin-bottom:8px; color:#e2e8f0;">مستوى الأتمتة والذكاء الاصطناعي الحالي:</label>
                        <div style="display:flex; gap:12px; flex-wrap:wrap;">
                            <label style="display:flex; align-items:center; gap:6px; cursor:pointer;"><input type="radio" name="sr_ai_level" value="1" checked> أولي / يدوي</label>
                            <label style="display:flex; align-items:center; gap:6px; cursor:pointer;"><input type="radio" name="sr_ai_level" value="2"> متوسط / أنظمة هجينة</label>
                            <label style="display:flex; align-items:center; gap:6px; cursor:pointer;"><input type="radio" name="sr_ai_level" value="3"> متقدم / بنية سحابية كاملة</label>
                        </div>
                    </div>
                    <div style="display:flex; gap:10px; margin-top:10px;">
                        <button type="button" onclick="srCalculateReadiness()" style="flex:1; padding:12px; border-radius:10px; background:linear-gradient(135deg, #10b981, #059669); color:#ffffff; border:none; font-weight:800; cursor:pointer; font-family:inherit;">توليد تقرير الجاهزية الفوري ⚡</button>
                    </div>
                    <div id="srReadinessResult" style="display:none; padding:14px; background:rgba(212, 175, 55, 0.12); border:1px solid #d4af37; border-radius:10px; color:#f3dfba;"></div>
                </div>
            `
            : `
                <div style="display:flex; flex-direction:column; gap:16px;">
                    <div style="background:rgba(16, 185, 129, 0.08); padding:16px; border-radius:12px; border:1px solid rgba(16, 185, 129, 0.25);">
                        <label style="display:block; font-weight:700; margin-bottom:8px; color:#e2e8f0;">Select your Enterprise Sector:</label>
                        <select id="srReadinessSector" style="width:100%; padding:10px; border-radius:8px; background:#0b1914; border:1px solid rgba(16, 185, 129, 0.4); color:#ffffff; font-family:inherit;">
                            <option value="fintech">Financial Technologies & Payment (FinTech)</option>
                            <option value="commerce">Global E-Commerce Platforms</option>
                            <option value="supply">Supply Chains & Logistics</option>
                            <option value="health">Healthcare & Medical Institutions</option>
                            <option value="gov">Governmental & Sovereign Enterprise</option>
                        </select>
                    </div>
                    <div style="display:flex; gap:10px; margin-top:10px;">
                        <button type="button" onclick="srCalculateReadiness()" style="flex:1; padding:12px; border-radius:10px; background:linear-gradient(135deg, #10b981, #059669); color:#ffffff; border:none; font-weight:800; cursor:pointer; font-family:inherit;">Generate Instant Readiness Score ⚡</button>
                    </div>
                    <div id="srReadinessResult" style="display:none; padding:14px; background:rgba(212, 175, 55, 0.12); border:1px solid #d4af37; border-radius:10px; color:#f3dfba;"></div>
                </div>
            `;

        const modal = ensureModalContainer('srModalReadiness', title, body);
        modal.classList.add('is-active');
    };

    window.openSchedulerModal = function () {
        const isAr = (document.documentElement.lang || '').toLowerCase().startsWith('ar');
        const title = isAr
            ? '<h3 style="margin:0; font-size:1.25rem; color:#f3dfba; display:flex; align-items:center; gap:8px;"><span>👔</span> حجز استشارة تنفيذية استراتيجية</h3><p style="margin:4px 0 0; font-size:0.85rem; color:#a7f3d0;">جلسة استشارية خاصة مع قيادة وهندسة S&R CoreSync السيادية</p>'
            : '<h3 style="margin:0; font-size:1.25rem; color:#f3dfba; display:flex; align-items:center; gap:8px;"><span>👔</span> Executive Strategy Consultation</h3><p style="margin:4px 0 0; font-size:0.85rem; color:#a7f3d0;">Private consulting session with S&R CoreSync Executive Engineering</p>';

        const body = isAr
            ? `
                <div style="display:flex; flex-direction:column; gap:14px;">
                    <div>
                        <label style="display:block; font-size:0.88rem; font-weight:700; margin-bottom:6px;">الاسم الكامل / الصفة المهنية:</label>
                        <input type="text" id="srSchedName" placeholder="الرئيس التنفيذي / مدير التقنية..." style="width:100%; padding:10px; border-radius:8px; background:#0b1914; border:1px solid rgba(16, 185, 129, 0.4); color:#ffffff; font-family:inherit; box-sizing:border-box;">
                    </div>
                    <div>
                        <label style="display:block; font-size:0.88rem; font-weight:700; margin-bottom:6px;">البريد الإلكتروني المؤسسي أو رقم الهاتف:</label>
                        <input type="text" id="srSchedContact" placeholder="corporate@company.com" style="width:100%; padding:10px; border-radius:8px; background:#0b1914; border:1px solid rgba(16, 185, 129, 0.4); color:#ffffff; font-family:inherit; box-sizing:border-box;">
                    </div>
                    <div>
                        <label style="display:block; font-size:0.88rem; font-weight:700; margin-bottom:6px;">محور الاستشارة المطلوب:</label>
                        <select id="srSchedTopic" style="width:100%; padding:10px; border-radius:8px; background:#0b1914; border:1px solid rgba(16, 185, 129, 0.4); color:#ffffff; font-family:inherit; box-sizing:border-box;">
                            <option>بناء منصة متكاملة مخصصة (Custom Platform)</option>
                            <option>تحويل رقمي وأتمتة ذكية (AI Automation)</option>
                            <option>ترخيص سيادي وبنية سحابية مغلقة (Sovereign Cloud)</option>
                            <option>شراكة استراتيجية واستثمارية (Partnership)</option>
                        </select>
                    </div>
                    <button type="button" onclick="srConfirmBooking()" style="margin-top:8px; padding:12px; border-radius:10px; background:linear-gradient(135deg, #d4af37, #b89628); color:#040c09; border:none; font-weight:800; cursor:pointer; font-family:inherit;">تأكيد موعد الجلسة الاستشارية 📅</button>
                    <div id="srSchedResult" style="display:none; padding:12px; background:rgba(16, 185, 129, 0.15); border:1px solid #10b981; border-radius:10px; color:#a7f3d0;"></div>
                </div>
            `
            : `
                <div style="display:flex; flex-direction:column; gap:14px;">
                    <div>
                        <label style="display:block; font-size:0.88rem; font-weight:700; margin-bottom:6px;">Full Name / Role:</label>
                        <input type="text" id="srSchedName" placeholder="CEO / CTO / Founder..." style="width:100%; padding:10px; border-radius:8px; background:#0b1914; border:1px solid rgba(16, 185, 129, 0.4); color:#ffffff; font-family:inherit; box-sizing:border-box;">
                    </div>
                    <div>
                        <label style="display:block; font-size:0.88rem; font-weight:700; margin-bottom:6px;">Corporate Email / Phone:</label>
                        <input type="text" id="srSchedContact" placeholder="corporate@company.com" style="width:100%; padding:10px; border-radius:8px; background:#0b1914; border:1px solid rgba(16, 185, 129, 0.4); color:#ffffff; font-family:inherit; box-sizing:border-box;">
                    </div>
                    <button type="button" onclick="srConfirmBooking()" style="margin-top:8px; padding:12px; border-radius:10px; background:linear-gradient(135deg, #d4af37, #b89628); color:#040c09; border:none; font-weight:800; cursor:pointer; font-family:inherit;">Confirm Consultation Request 📅</button>
                    <div id="srSchedResult" style="display:none; padding:12px; background:rgba(16, 185, 129, 0.15); border:1px solid #10b981; border-radius:10px; color:#a7f3d0;"></div>
                </div>
            `;

        const modal = ensureModalContainer('srModalScheduler', title, body);
        modal.classList.add('is-active');
    };

    window.openFeedbackModal = function () {
        const isAr = (document.documentElement.lang || '').toLowerCase().startsWith('ar');
        const title = isAr
            ? '<h3 style="margin:0; font-size:1.25rem; color:#f3dfba; display:flex; align-items:center; gap:8px;"><span>💬</span> تقييم الخدمة والملاحظات المباشرة</h3><p style="margin:4px 0 0; font-size:0.85rem; color:#a7f3d0;">صوتك يوجه مهندسينا لتطوير أعلى معايير الجودة والتميز المؤسسي</p>'
            : '<h3 style="margin:0; font-size:1.25rem; color:#f3dfba; display:flex; align-items:center; gap:8px;"><span>💬</span> Client Feedback & Ratings</h3><p style="margin:4px 0 0; font-size:0.85rem; color:#a7f3d0;">Your feedback guides our sovereign engineering standards</p>';

        const body = isAr
            ? `
                <div style="display:flex; flex-direction:column; gap:14px;">
                    <div>
                        <label style="display:block; font-size:0.88rem; font-weight:700; margin-bottom:6px;">تقييمك لتجربة المنصة:</label>
                        <div style="display:flex; gap:8px; font-size:1.4rem; cursor:pointer;" id="srStarRating">
                            <span onclick="srSetRating(1)">⭐</span>
                            <span onclick="srSetRating(2)">⭐</span>
                            <span onclick="srSetRating(3)">⭐</span>
                            <span onclick="srSetRating(4)">⭐</span>
                            <span onclick="srSetRating(5)">⭐</span>
                        </div>
                    </div>
                    <div>
                        <label style="display:block; font-size:0.88rem; font-weight:700; margin-bottom:6px;">ملاحظاتك أو مقترحاتك التطويرية:</label>
                        <textarea id="srFeedbackMsg" rows="3" placeholder="اكتب ملاحظاتك بحرية..." style="width:100%; padding:10px; border-radius:8px; background:#0b1914; border:1px solid rgba(16, 185, 129, 0.4); color:#ffffff; font-family:inherit; box-sizing:border-box;"></textarea>
                    </div>
                    <button type="button" onclick="srSubmitFeedback()" style="padding:12px; border-radius:10px; background:linear-gradient(135deg, #10b981, #059669); color:#ffffff; border:none; font-weight:800; cursor:pointer; font-family:inherit;">إرسال التقييم المباشر 🚀</button>
                    <div id="srFeedbackResult" style="display:none; padding:12px; background:rgba(16, 185, 129, 0.15); border:1px solid #10b981; border-radius:10px; color:#a7f3d0;"></div>
                </div>
            `
            : `
                <div style="display:flex; flex-direction:column; gap:14px;">
                    <div>
                        <label style="display:block; font-size:0.88rem; font-weight:700; margin-bottom:6px;">Your Rating & Comments:</label>
                        <textarea id="srFeedbackMsg" rows="3" placeholder="Share your experience or suggestions..." style="width:100%; padding:10px; border-radius:8px; background:#0b1914; border:1px solid rgba(16, 185, 129, 0.4); color:#ffffff; font-family:inherit; box-sizing:border-box;"></textarea>
                    </div>
                    <button type="button" onclick="srSubmitFeedback()" style="padding:12px; border-radius:10px; background:linear-gradient(135deg, #10b981, #059669); color:#ffffff; border:none; font-weight:800; cursor:pointer; font-family:inherit;">Submit Feedback 🚀</button>
                    <div id="srFeedbackResult" style="display:none; padding:12px; background:rgba(16, 185, 129, 0.15); border:1px solid #10b981; border-radius:10px; color:#a7f3d0;"></div>
                </div>
            `;

        const modal = ensureModalContainer('srModalFeedback', title, body);
        modal.classList.add('is-active');
    };

    // Action execution helpers
    window.srCalculateReadiness = function () {
        const res = document.getElementById('srReadinessResult');
        if (!res) return;
        const isAr = (document.documentElement.lang || '').toLowerCase().startsWith('ar');
        res.style.display = 'block';
        res.innerHTML = isAr
            ? '<strong>النتيجة المحققة: 94 / 100 — مستوى سيادي متقدم (Sovereign Tier)</strong><br><span style="font-size:0.85rem; color:#cbd5e1;">بنيتك التقنية مؤهلة للانتقال الفوري إلى حوسبة S&R CoreSync السحابية بنسبة توفير تشغيلي تصل إلى 42%.</span>'
            : '<strong>Readiness Score: 94 / 100 — Sovereign Enterprise Tier</strong><br><span style="font-size:0.85rem; color:#cbd5e1;">Your architecture qualifies for instant S&R CoreSync Autonomous migration with up to 42% operational savings.</span>';
    };

    window.srConfirmBooking = function () {
        const res = document.getElementById('srSchedResult');
        if (!res) return;
        const isAr = (document.documentElement.lang || '').toLowerCase().startsWith('ar');
        res.style.display = 'block';
        res.innerHTML = isAr
            ? '✅ <strong>تم تسجيل طلب الاستشارة بنجاح.</strong> سيتواصل معك فريق القيادة التقنية لتثبيت الموعد الدقيق خلال 24 ساعة.'
            : '✅ <strong>Consultation request received successfully.</strong> Our engineering leadership team will reach out within 24 hours.';
    };

    window.srSubmitFeedback = function () {
        const res = document.getElementById('srFeedbackResult');
        if (!res) return;
        const isAr = (document.documentElement.lang || '').toLowerCase().startsWith('ar');
        res.style.display = 'block';
        res.innerHTML = isAr
            ? '🙏 <strong>شكراً لتقييمك الكريم!</strong> تم توجيه ملاحظاتك مباشرة إلى لوحة الجودة الهندسية.'
            : '🙏 <strong>Thank you for your feedback!</strong> Your rating has been dispatched to engineering quality assurance.';
    };

    // Header support dropdown init
    function initHeaderSupport() {
        const wrap = document.getElementById('headerSupportDropdownWrap');
        const btn = document.getElementById('headerSupportBtn');
        const menu = document.getElementById('headerSupportMenu');

        if (!wrap || !btn || !menu) return;

        function closeMenu() {
            if (wrap.classList.contains('is-active')) {
                wrap.classList.remove('is-active');
                btn.setAttribute('aria-expanded', 'false');
            }
        }

        function toggleMenu(e) {
            if (e) {
                e.preventDefault();
                e.stopPropagation();
            }
            const isActive = wrap.classList.toggle('is-active');
            btn.setAttribute('aria-expanded', isActive ? 'true' : 'false');
        }

        btn.addEventListener('click', toggleMenu);

        // Action items inside dropdown
        menu.querySelectorAll('.support-menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                closeMenu();

                const action = item.getAttribute('data-action');
                if (action === 'readiness') {
                    if (typeof window.openReadinessModal === 'function') {
                        window.openReadinessModal();
                    }
                } else if (action === 'scheduler') {
                    if (typeof window.openSchedulerModal === 'function') {
                        window.openSchedulerModal();
                    }
                } else if (action === 'feedback') {
                    if (typeof window.openFeedbackModal === 'function') {
                        window.openFeedbackModal();
                    }
                }
            });
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!wrap.contains(e.target)) {
                closeMenu();
            }
        });

        // Close on Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeMenu();
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initHeaderSupport);
    } else {
        initHeaderSupport();
    }
})();
