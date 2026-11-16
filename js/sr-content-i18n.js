/* S&R CoreSync — page-content translator for locale portals.

   The locale pages still carry English blocks (pricing tables, ROI simulator,
   section headings). This layer maps those exact strings to the page language.

   Data: js/sr-content-<lang>.json  ->  { "<English source>": "<localized>" }
   Loaded only when the file exists and <html lang> is not Arabic. */
(function () {
  'use strict';
  if (window.__SRContentI18n) { return; }
  window.__SRContentI18n = true;

  var LANG = (document.documentElement.getAttribute('lang') || 'ar').toLowerCase().split('-')[0];
  if (LANG === 'ar') { return; }

  var ATTRS = ['title', 'aria-label', 'placeholder', 'alt'];
  var MAP = null;
  var done = typeof WeakSet === 'function' ? new WeakSet() : null;

  function src() {
    var s = document.currentScript;
    return s && s.src ? s.src : '';
  }

  function load() {
    var self = src();
    var ver = (self.match(/[?&]v=([^&]+)/) || [])[1] || '';
    var url = self.replace(/sr-content-i18n\.js.*$/, 'sr-content-' + LANG + '.json') + (ver ? '?v=' + ver : '');
    return fetch(url, { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; });
  }

  function core(v) {
    return (v || '').replace(/[^\p{L}\p{N}\s]/gu, ' ').replace(/\s+/g, ' ').trim().toLowerCase();
  }

  var CORE = null;
  function buildCore() {
    CORE = Object.create(null);
    Object.keys(MAP).forEach(function (k) {
      var c = core(k);
      if (c && !CORE[c]) { CORE[c] = MAP[k]; }
    });
  }

  function hit(value) {
    if (!value) { return null; }
    var t = value.trim();
    if (MAP[t]) { return MAP[t]; }
    if (CORE) { var c = core(t); if (c && CORE[c]) { return CORE[c]; } }
    return null;
  }

  function textNode(n) {
    if (!n || n.nodeType !== 3 || (done && done.has(n))) { return; }
    var raw = n.nodeValue;
    if (!raw || !raw.trim()) { return; }
    var t = hit(raw);
    if (!t) { return; }
    var lead = raw.match(/^\s*/)[0], trail = raw.match(/\s*$/)[0];
    n.nodeValue = lead + t + trail;
    if (done) { done.add(n); }
  }

  function element(el) {
    if (!el || el.nodeType !== 1) { return; }
    var tag = (el.tagName || '').toLowerCase();
    if (tag === 'script' || tag === 'style') { return; }
    for (var i = 0; i < ATTRS.length; i++) {
      var v = el.getAttribute && el.getAttribute(ATTRS[i]);
      if (!v) { continue; }
      var t = hit(v);
      if (t) { el.setAttribute(ATTRS[i], t); }
    }
  }

  function walk(root) {
    if (!root) { return; }
    if (root.nodeType === 3) { textNode(root); return; }
    if (root.nodeType === 1) { element(root); }
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT, null), n;
    while ((n = w.nextNode())) {
      if (n.nodeType === 3) { textNode(n); } else { element(n); }
    }
  }

  var queued = false;
  function soon(node) {
    if (queued) { return; }
    queued = true;
    requestAnimationFrame(function () { queued = false; walk(node || document.body); });
  }

  function start() {
    load().then(function (map) {
      if (!map || !Object.keys(map).length) { ready(); return; }
      MAP = map;
      buildCore();
      walk(document.body);
      ready();
      if (window.MutationObserver) {
        new MutationObserver(function (recs) {
          for (var i = 0; i < recs.length; i++) {
            var r = recs[i];
            if (r.type === 'childList') {
              for (var j = 0; j < r.addedNodes.length; j++) {
                var a = r.addedNodes[j];
                if (a.nodeType === 1) { soon(a); } else if (a.nodeType === 3) { textNode(a); }
              }
            } else if (r.type === 'attributes' && r.target) {
              element(r.target);
            } else if (r.type === 'characterData' && r.target) {
              if (done) { done.delete(r.target); }
              textNode(r.target);
            }
          }
        }).observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ATTRS, characterData: true });
      }
      var ticks = 0;
      var iv = setInterval(function () {
        ticks++; walk(document.body);
        if (ticks > 24) { clearInterval(iv); }
      }, 500);
    });
  }

  function ready() {
    try { window.dispatchEvent(new Event('sr-i18n-ready')); } catch (e) {}
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
