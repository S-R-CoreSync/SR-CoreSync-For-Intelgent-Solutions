/**
 * [2026-11-27] Option C — one dock.
 *
 * This module used to move the whole flag dock into the quick dock once the
 * hero scrolled away, which put seven flags next to the control icons. The
 * owner asked for a single language control instead: a globe with the current
 * flag, rendered by js/sr-quick-dock.js and opening the 29-language launchpad.
 *
 * The flag dock now simply retires while the quick dock is on screen
 * (body.sr-qdock-on, see css/sr-unified-design-system.css). This file stays as
 * a compatibility stub so older pages that still load it cannot re-merge, and
 * so any wrapper hidden by the previous version is restored on load.
 */
(function () {
  'use strict';

  var wrap = document.getElementById('appleMacosDockWrapper');
  if (wrap && wrap.style && wrap.style.getPropertyValue('display') === 'none') {
    wrap.style.removeProperty('display');
  }
  document.body.classList.remove('sr-dock-merged');
})();
