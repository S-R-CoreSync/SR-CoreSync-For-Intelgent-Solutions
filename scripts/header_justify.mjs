// Three clean variants for the nav box: where does the menu land?
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

  const read = `(() => {
    const nav = document.querySelector('.header-col-nav');
    const box = nav.querySelector('.box-navigation');
    const menu = nav.querySelector('.nav-menu-main');
    const brand = document.querySelector('.header-col-brand').getBoundingClientRect();
    const b = box.getBoundingClientRect(), m = menu.getBoundingClientRect();
    return { navBox: [Math.round(b.left), Math.round(b.right)], menu: [Math.round(m.left), Math.round(m.right)],
             gapToBrand: Math.round(brand.left - m.right), brandLeft: Math.round(brand.left),
             boxDir: getComputedStyle(box).direction, justify: getComputedStyle(box).justifyContent };
  })()`;

  for (const j of ['flex-start', 'flex-end', 'center']) {
    await send('Runtime.evaluate', { expression: `(() => { const b=document.querySelector('.header-col-nav .box-navigation');
        b.style.setProperty('justify-content', ${JSON.stringify(j)}, 'important'); return true; })()`, returnByValue: true });
    await new Promise(r => setTimeout(r, 400));
    const v = await send('Runtime.evaluate', { expression: read, returnByValue: true });
    console.log(j.padEnd(11), JSON.stringify(v.result.value));
    const s = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(`${outDir}/hdr-${j}.png`, Buffer.from(s.data, 'base64'));
  }
  ws.close();
})();
