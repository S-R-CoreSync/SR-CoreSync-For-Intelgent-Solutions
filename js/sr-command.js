/* S&R CoreSync - command palette (Ctrl/Cmd+K).
   Index is read from the rendered page: [data-sr-decision-bar] links for the
   sections and header/footer anchors for the rest, so every label is already
   in the reader's language. No network, no dependencies, ~3 KB. */
(function () {
  'use strict';
  if (window.__srCommand) return;
  window.__srCommand = true;

  var LABEL = { open: 'Ctrl+K', hint: '' };
  var box = null, input = null, list = null, items = [], active = 0;

  function collect() {
    var out = [], seen = {};
    function add(label, href, group) {
      label = (label || '').replace(/\s+/g, ' ').trim();
      if (!label || !href || seen[href]) return;
      if (href.charAt(0) === '#') {
        if (!document.getElementById(href.slice(1))) return;
      }
      seen[href] = 1;
      out.push({ label: label, href: href, group: group });
    }
    var strip = document.querySelector('[data-sr-decision-bar]');
    if (strip) {
      Array.prototype.forEach.call(strip.querySelectorAll('a[href^="#"]'), function (a) {
        add(a.textContent, a.getAttribute('href'), 'section');
      });
    }
    Array.prototype.forEach.call(document.querySelectorAll('header a[href], footer a[href], .sr-jump a[href]'), function (a) {
      var href = a.getAttribute('href');
      if (!href || href === '#' || href.indexOf('javascript:') === 0) return;
      add(a.textContent, href, 'page');
    });
    return out;
  }

  function render(query) {
    var q = (query || '').toLowerCase();
    var shown = items.filter(function (it) {
      return !q || it.label.toLowerCase().indexOf(q) !== -1 || it.href.toLowerCase().indexOf(q) !== -1;
    }).slice(0, 12);
    active = 0;
    list.innerHTML = '';
    if (!shown.length) {
      var empty = document.createElement('li');
      empty.className = 'sr-cmd__empty';
      empty.textContent = '—';
      list.appendChild(empty);
      return;
    }
    shown.forEach(function (it, i) {
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = it.href;
      a.textContent = it.label;
      if (i === 0) li.className = 'is-active';
      li.appendChild(a);
      li.setAttribute('role', 'option');
      list.appendChild(li);
    });
    list.__shown = shown;
  }

  function move(delta) {
    var nodes = list.querySelectorAll('li');
    if (!nodes.length) return;
    nodes[active] && nodes[active].classList.remove('is-active');
    active = (active + delta + nodes.length) % nodes.length;
    nodes[active].classList.add('is-active');
    nodes[active].scrollIntoView({ block: 'nearest' });
  }

  function close() {
    if (!box) return;
    box.hidden = true;
    document.documentElement.classList.remove('sr-cmd-open');
  }

  function open() {
    if (!box) build();
    box.hidden = false;
    document.documentElement.classList.add('sr-cmd-open');
    items = collect();
    input.value = '';
    render('');
    input.focus();
  }

  function build() {
    box = document.createElement('div');
    box.className = 'sr-cmd';
    box.hidden = true;
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.innerHTML =
      '<div class="sr-cmd__panel">' +
      '<input class="sr-cmd__input" type="search" autocomplete="off" spellcheck="false" ' +
      'aria-label="Ctrl+K" placeholder="Search / بحث / Zoeken / Suche">' +
      '<ul class="sr-cmd__list" role="listbox"></ul>' +
      '<p class="sr-cmd__foot">↑ ↓ · Enter · Esc</p>' +
      '</div>';
    document.body.appendChild(box);
    input = box.querySelector('.sr-cmd__input');
    list = box.querySelector('.sr-cmd__list');

    input.addEventListener('input', function () { render(input.value); });
    box.addEventListener('click', function (e) { if (e.target === box) close(); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); move(1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); }
      else if (e.key === 'Enter') {
        var nodes = list.querySelectorAll('li a');
        if (nodes[active]) { window.location.href = nodes[active].getAttribute('href'); close(); }
      } else if (e.key === 'Escape') { close(); }
    });
  }

  document.addEventListener('keydown', function (e) {
    var tag = (e.target && e.target.tagName) || '';
    var typing = tag === 'INPUT' || tag === 'TEXTAREA' || (e.target && e.target.isContentEditable);
    if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
      e.preventDefault();
      if (box && !box.hidden) close(); else open();
      return;
    }
    if (e.key === 'Escape' && box && !box.hidden) close();
    if (e.key === '/' && !typing && !(box && !box.hidden)) {
      e.preventDefault();
      open();
    }
  });
})();
