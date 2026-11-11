/* S&R CoreSync - interface sound.
   Rules baked in: off until the visitor asks for it, one sound per action,
   nothing longer than 160 ms, no loops, no reverb tails, no sound on load,
   scroll or hover. Generated with WebAudio, so there is no file to download and
   nothing for the CSP to block. */
(function () {
  'use strict';
  if (window.__srSound) return;
  window.__srSound = true;

  var KEY = 'sr_sound_v1';
  var ctx = null, enabled = false, last = 0;

  function readPref() {
    try { return localStorage.getItem(KEY) === 'on'; } catch (e) { return false; }
  }
  function writePref(on) {
    try { localStorage.setItem(KEY, on ? 'on' : 'off'); } catch (e) { /* private mode */ }
  }
  function audio() {
    if (!ctx) {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      try { ctx = new AC(); } catch (e) { return null; }
    }
    if (ctx.state === 'suspended' && ctx.resume) ctx.resume();
    return ctx;
  }

  function tone(freq, dur, gain, slideTo) {
    var c = audio();
    if (!c) return;
    var t = c.currentTime;
    var osc = c.createOscillator();
    var amp = c.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(freq, t);
    if (slideTo) osc.frequency.exponentialRampToValueAtTime(slideTo, t + dur);
    amp.gain.setValueAtTime(0.0001, t);
    amp.gain.exponentialRampToValueAtTime(gain, t + 0.008);     // soft attack
    amp.gain.exponentialRampToValueAtTime(0.0001, t + dur);     // clean decay
    osc.connect(amp).connect(c.destination);
    osc.start(t);
    osc.stop(t + dur + 0.02);
  }

  function tick(dur, gain) {
    var c = audio();
    if (!c) return;
    var buffer = c.createBuffer(1, Math.ceil(c.sampleRate * dur), c.sampleRate);
    var data = buffer.getChannelData(0);
    for (var i = 0; i < data.length; i++) {
      data[i] = (Math.random() * 2 - 1) * (1 - i / data.length);   // short decay
    }
    var src = c.createBufferSource();
    var filter = c.createBiquadFilter();
    var amp = c.createGain();
    filter.type = 'bandpass';
    filter.frequency.value = 1800;
    amp.gain.value = gain;
    src.buffer = buffer;
    src.connect(filter).connect(amp).connect(c.destination);
    src.start();
  }

  var RECIPES = {
    tap: function () { tick(0.02, 0.05); tone(1200, 0.045, 0.035); },
    switch: function () { tone(320, 0.09, 0.038, 900); },
    toggle: function () { tone(760, 0.05, 0.032); },
    success: function () { tone(660, 0.09, 0.045); setTimeout(function () { tone(880, 0.1, 0.045); }, 70); },
    error: function () { tone(220, 0.12, 0.05); },
    copy: function () { tone(880, 0.05, 0.034); }
  };

  function play(name) {
    if (!enabled) return;
    var now = Date.now();
    if (now - last < 40) return;                 // never stack sounds
    last = now;
    if (RECIPES[name]) RECIPES[name]();
  }

  var SWITCHERS = '[role="tab"], .sp-tab, .showcase-tab-btn, .nav-more-btn, .tab-btn, .software-filter-bar button';
  var TOGGLERS = '.accordion-button, [aria-expanded], details > summary, .faq-question, .faq-item button';

  document.addEventListener('click', function (event) {
    var target = event.target;
    if (!target || !target.closest) return;
    if (target.closest('.sr-sound-toggle')) return;
    if (target.closest(TOGGLERS)) { play('toggle'); return; }
    if (target.closest(SWITCHERS)) { play('switch'); return; }
    if (target.closest('[data-copy], .copy-btn, [class*="copy-link"]')) { play('copy'); return; }
    if (target.closest('a[href], button')) { play('tap'); }
  }, true);

  function paint(button) {
    button.setAttribute('aria-pressed', enabled ? 'true' : 'false');
    button.classList.toggle('is-on', enabled);
    button.innerHTML = enabled
      ? '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 9v6h3l4 4V5L7 9H4z"/><path d="M16 8a5 5 0 010 8"/><path d="M18.5 5.5a9 9 0 010 13"/></svg>'
      : '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 9v6h3l4 4V5L7 9H4z"/><path d="M16 9l5 6M21 9l-5 6"/></svg>';
  }

  function setEnabled(on) {
    enabled = !!on;
    writePref(enabled);
    var button = document.querySelector('.sr-sound-toggle');
    if (button) paint(button);
    if (enabled) play('toggle');
  }

  function buildToggle() {
    if (document.querySelector('.sr-sound-toggle')) return;
    var host = document.querySelector('.sr-intent') || document.querySelector('.sr-jump');
    if (!host) return;
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'sr-sound-toggle';
    button.setAttribute('aria-pressed', 'false');
    button.setAttribute('aria-label', 'Interface sound');
    button.setAttribute('title', 'Interface sound');
    button.addEventListener('click', function (event) {
      event.preventDefault();
      setEnabled(!enabled);
    });
    host.appendChild(button);
    paint(button);
  }

  function start() {
    enabled = readPref();
    buildToggle();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();

  window.srSound = { play: play, setEnabled: setEnabled, isEnabled: function () { return enabled; } };
})();
