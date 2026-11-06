import { Pw, sp, simKur } from './common.mjs';
const S=simKur(Pw,{senaryo:'birakma',sp,tohum:1});
let Imax=0,tilt=0; for(let i=0;i<70*500;i++){S.adim(); if(S.ip.kesildi) Imax=Math.max(Imax,S.diag.Ibat);}
console.log(JSON.stringify({tutuldu:S.tutuldu,minGap:S.minAciklik,Imax,lim:2*3.35*Pw.batarya.paralel,par:Pw.batarya.paralel}));
const M=simKur(Pw,{senaryo:'motor',sp,tohum:1});
let hmin=1e9,I2=0,rp=0; for(let i=0;i<60*500;i++){M.adim(); hmin=Math.min(hmin,M.y[2]); I2=Math.max(I2,M.diag.Ibat); }
console.log(JSON.stringify({lost:55000-hmin,I2}), JSON.stringify(M.telemetri().rpm));
