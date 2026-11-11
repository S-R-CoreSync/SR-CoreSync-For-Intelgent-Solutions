/* S&R CoreSync - analytics consent gate.
   GA4 does not exist in the HTML any more. This file is the only thing that can
   load it, and only after the visitor says yes: no request, no cookie, no ping
   before that. Ads signals stay denied because the site runs no advertising.
   A page with no data-ga4 attribute gets no banner and no analytics at all. */
(function () {
  'use strict';
  if (window.__srConsent) return;
  window.__srConsent = true;

  var ID = document.documentElement.getAttribute('data-ga4');
  if (!ID) return;                       // nothing configured on this page

  var KEY = 'sr_consent_v1';
  var STR = {
    "ar": {
      "accept": "موافق",
      "body": "نستخدم تحليلات مجهولة لتحسين موقعنا، فهل توافق؟",
      "reject": "رفض",
      "settings": "إعدادات التحليلات",
      "title": "ملفات التحليلات"
    },
    "bg": {
      "accept": "Приемам",
      "body": "Използваме анонимна аналитика, за да подобрим сайта – съгласни ли сте?",
      "reject": "Отказвам",
      "settings": "Настройки бисквитки",
      "title": "Аналитични бисквитки"
    },
    "ckb": {
      "accept": "ڕەزامەندم",
      "body": "شیکاریی بێناسنامە بەکاردەهێنین بۆ باشترکردنی ماڵپەڕ؛ ڕەزامەندیت؟",
      "reject": "ڕەتکردنەوە",
      "settings": "ڕێکخستنی کوکی",
      "title": "کوکیی شیکاری"
    },
    "cs": {
      "accept": "Přijmout",
      "body": "Používáme anonymní analytiku ke zlepšování webu – souhlasíte?",
      "reject": "Odmítnout",
      "settings": "Nastavení cookies",
      "title": "Analytické cookies"
    },
    "da": {
      "accept": "Accepter",
      "body": "Vi bruger anonym analyse for at forbedre webstedet – accepterer du?",
      "reject": "Afvis",
      "settings": "Cookieindstillinger",
      "title": "Analysecookies"
    },
    "de": {
      "accept": "Akzeptieren",
      "body": "Wir nutzen anonyme Analysen zur Verbesserung unserer Website – stimmen Sie zu?",
      "reject": "Ablehnen",
      "settings": "Cookie-Einstellungen",
      "title": "Analyse-Cookies"
    },
    "el": {
      "accept": "Αποδοχή",
      "body": "Χρησιμοποιούμε ανώνυμα cookies ανάλυσης για να βελτιώνουμε τον ιστότοπο – συμφωνείτε;",
      "reject": "Απόρριψη",
      "settings": "Ρυθμίσεις cookies",
      "title": "Cookies ανάλυσης"
    },
    "en": {
      "accept": "Accept",
      "body": "We use anonymous analytics to improve our site; do you consent?",
      "reject": "Reject",
      "settings": "Cookie settings",
      "title": "Analytics cookies"
    },
    "es": {
      "accept": "Aceptar",
      "body": "Usamos cookies analíticas anónimas para mejorar el sitio; ¿aceptas?",
      "reject": "Rechazar",
      "settings": "Configurar cookies",
      "title": "Cookies analíticas"
    },
    "et": {
      "accept": "Nõustu",
      "body": "Kasutame saidi parandamiseks anonüümset analüütikat – kas nõustute?",
      "reject": "Keeldu",
      "settings": "Küpsiste seaded",
      "title": "Analüütikaküpsised"
    },
    "fi": {
      "accept": "Hyväksy",
      "body": "Käytämme anonyymia analytiikkaa parantaaksemme sivustoa – hyväksytkö?",
      "reject": "Hylkää",
      "settings": "Evästeasetukset",
      "title": "Analytiikkaevästeet"
    },
    "fr": {
      "accept": "Accepter",
      "body": "Nous utilisons des cookies analytiques anonymes pour améliorer notre site ; acceptez-vous ?",
      "reject": "Refuser",
      "settings": "Paramètres cookies",
      "title": "Cookies analytiques"
    },
    "ga": {
      "accept": "Glac",
      "body": "Úsáidimid anailísíocht anaithnid chun an suíomh a fheabhsú – an aontaíonn tú?",
      "reject": "Diúltaigh",
      "settings": "Socruithe fianán",
      "title": "Fianáin anailíseacha"
    },
    "hr": {
      "accept": "Prihvati",
      "body": "Koristimo anonimnu analitiku za poboljšanje stranice – slažete li se?",
      "reject": "Odbij",
      "settings": "Postavke kolačića",
      "title": "Analitički kolačići"
    },
    "hu": {
      "accept": "Elfogad",
      "body": "Névtelen analitikát használunk weboldalunk fejlesztéséhez – hozzájárul ehhez?",
      "reject": "Elutasít",
      "settings": "Sütibeállítások",
      "title": "Analitikai sütik"
    },
    "it": {
      "accept": "Accetta",
      "body": "Usiamo cookie analitici anonimi per migliorare il sito: acconsenti?",
      "reject": "Rifiuta",
      "settings": "Preferenze cookie",
      "title": "Cookie analitici"
    },
    "ku": {
      "accept": "Qebûl bike",
      "body": "Em analîtîka anonîm bikar tînin ji bo baştirkirina malperê – razî yî?",
      "reject": "Red bike",
      "settings": "Mîhengên çerezan",
      "title": "Çerezên analîtîk"
    },
    "lt": {
      "accept": "Sutinku",
      "body": "Naudojame anoniminę analitiką svetainei gerinti – ar sutinkate?",
      "reject": "Nesutinku",
      "settings": "Slapukų nustatymai",
      "title": "Analitiniai slapukai"
    },
    "lv": {
      "accept": "Pieņemt",
      "body": "Mēs izmantojam anonīmu analītiku vietnes uzlabošanai – vai piekrītat?",
      "reject": "Noraidīt",
      "settings": "Sīkdatņu iestatījumi",
      "title": "Analītiskās sīkdatnes"
    },
    "mt": {
      "accept": "Naqbel",
      "body": "Nużaw analitika anonima biex intejbu s-sit – taqbel?",
      "reject": "Irrifjuta",
      "settings": "Settings tal-cookies",
      "title": "Cookies analitiċi"
    },
    "nl": {
      "accept": "Accepteren",
      "body": "Met anonieme analytische cookies verbeteren wij onze website; gaat u daarmee akkoord?",
      "reject": "Weigeren",
      "settings": "Cookievoorkeuren",
      "title": "Analytische cookies"
    },
    "no": {
      "accept": "Godta",
      "body": "Vi bruker anonym analyse for å forbedre nettstedet – godkjenner du det?",
      "reject": "Avvis",
      "settings": "Cookieinnstillinger",
      "title": "Analysecookies"
    },
    "pl": {
      "accept": "Akceptuj",
      "body": "Używamy anonimowych analitycznych plików cookie, aby ulepszać witrynę — zgadzasz się?",
      "reject": "Odrzuć",
      "settings": "Ustawienia cookies",
      "title": "Ciasteczka analityczne"
    },
    "pt": {
      "accept": "Aceitar",
      "body": "Usamos cookies analíticos anónimos para melhorar o site; aceita?",
      "reject": "Recusar",
      "settings": "Configurar cookies",
      "title": "Cookies analíticos"
    },
    "ro": {
      "accept": "Accept",
      "body": "Folosim analize anonime pentru a îmbunătăți site-ul – sunteți de acord?",
      "reject": "Refuz",
      "settings": "Setări cookie",
      "title": "Cookie-uri analitice"
    },
    "sk": {
      "accept": "Prijať",
      "body": "Používame anonymnú analytiku na zlepšenie stránky – súhlasíte?",
      "reject": "Odmietnuť",
      "settings": "Nastavenia cookies",
      "title": "Analytické cookies"
    },
    "sl": {
      "accept": "Sprejmi",
      "body": "Uporabljamo anonimno analitiko za izboljšanje spletne strani – se strinjate?",
      "reject": "Zavrni",
      "settings": "Nastavitve piškotkov",
      "title": "Analitični piškotki"
    },
    "sv": {
      "accept": "Acceptera",
      "body": "Vi använder anonym analys för att förbättra webbplatsen – godkänner du?",
      "reject": "Avböj",
      "settings": "Cookieinställningar",
      "title": "Analyscookies"
    },
    "tr": {
      "accept": "Kabul et",
      "body": "Anonim analitik çerezlerle siteyi geliştiriyoruz; kabul ediyor musunuz?",
      "reject": "Reddet",
      "settings": "Çerez ayarları",
      "title": "Analitik çerezler"
    }
  };

  function read() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function write(v) { try { localStorage.setItem(KEY, v); } catch (e) { /* private mode */ } }

  function load() {
    if (window.__srGaLoaded) return;
    window.__srGaLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', {
      ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied',
      analytics_storage: 'granted'
    });
    window.gtag('js', new Date());
    window.gtag('config', ID, { anonymize_ip: true });
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(ID);
    document.head.appendChild(s);
  }

  function lang() {
    var l = (document.documentElement.lang || 'en').toLowerCase().split('-')[0];
    return STR[l] ? l : 'en';
  }

  var box = null;

  function close() {
    if (box && box.parentNode) box.parentNode.removeChild(box);
    box = null;
  }

  function build() {
    if (box) return;
    var t = STR[lang()];
    var rtl = document.documentElement.dir === 'rtl';

    box = document.createElement('div');
    box.className = 'sr-consent';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'false');
    box.setAttribute('aria-label', t.title);
    if (rtl) box.setAttribute('dir', 'rtl');

    var h = document.createElement('p');
    h.className = 'sr-consent__title';
    h.textContent = t.title;

    var p = document.createElement('p');
    p.className = 'sr-consent__body';
    p.textContent = t.body;

    var row = document.createElement('div');
    row.className = 'sr-consent__row';

    var yes = document.createElement('button');
    yes.type = 'button';
    yes.className = 'sr-consent__btn sr-consent__btn--yes';
    yes.textContent = t.accept;
    yes.addEventListener('click', function () { write('granted'); load(); close(); });

    var no = document.createElement('button');
    no.type = 'button';
    no.className = 'sr-consent__btn';
    no.textContent = t.reject;
    no.addEventListener('click', function () { write('denied'); close(); });

    row.appendChild(yes);
    row.appendChild(no);
    box.appendChild(h);
    box.appendChild(p);
    box.appendChild(row);

    box.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
    document.body.appendChild(box);
    yes.focus();
  }

  function start() {
    var state = read();
    if (state === 'granted') { load(); return; }
    if (state === 'denied') return;
    build();
  }

  document.addEventListener('click', function (event) {
    if (event.target.closest && event.target.closest('.sr-consent-open')) {
      event.preventDefault();
      build();
    }
  }, true);

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();

  window.srConsent = {
    open: build,
    reset: function () { write(''); try { localStorage.removeItem(KEY); } catch (e) {} },
    state: read
  };
})()
