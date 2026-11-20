/* Loads the language map the first time someone asks for it.

   sr-lang-map.js is 142 KB (51 KB compressed) and builds a 34-market map that
   nobody sees until they click. It used to be downloaded on every visit. This
   listens for the same triggers, then fetches it once and opens it.

   No markup, no styles: the page is identical until the click. */
(function () {
  'use strict';
  if (window.__srLangMapLazy) { return; }
  window.__srLangMapLazy = true;

  // resolve the real file from this script's own address, so the same loader
  // works at / and at /de/ without a hard-coded relative path
  var self = document.currentScript ? document.currentScript.src : '';
  var target = self ? self.replace(/sr-lang-map-lazy\.js.*$/, 'sr-lang-map.js?v=20261120-hud2')
                    : 'js/sr-lang-map.js?v=20261120-hud2';

  var SEL = '[aria-label*="Languages"], [aria-label*="اللغات"], #srLangMenuBtn, ' +
            '#appleDockLaunchpadBtn, .sr-lang-menu-trigger, .hv2__flag.more, ' +
            '.header-language summary, [href="#languages"]';
  var state = 'idle';

  function load(done) {
    if (window.SRLangMap) { done(); return; }
    var s = document.createElement('script');
    s.src = target;
    s.async = true;
    s.onload = done;
    s.onerror = function () { state = 'idle'; };
    document.head.appendChild(s);
  }

  document.addEventListener('click', function (e) {
    var el = e.target && e.target.closest ? e.target.closest(SEL) : null;
    if (!el) { return; }
    // once the map is loaded its own listener owns the click
    if (window.SRLangMap) { return; }
    e.preventDefault();
    e.stopPropagation();
    if (state === 'loading') { return; }
    state = 'loading';
    load(function () {
      state = 'ready';
      if (window.SRLangMap && window.SRLangMap.open) { window.SRLangMap.open(); }
    });
  }, true);

  // Sovereign Global Hotkeys: M or L opens map from anywhere
  document.addEventListener('keydown', function (e) {
    if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable)) {
      return;
    }
    var key = (e.key || '').toLowerCase();
    if (key === 'm' || key === 'l') {
      if (window.SRLangMap && window.SRLangMap.open) {
        if (window.SRLangMap.isOpen && window.SRLangMap.isOpen()) {
          window.SRLangMap.close();
        } else {
          window.SRLangMap.open();
        }
        e.preventDefault();
        return;
      }
      e.preventDefault();
      if (state === 'loading') { return; }
      state = 'loading';
      load(function () {
        state = 'ready';
        if (window.SRLangMap && window.SRLangMap.open) { window.SRLangMap.open(); }
      });
    }
  });
})();
