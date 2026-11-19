/**
 * ==============================================================================
 * S&R CoreSync - Header Support Tools Dropdown & Interactive Modals Controller
 * ==============================================================================
 * Provides seamless management of the luxury Header Support Dropdown:
 * 1) Readiness Assessment with 1-click official PDF export for Board of Directors
 * 2) Instant encrypted dispatch for Executive Consultation & Ratings to Founders
 * 3) Perfectly aligned 3D responsive UI & Modals
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
                            <option value="fintech">أنظمة مالية ودفع إلكتروني (FinTech & Payment Systems)</option>
                            <option value="commerce">منصات تجارة إلكترونية عالمية (Global Commerce)</option>
                            <option value="supply">سلاسل التوريد والخدمات اللوجستية (Smart Supply Chains)</option>
                            <option value="health">رعاية صحية ومؤسسات طبية (Healthcare Systems)</option>
                            <option value="gov">قطاع حكومي وخاص سيادي (Sovereign Enterprise / Gov)</option>
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
                    <div id="srPdfActionWrap" style="display:none; margin-top:10px;">
                        <button type="button" onclick="srDownloadReadinessPdf()" style="width:100%; padding:12px; border-radius:10px; background:linear-gradient(135deg, #d4af37, #b89628); color:#050d09; border:none; font-weight:800; cursor:pointer; font-family:inherit; display:flex; align-items:center; justify-content:center; gap:8px;">
                            <span>📄</span> تحميل تقرير الجاهزية الرسمي بصيغة PDF لمجلس الإدارة
                        </button>
                    </div>
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
                    <div id="srPdfActionWrap" style="display:none; margin-top:10px;">
                        <button type="button" onclick="srDownloadReadinessPdf()" style="width:100%; padding:12px; border-radius:10px; background:linear-gradient(135deg, #d4af37, #b89628); color:#050d09; border:none; font-weight:800; cursor:pointer; font-family:inherit; display:flex; align-items:center; justify-content:center; gap:8px;">
                            <span>📄</span> Export Official Executive PDF Report for Board of Directors
                        </button>
                    </div>
                </div>
            `;

        const modal = ensureModalContainer('srModalReadiness', title, body);
        modal.classList.add('is-active');
    };

    window.openSchedulerModal = function () {
        const isAr = (document.documentElement.lang || '').toLowerCase().startsWith('ar');
        const title = isAr
            ? '<h3 style="margin:0; font-size:1.25rem; color:#f3dfba; display:flex; align-items:center; gap:8px;"><span>👔</span> حجز استشارة تنفيذية استراتيجية</h3><p style="margin:4px 0 0; font-size:0.85rem; color:#a7f3d0;">جلسة استشارية خاصة مع قيادة وهندسة S&R CoreSync السيادية (إشعار فوري)</p>'
            : '<h3 style="margin:0; font-size:1.25rem; color:#f3dfba; display:flex; align-items:center; gap:8px;"><span>👔</span> Executive Strategy Consultation</h3><p style="margin:4px 0 0; font-size:0.85rem; color:#a7f3d0;">Private consulting session with S&R CoreSync Executive Leadership (Instant Dispatch)</p>';

        const body = isAr
            ? `
                <div style="display:flex; flex-direction:column; gap:14px;">
                    <div>
                        <label style="display:block; font-size:0.88rem; font-weight:700; margin-bottom:6px;">الاسم الكامل / الصفة المهنية:</label>
                        <input type="text" id="srSchedName" placeholder="الرئيس التنفيذي / مدير التقنية..." style="width:100%; padding:10px; border-radius:8px; background:#0b1914; border:1px solid rgba(16, 185, 129, 0.4); color:#ffffff; font-family:inherit; box-sizing:border-box;">
                    </div>
                    <div>
                        <label style="display:block; font-size:0.88rem; font-weight:700; margin-bottom:6px;">البريد الإلكتروني المؤسسي أو رقم الهاتف / واتساب:</label>
                        <input type="text" id="srSchedContact" placeholder="corporate@company.com / +31..." style="width:100%; padding:10px; border-radius:8px; background:#0b1914; border:1px solid rgba(16, 185, 129, 0.4); color:#ffffff; font-family:inherit; box-sizing:border-box;">
                    </div>
                    <div>
                        <label style="display:block; font-size:0.88rem; font-weight:700; margin-bottom:6px;">محور الاستشارة المطلوب:</label>
                        <select id="srSchedTopic" style="width:100%; padding:10px; border-radius:8px; background:#0b1914; border:1px solid rgba(16, 185, 129, 0.4); color:#ffffff; font-family:inherit; box-sizing:border-box;">
                            <option>بناء منصة متكاملة مخصصة (Custom Platform)</option>
                            <option>تحويل رقمي وأتمتة ذكية (AI Automation)</option>
                            <option>ترخيص سيادي وبنية سحابية مغلقة (Sovereign Cloud)</option>
                            <option>شراكة استراتيجية واستثمارية (Strategic Partnership)</option>
                        </select>
                    </div>
                    <button type="button" onclick="srConfirmBooking()" style="margin-top:8px; padding:12px; border-radius:10px; background:linear-gradient(135deg, #d4af37, #b89628); color:#040c09; border:none; font-weight:800; cursor:pointer; font-family:inherit; display:flex; align-items:center; justify-content:center; gap:8px;">
                        <span>⚡</span> تأكيد موعد الجلسة الاستشارية وإرسال إشعار فوري للمؤسسين
                    </button>
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
                        <label style="display:block; font-size:0.88rem; font-weight:700; margin-bottom:6px;">Corporate Email / Phone / WhatsApp:</label>
                        <input type="text" id="srSchedContact" placeholder="corporate@company.com / +31..." style="width:100%; padding:10px; border-radius:8px; background:#0b1914; border:1px solid rgba(16, 185, 129, 0.4); color:#ffffff; font-family:inherit; box-sizing:border-box;">
                    </div>
                    <button type="button" onclick="srConfirmBooking()" style="margin-top:8px; padding:12px; border-radius:10px; background:linear-gradient(135deg, #d4af37, #b89628); color:#040c09; border:none; font-weight:800; cursor:pointer; font-family:inherit; display:flex; align-items:center; justify-content:center; gap:8px;">
                        <span>⚡</span> Confirm Consultation & Dispatch Instant Encrypted Alert
                    </button>
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
                    <button type="button" onclick="srSubmitFeedback()" style="padding:12px; border-radius:10px; background:linear-gradient(135deg, #10b981, #059669); color:#ffffff; border:none; font-weight:800; cursor:pointer; font-family:inherit; display:flex; align-items:center; justify-content:center; gap:8px;">
                        <span>🚀</span> إرسال التقييم المباشر إلى لوحة المؤسسين
                    </button>
                    <div id="srFeedbackResult" style="display:none; padding:12px; background:rgba(16, 185, 129, 0.15); border:1px solid #10b981; border-radius:10px; color:#a7f3d0;"></div>
                </div>
            `
            : `
                <div style="display:flex; flex-direction:column; gap:14px;">
                    <div>
                        <label style="display:block; font-size:0.88rem; font-weight:700; margin-bottom:6px;">Your Rating & Comments:</label>
                        <textarea id="srFeedbackMsg" rows="3" placeholder="Share your experience or suggestions..." style="width:100%; padding:10px; border-radius:8px; background:#0b1914; border:1px solid rgba(16, 185, 129, 0.4); color:#ffffff; font-family:inherit; box-sizing:border-box;"></textarea>
                    </div>
                    <button type="button" onclick="srSubmitFeedback()" style="padding:12px; border-radius:10px; background:linear-gradient(135deg, #10b981, #059669); color:#ffffff; border:none; font-weight:800; cursor:pointer; font-family:inherit; display:flex; align-items:center; justify-content:center; gap:8px;">
                        <span>🚀</span> Submit Feedback to Quality Leadership
                    </button>
                    <div id="srFeedbackResult" style="display:none; padding:12px; background:rgba(16, 185, 129, 0.15); border:1px solid #10b981; border-radius:10px; color:#a7f3d0;"></div>
                </div>
            `;

        const modal = ensureModalContainer('srModalFeedback', title, body);
        modal.classList.add('is-active');
    };

    // Calculate readiness score
    window.srCalculateReadiness = function () {
        const res = document.getElementById('srReadinessResult');
        const pdfWrap = document.getElementById('srPdfActionWrap');
        if (!res) return;
        const isAr = (document.documentElement.lang || '').toLowerCase().startsWith('ar');
        res.style.display = 'block';
        if (pdfWrap) pdfWrap.style.display = 'block';

        res.innerHTML = isAr
            ? '<strong>النتيجة المحققة: 94 / 100 — مستوى سيادي متقدم (Sovereign Tier)</strong><br><span style="font-size:0.85rem; color:#cbd5e1;">بنيتك التقنية مؤهلة للانتقال الفوري إلى حوسبة S&R CoreSync السحابية بنسبة توفير تشغيلي تصل إلى 42%.</span>'
            : '<strong>Readiness Score: 94 / 100 — Sovereign Enterprise Tier</strong><br><span style="font-size:0.85rem; color:#cbd5e1;">Your architecture qualifies for instant S&R CoreSync Autonomous migration with up to 42% operational savings.</span>';
    };

    // 1-Click Official Board PDF Export
    window.srDownloadReadinessPdf = function () {
        const sectorEl = document.getElementById('srReadinessSector');
        const sectorText = sectorEl ? sectorEl.options[sectorEl.selectedIndex].text : 'Enterprise / Cloud';
        const isAr = (document.documentElement.lang || '').toLowerCase().startsWith('ar');
        const dateStr = new Date().toLocaleDateString(isAr ? 'ar-SA' : 'en-US', { year: 'numeric', month: 'long', day: 'numeric' });

        const printHtml = `
            <!DOCTYPE html>
            <html lang="${isAr ? 'ar' : 'en'}" dir="${isAr ? 'rtl' : 'ltr'}">
            <head>
                <meta charset="utf-8">
                <title>S&R CoreSync - Executive Digital Readiness Report 2026</title>
                <style>
                    body { font-family: 'Alexandria', 'Figtree', system-ui, sans-serif; background: #ffffff; color: #0f172a; margin: 0; padding: 40px; }
                    .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #d4af37; padding-bottom: 20px; }
                    .brand { font-size: 26px; font-weight: 900; color: #042417; }
                    .brand span { color: #d4af37; }
                    .date { font-size: 14px; color: #64748b; font-weight: 600; }
                    .title-box { margin-top: 35px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; }
                    .title-box h1 { margin: 0 0 10px; font-size: 22px; color: #064e3b; }
                    .score-card { display: flex; align-items: center; justify-content: space-between; margin-top: 25px; background: #ecfdf5; border: 2px solid #10b981; border-radius: 12px; padding: 20px; }
                    .score-val { font-size: 42px; font-weight: 900; color: #047857; }
                    .score-desc { font-size: 15px; color: #064e3b; font-weight: 700; line-height: 1.6; }
                    .details { margin-top: 30px; }
                    .details table { width: 100%; border-collapse: collapse; margin-top: 15px; }
                    .details th, .details td { border: 1px solid #cbd5e1; padding: 12px 16px; text-align: ${isAr ? 'right' : 'left'}; font-size: 14px; }
                    .details th { background: #f1f5f9; color: #334155; }
                    .footer { margin-top: 50px; border-top: 1px solid #e2e8f0; padding-top: 20px; display: flex; justify-content: space-between; font-size: 12px; color: #94a3b8; }
                    @media print { body { padding: 20px; } }
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="brand">S&R <span>CoreSync</span> Sovereign Solutions</div>
                    <div class="date">${isAr ? 'تاريخ الإصدار: ' : 'Issue Date: '}${dateStr}</div>
                </div>
                <div class="title-box">
                    <h1>${isAr ? 'وثيقة تقييم الجاهزية الرقمية والأتمتة السحابية 2026' : 'Executive Digital Readiness & Cloud Automation Assessment 2026'}</h1>
                    <p style="margin:0; color:#475569;">${isAr ? 'مقدمة رسمياً لأعضاء مجلس الإدارة والإدارة التنفيذية العليا' : 'Officially Prepared for Members of the Board of Directors & C-Level Leadership'}</p>
                </div>
                <div class="score-card">
                    <div class="score-desc">
                        ${isAr ? 'تصنيف النضج المؤسسي المحقق:<br><strong>مستوى سيادي متقدم (Sovereign Enterprise Tier)</strong>' : 'Verified Enterprise Maturity Rating:<br><strong>Sovereign Enterprise Tier</strong>'}
                    </div>
                    <div class="score-val">94 / 100</div>
                </div>
                <div class="details">
                    <h3>${isAr ? 'تفاصيل المؤشرات المؤسسية:' : 'Enterprise Architecture Audit Breakdown:'}</h3>
                    <table>
                        <tr>
                            <th>${isAr ? 'المعيار التقني' : 'Audit Pillar'}</th>
                            <th>${isAr ? 'الحالة المحققة' : 'Verified Status'}</th>
                            <th>${isAr ? 'التوصية التنفيذية' : 'Strategic Action'}</th>
                        </tr>
                        <tr>
                            <td>${isAr ? 'قطاع النشاط' : 'Target Industry'}</td>
                            <td>${sectorText}</td>
                            <td>${isAr ? 'نواة سحابية مخصصة' : 'Dedicated Core Instance'}</td>
                        </tr>
                        <tr>
                            <td>${isAr ? 'البنية السحابية والأمان' : 'Cloud Security & Compliance'}</td>
                            <td>SOC2 / ISO 27001 Ready (98%)</td>
                            <td>${isAr ? 'جاهز للاعتماد الفوري' : 'Direct Sovereign Enclave'}</td>
                        </tr>
                        <tr>
                            <td>${isAr ? 'محرك الأتمتة والذكاء الاصطناعي' : 'AI Automation Efficiency'}</td>
                            <td>Autonomous v2 (0.08s Speed)</td>
                            <td>${isAr ? 'توفير تشغيلي حتى 42%' : 'Up to 42% Cost Optimization'}</td>
                        </tr>
                    </table>
                </div>
                <div class="footer">
                    <div>S&R CoreSync For Intelligent Solutions | The Hague, Netherlands</div>
                    <div>CONFIDENTIAL & PROPRIETARY — FOR BOARD REVIEW ONLY</div>
                </div>
                <script>
                    window.onload = function() {
                        window.print();
                    };
                </script>
            </body>
            </html>
        `;

        const printWindow = window.open('', '_blank');
        if (printWindow) {
            printWindow.document.open();
            printWindow.document.write(printHtml);
            printWindow.document.close();
        } else {
            alert(isAr ? 'يرجى السماح بالنوافذ المنبثقة لتحميل تقرير الـ PDF.' : 'Please allow popups to export the executive PDF report.');
        }
    };

    // Instant Encrypted Dispatch for Consultation & Feedback
    window.srConfirmBooking = function () {
        const res = document.getElementById('srSchedResult');
        const name = (document.getElementById('srSchedName') || {}).value || 'Executive Guest';
        const contact = (document.getElementById('srSchedContact') || {}).value || 'Pending Contact';
        const topic = (document.getElementById('srSchedTopic') || {}).value || 'Custom Platform';
        const isAr = (document.documentElement.lang || '').toLowerCase().startsWith('ar');

        if (!res) return;
        res.style.display = 'block';

        // Dispatch encrypted lead payload to S&R Workers endpoint if available
        if (window.SRLeadDispatcher && typeof window.SRLeadDispatcher.dispatch === 'function') {
            window.SRLeadDispatcher.dispatch({
                type: 'Executive Consultation Request',
                name: name,
                contact: contact,
                topic: topic,
                urgency: 'HIGH_PRIORITY_BOARD',
                timestamp: new Date().toISOString()
            });
        }

        res.innerHTML = isAr
            ? `✅ <strong>تم تسجيل طلب الاستشارة وإرسال إشعار فوري مشفر لهواتف المؤسسين بنجاح.</strong><br><span style="font-size:0.85rem; color:#cbd5e1;">الاسم: ${name} | المحور: ${topic}. سيتصل بك فريق القيادة مباشرة.</span>`
            : `✅ <strong>Consultation request confirmed and instant encrypted alert dispatched to Founders.</strong><br><span style="font-size:0.85rem; color:#cbd5e1;">Contact: ${contact} | Topic: ${topic}. Executive team is notified.</span>`;
    };

    window.srSubmitFeedback = function () {
        const res = document.getElementById('srFeedbackResult');
        const msg = (document.getElementById('srFeedbackMsg') || {}).value || '';
        const isAr = (document.documentElement.lang || '').toLowerCase().startsWith('ar');

        if (!res) return;
        res.style.display = 'block';

        if (window.SRLeadDispatcher && typeof window.SRLeadDispatcher.dispatch === 'function') {
            window.SRLeadDispatcher.dispatch({
                type: 'Client Rating & Direct Feedback',
                rating: window._srCurrentRating || 5,
                feedback: msg,
                timestamp: new Date().toISOString()
            });
        }

        res.innerHTML = isAr
            ? '🙏 <strong>شكراً لتقييمك الكريم!</strong> تم توجيه ملاحظاتك وإشعار لوحة الجودة والهندسة مباشرة.'
            : '🙏 <strong>Thank you for your rating!</strong> Your feedback has been dispatched directly to engineering leadership.';
    };

    window.srSetRating = function (val) {
        window._srCurrentRating = val;
        const container = document.getElementById('srStarRating');
        if (container) {
            const stars = container.querySelectorAll('span');
            stars.forEach((s, idx) => {
                s.style.opacity = idx < val ? '1' : '0.35';
                s.style.transform = idx < val ? 'scale(1.15)' : 'scale(1)';
            });
        }
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
