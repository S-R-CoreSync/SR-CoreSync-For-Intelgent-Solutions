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
    timer = setInterval(apply, 250);
  }

  window.__srDock = { apply: apply, state: function () { return { past: past }; } };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
  } else {
    start();
  }
  window.addEventListener('load', start, { once: true });
})();
