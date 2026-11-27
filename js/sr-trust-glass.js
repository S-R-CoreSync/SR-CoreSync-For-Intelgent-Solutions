/* ============================================================================
   S&R CoreSync — interactive glass for the hero trust strip (2026-11-27)
   The strip that sits under the System-Setup bar follows the pointer: a warm
   light pools under the cursor and the surface tilts by at most ~3 degrees.
   No dependency, no layout reads on scroll, and it stands down for
   prefers-reduced-motion and touch-first devices.
   ========================================================================== */
(function () {
  'use strict';

  var stripSelector = '.c3-center-stage .section-trust-metrics .hero-trust-metrics-strip';
  var strips = document.querySelectorAll(stripSelector);
  if (!strips.length) { return; }

  var mq = window.matchMedia ? window.matchMedia.bind(window) : null;
  var reduce = mq && mq('(prefers-reduced-motion: reduce)').matches;
  var coarse = mq && mq('(pointer: coarse)').matches;
  if (reduce || coarse) { return; }

  function reset(el) {
    el.style.setProperty('--sr-rx', '0deg');
    el.style.setProperty('--sr-ry', '0deg');
    el.style.setProperty('--sr-px', '50%');
    el.style.setProperty('--sr-py', '50%');
  }

  Array.prototype.forEach.call(strips, function (el) {
    var frame = 0;
    var nx = 0;
    var ny = 0;

    function paint() {
      frame = 0;
      el.style.setProperty('--sr-rx', (-ny * 3).toFixed(2) + 'deg');
      el.style.setProperty('--sr-ry', (nx * 4).toFixed(2) + 'deg');
    }

    function onMove(event) {
      var box = el.getBoundingClientRect();
      if (!box.width || !box.height) { return; }
      nx = (event.clientX - box.left) / box.width - 0.5;
      ny = (event.clientY - box.top) / box.height - 0.5;
      el.style.setProperty('--sr-px', ((nx + 0.5) * 100).toFixed(1) + '%');
      el.style.setProperty('--sr-py', ((ny + 0.5) * 100).toFixed(1) + '%');
      if (!frame) { frame = window.requestAnimationFrame(paint); }
    }

    el.addEventListener('pointermove', onMove);
    el.addEventListener('pointerleave', function () { reset(el); });
    el.addEventListener('blur', function () { reset(el); }, true);
  });

  Array.prototype.forEach.call(strips, reset);
})();
