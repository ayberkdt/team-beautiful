# R_lpv_par_wiki — Wikipedia, "Localizer performance with vertical guidance" and "Precision approach radar"

## Citation
1. Wikipedia contributors, "Localizer performance with vertical guidance", English Wikipedia, last edit 14:50, 22 October 2026. https://en.wikipedia.org/wiki/Localizer_performance_with_vertical_guidance
2. Wikipedia contributors, "Precision approach radar", English Wikipedia, last edit 15:31, 4 December 2025. https://en.wikipedia.org/wiki/Precision_approach_radar
Two short secondary articles are grouped in one file. Date read: 2026-11-04 (raw wikitext, references stripped for reading). Source class: SECONDARY.
Labels: [D-ag] read this session.

## LPV [D-ag]
- LPV is a GPS procedure with SBAS (WAAS, EGNOS, MSAS). Minima are similar to ILS CAT I: DH 200 ft, visibility 800 m. Early procedures were **LPV-250** (DA 250 ft); **LPV-200** came into use in the late 2010s and early 2020s.
- "Designed to provide 25 ft lateral and vertical accuracy 95 percent of the time." The "never > 12 m vertical error" claim carries a {{Citation needed}} tag and is not used.
- Classified as **APV** (approach with vertical guidance), not a precision approach under ICAO Annex 10. SBAS criteria include a vertical alarm limit "more than 12 m, but less than 50 m".
- FAA counts: 3,567 LPV approaches at 1,739 airports (17 Sep 2015); 4,088 at 1,965 airports (7 Oct 2021), more than the number of CAT I ILS procedures.
- LP (no vertical guidance) is flown to an MDA. FAA AC 90-107 is the reference.
- Not found in this article: HAL/VAL numbers for LPV-200 (e.g. 40 m / 35 m) and GBAS GAST-C/D figures. "Ground-based augmentation system" redirects to "GNSS augmentation"; **not read**. GBAS/LPV-200 alert limits remain an open item and have NOT been verified.

## PAR [D-ag]
- PAR gives lateral and vertical guidance until threshold. Controllers watch the display and talk the aircraft down; this is GCA. After DH/DA, guidance is advisory only.
- The display has two traces: elevation against the glideslope (upper) and azimuth against the centreline (lower).
- Mostly military (AN/FPN-63, AN/MPN, AN/TPN-22). It guides from "10 to 20 miles" down to threshold. Favoured by the Navy because it emits no directional beam an enemy could exploit.
- Non-traditional PAR: the **Transponder Landing System (TLS)** uses Mode 3/A replies with TOA, DTOA and AOA to compute a 3-D position for the GCA display. It is L-band, so there is no rain fade, and it has a 60 NM operational range. It depends on the transponder.
- Frequency band and accuracy are **not given** in this article. See R_par_enri_soumu.md (9080 ± 80 MHz example; Annex 10 accuracy summary).

## Relevance to us [Y]
TLS is a close existing analogue to our "automated approach guidance from SSR/MLAT data" concept: ground computes the position from transponder replies and shows deviation from the glide path. This is a strong prior-art point to raise with the radar/SSR sponsor. LPV-200 ≈ CAT I minima is the satellite-based competitor baseline.
