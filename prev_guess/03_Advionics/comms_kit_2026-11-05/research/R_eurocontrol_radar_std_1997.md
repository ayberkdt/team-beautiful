# R_eurocontrol_radar_std_1997 — EUROCONTROL Standard Document for Radar Surveillance in En-Route Airspace and Major Terminal Areas

## Citation
EUROCONTROL (EATCHIP), *EUROCONTROL Standard Document for Radar Surveillance in En-Route Airspace and Major Terminal Areas*, SUR.ET1.ST01.1000-STD-01-01, Edition 1.0, March 1997, Released Issue, General Public. 108 PDF pages.
URL: https://www.eurocontrol.int/sites/default/files/publication/files/surveillance-standard-document-for-radar-surveillance-in-en-route-airspace-and-major-terminal-areas199703.pdf
Landing page: https://www.eurocontrol.int/publication/eurocontrol-standard-radar-surveillance-en-route-airspace-and-major-terminal-areas
Date read: 2026-11-04. Read method: PDF text extracted with PyMuPDF; chapters 4–6 and Annex E tables read. "doc p." = printed page number.
Source class: PRIMARY. It is old (1997). ESASSP (R_esassp.md, Vol 1 Ed 1.3, 2024) refers to it as [RD 2], and ESASSP's system-level requirements supersede it. The sensor-level Pd and accuracy figures below are still widely quoted as the benchmark.
Labels: [D-ag] read this session.

## Operational requirements [D-ag]
- §4.1.2 (doc p.11): separation minima of 5 NM in high-density en-route, 10 NM in other en-route, and 3 NM in major terminal areas. Final approach surveillance is excluded from scope (§1.2, doc p.1 area).
- §5.1.3 (doc p.16): duplicated SSR coverage en route. Coverage must reach ≥ 30 NM beyond the ACC area of responsibility.
- §5.2.1 (doc p.17): data to display are horizontal position and history, identification, vertical position, the special codes 7500/7600/7700, ground speed, and track status (primary/secondary/combined/extrapolated). Recommended (§5.2.2): track prediction vectors. When STCA and MSAW are in use, their warnings are displayed.
- §5.2.3 (doc p.17): positional accuracy at the control position must be RMS ≤ 500 m en route and ≤ 300 m in major TMA.
- §5.2.4 (doc p.18): display update must be ≤ 5 s in major TMA and ≤ 8 s en route. "A maximum of 2 successive updates by extrapolation is acceptable". §5.2.5: Mode C is not extrapolated for display.
- §5.3.2, Table 1 (doc p.19): full data availability 0.995 (44 h/yr, max 4 h outage). Full data at reduced performance 0.999 (9 h, 10 min). Essential data 0.99999 (6 min/yr, max 10 s).

## SSR sensor requirements, §6.3 (doc p.30–33), recommended, "relevant to monopulse SSR" [D-ag]
- Overall Pd "> 97 %". False target report ratio "< 0.1 %".
- Multiple target reports < 0.3 % in total (reflections < 0.2 %, side lobes < 0.1 %, splits < 0.1 %).
- Mode A code detection > 98 %; Mode C code detection > 96 %.
- Systematic errors: slant range bias < 100 m; azimuth bias < 0.1°; range gain error < 1 m/NM; time stamp error < 100 ms.
- Random errors (σ): slant range < 70 m; azimuth < 0.08°. Jumps (> 1° or 700 m) < 0.05 %.
- False codes < 0.2 % overall; validated false Mode A < 0.1 %; validated false Mode C < 0.1 %.
- Resolution (Table 2): area 1 / 2 / 3 give Pd > 98 / > 98 / > 60 % and correct-code probability > 98 / > 90 / > 30 %. The stated conditions are 2 modes, IRF 240 Hz, rotation 10 s, Δθ1 = 2·n·360/(f·t), typically 0.6°.
- Availability: maximum outage ≤ 4 h; cumulative ≤ 10 h/yr. Switch-over to duplicated electronics within 2 s.
- §6.3.5 IRF plan: stagger the IRF; adjacent stations differ by ≥ 1 Hz; no IRF may be a multiple or sub-multiple of another station's (against synchronous FRUIT and second-time-around replies).
- §6.2.2.3 definitions: FRUIT = replies to another station's interrogation. Asynchronous FRUIT means the stations have different IRTs; synchronous FRUIT means identical IRTs. Second-time-around replies come from beyond the IRT-defined range.

## PSR sensor requirements, §6.4 (doc p.34–35), recommended [D-ag]
- Overall target position detection probability "> 90 %". False target reports "< 20" on average per antenna scan.
- Systematic errors: range bias < 100 m; azimuth bias < 0.1°; gain error < 1 m/NM; time stamp < 100 ms.
- Random errors (σ): slant range < 120 m; azimuth < 0.15°.
- Resolution: two targets are resolved like isolated targets if Δrange > 2 × compressed pulse width or Δazimuth > 3 × the 3 dB beamwidth. No resolution is required below 1.5 × pulse width and 1.5 × beamwidth.
- Availability: maximum outage ≤ 4 h; cumulative ≤ 40 h/yr.
- §6.2.2.3.3: false PSR reports include side-lobe returns, splits (in azimuth or range), and large-error returns. Weather, terrain and clutter can also create false PSR reports.

## Tracker requirements, Annex E (doc p.E/3–E/11) [D-ag]
- Scenarios assume **antenna revolution time 4 s for major TMA and 12 s en route**, range 150 km (81 NM), 300 kt, transversal acceleration 4 m/s², longitudinal 1 m/s².
- Track initiation (Table 1): mean initiation delay TIDmn 14 s (3.5 scans) for PSR TMA, 10 s (2.5) for PSR/SSR TMA, 30 s (2.5) for SSR en route. False track probability 0.001 tracks per false report.
- Tracker RMS accuracy, TMA, uniform motion: PSR only (Table 3A) 85 m along and across, GS 1.25 m/s, course 0.8°. One SSR (Table 4A): 60 m, 0.6 m/s, 0.7°. Two SSRs (Table 5A): 50 m, 0.6 m/s, 0.5°. In a standard turn: PSR 150 m / 6°; one SSR 100 m / 6°; two SSRs 70 m / 4.5°.
- Transition peak errors (e.g. Table 4B, one SSR, uniform → turn): 230 m across track and 17° course, with τ = 24 s (0.5) relaxation. The full tables are on doc p.E/6–E/11.

## Relevance to us [Y]
These are the classic numbers the sponsor's radar engineers will know: PSR Pd > 90 %, SSR Pd > 97 %, SSR range σ < 70 m and azimuth σ < 0.08°, update ≤ 5 s in TMA, 4 s / 12 s rotation scenarios, and Annex E tracker accuracies (one SSR in TMA, uniform motion: 60 m RMS). They are good benchmark values for our simulated sensor noise and for a tracker-accuracy slide. Its successor ESASSP (R_esassp.md) must be quoted for current system-level requirements.
