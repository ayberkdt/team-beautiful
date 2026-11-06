import fs from 'node:fs'; import { Pw, sp, simKur } from './common.mjs';
const [,, name, etk, H0deg, dur] = process.argv;
const S = simKur(Pw, { senaryo:'birakma', sp, tohum:1, etkilesimAcik: etk==='1' });
S.gunesH0 = Number(H0deg)*Math.PI/180;
const out=[]; let started=false, sP=0,sS=0,k=0; const n=Math.round(Number(dur)*500);
for (let i=0;i<n;i++){ S.adim();
  if(!started && S.tutuldu && S.t>S.tutuldu.t0Abs+0){}
  if(!started && S.ip.kesildi && S.t> (S.ip.tKes??1e9)+60){ started=true; S.K.hRef=55000; S.K.vzMaxDown=1.5; S.K.vFF=[3.5,0]; out.push({ev:'descent start',t:S.t,h:S.y[2],soc:S.y[16]}); }
  if(i%50===0){sP+=S.diag.Pbus;sS+=S.diag.Psol;k++;}
  if(i%5000===4999){ out.push({t:+S.t.toFixed(0),h:+S.y[2].toFixed(1),vz:+S.y[5].toFixed(2),Pbus:+(sP/k).toFixed(0),Psol:+(sS/k).toFixed(0),soc:+S.y[16].toFixed(4),Tin:+(S.y[17]-273.15).toFixed(1),I:+S.diag.Ibat.toFixed(1),rpm:+(S.y[30]*30/Math.PI).toFixed(0)}); sP=sS=k=0; if(S.y[2]<55010 && started) break; }
}
fs.writeFileSync(name+'.json',JSON.stringify(out)); console.log(name, JSON.stringify(out[out.length-1]));
