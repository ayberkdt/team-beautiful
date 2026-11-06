import fs from 'node:fs'; import { Pw, sp, simKur } from './common.mjs';
const clone = (s) => ({...Pw, rotorlar: Pw.rotorlar.map(r => ({...r, pos: [r.pos[0]*s, r.pos[1]*s, r.pos[2]]}))});
const R0 = Math.hypot(Pw.rotorlar[0].pos[0], Pw.rotorlar[0].pos[1]);
function olc(P, e, V, {vd=0, vc=0, psi=0, km=55}={}) {
  const S = simKur(P, { senaryo:'hover', sp, ruzgar:0, tohum:1, etkilesim:e, h0:km*1000 });
  if (V) { S.K.pRef=null; S.K.vFF=[V,0]; S.K.vCmd=[V,0]; S.y[3]=-S.atm.u+V; }
  if (psi) S.K.psiRef=psi*Math.PI/180;
  if (vd) { S.K.hRef=40000; S.K.vzMaxDown=vd; }
  if (vc) { S.K.hRef=62000; }
  S.ilerle(30);
  let a=0,b=0,k=0,v0=0; const n=Math.round(10/S.dt);
  for (let i=0;i<n;i++){ S.adim(); if(i%10===0){a+=S.diag.Pshaft;b+=S.diag.Pbus;v0+=S.y[5];k++;} }
  return {sh:+(a/k).toFixed(1), el:+(b/k).toFixed(1), vz:+(v0/k).toFixed(3), h:+S.y[2].toFixed(0)};
}
const res={R0,pts:[]}; const add=(tag,o)=>{res.pts.push({tag,...o}); console.log(tag,JSON.stringify(o)); fs.writeFileSync('sim_pts2.json',JSON.stringify(res));};
const C=['off','low','nominal','high'];
for (const km of [55,53]) for (const e of C) { add('level35',{km,e,V:3.5,...olc(Pw,e,3.5,{km})}); add('descent',{km,e,V:3.5,vd:1.5,...olc(Pw,e,3.5,{vd:1.5,km})}); }
for (const km of [55,53]) for (const e of C) { add('climb',{km,e,V:8,vc:3,...olc(Pw,e,8,{vc:3,km})}); add('level8',{km,e,V:8,...olc(Pw,e,8,{km})}); }
for (const psi of [0,15,30,45]) add('heading',{V:9,psi,e:'nominal',...olc(Pw,'nominal',9,{psi})});
for (const c of [0.10,0.26,0.52,0.78]) { const s=(2.6+c)/R0; for (const V of [0,5,7,8,9,10,12]) add('spacing',{c,V,e:'nominal',...olc(clone(s),'nominal',V)}); }
for (const c of [0.26,0.52,0.78]) { const s=(2.6+c)/R0; for (const V of [8,9]) { add('spacing_off',{c,V,e:'off',...olc(clone(s),'off',V)}); add('spacing_high',{c,V,e:'high',...olc(clone(s),'high',V)});} }
