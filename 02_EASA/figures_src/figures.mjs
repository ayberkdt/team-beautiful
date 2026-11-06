/* EASA report figures in the sunumatik visual language: porcelain-ink palette tokens, chart-theme class contract,
 * arrows from sunumatik core/isaretci.mjs, utility-tier icons only. Every number comes from data.json, which
 * build_figures.py writes from the occurrence catalogue and outputs/tradeoffs/tradeoffs.json — nothing is typed here.
 *   figures.html?fig=F1a|F1b|F2|F3|F4
 * After drawing, the page measures every text box: text-text overlaps and text outside its card go to #audit. */
import { okSvg } from './vendor/core/isaretci.mjs';

const NS = 'http://www.w3.org/2000/svg';
const css = (n) => getComputedStyle(document.body).getPropertyValue(n).trim();
const C = {};
// Print scale: every report figure is drawn at its print width with K px per mm (data.json → print, from
// build_figures.py PRINT_MM), so a font size in px maps to one size in points on the page: pt = px / K / 0.3528.
const K = 960 / 115;                 // 8.35 px per mm
const FS = 24;                       // labels: 8.1 pt on the page
const SMALL = 23;                    // ticks, axis titles, notes: 7.8 pt (report tables are 7.6 pt)
const TITLE = 26;                    // panel titles: 8.8 pt (report body is 9 pt)
let PRINT_PX = {};
const SHORT7 = { '+ mechanical pawl': '+ cable pawl' };
const ICON = 'vendor/charts_icons/icon-library/sprite.svg';

