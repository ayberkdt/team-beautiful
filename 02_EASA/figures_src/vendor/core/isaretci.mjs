/* İŞARETÇİ ÇEKİRDEĞİ — ok, önder çizgisi ve yön işaretleri için TEK geometri.
 *
 * Neden: oklar onlarca dosyada elle çiziliyordu ve aynı kusurları
 * tekrarlıyordu — gövde ucun içinden taşar (yuvarlak/kare çizgi ucu ok
 * başının önünde görünür), eğri okun başı kirişe bakar (teğete değil),
 * sabit boyutlu baş kısa okta gövdeyi yutar, ok hedefin üstüne gömülür,
 * sıfır uzunlukta NaN üretir. Burada hepsi bir kez, sınanarak çözülür.
 *
 *   const g = okGeometrisi({ x1, y1, x2, y2, bukum: .2, kalinlik: 3, bosluk: [0, 6] });
 *   // g = { govde: 'M… Q…', bas: 'M… L… L… Z', uc: [x, y], aci, boy, basBoy } | null
 *   okSvg(svgGrup, { …ayni secenekler, sinif: 'ok', hale: true });
 *   okCanvas(ctx, { …ayni secenekler, renk: '#fff' });
 *   const o = onderGeometrisi({ hedef: [x, y], etiket: [x, y], dirsek: true, bosluk: 4 });
 *
 * Kurallar (validate-isaretci.mjs sayısal olarak denetler):
 *  - uç, hedeften tam `bosluk[1]` kadar geride; kuyruk kaynaktan `bosluk[0]` ileride
 *  - baş, eğrinin UÇTAKİ TEĞETİNE yönelir (kirişe değil)
 *  - gövde baş tabanının içinde biter: çizgi ucu başın önünden taşmaz
 *  - baş boyu = kalınlık × 4,5 (varsayılan), ama okun uzunluğunun en çok %40'ı
 *  - sıfır/NaN uzunluk → null (çizilmez, hata atmaz)
 *  - koordinatlar tek biçimli ölçekte olmalı (preserveAspectRatio="none" başı ezer)
 */

const SVGNS = 'http://www.w3.org/2000/svg';
const yuv = v => Math.round(v * 100) / 100;
const sonlu = (...v) => v.every(Number.isFinite);

/* --- ikinci derece Bézier yardımcıları --- */
const qNokta = (p0, c, p1, t) => {
  const u = 1 - t;
  return [u * u * p0[0] + 2 * u * t * c[0] + t * t * p1[0], u * u * p0[1] + 2 * u * t * c[1] + t * t * p1[1]];
};
const qTurev = (p0, c, p1, t) => [
  2 * (1 - t) * (c[0] - p0[0]) + 2 * t * (p1[0] - c[0]),
  2 * (1 - t) * (c[1] - p0[1]) + 2 * t * (p1[1] - c[1]),
];
/** [t0, t1] aralığındaki alt eğri (de Casteljau): yeni [p0, c, p1] */
function qAlt(p0, c, p1, t0, t1) {
  const a = qNokta(p0, c, p1, t0), b = qNokta(p0, c, p1, t1);
  const d = qTurev(p0, c, p1, t0);
  return [a, [a[0] + d[0] * (t1 - t0) / 2, a[1] + d[1] * (t1 - t0) / 2], b];
}
/** yay uzunluğu tablosu (n parça) ve s → t dönüşümü */
function yayTablosu(p0, c, p1, n = 64) {
  const s = [0];
  let onceki = p0;
  for (let i = 1; i <= n; i++) {
    const p = qNokta(p0, c, p1, i / n);
    s.push(s[i - 1] + Math.hypot(p[0] - onceki[0], p[1] - onceki[1]));
    onceki = p;
  }
  const L = s[n];
  const tBul = hedef => {
    if (hedef <= 0) return 0;
    if (hedef >= L) return 1;
    let lo = 0, hi = n;
    while (hi - lo > 1) { const m = (lo + hi) >> 1; s[m] < hedef ? lo = m : hi = m; }
    return (lo + (hedef - s[lo]) / (s[hi] - s[lo] || 1)) / n;
  };
  return { L, tBul };
}

