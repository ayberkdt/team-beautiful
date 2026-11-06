# R_faa_aim_ch1 — FAA Aeronautical Information Manual (AIM), Chapter 1 Section 1 "Navigation Aids"

## Citation
U.S. FAA, *Aeronautical Information Manual*, Chapter 1 "Air Navigation", Section 1 "Navigation Aids" (HTML edition). URL: https://www.faa.gov/air_traffic/publications/atpubs/aim_html/chap1_section_1.html
The edition date was not visible in the extracted text. Date read: 2026-11-04 (HTML fetched with curl, tags stripped, paragraphs read).
Source class: PRIMARY (FAA official publication; US rules).
Labels: [D-ag] read this session.

## ILS, para 1-1-9 [D-ag]
- Components: localizer, glide slope and OM (plus IM for CAT II/III). The OM can be substituted by PAR, ASR, DME, etc.
- **Localizer**: "one of 40 ILS channels within the frequency range of 108.10 to 111.95 MHz". Course width (full fly-left to full fly-right) is 700 ft at threshold. Coverage: 18 NM from the antenna, between 1,000 ft above terrain and 4,500 ft above the antenna site; proper off-course indications to ±10° out to 18 NM and from 10° to 35° at shorter range (the text continued beyond the excerpt read).
- **Glide slope**: "one of the 40 ILS channels within the frequency range 329.15 MHz, to 335.00 MHz". The antenna is 750–1,250 ft down the runway and offset 250–650 ft from the centreline. Beam 1.4° wide (vertically). Normally a 3° angle, crossing the MM at about 200 ft and the OM at about 1,400 ft. Normally usable to 10 NM.
- **TBL 1-1-9 frequency pairs** (LOC → GS, MHz), verbatim sample: 108.10→334.70, 108.15→334.55, 108.3→334.10, 108.35→333.95, 108.5→329.90, 108.55→329.75, 108.7→330.50, 108.75→330.35, 108.9→329.30, 108.95→329.15, 109.1→331.40, 109.15→331.25, 109.3→332.00, 109.35→331.85, 109.50→332.60, 109.55→332.45, 109.70→333.20, 109.75→333.05, 109.90→333.80, 109.95→333.65, 110.1→334.40, 110.15→334.25, 110.3→335.00, 110.35→334.85, 110.5→329.60, 110.55→329.45, 110.70→330.20, 110.75→330.05, 110.90→330.80, 110.95→330.65, 111.10→331.70, 111.15→331.55, 111.30→332.30, 111.35→332.15, 111.50→332.9… (the table continues; the remaining pairs were not copied).
- Reconciliation: the AIM's 329.15–335.00 MHz is the range of **allocated GS channels**. Wikipedia's 328.6–335.4 MHz (R_ils_wiki.md) is the wider **band**. Both can be correct.

## WAAS / LPV, para 1-1-18 [D-ag]
- LPV and LNAV/VNAV are APV approaches (ICAO Annex 6), not precision approaches.
- Lateral integrity changes "from the 0.3 NM (556 meter) limit for GPS, LNAV, and LNAV/VNAV approach mode, to **40 meters for LPV**".
- Vertical integrity: bounds the vertical error to **50 m** for LNAV/VNAV and LPV with minima ≥ 250 ft, and to **35 m** for LPV with minima below 250 ft (i.e. LPV-200).

## GBAS / GLS, para 1-1-19 [D-ag]
- GBAS (formerly LAAS) provides local differential GPS augmentation for GLS precision approach, with benefits "similar to ... an ILS or LPV".
- The GBAS Ground Facility has **at least four ground reference stations**, a corrections processor and a VHF Data Broadcast (VDB) antenna. The aircraft needs RNP APCH eligibility plus a GBAS receiver installation.
- No numeric GBAS alert limits were found in the excerpt read.

## Relevance to us [Y]
These are primary, citable numbers for the approach-aid comparison slide: ILS LOC 108.10–111.95 MHz (40 channels), GS 329.15–335.00 MHz, 3° glide path, 700 ft course width at threshold; LPV HAL 40 m, VAL 35 m (LPV-200) or 50 m; GBAS has ≥ 4 reference receivers plus VDB. They also give the frequency-pair table if we simulate an ILS receiver.
