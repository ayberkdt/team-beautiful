#!/usr/bin/env node
/* fly_short_demo.mjs — 0,5 kg gösterim varyantını Sunumatik simülatöründe uçurur; dosyalar değişmez, yalnız sonuç yazılır.
 *
 *   node 04_Venus/code/visual/fly_short_demo.mjs [--sunumatik <worktree>]
 *
 * Girdi: outputs/variants/short_demo/files_0p5kg/{design,sim_params}.json. aerokit_referans.json v0.6 kopyasıdır;
 * pala veteri, askı kütlesi, hover torku ve dikey türev bu tasarımdan yazılır. Çıktı: short_demo/sim_flight.json ve .md. */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const arg = process.argv.slice(2), i = arg.indexOf('--sunumatik');
const KOK = i >= 0 ? arg[i + 1] : 'D:/Custom Yetenekler/sunumatik/.claude/worktrees/venus-rotorcraft-visual-44d0d1';
const OUT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../outputs/variants/short_demo');
const SIM = path.join(KOK, 'presets/venus_rotorcraft/sim');
const u = (f) => pathToFileURL(path.join(SIM, f)).href;
const { parametreKur, simKur } = await import(u('venus-sim.mjs'));
const { eulerden } = await import(u('venus-kontrol.mjs'));
const oku = (f) => JSON.parse(fs.readFileSync(f, 'utf8'));
const sp = oku(path.join(OUT, 'files_0p5kg/sim_params.json')), tas = oku(path.join(OUT, 'files_0p5kg/design.json'));
const ref = oku(path.join(SIM, 'aerokit_referans.json'));

const R = tas.vehicle.rotor, v = (x) => (x && typeof x === 'object' && 'value' in x ? x.value : x);
const mass = v(sp.vehicle.mass), g = ref.atmosfer_55km.g, T = mass * g / 6;
const satir = v(sp.vehicle.rotors.curve_at_55km.rows ?? sp.vehicle.rotors.curve_at_55km);
const k = satir.findIndex(r => r.thrust_N >= T), a = satir[k - 1], b = satir[k], f = (T - a.thrust_N) / (b.thrust_N - a.thrust_N);
Object.assign(ref.rotor, { root_chord: R.root_chord_m, tip_chord: R.tip_chord_m, theta75_deg: R.collective_75_deg });
ref.kutle_kg = mass;
ref.hover_55km.torque_per_rotor_bemt_Nm = (a.torque_Nm + f * (b.torque_Nm - a.torque_Nm)) / ref.rotor.bemt_power_factor;
ref.heave_turevi_N_per_m_s = v(sp.vehicle.rotors.heave_derivative);
ref.birakma.m_suspended_kg = tas.entry.suspended_mass_kg;

const P = parametreKur(sp, tas, ref, { Nr: 10, Npsi: 6 });
const DEG = Math.PI / 180, limitA = 2 * 3.35 * P.batarya.paralel;
const egim = (S) => { const e = eulerden([S.y[6], S.y[7], S.y[8], S.y[9]]); return Math.hypot(e[0], e[1]) / DEG; };
const ort = (S, sure, fn) => { let s = 0, n = 0; for (let j = 0; j < sure * 500; j++) { S.adim(); if (j % 25 === 0) { s += fn(S); n++; } } return s / n; };

