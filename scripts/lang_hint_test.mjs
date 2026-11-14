// Does the hint now live inside the dock, and is the floating pill gone?
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
  await send('Runtime.evaluate', { expression: `try{localStorage.removeItem('sr_lang_hint_v1')}catch(e){}`, returnByValue: true });
  await send('Page.reload', { ignoreCache: true });
  await new Promise(r => setTimeout(r, 3000));

  const probe = `(() => {
    const ring = document.querySelector('.sr-lang-hint-pulse');
    const pill = document.querySelector('.sr-lang-hint');
    const r = ring ? ring.getBoundingClientRect() : null;
    return {
      ringOn: ring ? (ring.getAttribute('hreflang') || ring.getAttribute('aria-label') || ring.className).slice(0, 40) : null,
      ringBox: r ? { x: Math.round(r.left), y: Math.round(r.top) } : null,
      pillStillThere: !!pill,
      ringCount: document.querySelectorAll('.sr-lang-hint-pulse').length
    };
  })()`;
  console.log('t=3s', JSON.stringify((await send('Runtime.evaluate', { expression: probe, returnByValue: true })).result.value));

  const shot = await send('Page.captureScreenshot', { format: 'png', clip: { x: 560, y: 620, width: 520, height: 130, scale: 2 } });
  (await import('node:fs')).writeFileSync(process.argv[2], Buffer.from(shot.data, 'base64'));

  await new Promise(r => setTimeout(r, 5000));
  console.log('t=8s', JSON.stringify((await send('Runtime.evaluate', { expression: probe, returnByValue: true })).result.value));
  ws.close();
})();
