// Compare the rendered advance width of text set in both families, to 2 decimals.
const port = 9333;
(async () => {
  const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const page = list.find(t => t.type === 'page' && t.url.includes('8150'));
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0; const waiting = new Map();
  const send = (m, p) => new Promise(res => { const i = ++id; waiting.set(i, res); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
  ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && waiting.has(m.id)) { waiting.get(m.id)(m.result); waiting.delete(m.id); } };
  await new Promise(r => ws.onopen = r);
  await send('Emulation.setDeviceMetricsOverride', { width: 1600, height: 900, deviceScaleFactor: 1, mobile: false });
  await new Promise(r => setTimeout(r, 1500));

  const expr = `(async () => {
    await document.fonts.ready;
    // a canvas gives the pure advance width of the font, with no layout noise
    const c = document.createElement('canvas').getContext('2d');
    const sample = { alex: 'S&R CoreSync — هويات بصرية', jak: 'Enterprise Cloud ERP 129,00 €' };
    const out = {};
    for (const [k, text] of Object.entries(sample)) {
      const fam = k === 'alex' ? 'Alexandria' : '"Plus Jakarta Sans"';
      c.font = '500 40px ' + fam;
      out[k] = +c.measureText(text).width.toFixed(3);
    }
    // and the live elements that actually use each family
    const pick = sel => { const e = document.querySelector(sel); if (!e) return null;
      const r = e.getBoundingClientRect(); const cs = getComputedStyle(e);
      return { w: +r.width.toFixed(2), h: +r.height.toFixed(2), ff: cs.fontFamily.split(',')[0].replace(/"/g,''), fw: cs.fontWeight, fs: cs.fontSize }; };
    return { canvas: out, h1: pick('h1'), price: pick('.price, .plan-price, [class*="price"]'), btn: pick('a.btn, button.btn') };
  })()`;
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
  console.log(JSON.stringify(r.result.value));
  ws.close();
})();