/** Baş poligonu: uç, iki kanat, içbükey sırt (çentik) — dolgulu, keskin. */
function basPoligonu(uc, yon, boy, en, centik) {
  const [ux, uy] = yon, nx = -uy, ny = ux;
  const taban = [uc[0] - ux * boy, uc[1] - uy * boy];
  const sol = [taban[0] + nx * en, taban[1] + ny * en];
  const sag = [taban[0] - nx * en, taban[1] - ny * en];
  const cen = [uc[0] - ux * boy * (1 - centik), uc[1] - uy * boy * (1 - centik)];
  return `M${yuv(uc[0])},${yuv(uc[1])} L${yuv(sol[0])},${yuv(sol[1])} L${yuv(cen[0])},${yuv(cen[1])} L${yuv(sag[0])},${yuv(sag[1])} Z`;
}

/**
 * Ok geometrisi. bukum: kirişe dik kontrol ofseti / kiriş boyu (0 = düz, + saat yönü).
 * bas: { boy, en, centik } isteğe bağlı; cift: iki uçta baş.
 * Dönen null: çizilecek uzunluk yok (sıfır, NaN ya da boşluklar okun tamamını yiyor).
 */
export function okGeometrisi({ x1, y1, x2, y2, bukum = 0, kalinlik = 3, bas = {}, bosluk = [0, 0], cift = false, govdeOrani = .9 } = {}) {
  if (!sonlu(x1, y1, x2, y2, bukum, kalinlik)) return null;
  const kiris = Math.hypot(x2 - x1, y2 - y1);
  if (kiris < 1e-6) return null;
  const p0 = [x1, y1], p1 = [x2, y2];
  const nx = -(y2 - y1) / kiris, ny = (x2 - x1) / kiris;
  const c = [(x1 + x2) / 2 + nx * bukum * kiris, (y1 + y2) / 2 + ny * bukum * kiris];
  const { L, tBul } = yayTablosu(p0, c, p1);
  const [b0, b1] = Array.isArray(bosluk) ? bosluk : [0, bosluk];
  const kullanilir = L - b0 - b1;
  if (!(kullanilir > 1e-6)) return null;
  const basBoy = Math.min(bas.boy ?? kalinlik * 4.5, kullanilir * (cift ? .3 : .4));
  const basEn = (bas.en ?? basBoy * .5);
  const centik = bas.centik ?? .22;
  /* uç noktalar ve teğetler */
  const tUc = tBul(L - b1), tKuyruk = tBul(b0);
  const uc = qNokta(p0, c, p1, tUc), kuyruk = qNokta(p0, c, p1, tKuyruk);
  const birim = d => { const n = Math.hypot(d[0], d[1]) || 1; return [d[0] / n, d[1] / n]; };
  const yonUc = birim(qTurev(p0, c, p1, tUc));
  const yonKuyruk = birim(qTurev(p0, c, p1, tKuyruk));
  /* gövde: baş tabanının (çentik derinliğine kadar) içinde biter */
  const icDerinlik = basBoy * (1 - centik) * govdeOrani;
  const tGovdeSon = tBul(L - b1 - icDerinlik);
  const tGovdeIlk = cift ? tBul(b0 + icDerinlik) : tKuyruk;
  const [a, k, b] = qAlt(p0, c, p1, tGovdeIlk, tGovdeSon);
  const govde = bukum
    ? `M${yuv(a[0])},${yuv(a[1])} Q${yuv(k[0])},${yuv(k[1])} ${yuv(b[0])},${yuv(b[1])}`
    : `M${yuv(a[0])},${yuv(a[1])} L${yuv(b[0])},${yuv(b[1])}`;
  const basD = basPoligonu(uc, yonUc, basBoy, basEn, centik)
    + (cift ? ' ' + basPoligonu(kuyruk, [-yonKuyruk[0], -yonKuyruk[1]], basBoy, basEn, centik) : '');
  return {
    govde, bas: basD, uc, kuyruk, aci: Math.atan2(yonUc[1], yonUc[0]),
    yon: yonUc, boy: kullanilir, basBoy, basEn,
    govdeSon: b, govdeIlk: a,
  };
}

/**
 * Dirsekli (dik açılı) ok: noktalar dizisi boyunca, köşeler yuvarlatılmış;
 * baş SON parçanın yönüne bakar. Diyagram akışları için.
 */
