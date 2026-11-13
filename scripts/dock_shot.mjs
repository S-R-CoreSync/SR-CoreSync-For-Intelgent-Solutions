// Capture the dock area + the tooltip pseudo-styles, for a before/after proof.
const port = 9333;
const fs = await import('node:fs');
const [out] = process.argv.slice(2);
(async () => {
  const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const page = list.find(t => t.type === 'page' && t.url.includes('8150'));
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0; const waiting = new Map();
  const send = (m, p) => new Promise(res => { const i = ++id; waiting.set(i, res); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
  ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && waiting.has(m.id)) { waiting.get(m.id)(m.result); waiting.delete(m.id); } };
  await new Promise(r => ws.onopen = r);
  await send('Emulation.setDeviceMetricsOverride', { width: 1600, height: 900, deviceScaleFactor: 1, mobile: false });
  await new Promise(r => setTimeout(r, 1800));

  const probe = `(() => {
    const a = document.querySelector('.apple-dock-item');
    const aft = getComputedStyle(a, '::after');
    const r = document.getElementById('appleMacosDockWrapper').getBoundingClientRect();
    return { rect: { x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height) },
             tooltipFont: aft.fontFamily, tooltipSize: aft.fontSize, tooltipColor: aft.color,
             links: document.querySelectorAll('.apple-dock-item').length };
  })()`;
  const m = await send('Runtime.evaluate', { expression: probe, returnByValue: true });
  const v = m.result.value;
  console.log('probe', JSON.stringify(v));

  const clip = { x: Math.max(0, v.rect.x - 14), y: Math.max(0, v.rect.y - 60), width: v.rect.w + 28, height: v.rect.h + 74, scale: 1 };
  const s = await send('Page.captureScreenshot', { format: 'png', clip });
  fs.writeFileSync(out, Buffer.from(s.data, 'base64'));
  console.log('saved', out);
  ws.close();
})();
