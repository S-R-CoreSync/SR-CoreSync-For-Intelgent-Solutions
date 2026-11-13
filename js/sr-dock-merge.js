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
    seatTools();
    stickTools();
    setInterval(stickTools, 250);
    window.addEventListener("resize", stickTools, { passive: true });
    timer = setInterval(apply, 250);
  }

  /* the header tools live in a bottom-left capsule on desktop */
  function seatTools() {
    if (window.matchMedia && !window.matchMedia('(min-width:601px)').matches) { return; }
    var actions = document.querySelector('.header-col-actions');
    if (!actions || document.querySelector('.sr-tools-capsule')) { return; }
    var box = document.createElement('div');
    box.className = 'sr-tools-capsule';
    box.setAttribute('aria-label', 'Install and support');
    box.appendChild(actions);
    document.body.appendChild(box);
    stickTools();
  }

  /* desktop: the capsule sits at the far left edge, the mirror of the counters
     at the far right, with the dock holding the centre. When the space left of
     the dock is too tight, it steps one level up instead of crowding it. */
  function stickTools() {
    var cap = document.querySelector('.sr-tools-capsule');
    var dock = document.getElementById('appleMacosDockWrapper');
    if (!cap || !dock) { return; }
    var r = dock.getBoundingClientRect();
    if (r.height < 10) { return; }
    var box = cap.getBoundingClientRect();
    var cw = box.width || 260;
    var ch = box.height || 46;
    var edge = 22;
    var bottom = window.innerHeight - r.bottom;
    if (edge + cw + 12 > r.left) { bottom += ch + 18; }
    cap.style.setProperty('bottom', bottom + 'px', 'important');
    cap.style.setProperty('left', edge + 'px', 'important');
  }

  window.__srDock = { apply: apply, state: function () { return { past: past }; } };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
  } else {
    start();
  }
  window.addEventListener('load', start, { once: true });
})();
