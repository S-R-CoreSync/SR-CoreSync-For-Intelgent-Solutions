/* S&R CoreSync - language hint.
   If the visitor's browser language differs from the page, offer the matching
   language once. Labels come from the existing switcher (its data-tooltip is
   already the endonym), so this needs no translation and adds no copy. */
(function () {
  'use strict';
  if (window.__srLangHint) return;
  window.__srLangHint = true;

  var KEY = 'sr_lang_hint_v1';
  var current = (document.documentElement.getAttribute('lang') || 'en').toLowerCase().slice(0, 2);

  function seen(code) {
    try {
      var raw = localStorage.getItem(KEY);
      if (!raw) return false;
      var data = JSON.parse(raw);
      return data[code] && (Date.now() - data[code]) < 30 * 24 * 3600 * 1000;
    } catch (e) { return false; }
  }

  function remember(code) {
    try {
      var raw = localStorage.getItem(KEY);
      var data = raw ? JSON.parse(raw) : {};
      data[code] = Date.now();
      localStorage.setItem(KEY, JSON.stringify(data));
    } catch (e) { /* private mode */ }
  }

  function switcher() {
    var map = {};
    var links = document.querySelectorAll('.apple-macos-dock a[href], a[hreflang]');
    Array.prototype.forEach.call(links, function (a) {
      var href = a.getAttribute('href') || '';
      var m = href.match(/\/?([a-z]{2})\/(?:index\.html)?$/);
      var code = (a.getAttribute('hreflang') || (m && m[1]) || '').toLowerCase();
      if (!code || code.length !== 2 || map[code]) return;
      var label = (a.getAttribute('data-tooltip') || a.getAttribute('aria-label') ||
                   a.textContent || '').replace(/\s*\([^)]*\)\s*$/, '').trim();
      if (!label || label.length > 30) return;
      map[code] = { href: href, label: label };
    });
    return map;
  }

  function build(target) {
    var wrap = document.createElement('div');
    wrap.className = 'sr-lang-hint';
    wrap.innerHTML =
      '<a class="sr-lang-hint__link" href="' + target.href + '">' +
      '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" ' +
      'stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/>' +
      '<path d="M12 3a15 15 0 010 18a15 15 0 010-18"/></svg>' +
      '<span></span></a>' +
      '<button type="button" class="sr-lang-hint__close" aria-label="×">×</button>';
    wrap.querySelector('span').textContent = target.label;
    wrap.querySelector('.sr-lang-hint__close').addEventListener('click', function () {
      remember(target.code);
      wrap.remove();
    });
    document.body.appendChild(wrap);
  }

  function start() {
    var map = switcher();
    if (!map[current]) return;
    var wanted = (navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || '']);
    for (var i = 0; i < wanted.length; i++) {
      var code = String(wanted[i] || '').toLowerCase().slice(0, 2);
      if (!code || code === current || !map[code] || seen(code)) continue;
      map[code].code = code;
      build(map[code]);
      return;
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
