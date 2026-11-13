// Try two reorder candidates on the live header, measure each, keep a shot of each.
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
    const pick = s => { const e = h.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect();
      return { x: Math.round(r.left), right: Math.round(r.right), w: Math.round(r.width) }; };
    const row = h.querySelector('.header-row-layout');
    return { brand: pick('.header-col-brand'), nav: pick('.header-col-nav'), rowDir: getComputedStyle(row).direction,
             order: { brand: getComputedStyle(h.querySelector('.header-col-brand')).order,
                      nav: h.querySelector('.header-col-nav') ? getComputedStyle(h.querySelector('.header-col-nav')).order : null } };
  })()`;

  const apply = async css => {
    await send('Runtime.evaluate', { expression: `(() => { let s=document.getElementById('probe-hdr'); if(s) s.remove();
      s=document.createElement('style'); s.id='probe-hdr'; s.textContent=${JSON.stringify(css)}; document.head.appendChild(s);
      return true; })()`, returnByValue: true });
    await new Promise(r => setTimeout(r, 700));
    const m = await send('Runtime.evaluate', { expression: probe, returnByValue: true });
    return m.result.value;
  };

  const shot = async name => {
    const s = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(`${outDir}/${name}.png`, Buffer.from(s.data, 'base64'));
  };

  console.log('CURRENT ', JSON.stringify(await apply('/* none */')));
  await shot('hdr-0-current');

  const A = `html[lang="ar"] .header-col-brand{order:0 !important}`;
  console.log('A brand:0 ', JSON.stringify(await apply(A)));
  await shot('hdr-1-brand-first');

  const B = `html[lang="ar"] .header-col-brand{order:0 !important}
             html[lang="ar"] .header-col-nav{order:1 !important}
             html[lang="ar"] .header-row-layout{justify-content:space-between !important}`;
  console.log('B +nav  ', JSON.stringify(await apply(B)));
  await shot('hdr-2-brand-first-nav');

  ws.close();
})();
