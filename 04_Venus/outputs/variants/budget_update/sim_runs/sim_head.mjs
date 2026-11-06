import fs from 'node:fs'; import { Pw, sp, simKur } from './common.mjs';
const out=[];
for (const psi of [0,15,30,45,60]) {
  const S=simKur(Pw,{senaryo:'hover',sp,ruzgar:0,tohum:1,etkilesim:'nominal'});
  S.K.pRef=null; S.K.vFF=[9,0]; S.K.vCmd=[9,0]; S.y[3]=-S.atm.u+9; S.K.psiRef=psi*Math.PI/180;
  S.ilerle(120);
  let a=0,b=0,k=0; for(let i=0;i<10000;i++){S.adim(); if(i%10===0){a+=S.diag.Pshaft;b+=S.diag.Pbus;k++;}}
  const q=[S.y[6],S.y[7],S.y[8],S.y[9]]; const yaw=Math.atan2(2*(q[0]*q[3]+q[1]*q[2]),1-2*(q[2]*q[2]+q[3]*q[3]))*57.2958;
  const r={psi,sh:+(a/k).toFixed(1),el:+(b/k).toFixed(1),yaw:+yaw.toFixed(1),vAir:[+(S.y[3]+S.atm.u).toFixed(2),+S.y[4].toFixed(2)]};
  out.push(r); console.log(JSON.stringify(r)); fs.writeFileSync('sim_head.json',JSON.stringify(out));
}
