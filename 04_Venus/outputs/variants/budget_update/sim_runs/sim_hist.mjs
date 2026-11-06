import fs from 'node:fs'; import { Pw, sp, simKur } from './common.mjs';
const [,, name, senaryo, etk, H0deg, soc0, dur] = process.argv;
const R = process.env.RUZGAR ? Number(process.env.RUZGAR) : undefined; const S = simKur(Pw, { senaryo, sp, tohum: Number(process.env.TOHUM||1), etkilesimAcik: etk === '1', ...(R===undefined?{}:{ruzgar:R}) });
if (H0deg !== 'x') S.gunesH0 = Number(H0deg) * Math.PI / 180;
if (soc0 !== 'x') S.y[16] = Number(soc0);
const T = Number(dur), n = Math.round(T*500), out = [];
let sP=0,sS=0,sSh=0,k=0, tiltMax=0;
for (let i = 0; i < n; i++) { S.adim(); if (i%50===0){ sP+=S.diag.Pbus; sS+=S.diag.Psol; sSh+=S.diag.Pshaft; k++; }
 if (i % 15000 === 14999) { const sun=S.gunes(); out.push({t:+S.t.toFixed(0),h:+S.y[2].toFixed(1),vz:+S.y[5].toFixed(3),Pbus:+(sP/k).toFixed(1),Psh:+(sSh/k).toFixed(1),Psol:+(sS/k).toFixed(1),soc:+S.y[16].toFixed(4),Tin:+(S.y[17]-273.15).toFixed(2),mu0:+sun.mu0.toFixed(4),Ib:+S.diag.Ibat?.toFixed?.(2)}); sP=sS=sSh=k=0; } }
fs.writeFileSync(name+'.json', JSON.stringify(out)); console.log(name, JSON.stringify(out[out.length-1]));