function el(tag, attrs = {}, parent) {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) if (v != null) e.setAttribute(k, v);
  if (parent) parent.appendChild(e);
  return e;
}
function txt(p, x, y, s, o = {}) {
  const t = el('text', { x, y, 'font-size': o.size ?? FS, 'font-weight': o.weight ?? 500, fill: o.fill ?? C.ink,
    'text-anchor': o.anchor ?? 'start', 'dominant-baseline': o.base ?? 'middle', 'data-card': o.card,
    'font-variant-numeric': 'tabular-nums', class: o.cls }, p);
  t.textContent = s;
  return t;
}
function lines(p, x, y, arr, o = {}) {           // multi-line, vertically centred on y
  const lh = (o.size ?? FS) * 1.42, y0 = y - (arr.length - 1) * lh / 2;
  return arr.map((s, i) => txt(p, x, y0 + i * lh, s, o));
}
function card(p, id, x, y, w, h, o = {}) {
  return el('rect', { id, x, y, width: w, height: h, rx: o.rx ?? 10, fill: o.fill ?? C.surface,
    stroke: o.stroke ?? C.rule, 'stroke-width': o.sw ?? 1.5, 'data-cardbox': id }, p);
}
function icon(p, x, y, size, id, color) {
  const u = el('use', { href: `${ICON}#${id}`, x, y, width: size, height: size, color }, p);
  u.style.color = color;
  return u;
}
function root(W, H) {
  const s = el('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H, class: 'sci-chart' });
  document.getElementById('stage').appendChild(s);
  el('rect', { x: 0, y: 0, width: W, height: H, fill: C.canvas }, s);
  return s;
}
const fmtX = (v) => (v >= 1000 ? `${Math.floor(v / 1000)} ${String(Math.round(v % 1000)).padStart(3, '0')}` : `${v}`);

/* ---------- horizontal bar panel (F1a, F1b): total as a light tone with a full-colour edge, fatal part in ink ---------- */
function hbars(rows, o) {
  const [W, H] = PRINT_PX[o.fig];
  const s = root(W, H);
  const L = o.labelW, R = W - 92, top = 100, bot = H - 76;
  const rowH = (bot - top) / rows.length, bh = Math.min(34, rowH * 0.66);
  const max = o.max;
  const X = (v) => L + (R - L) * v / max;
  txt(s, 8, 28, o.panel, { weight: 700, size: TITLE });
  // key, on its own line under the panel title, aligned with the bars
  el('rect', { x: L, y: 52, width: 22, height: 18, fill: C.d1t, stroke: C.d1, 'stroke-width': 1.5 }, s);
  txt(s, L + 30, 61, 'all', { fill: C.muted, size: SMALL });
  el('rect', { x: L + 84, y: 52, width: 22, height: 18, fill: C.ink }, s);
  txt(s, L + 114, 61, 'fatal', { fill: C.muted, size: SMALL });
  for (let v = 0; v <= max; v += o.step) {
    el('line', { x1: X(v), x2: X(v), y1: top - 10, y2: bot, stroke: C.rule, 'stroke-width': 1 }, s);
    txt(s, X(v), bot + 22, `${v}`, { anchor: 'middle', fill: C.muted, size: SMALL });
  }
  txt(s, (L + R) / 2, H - 20, o.xTitle, { anchor: 'middle', fill: C.muted, size: SMALL });
  rows.forEach((r, i) => {
    const yc = top + rowH * (i + .5);
    txt(s, L - 12, yc, r.label, { anchor: 'end', weight: r.bold ? 700 : 500, size: o.labelSize ?? FS });
    el('rect', { x: X(0), y: yc - bh / 2, width: X(r.n) - X(0), height: bh, fill: C.d1t, stroke: C.d1, 'stroke-width': 1.5 }, s);
    if (r.fatal > 0) el('rect', { x: X(0), y: yc - bh / 2, width: X(r.fatal) - X(0), height: bh, fill: C.ink }, s);
    txt(s, X(r.n) + 8, yc, r.fatal > 0 ? `${r.n} (${r.fatal})` : `${r.n}`, { weight: 700, size: o.labelSize ?? FS });
  });
  el('line', { x1: X(0), x2: X(0), y1: top - 10, y2: bot, stroke: C.muted, 'stroke-width': 1.5 }, s);
  return s;
}

function F1a(D) {
  return hbars(D.phases, { fig: 'F1a', panel: '(a) Flight phase', labelW: 196, max: 80, step: 20,
    xTitle: 'Lock-related openings (fatal)' });
}
function F1b(D) {
  return hbars(D.families, { fig: 'F1b', panel: '(b) Type family', labelW: 262, max: 60, step: 20, labelSize: SMALL,
    xTitle: 'Lock-related openings (fatal)' });
}

/* ---------- F2 architecture ---------- */
function F2(D) {
  const W = 960, H = 560, s = root(W, H), A = C.accent;
  const heads = [[95, 'Canopy'], [305, 'Fuselage rim'], [525, 'Alert unit'], [815, 'Cockpit']];
  heads.forEach(([x, t]) => txt(s, x, 30, t, { anchor: 'middle', weight: 700, fill: C.muted }));
  const ys = [100, 190, 280, 370];
  D.arch.canopy.forEach((t, i) => {
    card(s, `c${i}`, 20, ys[i] - 30, 150, 60);
    txt(s, 95, ys[i], t, { anchor: 'middle', card: `c${i}` });
  });
  el('line', { x1: 192, x2: 192, y1: 56, y2: 420, stroke: css('--chart-series-6') || '#9a5b44', 'stroke-width': 2, 'stroke-dasharray': '8 7' }, s);
  txt(s, 192, 444, 'split line: nothing crosses', { anchor: 'middle', fill: C.muted });
  D.arch.sensors.forEach((t, i) => {
    card(s, `s${i}`, 220, ys[i] - 30, 170, 60, { fill: C.acct, stroke: A, sw: 2 });
    txt(s, 305, ys[i], t, { anchor: 'middle', weight: 600, card: `s${i}` });
    okSvg(s, { x1: 172, y1: ys[i], x2: 218, y2: ys[i], renk: C.muted, kalinlik: 2, kesik: '4 5', bosluk: [2, 4] });
    okSvg(s, { x1: 392, y1: ys[i], x2: 428, y2: ys[i], renk: A, kalinlik: 3, bosluk: [2, 4] });
  });
  card(s, 'u', 430, 70, 190, 330, { fill: C.acct, stroke: A, sw: 2 });
  txt(s, 525, 104, 'green only if', { anchor: 'middle', card: 'u' });
  txt(s, 525, 140, 'all four agree', { anchor: 'middle', weight: 700, card: 'u' });
  ['phase logic', 'line monitor', 'self-test', 'event log'].forEach((t, i) => txt(s, 525, 214 + i * 42, t, { anchor: 'middle', fill: C.muted, card: 'u' }));
  card(s, 'in', 412, 448, 226, 96);
  lines(s, 525, 490, ['lever switch, MAP', 'IAS, GPS speed'], { anchor: 'middle', fill: C.muted, card: 'in' });
  okSvg(s, { x1: 525, y1: 448, x2: 525, y2: 402, renk: C.muted, kalinlik: 2, bosluk: [2, 4] });
  const oy = [96, 184, 272, 360, 448];
  D.arch.cues.forEach(([ic, t], i) => {
    const y = oy[i];
    card(s, `o${i}`, 670, y - 32, 270, 64, { fill: i < 4 ? C.acct : C.surface, stroke: i < 4 ? A : C.rule, sw: i < 4 ? 2 : 1.5 });
    icon(s, 684, y - 16, 32, ic, i < 4 ? A : C.muted);
    txt(s, 728, y, t, { weight: 600, card: `o${i}` });
    okSvg(s, { x1: 622, y1: Math.min(Math.max(y, 100), 380), x2: 668, y2: y, renk: A, kalinlik: 3, bosluk: [2, 4] });
  });
  return s;
}

/* ---------- F3 process ---------- */
function F3(D) {
  const W = 960, H = 560, s = root(W, H), A = C.accent;
  const gap = 18, x0 = 12, colW = (W - 2 * x0 - 3 * gap) / 4;
  D.process.forEach((ph, i) => {
    const x = x0 + i * (colW + gap);
    icon(s, x + 4, 14, 32, ph.icon, A);
    txt(s, x + 46, 31, ph.name, { weight: 700 });
    ph.steps.forEach((st, j) => {
      const y = 70 + j * 74;
      card(s, `p${i}_${j}`, x, y, colW, 58);
      txt(s, x + 14, y + 29, st[0], { weight: 700, fill: A, card: `p${i}_${j}` });
      txt(s, x + 52, y + 29, st[1], { card: `p${i}_${j}` });
    });
    const gy = 392;
    card(s, `g${i}`, x, gy, colW, 120, { fill: A, stroke: A, rx: 14 });
    icon(s, x + colW / 2 - 14, gy + 10, 28, i < 3 ? 'i-circle-check' : 'i-timer', C.accentInk);
    lines(s, x + colW / 2, gy + 80, ph.gate, { anchor: 'middle', fill: C.accentInk, weight: 600, size: 22, card: `g${i}` });
    if (i < 3) okSvg(s, { x1: x + colW + 1, y1: gy + 60, x2: x + colW + gap - 1, y2: gy + 60, renk: A, kalinlik: 3, bosluk: [1, 1] });
  });
  txt(s, W / 2, H - 22, 'Each block ends with a test the next block depends on', { anchor: 'middle', fill: C.muted });
  return s;
}

/* ---------- F4 risk reduction dot plot (log x) ---------- */
function F4(D) {
  const W = 960, H = 600, s = root(W, H);
  const L = 300, R = W - 40, top = 110, bot = H - 80;
  const rows = D.options, rowH = (bot - top) / rows.length;
  const lo = 0, hi = Math.log10(D.xmax);
  const X = (v) => L + (R - L) * (Math.log10(Math.max(v, 1)) - lo) / (hi - lo);
  // key
  el('circle', { cx: L + 10, cy: 30, r: 9, fill: C.d1, stroke: C.canvas, 'stroke-width': 2 }, s);
  txt(s, L + 28, 30, 'pilot acts on every noticed alert');
  el('rect', { x: L, y: 56, width: 22, height: 14, fill: C.d2, 'fill-opacity': .18 }, s);
  el('circle', { cx: L + 10, cy: 63, r: 9, fill: C.d2, stroke: C.canvas, 'stroke-width': 2 }, s);
  txt(s, L + 28, 63, 'pilot distrusts it (5–95 % range)');
  rows.forEach((r, i) => {
    const yc = top + rowH * (i + .5);
    if (r.recommended) el('rect', { x: 4, y: yc - rowH / 2 + 3, width: W - 8, height: rowH - 6, rx: 8, fill: C.acct }, s);
    txt(s, L - 14, yc, r.label, { anchor: 'end', weight: r.recommended ? 700 : 500 });
  });
  [1, 10, 100, 1000].filter((v) => v <= D.xmax).forEach((v) => {
    el('line', { x1: X(v), x2: X(v), y1: top - 10, y2: bot, stroke: C.rule, 'stroke-width': 1 }, s);
    txt(s, X(v), bot + 24, `${fmtX(v)}×`, { anchor: 'middle', fill: C.muted });
  });
  txt(s, (L + R) / 2, H - 22, 'Risk reduction factor (log scale; 1× = no system)', { anchor: 'middle', fill: C.muted });
  rows.forEach((r, i) => {
    const yc = top + rowH * (i + .5);
    el('rect', { x: X(r.lo), y: yc - 7, width: Math.max(X(r.hi) - X(r.lo), 2), height: 14, rx: 7, fill: C.d2, 'fill-opacity': .18 }, s);
    el('line', { x1: X(r.match), x2: X(r.acts), y1: yc, y2: yc, stroke: C.muted, 'stroke-width': 1.5 }, s);
    el('circle', { cx: X(r.match), cy: yc, r: 9, fill: C.d2, stroke: C.canvas, 'stroke-width': 2 }, s);
    el('circle', { cx: X(r.acts), cy: yc, r: 9, fill: C.d1, stroke: C.canvas, 'stroke-width': 2 }, s);
  });
  return s;
}

/* ---------- F5 electrical schematic ---------- */
function F5(D) {
  const W = 960, H = 600, s = root(W, H), A = C.accent;
  [[130, 'Inputs'], [480, 'Alert unit'], [825, 'Outputs']].forEach(([x, t]) => txt(s, x, 28, t, { anchor: 'middle', weight: 700, fill: C.muted }));
  const ins = D.elec.inputs, outs = D.elec.outputs;
  const yIn = (i) => 90 + i * (420 / (ins.length - 1));
  ins.forEach(([ic, a, b, isNew], i) => {
    const y = yIn(i);
    card(s, `i${i}`, 12, y - 40, 236, 80, { fill: isNew ? C.acct : C.surface, stroke: isNew ? A : C.rule, sw: isNew ? 2 : 1.5 });
    icon(s, 24, y - 16, 32, ic, isNew ? A : C.muted);
    lines(s, 68, y, [a, b], { size: 22, card: `i${i}`, fill: C.ink });
    okSvg(s, { x1: 250, y1: y, x2: 368, y2: Math.min(Math.max(y, 120), 480), renk: isNew ? A : C.muted, kalinlik: isNew ? 3 : 2, bosluk: [2, 4] });
  });
  card(s, 'u', 370, 90, 220, 420, { fill: C.acct, stroke: A, sw: 2 });
  icon(s, 464, 106, 32, 'i-cpu', A);
  D.elec.unit.forEach((t, i) => txt(s, 480, 180 + i * 50, t, { anchor: 'middle', card: 'u', weight: i === 0 ? 700 : 500, fill: i === 0 ? C.ink : C.muted }));
  const yOut = (i) => 90 + i * (420 / (outs.length - 1));
  outs.forEach(([ic, a, b, opt], i) => {
    const y = yOut(i);
    card(s, `o${i}`, 680, y - 40, 270, 80, { fill: opt ? C.surface : C.acct, stroke: opt ? C.rule : A, sw: opt ? 1.5 : 2 });
    icon(s, 692, y - 16, 32, ic, opt ? C.muted : A);
    lines(s, 736, y, [a, b], { size: 22, card: `o${i}` });
    okSvg(s, { x1: 592, y1: Math.min(Math.max(y, 120), 480), x2: 678, y2: y, renk: opt ? C.muted : A, kalinlik: opt ? 2 : 3, kesik: opt ? '7 6' : null, bosluk: [2, 4] });
  });
  txt(s, W / 2, H - 22, 'Blue = new parts · own 5 A breaker · each sensor on its own monitored loop', { anchor: 'middle', fill: C.muted, size: 22 });
  return s;
}

/* ---------- F6 sensor locations (schematic, not to scale) ---------- */
function F6(D) {
  const W = 960, H = 520, s = root(W, H), A = C.accent;
  txt(s, 300, 28, 'Left rail, top view (not to scale)', { anchor: 'middle', weight: 700, fill: C.muted });
  txt(s, 800, 28, 'One lug, side view', { anchor: 'middle', weight: 700, fill: C.muted });
  // canopy frame and fuselage rim
  el('rect', { x: 20, y: 96, width: 560, height: 70, rx: 10, fill: '#F1EFEA', stroke: C.rule, 'stroke-width': 1.5 }, s);
  txt(s, 36, 76, 'canopy frame (moves, hinged on the right)', { fill: C.muted, size: 22 });
  el('rect', { x: 20, y: 236, width: 560, height: 92, rx: 10, fill: '#F1EFEA', stroke: C.rule, 'stroke-width': 1.5 }, s);
  txt(s, 36, 352, 'fuselage rim (fixed)', { fill: C.muted, size: 22 });
  el('line', { x1: 20, x2: 580, y1: 201, y2: 201, stroke: C.d2, 'stroke-width': 2, 'stroke-dasharray': '9 7' }, s);
  txt(s, 580, 388, 'dashed = split line: nothing crosses it', { anchor: 'end', fill: C.muted, size: 22 });
  D.lugs.forEach(([lab, x], i) => {
    el('rect', { x: x - 12, y: 150, width: 24, height: 66, rx: 4, fill: '#8C9097' }, s);      // shoot bolt
    card(s, `l${i}`, x - 48, 250, 96, 64, { fill: C.acct, stroke: A, sw: 2 });
    txt(s, x, 282, `S${i + 1}`, { anchor: 'middle', weight: 700, fill: A, card: `l${i}` });
    txt(s, x, 131, lab, { anchor: 'middle', size: 22 });
  });
  card(s, 'seat', 360, 250, 76, 64, { fill: C.acct, stroke: A, sw: 2 });
  txt(s, 398, 282, 'S0', { anchor: 'middle', weight: 700, fill: A, card: 'seat' });
  txt(s, 300, 440, 'Blue = new sensors, fuselage side only.', { anchor: 'middle', size: 22 });
  txt(s, 300, 474, 'S0 sees a passive steel target on the frame.', { anchor: 'middle', size: 22, fill: C.muted });
  // side view
  card(s, 'lug', 840, 120, 100, 120, { fill: '#F1EFEA', stroke: '#8C9097', sw: 2 });
  txt(s, 890, 100, 'roller lug', { anchor: 'middle', size: 22 });
  el('rect', { x: 660, y: 160, width: 190, height: 34, rx: 6, fill: '#8C9097' }, s);
  el('path', { d: 'M850 160 L886 177 L850 194 Z', fill: '#8C9097' }, s);
  txt(s, 722, 224, 'shoot bolt, ramp tip', { anchor: 'middle', size: 22 });
  card(s, 'sen', 846, 330, 88, 64, { fill: C.acct, stroke: A, sw: 2 });
  txt(s, 890, 362, 'S', { anchor: 'middle', weight: 700, fill: A, card: 'sen' });
  okSvg(s, { x1: 890, y1: 328, x2: 890, y2: 196, renk: A, kalinlik: 2.5, cift: true, bosluk: [3, 3] });
  lines(s, 722, 310, ['gap to the bolt tip', 'at full lock'], { anchor: 'middle', size: 22, fill: A });
  lines(s, 800, 450, ['bracket under the existing', 'lug fasteners: no new holes'], { anchor: 'middle', size: 22, fill: C.muted });
  return s;
}

/* ---------- F7 compliance sweep (log y), direct labels ---------- */
function F7(D) {
  const [W, H] = PRINT_PX.F7, s = root(W, H);
  const L = 114, R = W - 218, top = 54, bot = H - 82;
  const c = D.sweep.c, ymax = D.sweep.ymax;   // 1.3 × the largest value (build_figures.py)
  const X = (v) => L + (R - L) * v;
  const Y = (v) => bot - (bot - top) * Math.log10(Math.max(v, 1)) / Math.log10(ymax);
  [1, 10, 100, 1000].filter((v) => v <= ymax).forEach((v) => {
    el('line', { x1: L, x2: R, y1: Y(v), y2: Y(v), stroke: C.rule, 'stroke-width': 1 }, s);
    txt(s, L - 10, Y(v), `${fmtX(v)}×`, { anchor: 'end', fill: C.muted, size: SMALL });
  });
  [0, .2, .4, .6, .8, 1].forEach((v) => txt(s, X(v), bot + 32, v.toFixed(1), { anchor: 'middle', fill: C.muted, size: SMALL }));
  el('line', { x1: L, x2: R, y1: bot, y2: bot, stroke: C.muted, 'stroke-width': 1.5 }, s);
  txt(s, (L + R) / 2, H - 22, 'Probability that the pilot acts on a noticed alert', { anchor: 'middle', fill: C.muted, size: SMALL });
  txt(s, 8, 22, 'Risk reduction (log)', { fill: C.muted, size: SMALL });
  // the value the text quotes: c = 0.5
  const i05 = c.indexOf(0.5);
  el('line', { x1: X(0.5), x2: X(0.5), y1: top, y2: bot, stroke: C.muted, 'stroke-width': 1.2, 'stroke-dasharray': '3 4' }, s);
  // accent: the chosen set; grey solid: the lamp alone; light grey dashed: rejected sets (drawn first, under the rest)
  const order = [...D.sweep.series].sort((a, b) => (a.recommended - b.recommended) || (a.barrier - b.barrier));
  const ends = [];
  order.forEach((sr) => {
    const col = sr.recommended ? C.accent : sr.barrier ? C.rejected : C.grey;
    const d = sr.vals.map((v, i) => `${i ? 'L' : 'M'}${X(c[i]).toFixed(1)},${Y(v).toFixed(1)}`).join(' ');
    el('path', { d, fill: 'none', stroke: col, 'stroke-width': sr.recommended ? 4 : 2.2, 'stroke-linejoin': 'round',
      'stroke-dasharray': sr.barrier && !sr.recommended ? '8 5' : null }, s);
    if (sr.recommended) sr.vals.forEach((v, i) => el('circle', { cx: X(c[i]), cy: Y(v), r: 4.5, fill: col }, s));
    ends.push({ y: Y(sr.vals.at(-1)), sr, col });
  });
  const gate = D.sweep.series.find((sr) => sr.recommended);
  const g05 = gate.vals[i05];
  el('circle', { cx: X(0.5), cy: Y(g05), r: 7, fill: C.canvas, stroke: C.accent, 'stroke-width': 3 }, s);
  txt(s, X(0.5) - 10, Y(g05) - 18, `${g05.toFixed(1)}×`, { anchor: 'end', fill: C.accent, weight: 700, size: SMALL });
  ends.sort((a, b) => a.y - b.y);
  for (let i = 1; i < ends.length; i++) ends[i].y = Math.max(ends[i].y, ends[i - 1].y + 28);   // de-collide labels
  ends.forEach(({ y, sr, col }) => txt(s, R + 12, y, SHORT7[sr.label] ?? sr.label,
    { fill: sr.recommended ? C.accent : C.muted, weight: sr.recommended ? 700 : 500, size: SMALL }));
  if (D.sweep.series.some((sr) => sr.barrier)) {      // key only when a rejected set is drawn
    const kt = txt(s, W - 8, 22, 'dashed: rejected', { fill: C.muted, size: SMALL, anchor: 'end' });
    const kx0 = W - 8 - kt.getComputedTextLength() - 40;
    el('line', { x1: kx0, x2: kx0 + 30, y1: 22, y2: 22, stroke: C.rejected, 'stroke-width': 2.2, 'stroke-dasharray': '8 5' }, s);
  }
  return s;
}

/* ---------- F8 take-off timeline: rolls, and when the median pilot acts after each alert trigger ---------- */
function F8(D) {
  const [W, H] = PRINT_PX.F8, s = root(W, H), A = C.accent, T = D.timeline;
  const L = 226, R = W - 30, t1 = T.tmax;
  const X = (t) => L + (R - L) * t / t1;
  const gTop = 26, gBot = H - 124;
  for (let t = 0; t <= t1; t += 2) {
    el('line', { x1: X(t), x2: X(t), y1: gTop, y2: gBot, stroke: C.rule, 'stroke-width': 1 }, s);
    txt(s, X(t), gBot + 20, `${t}`, { anchor: 'middle', fill: C.muted, size: SMALL });
  }
  txt(s, (L + R) / 2, gBot + 50, 'Seconds after the throttle goes forward', { anchor: 'middle', fill: C.muted, size: SMALL });
  const tag = (t, lab, y) => {                    // speed tag; kept inside the plot at the right edge
    const x = X(t), w = lab.length * 13.6;
    const anchor = x + w / 2 > R ? 'end' : 'middle';
    txt(s, anchor === 'end' ? Math.min(x + 6, R) : x, y, lab, { anchor, size: SMALL, fill: C.muted });
  };
  const row = (r, y, inner) => {
    txt(s, L - 14, y - 12, r.label, { anchor: 'end', weight: 700, size: FS });
    txt(s, L - 14, y + 16, `${r.a} m/s², ${r.m} m`, { anchor: 'end', fill: C.muted, size: SMALL });
    el('rect', { x: X(0), y: y - 14, width: X(r.t40) - X(0), height: 28, rx: 5, fill: C.d1t, stroke: C.d1, 'stroke-width': 1.5 }, s);
    el('rect', { x: X(r.t40), y: y - 14, width: X(r.tlof) - X(r.t40), height: 28, rx: 5, fill: C.late, stroke: C.rule, 'stroke-width': 1.5 }, s);
    if (inner) txt(s, X(0) + 4, y + 34, 'reject window', { size: SMALL, fill: C.d1ink, weight: 700 });
    [[r.t30, '30 kt', -32], [r.t40, '40 kt', 34], [r.tlof, 'lift-off 80 kt', -32]].forEach(([t, lab, dy]) => {
      el('line', { x1: X(t), x2: X(t), y1: y - 20, y2: y + 20, stroke: C.ink, 'stroke-width': 1.5 }, s);
      if (dy > 0) txt(s, X(t) + 6, y + dy, lab, { size: SMALL, fill: C.muted });   // below: start at the tick
      else tag(t, lab, y + dy);
    });
  };
  const [sr, lr] = T.rolls;
  const yS = 64, yL1 = yS + 72, yL2 = yS + 112, yR = gBot - 56;
  row(sr, yS, false);
  // trigger lanes under the brisk roll: onset ring, median response (solid), to the 95th percentile (light)
  el('line', { x1: X(sr.t30), x2: X(sr.t30), y1: yS + 20, y2: yL2 + 22, stroke: C.ink, 'stroke-width': 1.5, 'stroke-dasharray': '5 5' }, s);
  T.lanes.forEach((ln, k) => {
    const y = k ? yL2 : yL1, col = ln.ours ? A : C.muted;
    txt(s, L - 14, y, ln.label, { anchor: 'end', size: SMALL, fill: col, weight: 700 });
    el('rect', { x: X(ln.onset), y: y - 7, width: X(ln.p95_t) - X(ln.onset), height: 14, rx: 7, fill: col, 'fill-opacity': .28 }, s);
    el('rect', { x: X(ln.onset), y: y - 7, width: X(ln.med_t) - X(ln.onset), height: 14, rx: 7, fill: col }, s);
    el('circle', { cx: X(ln.onset), cy: y, r: 7, fill: C.canvas, stroke: col, 'stroke-width': 3 }, s);
    txt(s, X(ln.p95_t) + 12, y, `median ${ln.med_kt} kt, 95th ${ln.p95_kt} kt`, { size: SMALL, fill: col, weight: 700 });
  });
  row(lr, yR, true);
  // key for the lanes, drawn as samples of the marks
  const ky = H - 22;
  let kx = 16;                                   // laid out by measured text length
  el('circle', { cx: kx + 8, cy: ky, r: 7, fill: C.canvas, stroke: C.muted, 'stroke-width': 3 }, s);
  kx += 22 + txt(s, kx + 22, ky, 'alert onset', { size: SMALL, fill: C.muted }).getComputedTextLength() + 24;
  el('rect', { x: kx, y: ky - 7, width: 34, height: 14, rx: 7, fill: C.muted }, s);
  kx += 42 + txt(s, kx + 42, ky, 'to median', { size: SMALL, fill: C.muted }).getComputedTextLength() + 24;
  el('rect', { x: kx, y: ky - 7, width: 34, height: 14, rx: 7, fill: C.muted, 'fill-opacity': .28 }, s);
  txt(s, kx + 42, ky, 'to 95th percentile', { size: SMALL, fill: C.muted });
  return s;
}

/* ---------- F9 sensing options for the Extra NG: distrust RF with the recommended cue set (log x) ---------- */
function F9(D) {
  const W = 960, H = 560, s = root(W, H), A = C.accent;
  const L = 330, R = W - 130, top = 96, bot = H - 80, rows = D.sensing, rowH = (bot - top) / rows.length;
  const X = (v) => L + (R - L) * Math.log10(Math.max(v, 1)) / Math.log10(D.sensing_xmax);
  el('circle', { cx: 160, cy: 26, r: 9, fill: A, stroke: C.canvas, 'stroke-width': 2 }, s);
  txt(s, 178, 26, 'pilot distrusts it, recommended cue set (O6)', { size: 22 });
  el('circle', { cx: 160, cy: 58, r: 8, fill: C.canvas, stroke: C.muted, 'stroke-width': 3 }, s);
  txt(s, 178, 58, 'same, if 1 mm of handle moves the bolt only 0.5 mm', { size: 22, fill: C.muted });
  txt(s, W - 60, 86, 'sees P/O/U', { anchor: 'middle', size: 20, fill: C.muted });
  [1, 10].concat(D.sensing_xmax >= 100 ? [100] : []).forEach((v) => {
    el('line', { x1: X(v), x2: X(v), y1: top - 6, y2: bot, stroke: C.rule, 'stroke-width': 1 }, s);
    txt(s, X(v), bot + 24, `${v}×`, { anchor: 'middle', fill: C.muted });
  });
  txt(s, (L + R) / 2, H - 22, 'Risk reduction factor under distrust (log scale)', { anchor: 'middle', fill: C.muted });
  rows.forEach((r, i) => {
    const yc = top + rowH * (i + .5);
    if (r.recommended) el('rect', { x: 4, y: yc - rowH / 2 + 3, width: W - 8, height: rowH - 6, rx: 8, fill: C.acct }, s);
    txt(s, L - 14, yc, r.label, { anchor: 'end', weight: r.recommended ? 700 : 500, size: 22 });
    el('line', { x1: X(r.u), x2: X(r.c), y1: yc, y2: yc, stroke: C.muted, 'stroke-width': 1.5 }, s);
    el('circle', { cx: X(r.u), cy: yc, r: 8, fill: C.canvas, stroke: C.muted, 'stroke-width': 3 }, s);
    el('circle', { cx: X(r.c), cy: yc, r: 9, fill: A, stroke: C.canvas, 'stroke-width': 2 }, s);
    txt(s, W - 60, yc, r.sees, { anchor: 'middle', size: 22, weight: 600, fill: r.sees.includes('N') ? C.d2 : C.ink });
  });
  return s;
}

/* ---------- F10 one sensing point, side section (schematic): locked vs partly locked ---------- */
function F10(D) {
  const [W, H] = PRINT_PX.F10, s = root(W, H);
  const GREEN = '#1F8A5B', RED = '#B3261E', pw = (W - 16 - 28) / 2;
  const defs = el('defs', {}, s);
  const grad = (id, stops, vertical = true) => {
    const g = el('linearGradient', { id, x1: 0, y1: 0, x2: vertical ? 0 : 1, y2: vertical ? 1 : 0 }, defs);
    stops.forEach(([o, c, op]) => el('stop', { offset: o, 'stop-color': c, 'stop-opacity': op ?? 1 }, g));
  };
  grad('steel', [[0, '#F7F8FA'], [0.38, '#D5D9DE'], [0.55, '#A9AFB7'], [1, '#E3E6EA']]);
  grad('barrel', [[0, '#EEF0F3'], [0.4, '#C4C9D0'], [0.6, '#959CA6'], [1, '#D9DDE2']]);
  grad('nut', [[0, '#E9EBEE'], [0.5, '#B7BDC5'], [1, '#D3D7DC']]);
  grad('lug', [[0, '#F1EEE8'], [1, '#DCD7CD']]);
  grad('sill', [[0, '#E2DED5'], [1, '#CFCABF']]);
  grad('fieldOn', [[0, GREEN, 0.05], [1, GREEN, 0.4]], false);
  const rg = el('radialGradient', { id: 'roller', cx: 0.4, cy: 0.35, r: 0.7 }, defs);
  el('stop', { offset: 0, 'stop-color': '#F4F5F7' }, rg);
  el('stop', { offset: 1, 'stop-color': '#9EA4AC' }, rg);

  const yA = 196, R = 15;                            // bolt axis and radius
  const panel = (x0, locked) => {
    const col = locked ? GREEN : RED;
    // status bar with a check or a cross
    el('rect', { x: x0, y: 6, width: pw, height: 44, rx: 9, fill: col }, s);
    const ix = x0 + 26, iy = 28;
    if (locked) el('path', { d: `M${ix - 10},${iy} L${ix - 3},${iy + 8} L${ix + 11},${iy - 9}`, fill: 'none', stroke: '#FFFFFF', 'stroke-width': 4, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, s);
    else el('path', { d: `M${ix - 8},${iy - 8} L${ix + 8},${iy + 8} M${ix + 8},${iy - 8} L${ix - 8},${iy + 8}`, stroke: '#FFFFFF', 'stroke-width': 4, 'stroke-linecap': 'round' }, s);
    txt(s, x0 + 50, 28, locked ? 'Locked: sensor ON, green lamp' : 'Partly locked: sensor OFF, red alert',
      { weight: 700, fill: '#FFFFFF', size: FS });
    el('rect', { x: x0, y: 58, width: pw, height: 242, rx: 10, fill: '#F7F6F3' }, s);
    // fixed structure: fuselage sill, roller lug with its roller
    el('rect', { x: x0, y: 268, width: pw, height: 30, rx: 4, fill: 'url(#sill)', stroke: '#A8A296', 'stroke-width': 1.2 }, s);
    el('line', { x1: x0 + 2, x2: x0 + pw - 2, y1: 269.5, y2: 269.5, stroke: '#F4F2EC', 'stroke-width': 1.5 }, s);
    el('path', { d: `M${x0 + 160},268 L${x0 + 160},${yA - 34} Q${x0 + 160},${yA - 46} ${x0 + 172},${yA - 46} L${x0 + 290},${yA - 46} Q${x0 + 302},${yA - 46} ${x0 + 302},${yA - 34} L${x0 + 302},268 Z`,
      fill: 'url(#lug)', stroke: '#A8A296', 'stroke-width': 1.5 }, s);
    el('circle', { cx: x0 + 231, cy: yA + R + 17, r: 17, fill: 'url(#roller)', stroke: '#868C94', 'stroke-width': 1.2 }, s);
    el('circle', { cx: x0 + 231, cy: yA + R + 17, r: 4, fill: '#868C94' }, s);
    // canopy frame stub (moves with the canopy) and the shoot bolt
    const tip = x0 + (locked ? 478 : 404), cone = 30;
    el('path', { d: `M${x0 + 16},${yA - R} L${tip - cone},${yA - R} L${tip},${yA} L${tip - cone},${yA + R} L${x0 + 16},${yA + R} `
      + `C${x0 + 6},${yA + 6} ${x0 + 26},${yA - 6} ${x0 + 16},${yA - R} Z`, fill: 'url(#steel)', stroke: '#7D838B', 'stroke-width': 1.3 }, s);
    el('line', { x1: x0 + 24, x2: tip - cone - 2, y1: yA - R + 5, y2: yA - R + 5, stroke: '#FFFFFF', 'stroke-width': 2, 'stroke-opacity': 0.8 }, s);
    // direction of locking
    el('path', { d: `M${x0 + 70},${yA} L${x0 + 150},${yA}`, stroke: C.accent, 'stroke-width': 2.5, 'stroke-linecap': 'round' }, s);
    el('path', { d: `M${x0 + 140},${yA - 7} L${x0 + 152},${yA} L${x0 + 140},${yA + 7}`, fill: 'none', stroke: C.accent, 'stroke-width': 2.5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, s);
    // sensor: threaded barrel through a bracket plate, two nuts, cable
    const face = x0 + 494, back = x0 + 626, rb = 15;
    el('path', { d: `M${x0 + 552},268 L${x0 + 552},${yA - 40} L${x0 + 566},${yA - 40} L${x0 + 566},268`, fill: '#B9BEC5', stroke: '#868C94', 'stroke-width': 1.2 }, s);
    if (locked) el('path', { d: `M${face},${yA - rb} L${face - 24},${yA - 9} L${face - 24},${yA + 9} L${face},${yA + rb} Z`, fill: 'url(#fieldOn)' }, s);
    else el('path', { d: `M${face},${yA - rb} Q${face - 34},${yA} ${face},${yA + rb}`, fill: 'none', stroke: '#9AA0A6', 'stroke-width': 1.5, 'stroke-dasharray': '4 4' }, s);
    el('rect', { x: face, y: yA - rb, width: back - face, height: 2 * rb, rx: 5, fill: 'url(#barrel)', stroke: '#7D838B', 'stroke-width': 1.2 }, s);
    for (let x = face + 10; x < back - 6; x += 6) el('line', { x1: x, x2: x, y1: yA - rb + 2, y2: yA + rb - 2, stroke: '#8E959E', 'stroke-width': 0.9, 'stroke-opacity': 0.55 }, s);
    el('rect', { x: face, y: yA - rb, width: 6, height: 2 * rb, rx: 2, fill: locked ? GREEN : '#A3A9B1' }, s);
    [[x0 + 532, 18], [x0 + 568, 18]].forEach(([nx, nw]) => {
      el('rect', { x: nx, y: yA - rb - 9, width: nw, height: 2 * rb + 18, rx: 3, fill: 'url(#nut)', stroke: '#7D838B', 'stroke-width': 1.2 }, s);
      el('line', { x1: nx + nw / 2, x2: nx + nw / 2, y1: yA - rb - 7, y2: yA + rb + 7, stroke: '#9AA0A6', 'stroke-width': 1 }, s);
    });
    el('rect', { x: back, y: yA - 10, width: 14, height: 20, rx: 3, fill: '#5E646C' }, s);
    el('circle', { cx: back + 7, cy: yA, r: 4.5, fill: locked ? '#3DDC84' : '#8A9098' }, s);
    if (locked) el('circle', { cx: back + 7, cy: yA, r: 9, fill: '#3DDC84', 'fill-opacity': 0.3 }, s);
    el('path', { d: `M${back + 14},${yA} C${back + 44},${yA} ${back + 44},${yA + 46} ${x0 + pw - 8},${yA + 46}`, fill: 'none', stroke: '#3E434A', 'stroke-width': 5, 'stroke-linecap': 'round' }, s);
    return { tip, face };
  };
  const xL = 8, xR = 8 + pw + 28;
  const a = panel(xL, true), b = panel(xR, false);
  el('line', { x1: xL + pw + 14, x2: xL + pw + 14, y1: 60, y2: 298, stroke: C.rule, 'stroke-width': 1.5 }, s);
  // labels: parts named once, on the left panel
  const lab = (x, y, name, note, anchor, lx, ly) => {
    txt(s, x, y, name, { weight: 700, size: SMALL, anchor });
    txt(s, x, y + 30, note, { size: SMALL, fill: C.muted, anchor });
    el('line', { x1: lx, x2: lx, y1: y + 46, y2: ly, stroke: C.muted, 'stroke-width': 1.2 }, s);
  };
  lab(xL + 40, 76, 'Shoot bolt', 'on the canopy', 'start', xL + 120, yA - R - 2);
  lab(xL + 222, 76, 'Roller lug', 'on the fuselage', 'start', xL + 262, yA - 47);
  lab(xL + pw - 6, 76, 'Inductive sensor', 'on a lug bracket', 'end', xL + 600, yA - 25);
  // gap at full lock
  const gy = yA + 38;
  el('line', { x1: a.tip, x2: a.tip, y1: yA + 4, y2: gy + 6, stroke: C.ink, 'stroke-width': 1 }, s);
  el('line', { x1: a.face, x2: a.face, y1: yA + R + 2, y2: gy + 6, stroke: C.ink, 'stroke-width': 1 }, s);
  el('line', { x1: a.tip, x2: a.face, y1: gy, y2: gy, stroke: C.ink, 'stroke-width': 1.5 }, s);
  txt(s, a.tip - 8, gy + 2, '1.5 to 2 mm', { size: SMALL, anchor: 'end', weight: 700 });
  // right panel: what is missing
  el('line', { x1: b.tip + 4, x2: b.face - 4, y1: yA - R - 10, y2: yA - R - 10, stroke: RED, 'stroke-width': 2 }, s);
  [b.tip + 4, b.face - 4].forEach((x) => el('line', { x1: x, x2: x, y1: yA - R - 16, y2: yA - R - 4, stroke: RED, 'stroke-width': 2 }, s));
  txt(s, (b.tip + b.face) / 2, 86, 'Tip stops short: no steel', { size: SMALL, fill: RED, weight: 700, anchor: 'middle' });
  txt(s, (b.tip + b.face) / 2, 116, 'in the sensing range', { size: SMALL, fill: RED, weight: 700, anchor: 'middle' });
  [xL, xR].forEach((x) => txt(s, x + 12, 285, 'Fuselage sill', { size: SMALL, fill: '#5A5F66' }));
  txt(s, xL + 4, H - 20, 'One of three bolt sensors; a fourth sensor checks that the canopy is seated.', { size: SMALL, fill: C.ink });
  txt(s, W - 12, H - 20, 'Schematic, not to scale', { size: SMALL, fill: C.muted, anchor: 'end' });
  return s;
}

/* ---------- audit: text overlaps and text outside its card ---------- */
function audit() {
  const out = { overlaps: [], outside: [], clipped: [], texts: 0 };
  const svg = document.querySelector('#stage svg'), vb = svg.viewBox.baseVal;
  for (const e of svg.querySelectorAll('text, rect[data-cardbox], use, circle')) {
    const b = e.getBBox();
    const m = e.tagName === 'text' ? 6 : -.5;   // glyphs overhang their measured box: keep text 6 px inside the edge
    if (b.x < vb.x + m || b.y < vb.y + m || b.x + b.width > vb.x + vb.width - m || b.y + b.height > vb.y + vb.height - m)
      out.clipped.push(e.textContent || e.id || e.tagName);
  }
  const T = [...document.querySelectorAll('#stage text')].map((t) => ({ t, b: t.getBBox(), s: t.textContent }));
  out.texts = T.length;
  const hit = (a, b, m = 1) => a.x < b.x + b.width - m && b.x < a.x + a.width - m && a.y < b.y + b.height - m && b.y < a.y + a.height - m;
  for (let i = 0; i < T.length; i++) for (let j = i + 1; j < T.length; j++) if (hit(T[i].b, T[j].b)) out.overlaps.push([T[i].s, T[j].s]);
  for (const { t, b, s } of T) {
    const id = t.getAttribute('data-card');
    if (!id) continue;
    const r = document.getElementById(id).getBBox();
    if (b.x < r.x + 2 || b.y < r.y + 1 || b.x + b.width > r.x + r.width - 2 || b.y + b.height > r.y + r.height - 1) out.outside.push(s);
  }
  out.extent = T.reduce((e, { b }) => [Math.min(e[0], b.x), Math.min(e[1], b.y), Math.max(e[2], b.x + b.width), Math.max(e[3], b.y + b.height)], [1e9, 1e9, -1e9, -1e9]).map(Math.round);
  out.font = getComputedStyle(document.querySelector('#stage text')).fontFamily;
  out.font_loaded = ['400', '500', '700'].every((w) => document.fonts.check(`${w} 24px Montserrat`));
  out.min_px = Math.min(...T.map(({ t }) => parseFloat(t.getAttribute('font-size'))));
  out.min_pt = +(out.min_px / K / 0.3528).toFixed(2);
  document.getElementById('audit').textContent = JSON.stringify(out);
  document.title = `AUDIT ${out.overlaps.length} overlaps, ${out.outside.length} outside, ${out.clipped.length} clipped`;
}

async function main() {
  for (const [k, n] of Object.entries({ canvas: '--color-canvas', surface: '--color-surface', ink: '--color-ink',
    muted: '--color-muted', accent: '--color-accent', accentInk: '--color-accent-ink', rule: '--color-rule',
    d1: '--color-data-1', d2: '--color-data-2' })) C[k] = css(n);
  const mix = (hex, a) => {            // hex tint toward white (a = share of the colour); SVG attributes need plain colours
    const v = parseInt(hex.replace('#', ''), 16), c = [(v >> 16) & 255, (v >> 8) & 255, v & 255];
    return '#' + c.map((x) => Math.round(255 - (255 - x) * a).toString(16).padStart(2, '0')).join('');
  };
  C.d1t = mix(C.d1, 0.18);
  C.acct = mix(C.accent, 0.10);
  C.surface = '#FFFFFF';
  C.grey = '#A3A7AE';                  // alert-only sets in F7: present, not the message
  C.rejected = '#B9BDC4';              // rejected options in F7: light grey, dashed
  C.late = '#F1EFEA';                  // past the reject window (F8)
  C.d1ink = C.d1;                      // text on the light data-1 tint
  const D = await (await fetch('data.json', { cache: 'no-store' })).json();
  PRINT_PX = Object.fromEntries(Object.entries(D.print).map(([k, v]) => [k, v.px]));
  await Promise.all(['400', '500', '700'].map((w) => document.fonts.load(`${w} 24px Montserrat`)));
  const fig = new URLSearchParams(location.search).get('fig') || 'F1a';
  ({ F1a, F1b, F2, F3, F4, F5, F6, F7, F8, F9, F10 })[fig](D);
  await document.fonts.ready;
  audit();
}
main();