function birak(mu0, etkilesim) {
  const S = simKur(P, { senaryo: 'birakma', sp, tohum: 1, etkilesim, mu0 });
  let I = 0, tilt = 0;
  for (let j = 0; j < 70 * 500; j++) { S.adim(); I = Math.max(I, S.diag.Ibat); if (S.ip.kesildi) tilt = Math.max(tilt, egim(S)); }
  return { mu0, etkilesim, tutuldu: Boolean(S.tutuldu), kayip_m: S.tutuldu?.kayip ?? null, sure_s: S.tutuldu?.t ?? null, tepe_akim_A: I, limit_A: limitA, en_az_kanopi_m: S.minAciklik, tepe_egim_deg: tilt };
}
function izle(S, sure) {
  let hmin = Infinity, hmax = -Infinity, tilt = 0, I = 0; const h0 = S.y[2];
  for (let j = 0; j < sure * 500; j++) { S.adim(); hmin = Math.min(hmin, S.y[2]); hmax = Math.max(hmax, S.y[2]); tilt = Math.max(tilt, egim(S)); I = Math.max(I, S.diag.Ibat); }
  return { kayip_m: h0 - hmin, ust_m: hmax - h0, tepe_egim_deg: tilt, tepe_akim_A: I };
}
function seviye(V) {
  const S = simKur(P, { senaryo: 'hover', sp, ruzgar: 0, tohum: 1, etkilesim: 'nominal' });
  if (V) { S.K.pRef = null; S.K.vFF = [V, 0]; S.K.vCmd = [V, 0]; S.y[3] = -S.atm.u + V; }
  S.ilerle(30);
  return { V_m_s: V, bus_W: ort(S, 10, (s) => s.diag.Pbus), shaft_W: ort(S, 5, (s) => s.diag.Pshaft) };
}
function turbulans(sen, sure) { const S = simKur(P, { senaryo: sen, sp, tohum: 1, etkilesim: 'nominal' }); S.ilerle(10); return { senaryo: sen, sure_s: sure, ...izle(S, sure) }; }
function motorOut() {
  let en = { tepe_egim_deg: 0 };
  for (let r = 0; r < 6; r++) { const S = simKur(P, { senaryo: 'hover', sp, tohum: 1, etkilesim: 'nominal' }); S.ilerle(10); S.motorBoz(r); const x = izle(S, 50); if (x.tepe_egim_deg > en.tepe_egim_deg) en = { rotor: r + 1, ...x }; }
  return en;
}

const sonuc = {
  girdi: { kutle_kg: mass, paralel: P.batarya.paralel, batarya_Wh: P.power.battery_Wh, not: 'aerokit_referans.json v0.6 üstüne bu tasarımın veter, kütle, tork, dikey türev değerleri' },
  birakma: [birak(0.94, 'nominal'), birak(0.94, 'high'), birak(0.70, 'nominal')],
  seviye: [seviye(0), seviye(9)],
  turbulans: [turbulans('hover', 100), turbulans('gust', 70)],
  motor_arizasi_en_kotu: motorOut(),
};
const b = sonuc.birakma[0], m = sonuc.motor_arizasi_en_kotu;
sonuc.denetim = { tutuldu: sonuc.birakma.every(x => x.tutuldu), akim_limit_alti: sonuc.birakma.every(x => x.tepe_akim_A <= limitA), kanopi_acik: sonuc.birakma.every(x => x.en_az_kanopi_m > 0), motor_egim_45_alti: m.tepe_egim_deg <= 45, motor_kayip_30_alti: m.kayip_m <= 30 };
fs.writeFileSync(path.join(OUT, 'sim_flight.json'), `${JSON.stringify(sonuc, null, 1)}\n`);
const f1 = (x) => (x == null ? '—' : Number(x).toFixed(1));
const md = ['# Simülatör uçuşu, 0,5 kg gösterim varyantı', '', 'Üretildi: `node 04_Venus/code/visual/fly_short_demo.mjs`. Çözünürlük 10 × 6, tohum 1, nominal etkileşim (aksi yazmıyorsa).', `Kütle ${mass.toFixed(2)} kg, ${P.batarya.seri ?? 14}S${P.batarya.paralel}P, akım limiti ${limitA.toFixed(1)} A.`, '',
  '## Bırakma', '', ...sonuc.birakma.map(x => `- cos z ${x.mu0}, ${x.etkilesim}: kayıp ${f1(x.kayip_m)} m, ${f1(x.sure_s)} s, akım ${f1(x.tepe_akim_A)} A, kanopi ${x.en_az_kanopi_m?.toFixed(2)} m, eğim ${f1(x.tepe_egim_deg)}°`), '',
  '## Seviye uçuş', '', ...sonuc.seviye.map(x => `- ${x.V_m_s} m/s: bus ${x.bus_W.toFixed(0)} W`), '',
  '## Türbülans', '', ...sonuc.turbulans.map(x => `- ${x.senaryo} ${x.sure_s} s: −${f1(x.kayip_m)} / +${f1(x.ust_m)} m, eğim ${f1(x.tepe_egim_deg)}°, akım ${f1(x.tepe_akim_A)} A`), '',
  `## Motor arızası, altı rotorun en kötüsü`, '', `- Rotor ${m.rotor}: kayıp ${f1(m.kayip_m)} m, eğim ${f1(m.tepe_egim_deg)}°, akım ${f1(m.tepe_akim_A)} A`, '',
  '## Denetim', '', ...Object.entries(sonuc.denetim).map(([k2, v2]) => `- ${k2}: ${v2 ? 'geçti' : 'KALDI'}`), ''];
fs.writeFileSync(path.join(OUT, 'sim_flight.md'), md.join('\n'));
console.log(md.join('\n'));
void b;
