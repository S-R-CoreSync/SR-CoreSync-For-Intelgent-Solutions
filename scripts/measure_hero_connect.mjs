// Per-page measurement: open each page in a FRESH tab (/json/new), measure,
// close the tab — a page with a busy main thread cannot poison the next one.
// Browser on 9333, site on 8150 (started separately).
import { appendFileSync } from 'node:fs';
const log = (s) => { appendFileSync('/tmp/hero_connect_log.jsonl', s + '\n'); console.log(s); };
const PAGES = (process.env.SR_PAGES ||
    'index.html,en/index.html,de/index.html,ckb/index.html,tr/index.html,fi/index.html,mt/index.html')
    .split(',');
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

(async () => {
  for (const p of PAGES) {
    const t = await (await fetch('http://127.0.0.1:9333/json/new', { method: 'PUT' })).json();
    let done = false;
    try {
      const ws = new WebSocket(t.webSocketDebuggerUrl);
      let id = 0; const waiting = new Map();
      const send = (m, pa) => new Promise(res => { const i = ++id; waiting.set(i, res); ws.send(JSON.stringify({ id: i, method: m, params: pa })); });
      ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && waiting.has(m.id)) { waiting.get(m.id)(m.result); waiting.delete(m.id); } };
      await Promise.race([new Promise(r => ws.onopen = r), sleep(6000)]);
      await Promise.race([send('Emulation.setDeviceMetricsOverride',
        { width: 1600, height: 900, deviceScaleFactor: 1, mobile: false }), sleep(2000)]);
      // fire-and-forget navigation (its response is not awaited), then wait for load
      send('Page.navigate', { url: `http://127.0.0.1:8150/${p}` }).catch(() => { });
      await sleep(2800);
      const expr = `(() => {
        const g = s => { const e = document.querySelector(s); if (!e) return null;
          const r = e.getBoundingClientRect();
          return { h: Math.round(r.height), visible: !!(e.offsetParent || e.getClientRects().length) }; };
        return { page: ${JSON.stringify(p)},
          hero: g('section#hero'), cockpit: g('.concept-3-cockpit'),
          matrix: g('.hero-actions-2x2'), grid: g('#hero .hero-reference__grid'),
          wrap: g('#hero .content-wrap'), trust: g('section#trust-metrics'),
          marquee: g('.hero-sectors-marquee'),
          next: (() => { const h = document.querySelector('section#hero'); const a = h && h.nextElementSibling;
              return a ? a.tagName + '#' + (a.id || (a.className || '').slice(0, 30)) : null; })() };
      })()`;
      const r = await Promise.race([
        send('Runtime.evaluate', { expression: expr, returnByValue: true }),
        sleep(12000).then(() => ({ result: { value: { page: p, BLOCKED: true } } })),
      ]);
      log(JSON.stringify(r.result.value));
      done = true;
      ws.close();
    } catch (e) {
      log(JSON.stringify({ page: p, error: e.message }));
      done = true;
    }
    await fetch(`http://127.0.0.1:9333/json/close/${t.id}`).catch(() => { });
    if (!done) await sleep(500);
    await sleep(400);
  }
  process.exit(0);
})().catch(e => { console.error('CATCH', e.message); process.exit(1); });
