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
