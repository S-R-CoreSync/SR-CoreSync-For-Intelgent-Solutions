/* sr-hero-fit — one viewport height that survives a monitor change.
   CSS vh alone is recalculated lazily when a window moves between screens with a
   different height or scale factor, which made the hero look different on each
   display. This keeps a live --vh unit and recalculates on every change. */
(function () {
  'use strict';
  var root = document.documentElement;
  function fit() {
    var h = (window.visualViewport ? window.visualViewport.height : window.innerHeight) || 0;
    if (h > 0) root.style.setProperty('--vh', (h * 0.01).toFixed(2) + 'px');
  }
  window.addEventListener('resize', fit, { passive: true });
  window.addEventListener('orientationchange', fit);
  if (window.visualViewport) window.visualViewport.addEventListener('resize', fit, { passive: true });
  if (typeof ResizeObserver !== 'undefined') new ResizeObserver(fit).observe(root);
  fit();
})();
