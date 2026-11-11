/* S&R CoreSync - print guard.
   A visitor pressing Ctrl+P must get the page, not a blank sheet. The legacy
   enterprise-suite print rules hide the whole document and reveal a single
   paper; they now only bite while the body carries a print-mode class, and this
   file is what decides that per print job:
     .sr-printing-doc        a quote or ROI paper is open
     .sr-printing-blueprint  the A4 blueprint dossier is open
   Detection is layout based (getClientRects + computed style), never class
   names, so it cannot drift the day a modal learns a new open-state class. */
(function () {
  'use strict';
  if (window.__srPrintGuard) return;
  window.__srPrintGuard = true;

  var DOC_SELECTORS = [
    '.es-quote-modal',
    '.sr-exec-modal',
    '.roi-cert-modal',
    '#contractOf2026Modal',
    '#contractOf2026FinModal'
  ].join(',');
  var BLUEPRINT_SELECTOR = '#srBlueprintPreviewModal';

  function isVisible(el) {
    if (!el || !el.getClientRects().length) return false;
    var cs = window.getComputedStyle(el);
    return cs.visibility !== 'hidden' && cs.display !== 'none' && cs.opacity !== '0';
  }

  function anyVisible(selector) {
    try {
      return Array.prototype.some.call(document.querySelectorAll(selector), isVisible);
    } catch (e) {
      return false;
    }
  }

  function apply() {
    var blueprint = anyVisible(BLUEPRINT_SELECTOR);
    var doc = blueprint || anyVisible(DOC_SELECTORS);
    document.body.classList.toggle('sr-printing-blueprint', blueprint);
    document.body.classList.toggle('sr-printing-doc', doc);
    return blueprint || doc;
  }

  function clear() {
    document.body.classList.remove('sr-printing-doc', 'sr-printing-blueprint');
  }

  window.addEventListener('beforeprint', apply);
  window.addEventListener('afterprint', clear);

  /* Safari and older engines do not fire beforeprint reliably, and every print
     button in the project ends up in window.print() anyway. */
  var nativePrint = window.print;
  if (typeof nativePrint === 'function') {
    window.print = function () {
      apply();
      try {
        return nativePrint.apply(window, arguments);
      } finally {
        setTimeout(clear, 1500);
      }
    };
  }

  window.srPrintGuard = { apply: apply, clear: clear };
})();
