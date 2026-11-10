/* S&R CoreSync — structure bundle: platform tabs + AI idea guide */
/* S&R CoreSync — Sovereign platform tabs (products | white-label | lab) */
(function () {
  'use strict';
  if (window.__srPlatformTabs) return;
  window.__srPlatformTabs = true;

  var KEYS = ['store', 'wl', 'lab'];
  var TABS = { store: 'sp-tab-store', wl: 'sp-tab-wl', lab: 'sp-tab-lab' };
  var HASH = { 'software-hub': 'store', 'white-label': 'wl', 'sovereign-platform': 'store' };

  function show(key, focus) {
    if (KEYS.indexOf(key) === -1) return;
    KEYS.forEach(function (k) {
      var tab = document.getElementById(TABS[k]);
      var panel = document.getElementById('sp-panel-' + k);
      if (!tab || !panel) return;
      var active = (k === key);
      tab.classList.toggle('is-active', active);
      tab.setAttribute('aria-selected', active ? 'true' : 'false');
      tab.setAttribute('tabindex', active ? '0' : '-1');
      if (active) panel.removeAttribute('hidden');
      else panel.setAttribute('hidden', '');
    });
    /* hidden panels change layout — let measure-based scripts re-flow */
    try { window.dispatchEvent(new Event('resize')); } catch (e) {}
    if (focus) {
      var t = document.getElementById(TABS[key]);
      if (t) t.focus();
    }
  }

  document.addEventListener('click', function (e) {
    var b = e.target && e.target.closest ? e.target.closest('.sp-tab') : null;
    if (b) show(b.getAttribute('data-key'), false);
  });

  document.addEventListener('keydown', function (e) {
    var b = e.target && e.target.closest ? e.target.closest('.sp-tab') : null;
    if (!b) return;
    if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
    e.preventDefault();
    var k = b.getAttribute('data-key');
    var i = KEYS.indexOf(k);
    var dir = (e.key === 'ArrowLeft') ? -1 : 1;
    if (document.documentElement.getAttribute('dir') === 'rtl') dir = -dir;
    show(KEYS[(i + dir + KEYS.length) % KEYS.length], true);
  });

  function fromHash() {
    var h = (location.hash || '').replace('#', '');
    return HASH[h] || null;
  }
  window.addEventListener('hashchange', function () {
    var k = fromHash();
    if (k) show(k, false);
  });
  window.srPlatformTabs = { show: show };
  var initial = fromHash();
  if (initial) show(initial, false);
})();


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
