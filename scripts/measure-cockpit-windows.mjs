// Measure the hero cockpit height across every deployed language.
//
// Item 22b in PLAN.md waited for these numbers: the cockpit's height is driven by
// translated copy, so ar/en/nl/de do not settle at the same value and a "ceiling"
// cannot be chosen by eye. Runs one headless Chrome, walks the locale list, and
// prints the measured heights as JSON plus a summary.
//
// Usage:  node scripts/measure-cockpit-windows.mjs [baseUrl] [viewportWidth] [viewportHeight]
// Default base: http://127.0.0.1:8123  (serve the repo root first)
import { spawn } from 'node:child_process';
import path from 'node:path';

const BASE = process.argv[2] || 'http://127.0.0.1:8123';
const VW = Number(process.argv[3] || 1440);
const VH = Number(process.argv[4] || 900);
const PORT = 9344;
const CHROME = process.env.CHROME_PATH || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const LANGS = ['', 'en', 'nl', 'de', 'fr', 'es', 'sv', 'tr', 'ar'];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const chrome = spawn(CHROME, ['--headless=new', '--disable-gpu', '--hide-scrollbars',
  `--remote-debugging-port=${PORT}`,
  '--user-data-dir=' + path.join(process.cwd(), 'scratch', 'cdp-cockpit'), 'about:blank'],
  { stdio: 'ignore' });

async function main() {
  let target = null;
  for (let i = 0; i < 60 && !target; i++) {
    await sleep(250);
    try {
      const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
      target = list.find((x) => x.type === 'page');
    } catch { /* not up yet */ }
  }
  if (!target) throw new Error('chrome did not expose a page target');

  const ws = new WebSocket(target.webSocketDebuggerUrl);
  let id = 0;
  const pending = new Map();
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  };
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('CDP websocket did not open within 20s')), 20000);
    ws.onopen = () => { clearTimeout(timer); resolve(); };
    ws.onerror = (e) => { clearTimeout(timer); reject(new Error('CDP websocket error: ' + (e.message || 'unknown'))); };
  });
  const send = (method, params = {}) => new Promise((res, rej) => {
    const i = ++id;
    const timer = setTimeout(() => { pending.delete(i); rej(new Error(`${method} timed out after 30s`)); }, 30000);
    pending.set(i, (m) => { clearTimeout(timer); res(m); });
    ws.send(JSON.stringify({ id: i, method, params }));
  });

  await send('Emulation.setDeviceMetricsOverride',
    { width: VW, height: VH, deviceScaleFactor: 1, mobile: false });
  // The site registers a Service Worker. Once it controls the tab it answers
  // navigations from its own cache, which stalled every page after the second
  // one and made the sweep look like a hang. Measurements must hit the network.
  await send('Network.enable');
  await send('Network.setBypassServiceWorker', { bypass: true });

  const probe = `(() => {
    const box = document.querySelector('.concept-3-cockpit');
    if (!box) return JSON.stringify({ missing: true });
    const r = box.getBoundingClientRect();
    const cs = getComputedStyle(box);
    const kids = [...box.querySelectorAll(':scope > .c3-cockpit-layout > *')].map((el) => ({
      cls: (el.className || '').split(' ')[0],
      h: Math.round(el.getBoundingClientRect().height),
      scrollH: el.scrollHeight,
    }));
    return JSON.stringify({
      cockpitH: Math.round(r.height),
      cockpitW: Math.round(r.width),
      scrollH: box.scrollHeight,
      maxH: cs.maxHeight,
      kids,
    });
  })()`;

  const rows = [];
  const waitReady = async (budgetMs = 25000) => {
    const until = Date.now() + budgetMs;
    while (Date.now() < until) {
      const r = await send('Runtime.evaluate', { expression: 'document.readyState', returnByValue: true });
      if (r.result.result.value === 'complete') return true;
      await sleep(500);
    }
    return false;
  };

  for (const lang of LANGS) {
    const url = `${BASE}/${lang ? lang + '/' : ''}index.html`;
    console.log(`# ${url}`);
    try {
      // Release the previous document first: these pages take 5-9 s just to
      // commit a navigation, so reusing a busy tab made later pages look frozen.
      await send('Page.navigate', { url: 'about:blank' });
      await sleep(700);
      await send('Page.navigate', { url });
      const ready = await waitReady();
      await sleep(700);
      const m = await send('Runtime.evaluate', { expression: probe, returnByValue: true });
      const val = JSON.parse(m.result.result.value);
      rows.push({ lang: lang || 'ar', ready, ...val });
    } catch (err) {
      rows.push({ lang: lang || 'ar', error: err.message });
    }
    console.log(JSON.stringify(rows[rows.length - 1]));
  }

  const good = rows.filter((r) => !r.missing && !r.error);
  const failed = rows.filter((r) => r.error);
  const heights = good.map((r) => r.cockpitH).sort((a, b) => a - b);
  console.log('\n--- summary ---');
  console.log(`measured ${good.length} pages at ${VW}x${VH}`);
  console.log(`min ${heights[0]}  median ${heights[Math.floor(heights.length / 2)]}  max ${heights[heights.length - 1]}  spread ${heights[heights.length - 1] - heights[0]}`);
  for (const r of good) {
    const tall = r.kids.slice().sort((a, b) => b.h - a.h)[0];
    console.log(`  ${r.lang.padEnd(3)} ${String(r.cockpitH).padStart(4)}px  tallest child: ${tall ? tall.cls + ' ' + tall.h + 'px' : '-'}`);
  }
  if (failed.length) console.log('  unreachable: ' + failed.map((r) => `${r.lang} (${r.error})`).join(', '));
  ws.close(); chrome.kill(); process.exit(0);
}

main().catch((e) => { console.error('ERR', e.message); chrome.kill(); process.exit(1); });
