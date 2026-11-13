// Where do the menu items sit inside the nav column, and what anchors them?
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
  await new Promise(r => setTimeout(r, 1000));
  await send('Runtime.evaluate', { expression: `document.querySelectorAll('.header-col-brand,.header-col-nav,.header-col-actions').forEach(e=>e.style.removeProperty('order')); true`, returnByValue: true });
  await new Promise(r => setTimeout(r, 400));

  const expr = `(() => {
    const nav = document.querySelector('.header-col-nav');
    const kids = [...nav.querySelectorAll(':scope > *')].map(e => { const r = e.getBoundingClientRect(); const c = getComputedStyle(e);
      return { cls: String(e.className).slice(0, 30), x: Math.round(r.left), w: Math.round(r.width), justify: c.justifyContent, marginStart: c.marginInlineStart }; });
    const box = nav.querySelector('.box-navigation');
    const bc = box && getComputedStyle(box), br = box && box.getBoundingClientRect();
    const menu = nav.querySelector('.nav-menu-main');
    const mr = menu && menu.getBoundingClientRect();
    const first = menu && menu.firstElementChild && menu.firstElementChild.getBoundingClientRect();
    const last = menu && menu.lastElementChild && menu.lastElementChild.getBoundingClientRect();
    return { navKids: kids,
             box: box ? { x: Math.round(br.left), w: Math.round(br.width), justify: bc.justifyContent, display: bc.display } : null,
             menu: mr ? { x: Math.round(mr.left), w: Math.round(mr.width) } : null,
             firstItem: first ? { x: Math.round(first.left), w: Math.round(first.width) } : null,
             lastItem: last ? { x: Math.round(last.right), w: Math.round(last.width) } : null };
  })()`;
  const a = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  console.log('STRIPPED', JSON.stringify(a.result.value, null, 1));

  await send('Runtime.evaluate', { expression: `(() => { const nav=document.querySelector('.header-col-nav'); const b=nav.querySelector('.box-navigation');
     if (b) b.style.setProperty('justify-content','flex-end','important'); const m=nav.querySelector('.nav-menu-main');
     if (m) { m.style.setProperty('margin-inline-start','auto','important'); } return true; })()`, returnByValue: true });
  await new Promise(r => setTimeout(r, 500));
  const b2 = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  console.log('TUNED   ', JSON.stringify(b2.result.value, null, 1));
  const s = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(`${outDir}/hdr-e-end.png`, Buffer.from(s.data, 'base64'));
  ws.close();
})();
