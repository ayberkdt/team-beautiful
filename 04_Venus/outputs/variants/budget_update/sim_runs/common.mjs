import fs from 'node:fs'; import path from 'node:path'; import { pathToFileURL } from 'node:url';
export const DIR = 'D:/Custom Yetenekler/sunumatik/.claude/worktrees/venus-rotorcraft-visual-44d0d1/presets/venus_rotorcraft/sim';
const M = await import(pathToFileURL(path.join(DIR,'venus-sim.mjs')).href);
export const { parametreKur, simKur } = M;
const oku = (f) => JSON.parse(fs.readFileSync(path.join(DIR, f), 'utf8'));
export const sp = oku('sim_params.json'), tas = oku('../tasarim.json'), ref = oku('aerokit_referans.json');
export const Pw = parametreKur(sp, tas, ref, { Nr: 10, Npsi: 6 });
