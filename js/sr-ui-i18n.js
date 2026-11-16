/* S&R CoreSync — runtime translator for UI injected by the shared scripts.
   The language pages load sr-master-shell.js / sr-studio-peek.js / sr-quick-dock.js,
   which build their menus and modals from Arabic literals. This layer swaps those
   strings for the page language without touching the scripts themselves.

   Data: js/sr-ui-strings.json  ->  { "<lang>": { "<arabic>": "<translation>" } }
   Active only when <html lang> is a translated locale. */
(function () {
  'use strict';
  if (window.__SRUiI18n) { return; }
  window.__SRUiI18n = true;

  var LANG = (document.documentElement.getAttribute('lang') || 'ar').toLowerCase().split('-')[0];
  if (LANG === 'ar') { return; }

  var ATTRS = ['title', 'aria-label', 'placeholder', 'alt'];
  var MAP = null;
  var seen = typeof WeakSet === 'function' ? new WeakSet() : null;

  function selfUrl() {
    var s = document.currentScript;
    return s && s.src ? s.src : '';
  }

  function loadMap() {
    var url = selfUrl().replace(/sr-ui-i18n\.js.*$/, 'sr-ui-strings.json');
    var opts = { cache: 'no-store' };
    return fetch(url, opts).then(function (r) { return r.ok ? r.json() : {}; })
      .then(function (all) {
        if (!all) { return {}; }
        var own = all[LANG] || {};
        var en = all.en || {};
        /* page language wins; English is the interim fallback so no Arabic
           survives in a locale we have not translated yet */
        var out = Object.assign({}, en, own);
        return out;
      })
      .catch(function () { return {}; });
  }

  function core(value) {
    return (value || '')
      .replace(/[^\p{L}\p{N}\s]/gu, ' ')
      .replace(/\s+/g, ' ')
      .trim()
      .toLowerCase();
  }

  var CORE = null;

  function buildCore() {
    CORE = Object.create(null);
    Object.keys(MAP).forEach(function (k) {
      var c = core(k);
      if (c && !CORE[c]) { CORE[c] = MAP[k]; }
    });
  }

  function exact(value) {
    if (!value) { return null; }
    var t = value.trim();
    if (MAP[t]) { return MAP[t]; }
    if (CORE) {
      var c = core(t);
      if (c && CORE[c]) { return CORE[c]; }
    }
    return null;
  }

  function translateTextNode(node) {
    if (!node || node.nodeType !== 3) { return; }
    if (seen && seen.has(node)) { return; }
    var raw = node.nodeValue;
    if (!raw) { return; }
    var hit = exact(raw);
    if (!hit) { return; }
    var lead = raw.match(/^\s*/)[0];
    var trail = raw.match(/\s*$/)[0];
    node.nodeValue = lead + hit + trail;
    if (seen) { seen.add(node); }
  }

  function translateElement(el) {
    if (!el || el.nodeType !== 1) { return; }
    var tag = (el.tagName || '').toLowerCase();
    if (tag === 'script' || tag === 'style') { return; }
    for (var i = 0; i < ATTRS.length; i++) {
      var a = ATTRS[i];
      var v = el.getAttribute && el.getAttribute(a);
      if (!v) { continue; }
      var hit = exact(v);
      if (hit) { el.setAttribute(a, hit); }
    }
  }

  function walk(root) {
    if (!root) { return; }
    if (root.nodeType === 3) { translateTextNode(root); return; }
    if (root.nodeType === 1) { translateElement(root); }
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT, null);
    var n;
    while ((n = walker.nextNode())) {
      if (n.nodeType === 3) { translateTextNode(n); }
      else { translateElement(n); }
    }
    /* shadow roots and same-origin frames are rare here, but cheap to cover */
    var hosts = root.querySelectorAll ? root.querySelectorAll('*') : [];
    for (var i = 0; i < hosts.length; i++) {
      if (hosts[i].shadowRoot) { walk(hosts[i].shadowRoot); }
    }
  }

  var pending = false;
  function schedule(root) {
    if (pending) { return; }
    pending = true;
    requestAnimationFrame(function () {
      pending = false;
      walk(root || document.body);
    });
  }

  function start() {
    loadMap().then(function (map) {
      MAP = map;
      if (!MAP || !Object.keys(MAP).length) { return; }
      buildCore();
      walk(document.body);
      if (window.MutationObserver) {
        new MutationObserver(function (records) {
          for (var i = 0; i < records.length; i++) {
            var r = records[i];
            if (r.type === 'childList') {
              for (var j = 0; j < r.addedNodes.length; j++) {
                var n = r.addedNodes[j];
                if (n.nodeType === 1) { schedule(n); }
                else if (n.nodeType === 3) { translateTextNode(n); }
              }
            } else if (r.type === 'attributes' && r.target) {
              translateElement(r.target);
            }
          }
        }).observe(document.body, {
          childList: true, subtree: true, attributes: true,
          attributeFilter: ATTRS
        });
      }
      /* late paint passes (dock, launchpad, modals) */
      var ticks = 0;
      var iv = setInterval(function () {
        ticks++;
        walk(document.body);
        if (ticks > 24) { clearInterval(iv); }
      }, 500);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
