// Measure hero parity: #hero height, cockpit height, 2x2 matrix presence and
// visibility, on the ar root and a sample of portals. Reuses the audit's
// proven spawn pattern (free ports, headless chromium via SR_BROWSER).
import { spawn } from 'node:child_process';
import { existsSync, statSync, readFile } from 'node:fs';
import { join, resolve } from 'node:path';
import http from 'node:http';
import net from 'node:net';

const BROWSER = [process.env.SR_BROWSER, '/usr/bin/google-chrome', '/usr/bin/chromium']
    .filter(Boolean).find(p => existsSync(p));
if (!BROWSER) { console.error('no browser found (set SR_BROWSER)'); process.exit(1); }

const SITE = resolve(process.env.SR_SITE_DIR || join(process.cwd(), '_site'));
const PAGES = (process.env.SR_PAGES || ',en,de,ckb,tr,fi').split(',').filter(x => x !== '')
    .map(x => x === '' ? 'index.html' : `${x}/index.html`);

const freePort = async (pref) => {
    for (const p of [pref, 0]) {
        const got = await new Promise(res => {
            const s = net.createServer();
            s.once('error', () => res(-1));
            s.listen(p, '127.0.0.1', () => { const a = s.address().port; s.close(() => res(a)); });
        });
        if (got > 0) return got;
    }
    throw new Error('no free port');
};

const HTTP_PORT = await freePort(8251);
const CDP_PORT = await freePort(9251);
const server = http.createServer((req, res) => {
    const url = decodeURIComponent(req.url.split('?')[0]);
    let fp = join(SITE, url === '/' ? 'index.html' : url);
    try { statSync(fp).isDirectory() && (fp = join(fp, 'index.html')); } catch { }
    readFile(fp, (err, buf) => {
        if (err) { res.writeHead(404); res.end('nf'); return; }
        res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
        res.end(buf);
    });
});
await new Promise(r => server.listen(HTTP_PORT, '127.0.0.1', r));

let proc = null;
const launch = async (headlessFlag) => {
    const profile = `/tmp/sr-hero-parity-${Date.now()}`;
    const child = spawn(BROWSER, [
        '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage',
        '--no-first-run', '--no-default-browser-check', '--disable-extensions',
        '--disable-background-networking',
        `--remote-debugging-port=${CDP_PORT}`, `--user-data-dir=${profile}`,
        headlessFlag, 'about:blank',
    ], { stdio: 'ignore' });
    for (let i = 0; i < 40; i++) {
        try { await (await fetch(`http://127.0.0.1:${CDP_PORT}/json/version`)).json(); return child; }
        catch { await new Promise(r => setTimeout(r, 250)); }
    }
    child.kill();
    return null;
};
proc = await launch('--headless=new') || await launch('--headless');
if (!proc) { console.error('browser did not expose a DevTools endpoint'); process.exit(1); }
const list = await (await fetch(`http://127.0.0.1:${CDP_PORT}/json/list`)).json();
const page = list.find(t => t.type === 'page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0; const waiting = new Map();
const send = (method, params) => new Promise(res => {
    const i = ++id; waiting.set(i, res);
    ws.send(JSON.stringify({ id: i, method, params }));
});
ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && waiting.has(m.id)) { waiting.get(m.id)(m.result); waiting.delete(m.id); }
};
await new Promise(r => ws.onopen = r);

await send('Emulation.setDeviceMetricsOverride',
    { width: 1600, height: 900, deviceScaleFactor: 1, mobile: false });

const out = [];
for (const p of PAGES) {
    await send('Page.navigate', { url: `http://127.0.0.1:${HTTP_PORT}/${p}` });
    await new Promise(r => setTimeout(r, 2600));
    const expr = `(() => {
      const g = s => { const e = document.querySelector(s); if (!e) return null;
        const r = e.getBoundingClientRect();
        return { h: Math.round(r.height), top: Math.round(r.top), bottom: Math.round(r.bottom),
                 visible: !!(e.offsetParent || e.getClientRects().length) }; };
      const row = s => { const e = document.querySelector(s); return e ? Math.round(e.getBoundingClientRect().height) : null; };
      const m2 = g('.hero-actions-2x2');
      return { page: ${JSON.stringify(p)},
        hero: g('section#hero'), cockpit: g('.concept-3-cockpit'),
        matrix: m2, row1: row('.hero-actions-row'),
        grid: g('#hero .hero-reference__grid'), contentWrap: g('#hero .content-wrap'),
        trust: g('section#trust-metrics'),
        heroBottomGap: (() => { const h = document.querySelector('section#hero'); if (!h) return null;
            const after = h.nextElementSibling; return after ? (after.tagName + '#' + (after.id || '') ) : null; })() };
    })()`;
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    out.push(r.result.value);
    console.log(JSON.stringify(r.result.value));
}
console.log('---');
console.log(JSON.stringify(out.map(o => ({
    page: o.page, heroH: o.hero && o.hero.h, cockpitH: o.cockpit && o.cockpit.h,
    matrixVisible: o.matrix ? o.matrix.visible : null,
    matrixH: o.matrix ? o.matrix.h : null, wrapVisible: o.contentWrap ? o.contentWrap.visible : null,
})), null, 1));
proc.kill('SIGKILL');
server.close();
process.exit(0);
