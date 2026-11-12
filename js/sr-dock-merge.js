/* ==========================================================================
   S&R CoreSync — Dock state machine (hero ⇄ structural sections)
   - Inside the hero: the language dock stands alone, low, on the left edge.
   - Past the hero:  its flag strip is MOVED into the quick dock (one capsule).
   One node travels between two parents — no clones, no duplicate ids.
   Geometry polling instead of scroll events: the page scrolls through a
   virtualised container, so window 'scroll' is not a reliable signal.
   ========================================================================== */
(function () {
  'use strict';

  var hero = document.getElementById('hero');
  var wrap = document.getElementById('appleMacosDockWrapper');
  if (!hero || !wrap) { return; }

  var inner = wrap.querySelector('.apple-macos-dock');
  if (!inner) { return; }

  var seg = null, sep = null, merged = false, timer = null;

  function quickRoot() {
    return document.querySelector('#srQuickDockContainer .sr-quick-dock');
  }

  function merge() {
    var root = quickRoot();
    if (merged || !root || !inner || !inner.isConnected) { return; }
    seg = document.createElement('span');
    seg.className = 'sr-lang-seg';
    sep = document.createElement('span');
    sep.className = 'sr-dock-sep';
    seg.appendChild(inner);
    root.insertBefore(sep, root.firstChild);
    root.insertBefore(seg, sep);
    merged = true;
    document.body.classList.add('sr-dock-merged');
    wrap.style.setProperty('display', 'none', 'important');
  }

  function unmerge() {
    if (!merged) { return; }
    if (inner) { wrap.appendChild(inner); }
    if (seg && seg.parentNode) { seg.remove(); }
    if (sep && sep.parentNode) { sep.remove(); }
    seg = sep = null;
    merged = false;
    document.body.classList.remove('sr-dock-merged');
    wrap.style.removeProperty('display');
  }

  /* "Past the hero" = its bottom has climbed above 35% of the viewport.
     Hysteresis (0.35 down / 0.55 up) stops it flickering on the boundary. */
  function pastHero() {
    var r = hero.getBoundingClientRect();
    var vh = window.innerHeight || 800;
    return r.bottom < vh * (merged ? 0.55 : 0.35);
  }

  function evaluate() {
    if (!quickRoot()) { return; }
    if (pastHero()) { merge(); } else { unmerge(); }
  }

  function start() {
    if (timer) { return; }
    evaluate();
    timer = setInterval(evaluate, 250);
  }

  window.__srDock = {
    merge: merge, unmerge: unmerge, evaluate: evaluate, start: start,
    state: function () { return { merged: merged, seg: !!seg, inner: !!inner }; }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
  } else {
    start();
  }
  window.addEventListener('load', start, { once: true });
})();