export function dirsekGeometrisi({ noktalar, kalinlik = 3, kose = 10, bas = {}, bosluk = [0, 0], govdeOrani = .9 } = {}) {
  const p = (noktalar || []).filter(q => q && sonlu(q[0], q[1]));
  if (p.length < 2) return null;
  const [b0, b1] = Array.isArray(bosluk) ? bosluk : [0, bosluk];
  /* uçlardan boşluk kadar kısalt */
  const kisalt = (a, b, d) => { const L = Math.hypot(b[0] - a[0], b[1] - a[1]); return L < 1e-6 ? a : [a[0] + (b[0] - a[0]) * d / L, a[1] + (b[1] - a[1]) * d / L]; };
  const q = p.map(v => [...v]);
  q[0] = kisalt(q[0], q[1], b0);
  const n = q.length;
  q[n - 1] = kisalt(q[n - 1], q[n - 2], b1);
  const sonParca = Math.hypot(q[n - 1][0] - q[n - 2][0], q[n - 1][1] - q[n - 2][1]);
  if (sonParca < 1e-6) return null;
  const yon = [(q[n - 1][0] - q[n - 2][0]) / sonParca, (q[n - 1][1] - q[n - 2][1]) / sonParca];
  const basBoy = Math.min(bas.boy ?? kalinlik * 4.5, sonParca * .6);
  const basEn = bas.en ?? basBoy * .5, centik = bas.centik ?? .22;
  const uc = q[n - 1];
  const govdeSon = [uc[0] - yon[0] * basBoy * (1 - centik) * govdeOrani, uc[1] - yon[1] * basBoy * (1 - centik) * govdeOrani];
  const yol = [...q.slice(0, -1), govdeSon];
  let d = `M${yuv(yol[0][0])},${yuv(yol[0][1])}`;
  for (let i = 1; i < yol.length - 1; i++) {
    const A = yol[i - 1], B = yol[i], C = yol[i + 1];
    const r = Math.min(kose, Math.hypot(B[0] - A[0], B[1] - A[1]) / 2, Math.hypot(C[0] - B[0], C[1] - B[1]) / 2);
    const g = kisalt(B, A, r), h = kisalt(B, C, r);
    d += ` L${yuv(g[0])},${yuv(g[1])} Q${yuv(B[0])},${yuv(B[1])} ${yuv(h[0])},${yuv(h[1])}`;
  }
  d += ` L${yuv(yol[yol.length - 1][0])},${yuv(yol[yol.length - 1][1])}`;
  return { govde: d, bas: basPoligonu(uc, yon, basBoy, basEn, centik), uc, yon, basBoy, basEn, govdeSon };
}

/**
 * Önder çizgisi (etiket → hedef): hedefte küçük bir nokta, etikette yatay
 * kısa raf (dirsek), hedefe `bosluk` kadar mesafe. Ok başı YOK — önder
 * bir şeyi adlandırır, yön göstermez.
 */
export function onderGeometrisi({ hedef, etiket, dirsek = true, raf = 14, bosluk = 0, nokta = 3 } = {}) {
  if (!hedef || !etiket || !sonlu(hedef[0], hedef[1], etiket[0], etiket[1])) return null;
  const sagda = etiket[0] >= hedef[0];
  const rafUcu = dirsek ? [etiket[0] + (sagda ? -raf : raf), etiket[1]] : etiket;
  const dx = rafUcu[0] - hedef[0], dy = rafUcu[1] - hedef[1], L = Math.hypot(dx, dy);
  if (L < 1e-6) return null;
  const bas = [hedef[0] + dx / L * bosluk, hedef[1] + dy / L * bosluk];
  const d = `M${yuv(bas[0])},${yuv(bas[1])} L${yuv(rafUcu[0])},${yuv(rafUcu[1])}` + (dirsek ? ` L${yuv(etiket[0])},${yuv(etiket[1])}` : '');
  return { govde: d, nokta: nokta ? { cx: hedef[0], cy: hedef[1], r: nokta } : null, bas, rafUcu };
}

/* --- ölçüm kancası ---
   globalThis.__isaretciKayit bir dizi ise çizilen her ok EKRAN pikselinde
   kaydedilir (scripts/olc-oklar.mjs okur). Tanımlı değilse hiçbir şey yapmaz. */
