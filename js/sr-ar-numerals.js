/* S&R CoreSync — Arabic-Indic numerals for the Arabic portal.

   The Arabic master page renders Western (ASCII) digits inside Arabic prose,
   which reads as foreign numerals. This layer rewrites *quantities* (prices,
   counts, percentages, years) to ٠١٢٣٤٥٦٧٨٩ while leaving identifiers alone:
   standard names (ISO 27001, SOC 2, NIS2, AES-256, PSL 2.1), versions (v2.4),
   units glued to digits (30s, 16MB), phone numbers, e-mail, URLs, KVK/BTW codes.
   Inputs, selects, scripts and code are never touched.

   Opt out per element with data-no-arabic-digits. */
(function () {
  'use strict';
  if (window.__SRArabicNumerals) { return; }
  window.__SRArabicNumerals = true;

  var LANG = (document.documentElement.getAttribute('lang') || '').toLowerCase();
  if (LANG.indexOf('ar') !== 0) { return; }

  var D = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
  var SKIP_TAGS = /^(script|style|code|pre|kbd|samp|input|textarea|select|option|svg|math)$/i;
  var SKIP_CLASS = /(^|\s)(phone|tel|whatsapp|kvk|btw|vat|iban|version|sku|isbn|latency|id)(\s|$)/i;
  var SKIP_TEXT = /(@|https?:\/\/|www\.|\bKVK\b|\bBTW\b|IBAN|\bNL\d{9}B\d{2}\b|\+\d[\d\s()\-]{6,})/;
  var ACRONYM = /^[A-Z][A-Z0-9&.\-]{1,9}$/;
  var done = new WeakSet();
  var queued = false;

  function blocked(el) {
    if (!el || el.nodeType !== 1) { return false; }
    if (SKIP_TAGS.test(el.tagName || '')) { return true; }
    if (el.hasAttribute && el.hasAttribute('data-no-arabic-digits')) { return true; }
    if (el.closest && el.closest('a[href^="tel:"], a[href^="mailto:"], [data-no-arabic-digits]')) { return true; }
    var cls = (el.className && el.className.toString) ? el.className.toString() : '';
    return !!(cls && SKIP_CLASS.test(cls));
  }

  /* Convert one numeric run when it is a real quantity. */
  function quantity(before, token, after) {
    var pb = before.slice(-1), pa = after.slice(0, 1);
    if (pb && /[A-Za-z0-9_]/.test(pb)) { return false; }   // NIS2, v2.4, ISO27001
    if (pa && /[A-Za-z0-9_]/.test(pa)) { return false; }   // 30s, 16MB, 2x
    var digits = token.replace(/[^0-9]/g, '');
    if (digits.length >= 7) { return false; }              // ids, account numbers
    var prev = (before.match(/([A-Za-z][A-Za-z0-9&.\-]*)\s*$/) || [])[1];
    if (prev && ACRONYM.test(prev)) { return false; }      // ISO 27001, SOC 2, UBL 2.1
    return true;
  }

  function convert(raw) {
    if (!raw || !/[0-9]/.test(raw)) { return null; }
    var core = raw;
    if (SKIP_TEXT.test(core)) { return null; }
    var out = core.replace(/[0-9][0-9.,]*/g, function (token, offset, whole) {
      var before = whole.slice(0, offset);
      var after = whole.slice(offset + token.length);
      if (!quantity(before, token, after)) { return token; }
      return token.replace(/[0-9]/g, function (d) { return D[+d]; })
                  .replace(/,/g, '٬')
                  .replace(/\./g, '٫');
    });
    return out === core ? null : out;
  }

  function node(n) {
    if (!n || n.nodeType !== 3 || done.has(n)) { return; }
    if (!n.parentNode || blocked(n.parentNode)) { return; }
    var v = convert(n.nodeValue);
    if (v === null) { return; }
    n.nodeValue = v;
    done.add(n);
  }

  function walk(root) {
    if (!root) { return; }
    if (root.nodeType === 3) { node(root); return; }
    if (root.nodeType === 1 && SKIP_TAGS.test(root.tagName || '')) { return; }
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null), n;
    while ((n = w.nextNode())) { node(n); }
  }

  function soon(n) {
    if (queued) { return; }
    queued = true;
    requestAnimationFrame(function () { queued = false; walk(n || document.body); });
  }

  function start() {
    walk(document.body);
    if (window.MutationObserver) {
      new MutationObserver(function (recs) {
        for (var i = 0; i < recs.length; i++) {
          var r = recs[i];
          if (r.type === 'childList') {
            for (var j = 0; j < r.addedNodes.length; j++) {
              var a = r.addedNodes[j];
              if (a.nodeType === 1) { soon(a); } else { node(a); }
            }
          } else if (r.type === 'characterData') {
            if (r.target && r.target.nodeValue) { done.delete(r.target); node(r.target); }
          }
        }
      }).observe(document.body, { childList: true, subtree: true, characterData: true });
    }
    var ticks = 0;
    var iv = setInterval(function () {
      ticks++; walk(document.body);
      if (ticks > 20) { clearInterval(iv); }
    }, 500);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
