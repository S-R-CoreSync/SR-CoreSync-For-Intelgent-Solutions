/* S&R CoreSync — AI Idea Guide
 * After the hero AI bar analyses an idea, guide the visitor to the section
 * that answers it: when the voice-planner modal closes, smooth-scroll to the
 * matched section and pulse it once. Multilingual keyword matching; the
 * section ids are identical on every language page.
 */
(function () {
  'use strict';
  if (window.__srAiGuide) return;
  window.__srAiGuide = true;

  var TARGETS = [
    { id: 'software-hub',    kw: ['erp', 'inventory', 'warehouse', 'stock', 'invoice', 'billing', 'pos', 'محاسبة', 'فاتورة', 'مخزون', 'erp', 'buchhaltung', 'kasse'] },
    { id: 'tech-pillars',    kw: ['ai', 'agent', 'bot', 'chatbot', 'ml', 'cloud', 'hosting', 'kubernetes', 'ذكاء', 'وكيل', 'سحاب', 'سحابة', 'künstliche', 'intelligenz', 'ki ', 'nube'] },
    { id: 'tech-pillars',    kw: ['fintech', 'payment', 'tax', 'btw', 'vat', 'iban', 'sepa', 'ideal', 'ضريبة', 'دفع', 'مالية', 'steuer', 'paiement'] },
    { id: 'compliance',      kw: ['security', 'gdpr', 'iso', 'encryption', 'audit', 'أمن', 'سيبراني', 'حماية', 'امتثال', 'sicherheit', 'sécurité'] },
    { id: 'pricing',         kw: ['price', 'pricing', 'cost', 'budget', 'quote', 'package', 'سعر', 'أسعار', 'تكلفة', 'ميزانية', 'باقة', 'preis', 'prix', 'precio'] },
    { id: 'roi-calculator',  kw: ['roi', 'saving', 'savings', 'efficiency', 'توفير', 'كفاءة', 'عائد', 'rendement'] },
    { id: 'testimonials',    kw: ['portfolio', 'case', 'previous work', 'أعمال', 'سابقة', 'نموذج', 'مرجع'] },
    { id: 'contact',         kw: ['consult', 'meeting', 'call', 'talk', 'استشارة', 'اجتماع', 'تواصل', 'اتصال', 'kontakt', 'rendez-vous'] },
    { id: 'services',        kw: ['website', 'web', 'site', 'store', 'shop', 'e-commerce', 'ecommerce', 'brand', 'logo', 'موقع', 'ويب', 'متجر', 'هوية', 'شعار', 'webdesign', 'boutique', 'tienda'] }
  ];

  function pick(idea) {
    var text = ' ' + String(idea || '').toLowerCase() + ' ';
    var best = null, bestScore = 0;
    for (var i = 0; i < TARGETS.length; i++) {
      var t = TARGETS[i], score = 0;
      for (var j = 0; j < t.kw.length; j++) {
        var k = t.kw[j].toLowerCase();
        if (k && text.indexOf(k) !== -1) score++;
      }
      if (score > bestScore) { bestScore = score; best = t.id; }
    }
    return best || 'services';
  }

  var pending = null;

  function reveal(id) {
    var el = document.getElementById(id);
    if (!el) return;
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    try {
      el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    } catch (e) {
      try { el.scrollIntoView(); } catch (e2) {}
    }
    el.classList.remove('ai-guide-pulse');
    void el.offsetWidth; /* restart the animation */
    el.classList.add('ai-guide-pulse');
    window.setTimeout(function () { el.classList.remove('ai-guide-pulse'); }, 2800);
  }

  function watchModal() {
    var modal = document.getElementById('aiVoicePlannerModal');
    if (!modal) return;
    var observer = new MutationObserver(function () {
      if (!modal.classList.contains('active') && pending) {
        observer.disconnect();
        var t = pending; pending = null;
        window.setTimeout(function () { reveal(t); }, 350);
      }
    });
    observer.observe(modal, { attributes: true, attributeFilter: ['class'] });
  }

  document.addEventListener('sr:ai-idea-submitted', function (e) {
    try {
      pending = pick(e && e.detail && e.detail.idea);
      watchModal();
      /* safety: if the modal never opened/closed, clear the pending target */
      window.setTimeout(function () { pending = null; }, 30000);
    } catch (err) { /* guide is best-effort only */ }
  });
})();
