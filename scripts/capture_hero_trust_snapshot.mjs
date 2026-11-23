import { spawn } from 'node:child_process';
import { writeFileSync, mkdtempSync, rmSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { setTimeout as sleep } from 'node:timers/promises';
import http from 'node:http';
import net from 'node:net';
import { readFileSync as readFile, statSync } from 'node:fs';
import { extname } from 'node:path';

const ARTIFACT_DIR = 'C:\\Users\\msali\\.gemini\\antigravity\\brain\\0962b263-8a8f-494f-862a-6c196d69d79e';
const OUT_PATH = join(ARTIFACT_DIR, 'hero_integrated_trust_metrics_live.png');
const SITE = join(process.cwd(), '_site');

const BROWSER_CANDIDATES = [
    process.env.SR_BROWSER,
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    '/usr/bin/google-chrome',
    '/usr/bin/chromium',
].filter(Boolean);

const EDGE = BROWSER_CANDIDATES.find(p => existsSync(p));

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

function startServer(port) {
    const server = http.createServer((req, res) => {
        let p = decodeURIComponent(req.url.split('?')[0]);
        if (p.endsWith('/')) p += 'index.html';
        const file = join(SITE, p);
        if (!file.startsWith(SITE) || !existsSync(file) || !statSync(file).isFile()) {
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.end('not found');
            return;
        }
        res.writeHead(200, { 'Content-Type': MIME[extname(file).toLowerCase()] || 'application/octet-stream' });
        res.end(readFile(file));
    });
    return new Promise(r => server.listen(port, '127.0.0.1', () => r(server)));
}

async function main() {
    if (!EDGE) {
        console.error('No browser found');
        process.exit(1);
    }
    const cdpPort = await findFreePort(9266);
    const httpPort = await findFreePort(8133);
    const server = await startServer(httpPort);
    const profile = mkdtempSync(join(tmpdir(), 'sr-snap-hero-'));

    const child = spawn(EDGE, [
        '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage',
        '--no-first-run', '--no-default-browser-check', '--disable-extensions',
        '--remote-debugging-port=' + cdpPort,
        '--window-size=1500,950',
        '--user-data-dir=' + profile,
        '--headless=new',
        'about:blank'
    ], { stdio: 'ignore' });

    for (let i = 0; i < 40; i++) {
        try {
            const r = await fetch(`http://127.0.0.1:${cdpPort}/json/version`);
            if (r.ok) break;
        } catch { }
        await sleep(250);
    }

    const url = `http://127.0.0.1:${httpPort}/index.html`;
    const target = await fetch(`http://127.0.0.1:${cdpPort}/json/new?${encodeURIComponent(url)}`, { method: 'PUT' })
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

    await send('Page.enable');
    await send('Runtime.enable');
    await send('Page.navigate', { url });

    for (let i = 0; i < 20; i++) {
        await sleep(300);
        const ready = await send('Runtime.evaluate', { expression: 'document.readyState', returnByValue: true });
        if (ready?.result?.value === 'complete') break;
    }

    await sleep(2000);

    // Scroll to position showing bottom of hero and trust metrics seamlessly
    await send('Runtime.evaluate', {
        expression: `
            const tm = document.getElementById('trust-metrics');
            if (tm) {
                tm.scrollIntoView({ behavior: 'instant', block: 'center' });
            }
        `
    });

    await sleep(1000);

    const shot = await send('Page.captureScreenshot', { format: 'png' });
    if (shot && shot.data) {
        const buf = Buffer.from(shot.data, 'base64');
        writeFileSync(OUT_PATH, buf);
        console.log('Snapshot written to:', OUT_PATH, 'Size:', buf.length, 'bytes');
    }

    ws.close();
    child.kill();
    if (typeof server.closeAllConnections === 'function') server.closeAllConnections();
    server.close();
    try { rmSync(profile, { recursive: true, force: true }); } catch { }
}

main().catch(err => {
    console.error(err);
    process.exit(1);
});
