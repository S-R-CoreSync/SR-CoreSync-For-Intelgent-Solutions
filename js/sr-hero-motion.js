/*
 * S&R CoreSync For Intelligent Solutions - Hero Constellation Field
 * PROPRIETARY & CONFIDENTIAL INTELLECTUAL PROPERTY
 * Copyright (c) 2026 S&R CoreSync. All Rights Reserved.
 * Unauthorized copying, decompilation, redistribution, or external model training is prohibited.
 *
 * The living floor of the hero: up to 55 drifting points, every pair closer
 * than 115px joined by a gold filament, the whole lattice geometry emerging
 * from those joins; a 140px repulsion field around the pointer tears it open
 * as the mouse crosses it. Gold for most points, mint for the rest, each one
 * breathing on its own pulse and glowing through a 10px shadow.
 *
 * Moved verbatim out of index.html so the same engine can be loaded by any
 * page - including the redesign preview - instead of being re-implemented.
 * One source of truth: change the field here and every page follows.
 */
function constellation() { const e = document.getElementById("heroMotionCanvas"); if (!e) return; const t = e.getContext("2d"); if (!t) return; let n = 0, o = 0, i = [], a = null, s = { x: null, y: null, radius: 140 }; function d() { const t = e.parentElement; t && (n = e.width = t.clientWidth, o = e.height = t.clientHeight, function () { i = []; const e = Math.min(55, Math.floor(n * o / 22e3)); for (let t = 0; t < e; t++)i.push({ x: Math.random() * n, y: Math.random() * o, vx: .45 * (Math.random() - .5), vy: .45 * (Math.random() - .5), radius: 2.2 * Math.random() + 1, color: Math.random() > .4 ? "rgba(212,175,55, " : "rgba(110, 231, 183, ", alpha: .5 * Math.random() + .25, pulse: Math.random() * Math.PI }) }()) } function c() { t.clearRect(0, 0, n, o); for (let e = 0; e < i.length; e++)for (let n = e + 1; n < i.length; n++) { const o = i[e].x - i[n].x, a = i[e].y - i[n].y, s = Math.sqrt(o * o + a * a); if (s < 115) { const o = .22 * (1 - s / 115); t.beginPath(), t.moveTo(i[e].x, i[e].y), t.lineTo(i[n].x, i[n].y), t.strokeStyle = `rgba(212,175,55, ${o})`, t.lineWidth = .85, t.stroke() } } for (let e = 0; e < i.length; e++) { const a = i[e]; if (a.x += a.vx, a.y += a.vy, a.x < 0 && (a.x = n), a.x > n && (a.x = 0), a.y < 0 && (a.y = o), a.y > o && (a.y = 0), null !== s.x && null !== s.y) { const e = s.x - a.x, t = s.y - a.y, n = Math.sqrt(e * e + t * t); if (n < s.radius) { const o = 1.5 * (1 - n / s.radius); a.x -= e / n * o, a.y -= t / n * o } } a.pulse += .03; const d = a.alpha + .15 * Math.sin(a.pulse); t.beginPath(), t.arc(a.x, a.y, a.radius, 0, 2 * Math.PI), t.fillStyle = a.color + Math.max(.1, d) + ")", t.shadowBlur = 10, t.shadowColor = "rgba(212,175,55, 0.4)", t.fill(), t.shadowBlur = 0 } a = requestAnimationFrame(c) } window.addEventListener("resize", d, { passive: !0 }), window.addEventListener("mousemove", t => { const n = e.getBoundingClientRect(); t.clientY >= n.top && t.clientY <= n.bottom ? (s.x = t.clientX - n.left, s.y = t.clientY - n.top) : (s.x = null, s.y = null) }, { passive: !0 }), document.addEventListener("visibilitychange", () => { document.hidden ? a && cancelAnimationFrame(a) : a = requestAnimationFrame(c) }), d(), a = requestAnimationFrame(c) }

function startHeroMotion() {
    const canvas = document.getElementById('heroMotionCanvas');
    if (!canvas) { return; }
    constellation();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startHeroMotion);
} else {
    startHeroMotion();
}
