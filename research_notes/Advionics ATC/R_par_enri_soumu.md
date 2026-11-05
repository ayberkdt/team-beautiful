# R_par_enri_soumu — ENRI (Japan) presentation "Overview of Precision Approach Radar PAR" (精測進入レーダPARの概要)

## Citation
Author as printed: 小瀬木 滋 (romanisation not verified by the agent), National Institute of Maritime, Port and Aviation Technology, Electronic Navigation Research Institute (ENRI, 電子航法研究所), Surveillance and Communications Department. *精測進入レーダPARの概要* (Overview of PAR), document "資料SAR作2-5", hosted by the Japanese Ministry of Internal Affairs and Communications (総務省). 4 slides. No date visible in the text.
URL: https://www.soumu.go.jp/main_content/000376472.pdf
Date read: 2026-11-04 (PDF text extracted; Japanese read by the agent and translated here as paraphrase).
Source class: SECONDARY summary by a national research institute. Slide 2 summarises **ICAO Annex 10 Vol I, Ch. 3, §3.2.3** (PAR element); Annex 10 itself was not read (paywalled). Slides 3–4 cite Japanese textbooks (航空電子装置, 日刊工業新聞社, 1978; 改訂レーダ技術, IEICE, 1999).
Labels: [D-ag] read this session; [A] via search snippet only.

## Facts [D-ag]
Slide 2, "PAR performance international standard (Annex 10 Vol I, 3.2.3)":
- Coverage: at least 9 NM from the antenna; sector EL 7°, AZ 20°.
- Assumed target: RCS 15 m² (equivalent to a small twin-engine aircraft).
- Accuracy example on the landing course (stricter at the touchdown point):
  - EL: 6 m from course, or 0.4 % of range + 10 % of offset. Resolution 0.6°.
  - AZ: 9 m from course, or 0.6 % of range + 10 % of offset. Resolution 1.2°.
  - Range: 30 m, or 3 % of range.
- Display update: within 1 second.
Slide 3, example spec (c. 1975):
- Frequency **9080 ± 80 MHz** (X-band, fixed). AZ antenna beamwidth < 0.8° horizontal and < 3.0° vertical; EL antenna < 0.5° horizontal and < 4.0° vertical. Gain > 40 dBi.
- Scan rate 1 Hz (2 scans per second). Peak power ≥ 30 kW; pulse 0.25 μs; PRF 1833 pps.
Slide 4, example spec (1998 onward):
- Same frequency and antenna figures. Peak power ≥ 70 kW; PRF 2400 pps. A high-performance requirement example: Pd > 90 % at RCS = 2 m², with false-detection rate < 10⁻¹⁰. Modern designs use electronically scanned pencil beams, pulse compression and frequency agility.

Corroboration [A]: a search snippet of a Tanzanian CAA regulation (tcaa.go.tz; the PDF could not be downloaded) gave the same 9 NM, 20°/7°, 0.6 % + 10 % (AZ) and 0.4 % + 10 % (EL) values.

## Relevance to us [Y]
PAR is the radar precedent for "automated approach guidance": ground radar measures deviation from the glidepath and the controller talks the pilot down. Annex 10 accuracy (EL 0.4 % R + 10 % offset, AZ 0.6 % R + 10 % offset), a 1 s update and the 9 NM coverage are the benchmark our concept should beat or match using MLAT/ADS-B fusion. The X-band 9 GHz figure is confirmed by an example spec, not by Annex 10.
