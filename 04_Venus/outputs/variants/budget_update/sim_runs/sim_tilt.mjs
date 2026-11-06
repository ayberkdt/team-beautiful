import fs from 'node:fs'; import { Pw, sp, simKur } from './common.mjs';
const SIMD='D:/Custom Yetenekler/sunumatik/.claude/worktrees/venus-rotorcraft-visual-44d0d1/presets/venus_rotorcraft/sim';
const { eulerden } = await import('file:///'+SIMD+'/venus-kontrol.mjs');
const [,, name, floor, seed, H0] = process.argv;
const S=simKur(Pw,{senaryo:'dalis',sp,tohum:Number(seed),etkilesim:'nominal'});
S.gunesH0=Number(H0)*Math.PI/180;
const F=Number(floor)*1000; let set=false, tilt=0,tT=0,hT=0,minsoc=1,Tmax=0; const peaks=[];
const n=4400*500;
for(let i=0;i<n;i++){ S.adim(); if(!set&&S.t>6){S.K.hRef=F;set=true;}
 if(i%50===0){const e=eulerden([S.y[6],S.y[7],S.y[8],S.y[9]]); const a=Math.hypot(e[0],e[1])*57.2958; if(a>tilt){tilt=a;tT=S.t;hT=S.y[2];} if(a>25) peaks.push([+S.t.toFixed(0),+S.y[2].toFixed(0),+a.toFixed(1),+S.y[5].toFixed(2)]); minsoc=Math.min(minsoc,S.y[16]); Tmax=Math.max(Tmax,S.y[17]-273.15);} }
console.log(name,JSON.stringify({tilt:+tilt.toFixed(1),t:+tT.toFixed(0),h:+hT.toFixed(0),minsoc:+minsoc.toFixed(3),Tmax:+Tmax.toFixed(1),over25:peaks.length,first:peaks[0],last:peaks[peaks.length-1]}));
