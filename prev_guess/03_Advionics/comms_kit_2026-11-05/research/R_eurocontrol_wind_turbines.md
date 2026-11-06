# R_eurocontrol_wind_turbines — EUROCONTROL Guidelines: Potential Impact of Wind Turbines on Surveillance Sensors

## Citation
EUROCONTROL, *How to Assess the Potential Impact of Wind Turbines on Surveillance Sensors — EUROCONTROL Guidelines*, EUROCONTROL-GUID-130, Edition 1.2, September 2014, ISBN 978-2-87497-043-6. 68 PDF pages.
URL: https://www.eurocontrol.int/sites/default/files/2019-05/20140909-impact-wind-turbines-sur-sensors-guid-v1.2.pdf
Landing page: https://www.eurocontrol.int/publication/eurocontrol-guidelines-assessing-potential-impact-wind-turbines-surveillance-sensors
Date read: 2026-11-04. Read method: PDF text extracted with PyMuPDF; §4.1–4.4.3 read (doc p.27–35).
Source class: PRIMARY (EUROCONTROL guidelines).
Labels: [D-ag] read this session.

## Facts [D-ag]
- §4.1 (doc p.27): the first check is radar line of sight from the antenna's electrical centre. If no part of the turbine (e.g. a blade) is in line of sight, there is no impact.
- §4.2.1, Table 1 (doc p.28), **PSR zones**: Zone 1 is **0–500 m**, safeguarding (no turbines). Zone 2 is **500 m–15 km** in line of sight, detailed assessment. Zone 3 is **>15 km** within instrumented range and in line of sight, simple assessment. Zone 4 is not in line of sight or beyond instrumented range, no assessment. The 500 m and 15 km values derive from ICAO EUR DOC 015. They apply to 3-blade turbines, 30–200 m high, with a horizontal axis. "Zone 2 is not a No-Go area" (doc p.27).
- §4.2.2, Table 2 (doc p.31), **SSR zones (classical, monopulse, Mode S)**: Zone 1 is **0–500 m**, safeguarding. Zone 2 is **500 m–16 km** in line of sight, detailed assessment. Zone 4 is **>16 km** or not in line of sight, no assessment. There is no simple-assessment zone for SSR. The 16 km figure is justified from ICAO Annex 10 Vol IV.
- §4.2.3 (doc p.31): no turbines inside a sector **2 × the 3 dB horizontal beamwidth** centred on the far-field monitor azimuth, out to the monitor's range.
- §4.3.1 (doc p.33–34): PSR Pd is reduced in three ways: (1) a shadow behind the turbine; (2) a raised CFAR threshold in the turbine's range-azimuth cell and its neighbours, typically "one to sixteen clutter cells"; (3) a wider area if the plot extractor or tracker are affected. Footnote: the raised-threshold effect has been seen "at any range", so moving turbines further away does not necessarily help.
- §4.3.2 (doc p.34): a turbine is assumed detected if its tip (hub height + ½ rotor) is in line of sight. It can create false plots and even be promoted to a confirmed track.
- §4.3.3 (doc p.34): turbine echoes can overload the plot processor or tracker, triggering anti-overload measures.
- §4.4.2–4.4.3 (doc p.35): detailed assessment covers 3-D two-way attenuation (shadowing) and reflected energy across nacelle and blade orientations, frequency, wet surfaces, and terrain.

## Relevance to us [Y]
If our approach-area concept places sensors (or the airport has wind farms nearby), this is the EUROCONTROL rule of thumb: no turbines within 500 m, and a detailed study within 15 km (PSR) or 16 km (SSR). Wind turbine clutter is a known PSR false-track and Pd-hole problem, which motivates fusing with MLAT and ADS-B. It works as a "pain point" slide for the radar sponsor.
