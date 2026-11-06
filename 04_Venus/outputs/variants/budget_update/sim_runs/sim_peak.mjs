import { Pw, sp, simKur } from './common.mjs';
for (const H of [null,-50.55,-47.1,-44.94,-42.8]) {
  const S=simKur(Pw,{senaryo:'birakma',sp,tohum:1}); if(H!==null) S.gunesH0=H*Math.PI/180;
  let I=0,Pb=0,Ps=0,tI=0;
  for(let i=0;i<70*500;i++){S.adim(); if(S.ip.kesildi&&S.diag.Ibat>I){I=S.diag.Ibat;Pb=S.diag.Pbus;Ps=S.diag.Psol;tI=S.t-S.ip.tKes;}}
  console.log(JSON.stringify({H,mu0:+Math.cos(S.gunesH0).toFixed(3),Ipeak:+I.toFixed(2),Pbus:+Pb.toFixed(0),Psol:+Ps.toFixed(0),t_after_release:+tI.toFixed(2),lost:S.tutuldu&&+S.tutuldu.kayip.toFixed(1),gap:+S.minAciklik.toFixed(3)}));
}
