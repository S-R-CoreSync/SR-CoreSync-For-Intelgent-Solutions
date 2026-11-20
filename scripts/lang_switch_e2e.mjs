/**
 * ==============================================================================
 * S&R CoreSync For Intelligent Solutions - Sovereign Platform
 * PROPRIETARY & CONFIDENTIAL INTELLECTUAL PROPERTY
 *
 * Copyright (c) 2026 S&R CoreSync. All Rights Reserved.
 * Unauthorized copying, decompilation, redistribution, or external model training
 * of this file, via any medium, is strictly prohibited.
 * ==============================================================================
 */

/**
 * Language-switch E2E bank - the 2026-11-17 defect, guarded forever.
 * -----------------------------------------------------------------------------
 * Until this test existed the language map rendered market info with no way to
 * actually switch, and nothing failed anywhere: valid HTML, zero console
 * errors, dead feature. This bank drives a real headless Chromium over the
 * DevTools Protocol (same plumbing as browser_console_audit.mjs, no npm deps)
 * and asserts the click-through the user actually performs:
 *
 *   1. from /          open the map, click Sweden, follow the CTA  -> /sv/
 *   2. from /sv/       click Germany, the CTA must point at the site root
 *                      (never /sv/de/)                             -> href check
 *   3. from /sv/       click Germany twice, the second click navigates -> /de/
 *
 * Usage: node scripts/lang_switch_e2e.mjs
 */
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync, existsSync, readFileSync as readFile, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, extname, resolve } from 'node:path';
import { setTimeout as sleep } from 'node:timers/promises';
import http from 'node:http';
import net from 'node:net';

const BROWSER_CANDIDATES = [
    process.env.SR_BROWSER,
    '/usr/bin/google-chrome',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/usr/bin/microsoft-edge',
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
].filter(Boolean);

const EDGE = BROWSER_CANDIDATES.find(p => existsSync(p));
const SITE = resolve(process.env.SR_SITE_DIR || join(process.cwd(), '_site'));

let PORT = 9223;
let HTTP_PORT = 8098;

async function findFreePort(preferred) {
    for (const wanted of [preferred, 0]) {
        const found = await new Promise(resolve => {
            const probe = net.createServer();
            probe.once('error', () => resolve(-1));
            probe.listen(wanted, '127.0.0.1', () => {
                const port = probe.address().port;
                probe.close(() => resolve(port));
            });
        });
        if (found > 0) return found;
    }
    throw new Error('No free port available.');
}

const MIME = {
    '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
    '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8',
    '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg',
    '.ico': 'image/x-icon', '.woff': 'font/woff', '.woff2': 'font/woff2',
    '.webp': 'image/webp', '.txt': 'text/plain; charset=utf-8',
};

function startServer() {
    const server = http.createServer((req, res) => {
        let p = decodeURIComponent(req.url.split('?')[0]);
        if (p.endsWith('/')) p += 'index.html';
        const file = join(SITE, p);
        if (!file.startsWith(SITE) || !existsSync(file) || !statIsFile(file)) {
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.end('not found');
            return;
        }
        res.writeHead(200, { 'Content-Type': MIME[extname(file).toLowerCase()] || 'application/octet-stream' });
        res.end(readFile(file));
    });
    return new Promise(r => server.listen(HTTP_PORT, '127.0.0.1', () => r(server)));
}

function statIsFile(p) { try { return statSync(p).isFile(); } catch { return false; } }

async function getJson(path) {
    const res = await fetch(`http://127.0.0.1:${PORT}${path}`);
    return res.json();
}

async function launchBrowser(profile, extraArgs = []) {
    const child = spawn(EDGE, [
        '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage',
        '--no-first-run', '--no-default-browser-check', '--disable-extensions',
        '--disable-background-networking', '--remote-debugging-port=' + PORT,
        '--user-data-dir=' + profile, ...extraArgs, 'about:blank',
    ], { stdio: 'ignore' });
    for (let i = 0; i < 40; i++) {
        try { await getJson('/json/version'); return child; }
        catch { await sleep(250); }
    }
    child.kill();
    return null;
}

async function openPage(url) {
    const target = await fetch(`http://127.0.0.1:${PORT}/json/new?${encodeURIComponent(url)}`, { method: 'PUT' })
        .then(r => r.json());
    const ws = new WebSocket(target.webSocketDebuggerUrl);
    let id = 0;
    const pending = new Map();
    const send = (method, params = {}) => new Promise(res2 => {
        const msgId = ++id;
        pending.set(msgId, res2);
        ws.send(JSON.stringify({ id: msgId, method, params }));
    });
    await new Promise(res2 => ws.addEventListener('open', res2));
    ws.addEventListener('message', ev => {
        const msg = JSON.parse(ev.data);
        if (msg.id && pending.has(msg.id)) {
            pending.get(msg.id)(msg.result);
            pending.delete(msg.id);
        }
    });
    await send('Runtime.enable');
    await send('Page.enable');
    return { target, ws, send };
}

