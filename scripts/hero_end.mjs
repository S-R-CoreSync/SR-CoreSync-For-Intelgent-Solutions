// Where does the hero end? Print the first sibling after #home.
const port = 9333;
(async () => {
  const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const page = list.find(t => t.type === 'page' && t.url.includes('8150'));
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0; const waiting = new Map();
  const send = (m, p) => new Promise(res => { const i = ++id; waiting.set(i, res); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
  ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && waiting.has(m.id)) { waiting.get(m.id)(m.result); waiting.delete(m.id); } };
  await new Promise(r => ws.onopen = r);
  const expr = `(() => {
    const h = document.getElementById('home');
    const nx = h.nextElementSibling;
    const pv = h.previousElementSibling;
    return { nextTag: nx && nx.tagName, nextId: nx && nx.id, nextCls: nx && String(nx.className).slice(0,60),
             nextStart: nx && nx.outerHTML.slice(0,140),
             prevTag: pv && pv.tagName, prevCls: pv && String(pv.className).slice(0,60),
             homeParent: h.parentElement.tagName + '.' + String(h.parentElement.className).slice(0,40) };
  })()`;
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  console.log(JSON.stringify(r.result.value, null, 1));
  ws.close();
})();
