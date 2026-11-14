// Style fingerprint: prove the extracted sheet did not change a single computed value.
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
  // neutralise the consent banner so its height cannot move fixed elements
  await send('Runtime.evaluate', { expression: (() => {
    document.documentElement.style.setProperty('--privacy-h','0px');
    document.documentElement.style.setProperty('--consent-h','0px');
    document.body.style.setProperty('--privacy-h','0px');
    document.body.style.setProperty('--consent-h','0px');
    const st=document.createElement('style');
    st.textContent='.sr-privacy-banner-wrap,.cc-banner,#cookieConsent{display:none!important}';
    document.head.appendChild(st); return true; })(), returnByValue: true });
  await new Promise(r => setTimeout(r, 700));

  const expr = `(() => {
    const props = ['color','backgroundColor','fontSize','fontFamily','fontWeight','lineHeight','paddingLeft','paddingRight','marginTop','borderRadius','display','position','gridTemplateColumns','boxShadow'];
    const pick = ['h1','h2','.hero','#pricing','.wg-plan','.btn','.section-faq','footer','#appleMacosDockWrapper','.sr-tools-capsule'];
    const out = {};
    for (const sel of pick) {
      const el = document.querySelector(sel);
      if (!el) { out[sel] = null; continue; }
      const cs = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      const rec = { w: +r.width.toFixed(2), h: +r.height.toFixed(2), y: +(r.top + scrollY).toFixed(2) };
      for (const p of props) rec[p] = cs[p];
      out[sel] = rec;
    }
    return out;
  })()`;
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
  console.log(JSON.stringify(r.result.value));
  ws.close();
})();