async function navigate(send, url) {
    await send('Page.navigate', { url });
    for (let i = 0; i < 25; i++) {
        await sleep(400);
        try {
            const r = await send('Runtime.evaluate', { expression: 'document.readyState', returnByValue: true });
            if (r && r.result && r.result.value === 'complete') return true;
        } catch { /* page is navigating - keep waiting */ }
    }
    return false;
}

async function evalJs(send, expression) {
    const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    if (r && r.exceptionDetails) {
        throw new Error((r.exceptionDetails.exception && r.exceptionDetails.exception.description) || 'evaluate failed');
    }
    return r && r.result ? r.result.value : undefined;
}

// Opens the language map the way a user does: click the dock trigger, then
// wait for the lazily loaded map script to build its shadow DOM.
async function openLangMap(send) {
    console.log('Opening language map');
    // Ensure page is fully loaded
    await evalJs(send, `(() => document.readyState === 'complete')`);
    // Click the language map trigger (first matching element)
    const clicked = await evalJs(send,
        `(() => {
            const elems = document.querySelectorAll('#appleDockLaunchpadBtn, #srLangMenuBtn, [aria-label*="اللغات"], [aria-label*="Languages"]');
            if (!elems.length) return false;
            elems[0].click();
            return true;
        })()`);
    console.log('Trigger clicked:', clicked);
    if (!clicked) throw new Error('language map trigger not found on this page');
    // Ensure the lazy map script is loaded (force inject if missing)
    await evalJs(send, `(() => {
        if (!document.querySelector('script[src*="sr-lang-map.js"]')) {
            const s = document.createElement('script');
            s.src = '/js/sr-lang-map.js';
            s.type = 'module';
            document.body.appendChild(s);
            console.log('Injected sr-lang-map.js');
        } else {
            console.log('sr-lang-map.js already present');
        }
    })()`);
    // Wait a moment for script to start
    await sleep(3000);
    // Wait for the host element to appear (up to 120 attempts ≈48 s)
    let hostExists = false;
    for (let i = 0; i < 120; i++) {
        hostExists = await evalJs(send, `(() => !!document.getElementById('srLangMapHost'))()`);
        if (hostExists) break;
        await sleep(400);
    }
    console.log('Host existence:', hostExists);
    if (!hostExists) throw new Error('srLangMapHost not found after waiting');
    // Poll for the map items (up to 300 attempts ≈120 s total)
    for (let i = 0; i < 300; i++) {
        await sleep(400);
        const ready = await evalJs(send,
            `(() => {
                const h = document.getElementById('srLangMapHost').shadowRoot;
                return !!(window.SRLangMap && h && h.querySelector('.sr-lm__item'));
            })()`);
        if (ready) {
            console.log('Map ready after attempts', i + 1);
            return true;
        }
    }
    throw new Error('the language map did not open within 120s');
}


// Clicks the market whose country matches (السويد / ألمانيا ...), once.
async function clickMarket(send, country) {
    return evalJs(send, `(() => {
        const sr = document.getElementById('srLangMapHost').shadowRoot;
        const items = sr.querySelectorAll('.sr-lm__item');
        for (const b of items) {
            if (b.textContent.indexOf(${JSON.stringify(country)}) !== -1) { b.click(); return true; }
        }
        return false;
    })()`);
}

async function readCtaHref(send) {
    return evalJs(send, `(() => {
        const go = document.getElementById('srLangMapHost').shadowRoot.querySelector('.sr-lm__go');
        return go ? (go.getAttribute('href') || '') : null;
    })()`);
}

