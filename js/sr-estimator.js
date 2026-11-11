/* S&R CoreSync - estimator module.
   Self-contained: it owns its state, restores it from localStorage, marks the
   active options and calculates once on load, so a page that only links this
   file works without any inline bundle.

   Every string it composes for WhatsApp comes from data-wa-* on the widget root
   (.cost-estimator-grid). The Arabic defaults keep the master page byte-for-byte
   identical while a ported language supplies its own segments. */
(function () {
  'use strict';

  var _estimatorState = {
    type: { val: 'identity', price: 590, days: '5 - 7 أيام عمل', title: 'هوية بصرية متكاملة' },
    pages: { val: 'basic', price: 0, title: 'أساسي (1 - 5 صفحات)' },
    lang: { val: 'single', price: 0, title: 'لغة واحدة أساسية' },
    pay: { val: 'none', price: 0, title: 'بدون دفع إلكتروني' },
    speed: { val: 'standard', price: 0, title: 'تسليم قياسي' }
  };

  var DEFAULT_WA = {
    title: '*طلب تقدير مشروع جديد – S&R CoreSync*',
    type: '📦 *النوع:*',
    scope: '📄 *النطاق:*',
    lang: '🌐 *اللغات:*',
    pay: '💳 *الدفع:*',
    speed: '⚡ *التسليم:*',
    total: '💰 *التقدير الإجمالي: €{v}*',
    duration: '⏱ *المدة المتوقعة: {v}*',
    days: '5 - 7 أيام عمل'
  };

  function waConfig() {
    var root = document.querySelector('.cost-estimator-grid');
    var d = (root && root.dataset) || {};
    var cfg = {};
    Object.keys(DEFAULT_WA).forEach(function (k) {
      var key = 'wa' + k.charAt(0).toUpperCase() + k.slice(1);
      cfg[k] = d[key] || DEFAULT_WA[k];
    });
    return cfg;
  }

  function updateEstimatorOption(e) {
    var t = e.dataset.group;
    if (!t || !_estimatorState[t]) return;
    e.closest('.estimator-options').querySelectorAll('.estimator-option').forEach(function (o) {
      o.classList.remove('active');
    });
    e.classList.add('active');
    _estimatorState[t].val = e.dataset.val;
    _estimatorState[t].price = parseInt(e.dataset.price) || 0;
    _estimatorState[t].title = e.dataset.title || (e.querySelector('.option-title') || {}).textContent || '';
    if (e.dataset.days) _estimatorState[t].days = e.dataset.days;
    if (typeof gtag !== 'undefined') {
      gtag('event', 'estimator_option_selected', {
        event_category: 'Estimator', event_label: t + ': ' + _estimatorState[t].title,
        value: _estimatorState[t].price
      });
    }
    if (typeof hj !== 'undefined') hj('event', 'estimator_option_selected_' + t);
    try { localStorage.setItem('sr_estimator_state', JSON.stringify(_estimatorState)); } catch (err) {}
    _recalcEstimator();
  }

  function _recalcEstimator() {
    var total = Object.values(_estimatorState).reduce(function (sum, s) { return sum + (s.price || 0); }, 0);
    var cfg = waConfig();
    var days = _estimatorState.type.days || cfg.days;

    var amount = document.getElementById('estimatorTotalAmount');
    if (amount) {
      amount.style.opacity = '0.4';
      amount.style.transform = 'scale(0.95)';
      setTimeout(function () {
        amount.textContent = total.toLocaleString('en');
        amount.style.opacity = '1';
        amount.style.transform = 'scale(1)';
      }, 180);
    }
    var timeline = document.getElementById('estimatorTimelineText');
    if (timeline) timeline.textContent = days;

    Object.entries({
      type: 'summarySpecType', pages: 'summarySpecPages', lang: 'summarySpecLang',
      pay: 'summarySpecPay', speed: 'summarySpecSpeed'
    }).forEach(function (pair) {
      var el = document.getElementById(pair[1]);
      if (el) el.textContent = _estimatorState[pair[0]].title;
    });
  }

  function bookEstimatorViaWhatsApp() {
    var cfg = waConfig();
    var total = Object.values(_estimatorState).reduce(function (sum, s) { return sum + (s.price || 0); }, 0);
    var amount = '€' + total.toLocaleString('en');
    var lines = [
      cfg.title,
      cfg.type + ' ' + _estimatorState.type.title,
      cfg.scope + ' ' + _estimatorState.pages.title,
      cfg.lang + ' ' + _estimatorState.lang.title,
      cfg.pay + ' ' + _estimatorState.pay.title,
      cfg.speed + ' ' + _estimatorState.speed.title,
      cfg.total.replace('{v}', total.toLocaleString('en')),
      cfg.duration.replace('{v}', _estimatorState.type.days || cfg.days)
    ];
    var text = lines.join('\n');
    window.open('https://wa.me/31618111116?text=' + encodeURIComponent(text), '_blank');
  }

  function transferEstimatorToVipBooking() {
    var modal = document.getElementById('executiveBookingModal');
    if (!modal) return;
    var type = document.getElementById('bookingSessionType');
    if (type) { type.value = 'creative'; if (typeof togglePackageField === 'function') togglePackageField(type); }
    var notes = document.getElementById('bookingNotes') || document.getElementById('executiveNotes');
    if (notes) {
      var total = Object.values(_estimatorState).reduce(function (sum, s) { return sum + (s.price || 0); }, 0);
      notes.value = [
        'تقدير الحاسبة التفاعلية:',
        '- النوع: ' + _estimatorState.type.title,
        '- النطاق: ' + _estimatorState.pages.title,
        '- اللغات: ' + _estimatorState.lang.title,
        '- الدفع: ' + _estimatorState.pay.title,
        '- التسليم: ' + _estimatorState.speed.title,
        '- إجمالي التقدير: €' + total.toLocaleString('en')
      ].join('\n');
    }
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  }

  function seedFromMarkup() {
    document.querySelectorAll('.estimator-option.active').forEach(function (btn) {
      var g = btn.dataset.group;
      if (!g || !_estimatorState[g]) return;
      _estimatorState[g].val = btn.dataset.val;
      _estimatorState[g].price = parseInt(btn.dataset.price) || 0;
      _estimatorState[g].title = btn.dataset.title ||
        (btn.querySelector('.option-title') || {}).textContent || _estimatorState[g].title;
      if (btn.dataset.days) _estimatorState[g].days = btn.dataset.days;
    });
  }

  function restore() {
    try {
      var saved = localStorage.getItem('sr_estimator_state');
      if (!saved) return;
      var parsed = JSON.parse(saved);
      Object.keys(parsed).forEach(function (key) {
        if (!_estimatorState[key]) return;
        _estimatorState[key] = parsed[key];
        var wrapper = document.querySelector('.estimator-options[data-group-parent="' + key + '"]');
        if (!wrapper) return;
        var btn = wrapper.querySelector('[data-val="' + parsed[key].val + '"]');
        if (!btn) return;
        wrapper.querySelectorAll('.estimator-option').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
      });
    } catch (err) {}
  }

  function init() {
    seedFromMarkup();
    restore();
    if (document.getElementById('estimatorTotalAmount')) _recalcEstimator();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.updateEstimatorOption = updateEstimatorOption;
  window.bookEstimatorViaWhatsApp = bookEstimatorViaWhatsApp;
  window.transferEstimatorToVipBooking = transferEstimatorToVipBooking;
})();
