// Experiment: flip the header to RTL at runtime, measure before and after, keep both shots.
const port = 9333;
const fs = await import('node:fs');
const [outDir] = process.argv.slice(2);
(async () => {
  const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const page = list.find(t => t.type === 'page' && t.url.includes('8150'));
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0; const waiting = new Map();
  const send = (m, p) => new Promise(res => { const i = ++id; waiting.set(i, res); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
  ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && waiting.has(m.id)) { waiting.get(m.id)(m.result); waiting.delete(m.id); } };
  await new Promise(r => ws.onopen = r);
  await send('Emulation.setDeviceMetricsOverride', { width: 1600, height: 900, deviceScaleFactor: 1, mobile: false });
  await new Promise(r => setTimeout(r, 1200));

  const probe = `(() => {
    const h = document.querySelector('header.tf-header');
    const inner = h.querySelector('.header-inner');
    const pick = s => { const e = h.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect();
      return { x: Math.round(r.left), w: Math.round(r.width), y: Math.round(r.top) }; };
    return { kids: [...inner.children].map(e => { const r = e.getBoundingClientRect(); const c = getComputedStyle(e);
               return { cls: String(e.className).slice(0, 34), x: Math.round(r.left), w: Math.round(r.width), display: c.display, order: c.order }; }),
             brand: pick('.brand-logo-site, .brand'), nav: pick('.header-col-nav'), actions: pick('.header-col-actions, .header-tools') };
  })()`;

  const before = await send('Runtime.evaluate', { expression: probe, returnByValue: true });
  console.log('BEFORE', JSON.stringify(before.result.value));
  let shot = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(`${outDir}/hdr-before.png`, Buffer.from(shot.data, 'base64'));

  const css = `header.tf-header, header.tf-header .header-inner, header.tf-header .header-col-nav .nav-menu-main{direction:rtl !important}`;
  await send('Runtime.evaluate', { expression: `(() => { const s=document.createElement('style'); s.id='probe-rtl'; s.textContent=${JSON.stringify(css)}; document.head.appendChild(s); return true; })()`, returnByValue: true });
  await new Promise(r => setTimeout(r, 800));

  const after = await send('Runtime.evaluate', { expression: probe, returnByValue: true });
  console.log('AFTER ', JSON.stringify(after.result.value));
  shot = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(`${outDir}/hdr-after.png`, Buffer.from(shot.data, 'base64'));

  ws.close();
})();
