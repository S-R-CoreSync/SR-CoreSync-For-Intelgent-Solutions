// Which element is forcing the page wider than the viewport?
const port = 9333;
(async () => {
  const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const page = list.find(t => t.type === 'page' && t.url.includes('8150'));
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0; const waiting = new Map();
  const send = (m, p) => new Promise(res => { const i = ++id; waiting.set(i, res); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
  ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && waiting.has(m.id)) { waiting.get(m.id)(m.result); waiting.delete(m.id); } };
  await new Promise(r => ws.onopen = r);
  await new Promise(r => setTimeout(r, 800));
  const expr = `(() => {
    const vw = innerWidth, out = [];
    document.querySelectorAll('*').forEach(e => {
      const r = e.getBoundingClientRect();
      if (r.width > vw + 2 || r.right > vw + 2 || r.left < -2) {
        out.push({ tag: e.tagName, cls: String(e.className).slice(0, 26), w: Math.round(r.width), left: Math.round(r.left), right: Math.round(r.right) });
      }
    });
    return { vw, scrollW: document.documentElement.scrollWidth, bodyW: document.body.getBoundingClientRect().width, offenders: out.slice(0, 12) };
  })()`;
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  console.log(JSON.stringify(r.result.value, null, 1));
  ws.close();
})();
