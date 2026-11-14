/* S&R CoreSync - language hint, inside the dock.

   If the visitor's browser language differs from the page, the matching flag in
   the language dock gets a gold ring for six seconds. No new element, no second
   language control on screen: the hint lives where the visitor would look.

   Remembered for 30 days once shown, so it cannot become furniture. */
(function () {
  'use strict';
  if (window.__srLangHint) return;
  window.__srLangHint = true;

  var KEY = 'sr_lang_hint_v1';
  var SHOW_MS = 6000;
  var current = (document.documentElement.getAttribute('lang') || 'en').toLowerCase().slice(0, 2);
  var markers = [];

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

  function available() {
    var map = {};
    Array.prototype.forEach.call(document.querySelectorAll('a[hreflang]'), function (a) {
      var code = (a.getAttribute('hreflang') || '').toLowerCase();
      if (code.length === 2 && !map[code]) map[code] = a;
    });
    return map;
  }

  function start() {
    var map = available();
    if (!map[current]) return;

    var wanted = (navigator.languages && navigator.languages.length) ? navigator.languages : [navigator.language || ''];
    var target = null;
    for (var i = 0; i < wanted.length; i++) {
      var code = String(wanted[i] || '').toLowerCase().slice(0, 2);
      if (!code || code === current || !map[code] || seen(code)) continue;
      target = code;
      break;
    }
    if (!target) return;

    // the flag in the dock, if that language has one there
    var flag = document.querySelector('.apple-macos-dock a[hreflang="' + target + '"]') ||
               document.querySelector('.apple-macos-dock a[href*="/' + target + '/"]');

    // otherwise point at the control that opens all 29
    var marker = flag || document.querySelector('.apple-dock-launchpad-btn');
    if (!marker) return;

    marker.classList.add('sr-lang-hint-pulse');
    marker.setAttribute('title', map[target].getAttribute('data-tooltip') ||
                               map[target].getAttribute('aria-label') || target);
    markers.push(marker);
    remember(target);

    window.setTimeout(function () {
      marker.classList.remove('sr-lang-hint-pulse');
    }, SHOW_MS);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
