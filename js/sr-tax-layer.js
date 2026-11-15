/* S&R CoreSync — Golden line from Amsterdam HQ + floating tax card
   Same continents map, same dock. Data: js/sr-tax-markets.json
   UI language follows <html lang> (ar / de / en; fallback ar). */
(function () {
  'use strict';
  if (window.__SRTaxLayer) { return; }
  window.__SRTaxLayer = true;

  var VB_W = 1000, VB_H = 560, LAT_TOP = 78, LAT_BOTTOM = -58;
  var DATA = null;
  var LANG = 'ar';
  var host = null, card = null, lastKey = 'nl';

  function detectLang() {
    var l = (document.documentElement.getAttribute('lang') ||
             document.documentElement.getAttribute('data-page-language') || 'ar')
            .toLowerCase().split('-')[0];
    var ok = { ar: 1, de: 1, en: 1, fr: 1, nl: 1, tr: 1, es: 1, it: 1 };
    return ok[l] ? l : 'ar';
  }

  function isRTL() {
    var dir = document.documentElement.getAttribute('dir');
    if (dir) { return dir === 'rtl'; }
    return LANG === 'ar';
  }

  function ui() { return DATA.ui[LANG] || DATA.ui.ar; }
  function L(obj) {
    if (!obj) { return ''; }
    return obj[LANG] || obj.en || obj.ar || '';
  }
  function pick(key) { return DATA.markets[key] || null; }

  function proj(lat, lon) {
    return { x: (lon + 180) / 360 * VB_W, y: (LAT_TOP - lat) / (LAT_TOP - LAT_BOTTOM) * VB_H };
  }

  function root() {
    host = host || document.getElementById('srLangMapHost');
    if (!host) { return null; }
    return host.shadowRoot || null;
  }

  var SHADOW_CSS = '.sr-gold-arc{fill:none;stroke:#f7df94;stroke-width:2.2;stroke-linecap:round;vector-effect:non-scaling-stroke;filter:drop-shadow(0 0 6px rgba(247,223,148,.95)) drop-shadow(0 0 14px rgba(212,175,55,.7));stroke-dasharray:7 5;animation:srGoldDash 1.1s linear infinite;pointer-events:none}@keyframes srGoldDash{to{stroke-dashoffset:-24}}.sr-gold-glow{fill:none;stroke:rgba(247,223,148,.35);stroke-width:7;stroke-linecap:round;vector-effect:non-scaling-stroke;filter:blur(3px);pointer-events:none}.sr-hq-star{fill:#f7df94;stroke:#8a6a12;stroke-width:.6;filter:drop-shadow(0 0 5px rgba(247,223,148,.95));pointer-events:none}.sr-hq-label{font:700 9px "JetBrains Mono",monospace;fill:#f3dfba;paint-order:stroke;stroke:rgba(4,16,12,.85);stroke-width:2.4;pointer-events:none}.sr-extra-pin{fill:#e8c96a;cursor:pointer;filter:drop-shadow(0 0 4px rgba(212,175,55,.8))}.sr-extra-pin:hover,.sr-extra-pin.is-on{fill:#fff3c4}.sr-extra-halo{fill:rgba(212,175,55,.22);pointer-events:none}.sr-lit{fill:#fff3c4 !important;filter:drop-shadow(0 0 8px rgba(247,223,148,1)) !important}.sr-tax-card{position:absolute;inset-block-start:12px;inset-inline-end:14px;z-index:5;width:min(340px,calc(100% - 28px));max-height:calc(100% - 24px);overflow:auto;border:1px solid rgba(212,175,55,.45);border-radius:16px;background:linear-gradient(180deg,rgba(10,18,14,.97),rgba(4,16,12,.97));box-shadow:0 18px 48px rgba(0,0,0,.55),0 0 0 1px rgba(247,223,148,.12) inset;padding:14px;color:#dfe9f4;font:inherit;backdrop-filter:blur(8px);opacity:0;transform:translateY(8px) scale(.98);pointer-events:none;transition:opacity .22s ease,transform .22s ease}.sr-tax-card.is-on{opacity:1;transform:none;pointer-events:auto}.sr-tax-card h4{margin:0;font-size:.95rem;color:#f3dfba;display:flex;align-items:center;gap:8px}.sr-tax-card .sr-tc-flag{font-size:1.25rem}.sr-tax-card .sr-tc-cap{font-size:.72rem;color:#8fa0b5;margin:3px 0 0}.sr-tax-rows{display:grid;gap:8px;margin:11px 0 0;font-size:.76rem}.sr-tax-row{display:grid;grid-template-columns:96px minmax(0,1fr);gap:8px;align-items:start}.sr-tax-row span{color:#8fa0b5}.sr-tax-row b{color:#f3dfba;font-weight:700;line-height:1.6}.sr-tax-chips{display:flex;flex-wrap:wrap;gap:5px}.sr-tax-chip{border:1px solid rgba(212,175,55,.35);background:rgba(212,175,55,.1);color:#f3dfba;border-radius:999px;padding:2px 8px;font-size:.66rem;font-family:"JetBrains Mono",monospace}.sr-tax-invoice{margin-top:10px;border:1px dashed rgba(212,175,55,.4);border-radius:12px;padding:9px 10px;background:rgba(212,175,55,.05);font-size:.72rem;line-height:1.7;color:#dfe9f4}.sr-tax-invoice b{color:#f7df94}.sr-tax-note{margin:9px 0 0;font-size:.66rem;color:#c9a94a;line-height:1.6}.sr-tax-actions{display:flex;gap:8px;margin-top:11px}.sr-tax-dl{flex:1;border:0;border-radius:11px;padding:9px 12px;cursor:pointer;font:inherit;font-size:.76rem;font-weight:700;color:#04100c;background:linear-gradient(135deg,#f7df94,#d4af37);box-shadow:0 6px 18px rgba(212,175,55,.35)}.sr-tax-dl:hover{filter:brightness(1.08)}.sr-tax-x{width:34px;border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.05);color:#cbd7e5;border-radius:11px;cursor:pointer;font-size:14px}.sr-tax-close-hint{position:absolute;inset-inline-start:14px;bottom:10px;z-index:4;font-size:.66rem;color:rgba(247,223,148,.75);pointer-events:none}@media (max-width:760px){.sr-tax-card{inset-inline-end:8px;top:8px;width:calc(100% - 16px)}}';

  function injectShadowCss() {
    var r = root();
    if (!r || r.querySelector('#srTaxShadowCss')) { return; }
    var st = document.createElement('style');
    st.id = 'srTaxShadowCss';
    st.textContent = SHADOW_CSS;
    r.insertBefore(st, r.firstChild);
  }

  function drawArc(key) {
    var r = root();
    if (!r || !DATA) { return; }
    var svg = r.querySelector('.sr-lm__map svg');
    var d = pick(key);
    if (!svg || !d) { return; }
    lastKey = key;
    var a = proj(DATA.ams.lat, DATA.ams.lon);
    var b = proj(d.lat, d.lon);
    var mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
    var dx = b.x - a.x, dy = b.y - a.y;
    var len = Math.sqrt(dx * dx + dy * dy) || 1;
    var lift = Math.min(80, len * 0.22);
    var cx = mx + (-dy / len) * lift, cy = my + (dx / len) * lift;
    var path = 'M' + a.x.toFixed(1) + ' ' + a.y.toFixed(1) +
               ' Q' + cx.toFixed(1) + ' ' + cy.toFixed(1) +
               ' ' + b.x.toFixed(1) + ' ' + b.y.toFixed(1);
    var g = r.querySelector('.sr-gold-layer');
    if (!g) {
      g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.setAttribute('class', 'sr-gold-layer');
      svg.appendChild(g);
    }
    g.innerHTML =
      '<path class="sr-gold-glow" d="' + path + '"></path>' +
      '<path class="sr-gold-arc" d="' + path + '"></path>' +
      '<circle class="sr-hq-star" cx="' + a.x.toFixed(1) + '" cy="' + a.y.toFixed(1) + '" r="5"></circle>' +
      '<text class="sr-hq-label" x="' + (a.x + 8).toFixed(1) + '" y="' + (a.y - 6).toFixed(1) + '">AMS HQ</text>' +
      '<circle cx="' + b.x.toFixed(1) + '" cy="' + b.y.toFixed(1) + '" r="8" fill="none" stroke="#f7df94" stroke-width="1.4" opacity=".9"></circle>' +
      '<circle cx="' + b.x.toFixed(1) + '" cy="' + b.y.toFixed(1) + '" r="3.4" fill="#fff3c4"></circle>';
    Array.prototype.forEach.call(r.querySelectorAll('.sr-lm__pin, .sr-extra-pin'), function (p) {
      var on = Math.abs(parseFloat(p.getAttribute('cx')) - b.x) < 3 &&
               Math.abs(parseFloat(p.getAttribute('cy')) - b.y) < 3;
      p.classList.toggle('sr-lit', on);
    });
  }

  function invoiceText(d) {
    var tpl = DATA.invoice[d.billing] || DATA.invoice.non_eu;
    var head = d.hq ? ui().invoiceHq : ui().invoicePartner;
    var extra = d.note ? ' ' + L(d.note) : '';
    return head + '<br>' + tpl + extra;
  }

  function showCard(key) {
    var r = root();
    if (!r || !DATA) { return; }
    var d = pick(key);
    if (!d) { return; }
    var mapBox = r.querySelector('.sr-lm__map');
    if (!mapBox) { return; }
    if (!card) {
      card = document.createElement('div');
      card.className = 'sr-tax-card';
      card.setAttribute('role', 'dialog');
      mapBox.appendChild(card);
    } else if (card.parentNode !== mapBox) {
      mapBox.appendChild(card);
    }
    card.setAttribute('aria-label', ui().cardAria);
    card.style.direction = isRTL() ? 'rtl' : 'ltr';
    card.style.textAlign = 'start';
    var chips = (d.types || []).map(function (t) {
      return '<span class="sr-tax-chip">' + t + '</span>';
    }).join('');
    card.innerHTML =
      '<h4><span class="sr-tc-flag">' + d.flag + '</span> ' + L(d.name) + '</h4>' +
      '<p class="sr-tc-cap">' + ui().capital + ': <b>' + L(d.city) + '</b> · ' + key.toUpperCase() + '</p>' +
      '<div class="sr-tax-rows">' +
        '<div class="sr-tax-row"><span>' + ui().vat + '</span><b>' + d.vat + ' · ' + d.cur + '</b></div>' +
        '<div class="sr-tax-row"><span>' + ui().types + '</span><div class="sr-tax-chips">' + chips + '</div></div>' +
      '</div>' +
      '<div class="sr-tax-invoice">' + invoiceText(d) + '</div>' +
      '<p class="sr-tax-note">' + ui().disclaimer + '</p>' +
      '<div class="sr-tax-actions">' +
        '<button type="button" class="sr-tax-dl" data-dl-key="' + key + '">' + ui().download + '</button>' +
        '<button type="button" class="sr-tax-x" aria-label="✕">✕</button>' +
      '</div>';
    requestAnimationFrame(function () { card.classList.add('is-on'); });
    card.querySelector('.sr-tax-x').addEventListener('click', function () { card.classList.remove('is-on'); });
    card.querySelector('.sr-tax-dl').addEventListener('click', function () { downloadInfo(key); });
  }

  /* مزامنة القائمة الجانبية الأصلية (.sr-lm__card) مع الدولة المختارة */
  function syncSidebar(key) {
    var r = root();
    if (!r || !DATA) { return; }
    var d = pick(key);
    var cardEl = r.querySelector('.sr-lm__card');
    if (!d || !cardEl) { return; }
    var tz = Math.round(d.lon / 15);
    var u = ui();
    cardEl.innerHTML =
      '<div class="sr-lm__flag">' + d.flag + '</div>' +
      '<h3>' + L(d.name) + ' — ' + L(d.city) + '</h3>' +
      '<div class="sr-lm__rows">' +
        '<div class="sr-lm__row"><span>' + u.lang + '</span><b>' + L(d.langName) + ' <i>(' + key + ')</i></b></div>' +
        '<div class="sr-lm__row"><span>' + u.vat + '</span><b>' + d.vat + '</b></div>' +
        '<div class="sr-lm__row"><span>' + u.currency + '</span><b>' + d.cur + '</b></div>' +
        '<div class="sr-lm__row"><span>' + u.tz + '</span><b>UTC' + (tz >= 0 ? '+' : '') + tz + '</b></div>' +
      '</div>' +
      '<p class="sr-lm__note">' + u.demoNote + '</p>';
    Array.prototype.forEach.call(r.querySelectorAll('.sr-lm__item'), function (b) {
      var extra = b.getAttribute('data-extra');
      var idx = b.getAttribute('data-i');
      var on = extra ? extra === key : false;
      b.classList.toggle('is-on', on);
      if (extra !== key && idx != null) { /* اترك الأصلي كما هو إن لم تكن إضافية */ }
    });
    /* أبرز العنصر الإضافي المطابق، وأطفئ is-on عن الأصلي إن كنا على سوق إضافي */
    var isExtra = DATA.extraKeys.indexOf(key) !== -1;
    Array.prototype.forEach.call(r.querySelectorAll('.sr-lm__item'), function (b) {
      if (isExtra) {
        b.classList.toggle('is-on', b.getAttribute('data-extra') === key);
      }
    });
  }

  function downloadInfo(key) {
    var d = pick(key);
    if (!d || !DATA) { return; }
    var u = ui();
    var chips = (d.types || []).join(' · ');
    var plainInv = invoiceText(d).replace(/<\/?b>/g, '');
    var title = L(d.name) + ' — ' + L(d.city);
    var html = '<!DOCTYPE html><html lang="' + LANG + '" dir="' + (isRTL() ? 'rtl' : 'ltr') + '">' +
      '<head><meta charset="utf-8"><title>S&R CoreSync — ' + title + '</title>' +
      '<style>body{font-family:system-ui,"Segoe UI",Tahoma;background:#04100c;color:#dfe9f4;padding:32px;direction:' + (isRTL() ? 'rtl' : 'ltr') + '}' +
      '.c{max-width:640px;margin:auto;border:1px solid #d4af37;border-radius:18px;padding:24px;background:#0a120e}' +
      'h1{color:#f3dfba;font-size:1.3rem}table{width:100%;border-collapse:collapse;margin-top:12px}' +
      'td{padding:8px;border-bottom:1px solid rgba(212,175,55,.2);font-size:.9rem}' +
      'td:first-child{color:#8fa0b5;width:170px}.note{color:#c9a94a;font-size:.75rem;margin-top:14px}' +
      '.gold{color:#f7df94}</style></head><body><div class="c">' +
      '<h1>' + d.flag + ' ' + title + '</h1>' +
      '<p class="gold">S&R CoreSync For Intelligent Solutions · ' + key.toUpperCase() + '</p>' +
      '<table>' +
      '<tr><td>' + u.capital + '</td><td>' + L(d.city) + '</td></tr>' +
      '<tr><td>' + u.vat + '</td><td>' + d.vat + '</td></tr>' +
      '<tr><td>' + u.currency + '</td><td>' + d.cur + '</td></tr>' +
      '<tr><td>' + u.types + '</td><td>' + chips + '</td></tr>' +
      '<tr><td>' + (d.hq ? u.invoiceHq : u.invoicePartner) + '</td><td>' + plainInv + '</td></tr>' +
      '</table>' +
      '<p class="note">' + u.disclaimer + '</p>' +
      '<p style="font-size:.7rem;color:#8fa0b5">© 2026 S&R CoreSync For Intelligent Solutions · Amsterdam</p>' +
      '</div></body></html>';
    var blob = new Blob([html], { type: 'text/html;charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'SR-CoreSync-Info-' + key.toUpperCase() + '.html';
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 800);
  }

  function injectExtraPins() {
    var r = root();
    if (!r || !DATA) { return; }
    var g = r.querySelector('.sr-lm__pins');
    if (!g || g.querySelector('.sr-extra-pin')) { return; }
    var frag = '';
    DATA.extraKeys.forEach(function (k) {
      var m = DATA.markets[k];
      if (!m) { return; }
      var p = proj(m.lat, m.lon);
      frag += '<circle class="sr-extra-halo" cx="' + p.x.toFixed(1) + '" cy="' + p.y.toFixed(1) + '" r="11"></circle>';
      frag += '<circle class="sr-extra-pin" data-key="' + k + '" cx="' + p.x.toFixed(1) + '" cy="' + p.y.toFixed(1) + '" r="5.6">' +
              '<title>' + L(m.name) + ' — ' + L(m.langName) + ' — ' + m.vat + ' — ' + m.cur + '</title></circle>';
    });
    g.insertAdjacentHTML('beforeend', frag);
  }

  function injectListItems() {
    var r = root();
    if (!r || !DATA) { return; }
    var list = r.querySelector('.sr-lm__list');
    if (!list || list.querySelector('.sr-lm__item[data-extra]')) { return; }
    var html = '';
    DATA.extraKeys.forEach(function (k) {
      var m = DATA.markets[k];
      if (!m) { return; }
      html += '<button type="button" class="sr-lm__item" data-extra="' + k + '">' +
        '<span>' + L(m.name) + '</span><span class="sr-lm__code">' + k.toUpperCase() + ' · ' + m.cur + '</span></button>';
    });
    list.insertAdjacentHTML('beforeend', html);
    Array.prototype.forEach.call(list.querySelectorAll('[data-extra]'), function (b) {
      b.addEventListener('click', function () {
        var k = b.getAttribute('data-extra');
        drawArc(k); showCard(k); syncSidebar(k);
      });
    });
  }

  /* ترجمة أسماء الأسواق الأصلية في القائمة الجانبية وعناوين النقاط */
  function localizeOriginal() {
    var r = root();
    if (!r || !DATA) { return; }
    Array.prototype.forEach.call(r.querySelectorAll('.sr-lm__item:not([data-extra])'), function (b) {
      var span = b.querySelector('span');
      if (!span) { return; }
      var key = countryToKey(span.textContent);
      if (key) { span.textContent = L(DATA.markets[key].name); }
    });
    Array.prototype.forEach.call(r.querySelectorAll('.sr-lm__pin title'), function (t) {
      var key = countryToKey(t.textContent || '');
      if (key) {
        var m = DATA.markets[key];
        t.textContent = L(m.name) + ' — ' + L(m.langName) + ' — ' + m.vat + ' — ' + m.cur;
      }
    });
    var h2 = r.querySelector('.sr-lm__bar h2');
    if (h2 && !h2.dataset.srTaxH2) {
      h2.dataset.srTaxH2 = '1';
      h2.textContent = ui().h2;
    }
  }

  function renameTab() {
    var r = root();
    if (!r || !DATA) { return; }
    var btn = r.querySelector('[data-view="emea"]');
    if (btn) { btn.textContent = ui().tab; }
    var p = r.querySelector('.sr-lm__bar p');
    if (p) { p.textContent = ui().subtitle; }
  }

  function countryToKey(input) {
    var s = (input || '').trim();
    if (!s) { return null; }
    var keys = Object.keys(DATA.markets);
    /* مطابقة اسم في أي لغة */
    for (var i = 0; i < keys.length; i++) {
      var m = DATA.markets[keys[i]];
      if (s === L(m.name) || s === m.name.ar || s === m.name.de || s === m.name.en) { return keys[i]; }
    }
    /* أطول بادئة (عناوين النقاط الأصلية تبدأ باسم البلد) */
    var sorted = keys.slice().sort(function (a, b) { return L(DATA.markets[b].name).length - L(DATA.markets[a].name).length; });
    for (var j = 0; j < sorted.length; j++) {
      var nm = L(DATA.markets[sorted[j]].name);
      if (s.indexOf(nm) === 0 || s.indexOf(DATA.markets[sorted[j]].name.ar) === 0) { return sorted[j]; }
    }
    return null;
  }

  function keyFromPin(pin) {
    if (!pin) { return null; }
    if (pin.classList.contains('sr-extra-pin')) { return pin.getAttribute('data-key'); }
    var title = pin.querySelector('title');
    return countryToKey(title ? title.textContent : '');
  }

  function wireSvg() {
    var r = root();
    if (!r) { return; }
    var mapBox = r.querySelector('.sr-lm__map');
    if (!mapBox || mapBox.dataset.srTaxWired) { return; }
    mapBox.dataset.srTaxWired = '1';
    mapBox.addEventListener('click', function (e) {
      var t = e.target;
      if (!t || !t.classList) { return; }
      var key = keyFromPin(t);
      if (key) {
        drawArc(key); showCard(key);
        /* بعد select() الأصلي حتى لا يمسح القائمة الجانبية بالعربية */
        setTimeout(function () { syncSidebar(key); }, 0);
      }
    }, true);
    mapBox.addEventListener('mouseover', function (e) {
      var t = e.target;
      if (!t || !t.classList) { return; }
      if (t.classList.contains('sr-extra-pin') || t.classList.contains('sr-lm__pin')) {
        var key = keyFromPin(t);
        if (key) { drawArc(key); }
      }
    });
    if (!mapBox.querySelector('.sr-tax-close-hint')) {
      var hint = document.createElement('div');
      hint.className = 'sr-tax-close-hint';
      hint.textContent = ui().hqHint;
      mapBox.appendChild(hint);
    }
  }

  var DOCK = [
    { sel: '.apple-dock-item[href*="/de/"]', key: 'de' },
    { sel: '.apple-dock-item[href*="/fr/"]', key: 'fr' },
    { sel: '.apple-dock-item[href*="/nl/"]', key: 'nl' },
    { sel: '.apple-dock-item[href*="/en/"]', key: 'gb' },
    { sel: '.apple-dock-item[href*="/es/"]', key: 'es' },
    { sel: '.apple-dock-item.active[href*="index.html"]', key: 'sa' },
    { sel: '.apple-dock-item[href*="/tr/"]', key: 'tr' }
  ];

  function wireDock() {
    if (!DATA) { return; }
    DOCK.forEach(function (d) {
      var el = document.querySelector(d.sel);
      if (!el || el.dataset.srTaxHover) { return; }
      el.dataset.srTaxHover = '1';
      el.addEventListener('mouseenter', function () {
        if (window.SRLangMap && window.SRLangMap.isOpen && window.SRLangMap.isOpen()) {
          drawArc(d.key);
        }
      });
    });
  }

  function injectShadowCssAndHint() { injectShadowCss(); }

  function enhance() {
    if (!DATA) { return; }
    injectShadowCss();
    renameTab();
    injectExtraPins();
    injectListItems();
    wireSvg();
    wireDock();
    localizeOriginal();
    observe();
    drawArc(lastKey || 'nl');
    if (lastKey) { syncSidebar(lastKey); }
  }

  function wrapOpen() {
    if (!window.SRLangMap) { return; }
    var api = window.SRLangMap;
    if (!api.__taxWrapped) {
      api.__taxWrapped = true;
      var origOpen = api.open;
      api.open = function () {
        var out = origOpen.apply(this, arguments);
        setTimeout(enhance, 60);
        setTimeout(enhance, 280);
        setTimeout(enhance, 700);
        return out;
      };
    }
    if (api.isOpen && api.isOpen()) { setTimeout(enhance, 40); }
  }

  function trapSRLangMap() {
    try {
      var desc = Object.getOwnPropertyDescriptor(window, 'SRLangMap');
      if (desc && desc.set) { return; }
      var _v = window.SRLangMap;
      Object.defineProperty(window, 'SRLangMap', {
        configurable: true,
        get: function () { return _v; },
        set: function (v) {
          _v = v;
          if (v && !v.__taxWrapped && typeof v.open === 'function') {
            var origOpen = v.open;
            v.__taxWrapped = true;
            v.open = function () {
              var out = origOpen.apply(this, arguments);
              setTimeout(enhance, 50);
              setTimeout(enhance, 260);
              setTimeout(enhance, 700);
              return out;
            };
          }
          setTimeout(wrapOpen, 0);
        }
      });
    } catch (e) { /* ignore */ }
  }

  function observe() {
    var r = root();
    if (!r || r.__srTaxObs) { return; }
    r.__srTaxObs = true;
    var mo = new MutationObserver(function () {
      var g = r.querySelector('.sr-lm__pins');
      if (g && !g.querySelector('.sr-extra-pin')) { injectExtraPins(); }
      var list = r.querySelector('.sr-lm__list');
      if (list && !list.querySelector('[data-extra]')) { injectListItems(); }
      if (card && !r.querySelector('.sr-tax-card')) {
        var mapBox = r.querySelector('.sr-lm__map');
        if (mapBox) { mapBox.appendChild(card); }
      }
      /* أعِد الترجمة إذا أعاد buildList الأسماء العربية */
      var firstItem = list && list.querySelector('.sr-lm__item:not([data-extra]) span');
      if (firstItem && DATA) {
        var key = countryToKey(firstItem.textContent);
        if (key && firstItem.textContent !== L(DATA.markets[key].name)) {
          localizeOriginal();
        }
      }
    });
    mo.observe(r, { childList: true, subtree: true });
  }

  function loadData() {
    /* مسار الملف relative لهذا السكربت، فيشتغل من / ومن /de/ */
    var self = document.currentScript ? document.currentScript.src : '';
    var url = self ? self.replace(/sr-tax-layer\.js.*$/, 'sr-tax-markets.json')
                   : 'js/sr-tax-markets.json';
    url += (url.indexOf('?') === -1 ? '?v=20261115c' : '&v=20261115c');
    return fetch(url).then(function (res) {
      if (!res.ok) { throw new Error('tax json ' + res.status); }
      return res.json();
    });
  }

  function boot() {
    LANG = detectLang();
    trapSRLangMap();
    loadData().then(function (json) {
      DATA = json;
      wrapOpen();
      observe();
      wireDock();
      if (window.SRLangMap && window.SRLangMap.isOpen && window.SRLangMap.isOpen()) {
        enhance();
      }
    }).catch(function (err) {
      if (window.console) { console.warn('[sr-tax-layer] JSON load failed', err); }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