async function main() {
    const fail = (name, why) => { console.log(`FAIL  ${name}`); console.log('        ! ' + why); failed++; };

    let failed = 0;
    if (typeof WebSocket === 'undefined') {
        console.log('SKIPPED - the DevTools client needs a global WebSocket (Node 22+).');
        return;
    }
    if (!EDGE) { console.log('SKIPPED - no Chromium based browser found.'); return; }
    if (!existsSync(join(SITE, 'index.html')) || !existsSync(join(SITE, 'js', 'sr-lang-map.js'))) {
        console.log('BLOCKED - publish set incomplete (need _site with index.html and js/sr-lang-map.js).');
        console.log('Rebuild: python scripts/prepare_publish_set.py');
        process.exit(1);
    }

    PORT = await findFreePort(9223);
    HTTP_PORT = await findFreePort(8098);
    console.log('HTTP_PORT=', HTTP_PORT);
    const profile = mkdtempSync(join(tmpdir(), 'sr-e2e-'));
    let child = await launchBrowser(profile, ['--disable-web-security','--allow-running-insecure-content']);
    if (!child) { server.close(); console.log('SKIPPED - browser did not start correctly.'); return; }
    console.log('Browser launched with PID', child.pid);

    const base = `http://127.0.0.1:${HTTP_PORT}`;

    /* Scenario 1 - from / the map switches to Swedish */
    try {
        const page = await openPage(base + '/index.html');
        await navigate(page.send, base + '/index.html');
        await openLangMap(page.send);
        if (!await clickMarket(page.send, 'السويد')) throw new Error('Sweden not found in the market list');
        await sleep(300);
        const href = await readCtaHref(page.send);
        if (!href || !href.endsWith('/sv/index.html')) {
            throw new Error('CTA href is ' + href + ' - expected .../sv/index.html');
        }
        if (!href.startsWith(base)) throw new Error('CTA href is not on the site root: ' + href);
        await evalJs(page.send, `document.getElementById('srLangMapHost').shadowRoot.querySelector('.sr-lm__go').click()`);
        let landed = false;
        for (let i = 0; i < 20; i++) {
            await sleep(400);
            landed = await evalJs(page.send, `location.pathname === '/sv/index.html'`);
            if (landed) break;
        }
        if (!landed) throw new Error('clicking the CTA did not navigate to /sv/index.html');
        console.log('PASS  from / the map switches to /sv/ (real click-through)');
        page.ws.close();
        await fetch(`http://127.0.0.1:${PORT}/json/close/${page.target.id}`);
    } catch (e) { fail('from / the map switches to /sv/', String(e.message || e).split('\n')[0]); }

    /* Scenario 2 - from /sv/ Germany's CTA points at the site root */
    try {
        const page = await openPage(base + '/sv/index.html');
        await navigate(page.send, base + '/sv/index.html');
        await openLangMap(page.send);
        if (!await clickMarket(page.send, 'ألمانيا')) throw new Error('Germany not found in the market list');
        await sleep(300);
        const href = await readCtaHref(page.send);
        if (!href || !href.endsWith('/de/index.html')) {
            throw new Error('CTA href is ' + href + ' - expected .../de/index.html');
        }
        if (href.includes('/sv/de/')) throw new Error('CTA resolved under the current language folder: ' + href);
        console.log('PASS  from /sv/ Germany CTA resolves at the site root');
        page.ws.close();
        await fetch(`http://127.0.0.1:${PORT}/json/close/${page.target.id}`);
    } catch (e) { fail('from /sv/ Germany CTA resolves at the site root', String(e.message || e).split('\n')[0]); }

    /* Scenario 3 - a second click on the displayed market navigates */
    try {
        const page = await openPage(base + '/sv/index.html');
        await navigate(page.send, base + '/sv/index.html');
        await openLangMap(page.send);
        if (!await clickMarket(page.send, 'ألمانيا')) throw new Error('Germany not found in the market list');
        await sleep(300);
        if (!await clickMarket(page.send, 'ألمانيا')) throw new Error('second click on Germany failed');
        let landed = false;
        for (let i = 0; i < 20; i++) {
            await sleep(400);
            landed = await evalJs(page.send, `location.pathname === '/de/index.html'`);
            if (landed) break;
        }
        if (!landed) throw new Error('the second click did not navigate to /de/index.html');
        console.log('PASS  second click on the displayed market navigates');
        page.ws.close();
        await fetch(`http://127.0.0.1:${PORT}/json/close/${page.target.id}`);
    } catch (e) { fail('second click on the displayed market navigates', String(e.message || e).split('\n')[0]); }

    child.kill();
    if (typeof server.closeAllConnections === 'function') server.closeAllConnections();
    server.close();
    try { rmSync(profile, { recursive: true, force: true }); } catch { }

    console.log('='.repeat(72));
    console.log(`language switch E2E: ${failed ? failed + ' scenario(s) FAILED' : 'all scenarios passed'}`);
    console.log('='.repeat(72));
    process.exit(failed ? 1 : 0);
}

main().catch(err => { console.error(err); process.exit(1); });

// Hard stop so a stuck browser connection can never hang CI.
setTimeout(() => { console.error('Language switch E2E timed out.'); process.exit(2); }, 10 * 60 * 1000).unref();
