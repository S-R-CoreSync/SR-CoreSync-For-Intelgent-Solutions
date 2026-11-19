function build() {
    if (overlay) { return overlay; }

    host = document.getElementById('srLangMapHost');
    if (!host) {
      host = document.createElement('div');
      host.id = 'srLangMapHost';
      document.body.appendChild(host);
    }
    /* إعدادات الموقع على المضيف نفسه، بـ!important، فلا تتجاوزها ورقة الصفحة */
    host.style.setProperty('position', 'fixed', 'important');
    host.style.setProperty('inset', '0', 'important');
    host.style.setProperty('z-index', '100070', 'important');
    host.style.setProperty('display', 'none', 'important');

    root = host.shadowRoot || host.attachShadow({ mode: 'open' });
    root.innerHTML = '<style>' + STYLES + '</style>';

    var wrap = document.createElement('div');
    wrap.className = 'sr-lm is-on';
    wrap.setAttribute('role', 'dialog');
    wrap.setAttribute('aria-modal', 'true');
    wrap.setAttribute('aria-label', 'خريطة اللغات والأسواق');
    wrap.innerHTML =
      '<div class="sr-lm__panel">' +
        '<div class="sr-lm__bar">' +
          '<div><h2>أين تعمل؟ نُحدّث اللغة والضريبة والعملة معاً</h2>' +
          '<p>اضغط أي دولة لترى اللغة والضريبة (VAT/BTW) والعملة — 29 لغة · 34 سوقاً.</p></div>' +
          '<div class="sr-lm__views">' +
            '<button type="button" data-view="emea" class="is-on">أوروبا والشرق الأوسط</button>' +
            '<button type="button" data-view="world">العالم</button>' +
          '</div>' +
          '<label class="sr-lm__search"><input type="search" placeholder="ابحث عن دولة أو لغة…" autocomplete="off"></label>' +
          '<button type="button" class="sr-lm__close" aria-label="إغلاق">✕</button>' +
        '</div>' +
        '<div class="sr-lm__body">' +
          '<aside class="sr-lm__side"><div class="sr-lm__card"></div><div class="sr-lm__list"></div></aside>' +
'<div class="sr-lm__map">' +
            
            '<svg viewBox="' + VIEWS.emea + '" preserveAspectRatio="xMidYMid meet">' +
              '<path class="sr-lm__land" d="' + WORLD_PATH + '"></path>' +
              '<g class="sr-lm__arcs"></g>' + '<g class="sr-lm__pins"></g>' +
            '</svg>' +
          '</div>' +
                  '</div>' +
      '</div>';

    root.appendChild(wrap);

    overlay = wrap;
    cardEl = wrap.querySelector('.sr-lm__card');
    listEl = wrap.querySelector('.sr-lm__list');
    searchEl = wrap.querySelector('.sr-lm__search input');

    wrap.querySelector('.sr-lm__close').addEventListener('click', close);
    wrap.addEventListener('click', function (e) { if (e.target === wrap) { close(); } });
    Array.prototype.forEach.call(wrap.querySelectorAll('[data-view]'), function (b) {
      b.addEventListener('click', function () {
        view = b.getAttribute('data-view');
        Array.prototype.forEach.call(wrap.querySelectorAll('[data-view]'), function (o) {
          o.classList.toggle('is-on', o === b);
        });
        setView(view);
      });
    });
    searchEl.addEventListener('input', function () { buildList(searchEl.value); });
    wrap.querySelector('svg').addEventListener('click', function (e) {
      var t = e.target;
      if (t && t.classList && t.classList.contains('sr-lm__pin')) { select(Number(t.getAttribute('data-i'))); }
    });
    window.addEventListener('resize', function () { if (isOpen()) { setView(view); } }, { passive: true });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { close(); } });

    buildPins();
    buildList('');
    select(1);
    return overlay;
  }

  var FLAGS = { ar:'\uD83C\uDDF8\uD83C\uDDE6', nl:'\uD83C\uDDF3\uD83C\uDDF1', de:'\uD83C\uDDE9\uD83C\uDDEA',
    fr:'\uD83C\uDDEB\uD83C\uDDF7', es:'\uD83C\uDDEA\uD83C\uDDF8', it:'\uD83C\uDDEE\uD83C\uDDF9', pt:'\uD83C\uDDF5\uD83C\uDDF9',
    en:'\uD83C\uDDEC\uD83C\uDDE7', ga:'\uD83C\uDDEE\uD83C\uDDEA', da:'\uD83C\uDDE9\uD83C\uDDF0', no:'\uD83C\uDDF3\uD83C\uDDF4',
    sv:'\uD83C\uDDF8\uD83C\uDDEA', fi:'\uD83C\uDDEB\uD83C\uDDEE', et:'\uD83C\uDDEA\uD83C\uDDEA', lv:'\uD83C\uDDF1\uD83C\uDDFB',
    lt:'\uD83C\uDDF1\uD83C\uDDF9', pl:'\uD83C\uDDF5\uD83C\uDDF1', cs:'\uD83C\uDDE8\uD83C\uDDFF', sk:'\uD83C\uDDF8\uD83C\uDDF0',
    hu:'\uD83C\uDDED\uD83C\uDDFA', ro:'\uD83C\uDDF7\uD83C\uDDF4', bg:'\uD83C\uDDE7\uD83C\uDDEC', hr:'\uD83C\uDDED\uD83C\uDDF7',
    sl:'\uD83C\uDDF8\uD83C\uDDEE', el:'\uD83C\uDDEC\uD83C\uDDF7', mt:'\uD83C\uDDF2\uD83C\uDDF9', tr:'\uD83C\uDDF9\uD83C\uDDF7',
    ku:'\uD83C\uDDF8\uD83C\uDDFE', ckb:'\uD83C\uDDEE\uD83C\uDDF6' };

  function flagOf(m) {
    if (m.flag) { return m.flag; }
    return FLAGS[m.code] || '\uD83C\uDF10';
  }

  function buildPins() {
    var g = overlay.querySelector('.sr-lm__pins');
    var box = (overlay.querySelector('svg').getAttribute('viewBox') || VIEWS.emea).split(/[\s,]+/).map(Number);
    var k = (box[2] || 1000) / 1000;
    var out = '';
    MARKETS.forEach(function (m, i) {
      var pt = proj(m.lat, m.lon);
      out += '<circle class="sr-lm__halo" cx="' + pt.x.toFixed(1) + '" cy="' + pt.y.toFixed(1) + '" r="' + (12 * k).toFixed(2) + '"></circle>';
      out += '<circle class="sr-lm__pin" data-i="' + i + '" cx="' + pt.x.toFixed(1) + '" cy="' + pt.y.toFixed(1) + '" r="' + (5.6 * k).toFixed(2) + '"><title>' +
        esc(m.country) + ' — ' + esc(m.lang) + ' — VAT ' + esc(m.vat) + ' — ' + esc(m.cur) + '</title></circle>';
    });
    g.innerHTML = out;
  }

  function setView(name) {
    var svg = overlay.querySelector('svg');
    svg.setAttribute('viewBox', VIEWS[name] || VIEWS.emea);
    buildPins();
    buildEdges();
  }

  /* المسارات: ثلاثة أسواق متوسطة البعد + أقصى سوق ظاهر، لا كل الشبكة */
  function buildEdges() {
    renderArcs();
  }

  function renderArcs() {
    var g = overlay && overlay.querySelector('.sr-lm__arcs');
    if (!g) { return; }
    var svg = overlay.querySelector('svg');
    var box = (svg.getAttribute('viewBox') || VIEWS.emea).split(/[\s,]+/).map(Number);
    var inView = function (p) {
      return p.x > box[0] + 4 && p.x < box[0] + box[2] - 4 &&
             p.y > box[1] + 4 && p.y < box[1] + box[3] - 4;
    };

    var here = proj(MARKETS[current].lat, MARKETS[current].lon);
    var ranked = MARKETS.map(function (m, i) {
      var p = proj(m.lat, m.lon);
      var dx = p.x - here.x, dy = p.y - here.y;
      return { i: i, p: p, d: Math.sqrt(dx * dx + dy * dy) };
    }).filter(function (o) {
      return o.i !== current && inView(o.p);
    }).sort(function (a, b) { return a.d - b.d; });

    var picks = [];
    var mid = ranked.slice(2, 5);
    mid.forEach(function (o) { picks.push(o); });
    if (ranked.length) { picks.push(ranked[ranked.length - 1]); }

    var seen = {};
    var out = '';
    picks.forEach(function (o) {
      if (seen[o.i]) { return; }
      seen[o.i] = 1;
      var p2 = o.p;
      var mx = (here.x + p2.x) / 2, my = (here.y + p2.y) / 2;
      var dx = p2.x - here.x, dy = p2.y - here.y;
      var len = Math.sqrt(dx * dx + dy * dy) || 1;
      var lift = Math.min(90, len * 0.28) * (o.i > current ? 1 : -1);
      var cx = mx + (-dy / len) * lift, cy = my + (dx / len) * lift;
      var cls = len > 190 ? ' class="sr-lm__far"' : '';
      out += '<path d="M' + here.x.toFixed(1) + ' ' + here.y.toFixed(1) +
             ' Q' + cx.toFixed(1) + ' ' + cy.toFixed(1) +
             ' ' + p2.x.toFixed(1) + ' ' + p2.y.toFixed(1) + '"' + cls + '></path>';
    });
    g.innerHTML = out;
  }

  function buildList(filter) {
    var q = (filter || '').trim().toLowerCase();
    var out = '';
    MARKETS.forEach(function (m, i) {
      var hay = (m.country + ' ' + m.lang + ' ' + m.city + ' ' + m.code + ' ' + m.cur).toLowerCase();
      if (q && hay.indexOf(q) === -1) { return; }
      out += '<button type="button" class="sr-lm__item' + (i === current ? ' is-on' : '') + '" data-i="' + i + '">' +
        '<span>' + esc(m.country) + '</span><span class="sr-lm__code">' + esc(m.code.toUpperCase()) + ' · ' + esc(m.cur) + '</span></button>';
    });
    listEl.innerHTML = out;
    Array.prototype.forEach.call(listEl.children, function (b) {
      b.addEventListener('click', function () {
        var i = Number(b.getAttribute('data-i'));
        /* نقرة أولى تعرض الدولة، ونقرة ثانية على الدولة المعروضة تحوّل إليها */
        if (i === lastPicked && MARKETS[i] && MARKETS[i].code !== CUR) { window.location.href = langUrl(MARKETS[i].code); return; }
        lastPicked = i;
        select(i);
      });
    });
  }

  function select(i) {
    current = i;
    var m = MARKETS[i];
    if (!m) { return; }
    var outside = m.lon < REGION.lonMin || m.lon > REGION.lonMax || m.lat < REGION.latMin || m.lat > REGION.latMax;
    var want = outside ? 'world' : 'emea';
    if (want !== view) {
      view = want;
      Array.prototype.forEach.call(overlay.querySelectorAll('[data-view]'), function (o) {
        o.classList.toggle('is-on', o.getAttribute('data-view') === want);
      });
      setView(want);
    }
    var tz = Math.round(m.lon / 15);
    cardEl.innerHTML =
      '<div class="sr-lm__flag">' + esc(flagOf(m)) + '</div>' +
      '<h3>' + esc(m.country) + ' — ' + esc(m.city) + '</h3>' +
      '<div class="sr-lm__rows">' +
        '<div class="sr-lm__row"><span>اللغة</span><b>' + esc(m.lang) + ' <i>(' + esc(m.code) + ')</i></b></div>' +
        '<div class="sr-lm__row"><span>ضريبة القيمة المضافة</span><b>' + esc(m.vat) + '</b></div>' +
        '<div class="sr-lm__row"><span>العملة</span><b>' + esc(m.cur) + '</b></div>' +
        '<div class="sr-lm__row"><span>المنطقة الزمنية</span><b>UTC' + (tz >= 0 ? '+' : '') + tz + '</b></div>' +
      '</div>' +
      (m.code === CUR
        ? '<a class="sr-lm__go is-current" aria-current="page">أنت على هذه اللغة الآن</a>'
        : '<a class="sr-lm__go" href="' + esc(langUrl(m.code)) + '">فتح ' + esc(m.lang) + ' والتحويل إليها ←</a>') +
      '<p class="sr-lm__note">البيانات للعرض التوضيحي — تُثبَّت نهائياً من مصدر ضريبي رسمي قبل النشر.</p>';
    buildList(searchEl ? searchEl.value : '');
    Array.prototype.forEach.call(overlay.querySelectorAll('.sr-lm__pin'), function (p) {
      p.classList.toggle('is-on', Number(p.getAttribute('data-i')) === i);
    });
    if (overlay.querySelector('.sr-lm__arcs')) { renderArcs(); }
  }

  function open() {
    build();
    host.style.setProperty('display', 'block', 'important');
    overlay.classList.add('is-on');
    document.documentElement.style.overflow = 'hidden';
    setTimeout(function () { setView(view); }, 60);
    setTimeout(function () { setView(view); }, 260);
    setTimeout(function () { setView(view); }, 700);
  }

  function close() {
    if (!overlay) { return; }
    overlay.classList.remove('is-on');
    if (host) { host.style.setProperty('display', 'none', 'important'); }
    document.documentElement.style.overflow = '';
  }

  function isOpen() { return !!(host && host.style.display !== 'none'); }

  /* كل مدخل لغوي يفتح الخريطة: زر الكرة الأرضية في الدوك، ورابط +29، وقائمة الهيدر */
  function wire() {
    var SEL = '[aria-label*="Languages"], [aria-label*="اللغات"], #srLangMenuBtn, ' +
              '#appleDockLaunchpadBtn, .sr-lang-menu-trigger, .hv2__flag.more, ' +
              '.header-language summary, [href="#languages"]';

    document.addEventListener('click', function (e) {
      var el = e.target && e.target.closest ? e.target.closest(SEL) : null;
      if (!el) { return; }
      /* لا نترك launchpad القديم يفتح في اللحظة نفسها */
      e.preventDefault();
      e.stopPropagation();
      if (typeof window.toggleAppleDockLaunchpad === 'function' && window.__srLaunchpadOpen) {
        try { window.toggleAppleDockLaunchpad(e); } catch (err) {}
      }
      open();
    }, true);
  }

  var STYLES = '.sr-lm{position:fixed;inset:0;z-index:100070;direction:rtl;text-align:start;background:rgba(2,7,5,.96)}.sr-lm__panel{position:absolute;inset:14px;border:1px solid rgba(212,175,55,.28);border-radius:20px;overflow:hidden;background:radial-gradient(ellipse at 50% 0%,rgba(212,175,55,.09),transparent 60%),#04100c;display:grid;grid-template-rows:auto 1fr}.sr-lm__bar{display:flex;align-items:center;gap:14px;padding:14px 18px;border-bottom:1px solid rgba(255,255,255,.07);flex-wrap:wrap}.sr-lm__bar h2{font-size:1rem;color:#f3dfba;margin:0}.sr-lm__bar p{font-size:.74rem;color:#8fa0b5;margin:4px 0 0}.sr-lm__views{display:flex;gap:3px;padding:3px;border:1px solid rgba(255,255,255,.1);border-radius:999px}.sr-lm__views button{border:0;background:none;color:#9fb0c4;font:inherit;font-size:.72rem;font-weight:700;padding:6px 11px;border-radius:999px;cursor:pointer}.sr-lm__views button.is-on{background:rgba(212,175,55,.2);color:#f3dfba}.sr-lm__search{margin-inline-start:auto}.sr-lm__search input{border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.04);border-radius:999px;padding:8px 14px;color:#e8eef6;font:inherit;font-size:.8rem;min-width:200px}.sr-lm__close{width:38px;height:38px;border-radius:11px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.04);color:#cbd7e5;cursor:pointer;font-size:15px}.sr-lm__body{position:relative;display:grid;grid-template-columns:318px minmax(0,1fr);min-height:0}.sr-lm__map{position:relative;min-width:0;min-height:220px;margin:10px}.sr-lm__map svg{width:100%;height:100%;display:block;position:relative;z-index:1}.sr-lm__land{fill:rgba(212,175,55,.06);stroke:rgba(212,175,55,.3);stroke-width:.42;stroke-linejoin:round;vector-effect:non-scaling-stroke}.sr-lm__arcs path{fill:none;stroke:rgba(247,223,148,.5);stroke-width:1.3;vector-effect:non-scaling-stroke}.sr-lm__arcs path.sr-lm__far{stroke:rgba(212,175,55,.4);stroke-width:1;stroke-dasharray:5 5}.sr-lm__pin{fill:#d4af37;cursor:pointer}.sr-lm__pin:hover,.sr-lm__pin.is-on{fill:#f7df94}.sr-lm__halo{fill:rgba(212,175,55,.18);pointer-events:none}.sr-lm__side{position:relative;min-height:0;border-inline-end:1px solid rgba(255,255,255,.07);background:rgba(6,12,9,.55);overflow:auto;padding:12px;scrollbar-width:thin;scrollbar-color:rgba(212,175,55,.45) transparent}.sr-lm__card{border:1px solid rgba(212,175,55,.3);border-radius:14px;padding:13px;background:rgba(212,175,55,.06);margin-bottom:12px}.sr-lm__flag{font-size:1.4rem}.sr-lm__card h3{font-size:.95rem;color:#f3dfba;margin:6px 0 0}.sr-lm__rows{display:grid;grid-template-columns:auto minmax(0,1fr);gap:7px 12px;margin:10px 0 0;font-size:.77rem}.sr-lm__row{display:contents}.sr-lm__row span{color:#8fa0b5}.sr-lm__row b{color:#dfe9f4;font-weight:700;justify-self:start;text-align:start}.sr-lm__row i{font-style:normal;font-family:\"JetBrains Mono\",monospace;font-size:.7rem;opacity:.75}.sr-lm__note{margin:10px 0 0;font-size:.68rem;color:#8fa0b5;line-height:1.7}.sr-lm__mono{font-family:"JetBrains Mono",monospace;direction:ltr;display:inline-block}.sr-lm__side::-webkit-scrollbar{width:7px}.sr-lm__side::-webkit-scrollbar-track{background:transparent}.sr-lm__side::-webkit-scrollbar-thumb{background:rgba(212,175,55,.38);border-radius:99px}.sr-lm__list{display:grid;gap:4px;align-content:start}.sr-lm__item{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:10px;cursor:pointer;border:1px solid transparent;background:none;color:#cfdbeb;font:inherit;font-size:.79rem;text-align:start;width:100%}.sr-lm__item:hover,.sr-lm__item.is-on{background:rgba(212,175,55,.1);border-color:rgba(212,175,55,.3);color:#f3dfba}.sr-lm__code{margin-inline-start:auto;font-family:"JetBrains Mono",monospace;font-size:.64rem;color:#8fa0b5}.sr-lm__go{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;margin:12px 0 0;padding:10px 14px;border-radius:12px;border:1px solid rgba(212,175,55,.55);background:linear-gradient(180deg,rgba(212,175,55,.28),rgba(212,175,55,.16));color:#f7df94;font:inherit;font-size:.85rem;font-weight:800;text-decoration:none;cursor:pointer}.sr-lm__go:hover{background:linear-gradient(180deg,rgba(212,175,55,.4),rgba(212,175,55,.24));color:#fff2d0;border-color:rgba(212,175,55,.8)}.sr-lm__go.is-current{background:none;border-style:dashed;border-color:rgba(255,255,255,.14);color:#8fa0b5;cursor:default;font-weight:600}@media (max-width:760px){.sr-lm__body{grid-template-columns:minmax(0,1fr);grid-template-rows:minmax(0,1fr) auto}.sr-lm__map{order:-1}.sr-lm__side{max-height:42vh;border-inline-end:0;border-top:1px solid rgba(255,255,255,.07);display:grid;grid-template-columns:minmax(0,260px) minmax(0,1fr);gap:12px}.sr-lm__card{margin-bottom:0}.sr-lm__list{grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}}';

  global.SRLangMap = { open: open, close: close, isOpen: isOpen };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wire);
  } else {
    wire();
  }
})(window);
