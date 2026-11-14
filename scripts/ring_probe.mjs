// Is the ring pseudo-element actually painted, or clipped by the dock?
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
  await new Promise(r => setTimeout(r, 2000));

  const expr = `(() => {
    const it = document.querySelector('.apple-dock-item[hreflang="en"]');
    if (!it) return { none: true };
    const a = getComputedStyle(it, '::after');
    const d = document.getElementById('appleMacosDock');
    const dc = d ? getComputedStyle(d) : null;
    const r = it.getBoundingClientRect();
    return {
      pulsing: it.classList.contains('sr-lang-hint-pulse'),
      rect: [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)],
      afterContent: a.content, afterBorder: a.borderTopWidth + ' ' + a.borderTopColor,
      afterOpacity: a.opacity, afterInset: a.insetTop, afterAnim: a.animationName,
      dockOverflow: dc ? dc.overflow : null,
      hintCssLoaded: [...document.styleSheets].some(s => { try { return [...s.cssRules].some(x => x.cssText && x.cssText.includes('sr-lang-hint-pulse')); } catch (e) { return false; } })
    };
  })()`;
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  console.log(JSON.stringify(r.result.value));
  ws.close();
})();
