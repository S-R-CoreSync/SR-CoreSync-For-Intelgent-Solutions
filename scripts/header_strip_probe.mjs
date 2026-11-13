// Remove the inline order and see where the brand lands, at desktop and phone widths.
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

  const probe = `(() => {
    const row = document.querySelector('.header-row-layout');
    const g = e => { const r = e.getBoundingClientRect(); return { x: Math.round(r.left), right: Math.round(r.right), w: Math.round(r.width) }; };
    const brand = row.querySelector('.header-col-brand'), nav = row.querySelector('.header-col-nav');
    const h = document.querySelector('header.tf-header');
    return { vw: innerWidth, brand: g(brand), nav: nav ? g(nav) : null,
             brandOrder: getComputedStyle(brand).order, navOrder: nav ? getComputedStyle(nav).order : null,
             headerH: Math.round(h.getBoundingClientRect().height) };
  })()`;

  const measure = async () => (await send('Runtime.evaluate', { expression: probe, returnByValue: true })).result.value;
  const shot = async n => { const s = await send('Page.captureScreenshot', { format: 'png' }); fs.writeFileSync(`${outDir}/${n}.png`, Buffer.from(s.data, 'base64')); };

  const strip = `(() => { document.querySelectorAll('.header-col-brand, .header-col-nav, .header-col-actions')
      .forEach(e => e.style.removeProperty('order')); return true; })()`;

  // desktop
  await send('Emulation.setDeviceMetricsOverride', { width: 1600, height: 900, deviceScaleFactor: 1, mobile: false });
  await new Promise(r => setTimeout(r, 1000));
  console.log('1600 inline :', JSON.stringify(await measure()));
  await shot('hdr-a-inline');
  await send('Runtime.evaluate', { expression: strip, returnByValue: true });
  await new Promise(r => setTimeout(r, 500));
  console.log('1600 stripped:', JSON.stringify(await measure()));
  await shot('hdr-b-stripped');

  // phone
  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
  await new Promise(r => setTimeout(r, 900));
  console.log('390 stripped :', JSON.stringify(await measure()));
  await shot('hdr-c-phone');

  ws.close();
})();