function kaydet(tur, geo, secenek, olcek, donustur, ek) {
  const K = globalThis.__isaretciKayit;
  if (!Array.isArray(K) || !geo) return;
  const k = secenek.kalinlik ?? (tur === 'onder' ? 1.5 : 3);
  K.push({
    tur, sinif: secenek.sinif || '', renk: String(secenek.renk ?? 'currentColor'),
    alfa: (secenek.alfa ?? 1) * (ek?.alfa ?? 1),
    boy: (geo.boy ?? 0) * olcek, basBoy: (geo.basBoy ?? 0) * olcek, basEn: (geo.basEn ?? 0) * olcek,
    kalinlik: k * olcek, uc: geo.uc ? donustur(geo.uc) : null,
    kuyruk: geo.kuyruk ? donustur(geo.kuyruk) : (geo.bas && Array.isArray(geo.bas) ? donustur(geo.bas) : null),
    kare: globalThis.__isaretciKare ?? 0, sira: (globalThis.__isaretciSira = (globalThis.__isaretciSira || 0) + 1),
    ...(ek?.kimlik ? { kimlik: ek.kimlik } : {}),
    kutu: ek?.kutu ? [ek.kutu.left, ek.kutu.top, ek.kutu.right, ek.kutu.bottom] : null,
  });
}
const svgOlcum = ebeveyn => {
  const m = ebeveyn?.getScreenCTM?.();
  if (!m) return [1, p => p, null];
  const kok = ebeveyn.ownerSVGElement || ebeveyn;
  return [Math.sqrt(Math.abs(m.a * m.d - m.b * m.c)), p => [m.a * p[0] + m.c * p[1] + m.e, m.b * p[0] + m.d * p[1] + m.f], kok.getBoundingClientRect?.()];
};
const canvasOlcum = ctx => {
  const t = ctx.getTransform?.(), cv = ctx.canvas;
  const r = cv?.getBoundingClientRect?.();
  if (!t || !r || !cv.width) return [1, p => p, cv || null, null];
  const sx = r.width / cv.width, sy = r.height / cv.height;
  return [Math.sqrt(Math.abs(t.a * t.d - t.b * t.c)) * Math.sqrt(sx * sy),
    p => [r.left + (t.a * p[0] + t.c * p[1] + t.e) * sx, r.top + (t.b * p[0] + t.d * p[1] + t.f) * sy],
    cv, r];
};

/* --- SVG çizici --- */
const el = (ad, attrs, ebeveyn) => {
  const n = document.createElementNS(SVGNS, ad);
  for (const [k, v] of Object.entries(attrs)) if (v != null) n.setAttribute(k, v);
  ebeveyn?.appendChild(n);
  return n;
};

/**
 * SVG ok: <g class="isaretci {sinif}"> [hale] gövde + baş. Renk currentColor
 * (CSS `color` ile) ya da `renk`; kalınlık kullanıcı biriminde.
 * Dönen { g, govde, bas, geo } ya da null.
 */
