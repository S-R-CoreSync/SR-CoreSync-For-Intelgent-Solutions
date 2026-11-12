/*
 * S&R CoreSync For Intelligent Solutions - Mission 101 - Advisor Session Binder
 * PROPRIETARY & CONFIDENTIAL INTELLECTUAL PROPERTY
 * Copyright (c) 2026 S&R CoreSync. All Rights Reserved.
 * Unauthorized copying, decompilation, redistribution, or external model training is prohibited.
 *
 * Extracted verbatim from the page's inline block (Mission 108): an external
 * script needs no CSP hash, so the published hash manifest stays shorter and
 * the engine can be cached across visits.
 */
// ربط جلسة المستشار الذكي بمحرك التدقيق تلقائياً
(function () {
    var params = new URLSearchParams(window.location.search);
    var sessionId = params.get('advisor_session');
    var stored = sessionStorage.getItem('coresync_advisor_session');
    if (!sessionId && !stored) return;

    var session = stored ? JSON.parse(stored) : { id: sessionId };
    var banner = document.createElement('div');
    banner.style.cssText = [
        'position:fixed;bottom:20px;left:20px;right:20px;max-width:600px;margin:0 auto',
        'background:linear-gradient(135deg,rgba(12,25,22,.97),rgba(16,33,28,.97))',
        'border:1px solid rgba(57,214,160,.4);border-radius:14px;padding:18px 22px',
        'display:flex;align-items:center;gap:14px;z-index:9999',
        'box-shadow:0 8px 32px rgba(0,0,0,.5);backdrop-filter:blur(12px)'
    ].join(';');

    var info = session.revenue
        ? 'مبيعات: €' + Math.round(session.revenue).toLocaleString('nl-NL') +
          ' · وفورات: €' + Math.round(session.taxSavings || 0).toLocaleString('nl-NL')
        : 'جلسة: ' + session.id;

    banner.innerHTML = [
        '<span style="font-size:1.6rem">🔗</span>',
        '<div style="flex:1">',
        '<strong style="color:#39d6a0;display:block;margin-bottom:4px">تم الربط بجلسة المستشار الذكي</strong>',
        '<span style="color:#9aa9a2;font-size:.8rem">' + info + '</span>',
        '</div>',
        '<a href="smart-business-advisor.html" style="padding:8px 14px;border:1px solid rgba(57,214,160,.4);border-radius:8px;color:#39d6a0;font-size:.78rem;white-space:nowrap">عودة للمستشار</a>',
        '<button id="close-advisor-banner" style="background:transparent;border:none;color:#9aa9a2;font-size:1.2rem;cursor:pointer;padding:4px 8px;" aria-label="إغلاق">×</button>'
    ].join('');

    document.body.appendChild(banner);
    document.getElementById('close-advisor-banner').addEventListener('click', function () {
        banner.remove();
    });
}());
