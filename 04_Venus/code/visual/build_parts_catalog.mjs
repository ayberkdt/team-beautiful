#!/usr/bin/env node
/* build_parts_catalog.mjs — 3B mekanizma kataloğunu Sunumatik kaynağından ölçerek yazar: catalog/parts_3d.md ve .json.
 *
 *   node 04_Venus/code/visual/build_parts_catalog.mjs [--sunumatik <worktree yolu>]
 *
 * Kaynak: presets/venus_rotorcraft/arac/katalog.mjs (görev, alt parça, modül) ve aynı kurucuların mesh sayımı.
 * Üretim saati yazılmaz; aynı kod aynı dosyayı verir. */
import fs from 'node:fs';
import path from 'node:path';
import { register } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const arg = process.argv.slice(2), i = arg.indexOf('--sunumatik');
const KOK = i >= 0 ? arg[i + 1] : 'D:/Custom Yetenekler/sunumatik/.claude/worktrees/venus-rotorcraft-visual-44d0d1';
const CATALOG = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../catalog');
const yol = (p) => pathToFileURL(path.join(KOK, p)).href;
register(yol('scripts/three-resolver.mjs'));
const THREE = await import(yol('presets/moon_advanced/vendor/three.module.min.js'));
const { baglamKur } = await import(yol('presets/venus_rotorcraft/arac/yardimci.mjs'));
const { MEKANIZMALAR, mekanizmaKur } = await import(yol('presets/venus_rotorcraft/arac/katalog.mjs'));
const { aracKur } = await import(yol('presets/venus_rotorcraft/arac/montaj.mjs'));
const { tasarimHazirla } = await import(yol('presets/venus_rotorcraft/venus-tasarim.mjs'));
const H = tasarimHazirla(JSON.parse(fs.readFileSync(path.join(KOK, 'presets/venus_rotorcraft/tasarim.json'), 'utf8')));
const C = baglamKur(H);

const say = (o) => { let mesh = 0, tri = 0; o.traverse(m => { if (!m.isMesh) return; mesh++; const g = m.geometry, n = (g.index ? g.index.count : g.attributes.position.count) / 3; tri += n * (m.isInstancedMesh ? m.count : 1); }); return { mesh, tri: Math.round(tri) }; };
const satirlar = MEKANIZMALAR.map((m) => {
  const { g } = mekanizmaKur(m.id, C), b = new THREE.Box3().setFromObject(g), s = b.getSize(new THREE.Vector3());
  const c = H.bilesen.get(m.bilesen), e = m.ek ? H.bilesen.get(m.ek) : null;
  return { id: m.id, ad: m.ad, modul: m.modul, gorev: m.gorev, alt: m.alt, ...say(g), boyut_m: [s.x, s.y, s.z].map(v => Number(v.toFixed(3))),
    kutle_kg: Number(((c?.mass_kg ?? 0) + (e?.mass_kg ?? 0)).toFixed(3)), kutle_notu: m.adet === 'rotor' ? `grup kütlesi, ${H.rotor.count} rotora bölünür` : (e ? `${m.bilesen} + ${m.ek}` : m.bilesen) };
});
const tum = say(aracKur(H).kok);

/* kolun arka yüz gölgesi: kol güvertenin altından geçer; alan = tüp çapı × (altıgen iç teğeti − delik yarıçapı) × kol sayısı */
const S = H.arac.solar, delik = Math.max(C.tx, C.ty) / 2 * 1.04, apotem = S.circumradius_m * Math.cos(Math.PI / 6);
const golge = 2 * C.tR * (apotem - delik) * H.rotor.count, oran = golge / S.area_m2;

const json = { kaynak: 'presets/venus_rotorcraft/arac/katalog.mjs', tasarim: `${H.d.version} · ${H.arac.total_mass_kg} kg`, arac: tum, mekanizmalar: satirlar,
  kol_arka_golge: { alan_m2: Number(golge.toFixed(3)), guverte_orani: Number(oran.toFixed(3)), etiket: 'K on Y; çizim yerleşiminden, hesapta yok' } };
fs.writeFileSync(path.join(CATALOG, 'parts_3d.json'), `${JSON.stringify(json, null, 2)}\n`);

const md = [
  '# 3B mekanizma kataloğu', '',
  'Üretildi: `node 04_Venus/code/visual/build_parts_catalog.mjs`. Elle değiştirmeyin.',
  `Kaynak: Sunumatik \`presets/venus_rotorcraft/arac/\`. Tasarım: ${json.tasarim}. Bütün araç: ${tum.mesh} mesh, ${tum.tri} üçgen.`, '',
  'Kütle tasarım dosyasından, bileşen düzeyindedir. Alt parçaların yerleşimi ve oranı çizim seçimidir; ayrı kütleleri hesaplanmadı.', '',
  '| Mekanizma | Kod | Kütle kg | Mesh | Üçgen | Boyut m |', '|:---|:---|---:|---:|---:|:---|',
  ...satirlar.map(r => `| ${r.ad} | \`${r.modul}\` | ${r.kutle_kg.toFixed(2)} (${r.kutle_notu}) | ${r.mesh} | ${r.tri} | ${r.boyut_m.join(' × ')} |`), '',
  ...satirlar.flatMap(r => [`## ${r.ad}`, '', r.gorev, '', ...r.alt.map(a => `- ${a}`), '']),
  '## Modelden çıkan tasarım notu', '',
  `Kol tüpleri güvertenin altından geçer. Üst yüzü gölgelemez, arka yüzün ${golge.toFixed(2)} m²'sini kapatır: güverte alanının yaklaşık %${(oran * 100).toFixed(1)}'i [K on Y].`,
  'Bu kayıp `aerokit.venus.power` içinde yoktur. Doc 25 §4.4 yalnız kabın gölgesini (%6) not eder. Arka yüz güç payı 0,42 olduğundan etkisi toplam güçte üst sınır olarak yaklaşık %4 olur; ışık yaygın olduğu için gerçek kayıp daha küçük olabilir, ölçülmedi.', '',
];
fs.writeFileSync(path.join(CATALOG, 'parts_3d.md'), md.join('\n'));
console.log(`parts_3d: ${satirlar.length} mekanizma, araç ${tum.mesh} mesh, ${tum.tri} üçgen, kol gölgesi ${(oran * 100).toFixed(1)} %`);