export function okSvg(ebeveyn, secenek = {}) {
  const saydam = yariSaydam(secenek.renk, secenek.alfa);
  const s2 = saydam ? { ...secenek, govdeOrani: 1 } : secenek;
  const geo = s2.noktalar ? dirsekGeometrisi(s2) : okGeometrisi(s2);
  if (!geo) return null;
  const k = secenek.kalinlik ?? 3, renk = secenek.renk ?? 'currentColor';
  const g = el('g', { class: `isaretci ${secenek.sinif || ''}`.trim() }, ebeveyn);
  if (secenek.hale) {
    const hk = secenek.haleKalinlik ?? k + 4, hr = secenek.haleRenk ?? 'var(--color-canvas, #000)';
    el('path', { d: geo.govde, fill: 'none', stroke: hr, 'stroke-width': hk, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', class: 'isaretci__hale' }, g);
    el('path', { d: geo.bas, fill: hr, stroke: hr, 'stroke-width': hk - k, 'stroke-linejoin': 'round', class: 'isaretci__hale' }, g);
  }
  const govde = el('path', { d: geo.govde, fill: 'none', stroke: renk, 'stroke-width': k, 'stroke-linecap': saydam ? 'butt' : 'round', 'stroke-linejoin': 'round', class: 'isaretci__govde' }, g);
  if (secenek.alfa != null) g.setAttribute('opacity', secenek.alfa);   /* grup opaklığı: gövde+baş tek katman */
  if (secenek.kesik) govde.setAttribute('stroke-dasharray', secenek.kesik);
  const bas = el('path', { d: geo.bas, fill: renk, stroke: 'none', class: 'isaretci__bas' }, g);
  if (globalThis.__isaretciKayit) { const [o, d, r] = svgOlcum(ebeveyn); kaydet('svg', geo, secenek, o, d, { kimlik: g, kutu: r }); }
  return { g, govde, bas, geo };
}

/** SVG önder: çizgi + hedef noktası. */
export function onderSvg(ebeveyn, secenek = {}) {
  const geo = onderGeometrisi(secenek);
  if (!geo) return null;
  const k = secenek.kalinlik ?? 1.5, renk = secenek.renk ?? 'currentColor';
  const g = el('g', { class: `isaretci isaretci--onder ${secenek.sinif || ''}`.trim() }, ebeveyn);
  if (secenek.hale) el('path', { d: geo.govde, fill: 'none', stroke: secenek.haleRenk ?? 'var(--color-canvas, #000)', 'stroke-width': k + 4, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, g);
  el('path', { d: geo.govde, fill: 'none', stroke: renk, 'stroke-width': k, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', class: 'isaretci__govde' }, g);
  if (geo.nokta) el('circle', { ...geo.nokta, fill: renk, class: 'isaretci__nokta' }, g);
  if (globalThis.__isaretciKayit) { const [o, d, r] = svgOlcum(ebeveyn); kaydet('onder', { ...geo, uc: geo.bas, kuyruk: geo.rafUcu }, secenek, o, d, { kimlik: g, kutu: r }); }
  return { g, geo };
}

/** Renk ya da opaklık yarı saydam mı? (rgba/hsla/#rrggbbaa alfa < 1) */
const yariSaydam = (renk, alfa) => {
  if (alfa != null && alfa < 1) return true;
  const m = String(renk || '').match(/^(?:rgba|hsla)\([^)]*[,/]\s*([\d.]+%?)\s*\)$/i);
  if (m) return m[1].endsWith('%') ? parseFloat(m[1]) < 100 : parseFloat(m[1]) < 1;
  const h = String(renk || '').match(/^#[0-9a-f]{8}$/i);
  return !!h && parseInt(renk.slice(7), 16) < 255;
};

/* --- Canvas 2D çizici (aynı geometri) ---
   Yarı saydamken gövde DÜZ uçla tam çentikte biter: gövde ile baş üst üste
   binmez, kesişim iki kez boyanıp koyu/açık leke yapmaz. */
export function okCanvas(ctx, secenek = {}) {
  const saydam = yariSaydam(secenek.renk, secenek.alfa);
  const s2 = saydam ? { ...secenek, govdeOrani: 1 } : secenek;
  const geo = s2.noktalar ? dirsekGeometrisi(s2) : okGeometrisi(s2);
  if (!geo || typeof Path2D !== 'function') return geo;
  const k = secenek.kalinlik ?? 3, renk = secenek.renk ?? '#fff';
  ctx.save();
  if (secenek.alfa != null) ctx.globalAlpha = secenek.alfa;
  ctx.lineCap = saydam ? 'butt' : 'round'; ctx.lineJoin = 'round';
  if (secenek.hale) {
    ctx.strokeStyle = secenek.haleRenk ?? 'rgba(0,0,0,.6)';
    ctx.lineWidth = secenek.haleKalinlik ?? k + 4;
    ctx.stroke(new Path2D(geo.govde));
    ctx.stroke(new Path2D(geo.bas));
  }
  ctx.strokeStyle = renk; ctx.lineWidth = k;
  if (secenek.kesik) ctx.setLineDash(String(secenek.kesik).split(/[\s,]+/).map(Number));
  ctx.stroke(new Path2D(geo.govde));
  ctx.setLineDash([]);
  ctx.fillStyle = renk;
  ctx.fill(new Path2D(geo.bas));
  ctx.restore();
  if (globalThis.__isaretciKayit) { const [o, d, ad, r] = canvasOlcum(ctx); kaydet('canvas', geo, secenek, o, d, { alfa: ctx.globalAlpha, kimlik: ad, kutu: r }); }
  return geo;
}
