// Measure + screenshot the bottom row at three widths, in one session.
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

  const expr = `(() => {
    const g = s => { const e = document.querySelector(s); if (!e) return null;
      const r = e.getBoundingClientRect(), c = getComputedStyle(e);
      return { x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height), cy: Math.round(r.top + r.height/2), pos: c.position, ff: c.fontFamily.split(',')[0].replace(/"/g,'') }; };
    return { vw: innerWidth, tools: g('.sr-tools-capsule'), dock: g('#appleMacosDockWrapper'), metrics: g('.section-trust-metrics'), strip: g('.hero-trust-metrics-strip') };
  })()`;

  for (const [w, h] of [[1600, 900], [1024, 800], [390, 844]]) {
    await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: w < 600 });
    await new Promise(r => setTimeout(r, 1200));
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    console.log(w + ':', JSON.stringify(r.result.value));
    const shot = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(`${outDir}/row-${w}.png`, Buffer.from(shot.data, 'base64'));
  }
  ws.close();
})();
