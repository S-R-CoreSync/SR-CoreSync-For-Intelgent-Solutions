/* ==========================================================================
   S&R CoreSync — Dock visibility (no merging)
   - Inside the hero: the language dock is shown.
   - Past the hero:    the language dock hides, and the quick dock appears
                       on its own. The two are never combined.
   ========================================================================== */
(function () {
  'use strict';

  var hero = document.getElementById('hero');
  if (!hero) { return; }

  var past = false, timer = null;

  function isPast() {
    var r = hero.getBoundingClientRect();
    var vh = window.innerHeight || 800;
    return r.bottom < vh * (past ? 0.55 : 0.35);
  }

  function apply() {
    var p = isPast();
    if (p === past) { return; }
    past = p;
    document.body.classList.toggle('sr-past-hero', p);
  }

  function start() {
    if (timer) { return; }
    apply();
    // Do not move .header-col-actions to bottom capsule; keep it in the top header bar at far left
    timer = setInterval(apply, 250);
  }

  /* Disabled: .header-col-actions stays in the top header bar per user requirement */
  function seatTools() {
    return;
  }

  function stickTools() {
    return;
  }

  window.__srDock = { apply: apply, state: function () { return { past: past }; } };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
  } else {
    start();
  }
  window.addEventListener('load', start, { once: true });
})();
/* Arabic portal: western digits inside Arabic prose read as foreign numerals.
   Loaded from here as well as from index.html so the layer survives any stale
   CDN copy of the home page. */
(function () {
  if ((document.documentElement.getAttribute('lang') || '').toLowerCase().indexOf('ar') !== 0) { return; }
  if (document.querySelector('script[src*="sr-ar-numerals"]')) { return; }
  var s = document.createElement('script');
  s.src = 'js/sr-ar-numerals.js?v=20261120b';
  s.defer = true;
  (document.head || document.documentElement).appendChild(s);
})();
