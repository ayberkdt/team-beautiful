# S_intersoft_liesa_leaflet: L-IESA® NR-IFF leaflet (IE-CD-01489-002)

- **URL:** https://intersoft-electronics.com/wp-content/uploads/2026/10/IE-CD-01489-002-L-IESA-LEAFLET-A4-1.pdf
- **Date read:** 2026-11-04. WebFetch saved the PDF and I read it with `pdftotext -layout`.
- **Caveat:** in the text extraction, the specification labels and values came out **shifted by one row**. I re-paired them by meaning (gain ↔ dBi, beamwidth ↔ degrees, and so on). The pairing is my reading [Y]. The values themselves are quoted exactly [D-ag].

## Capabilities box (read directly, not affected by the shift) [D-ag]
- "Extended IFF Range Coverage (200NM) with medium power interrogator (1200W)".
- "Electronic Scanning Surveillance (360°, as fast as 120rpm)" and "Agile Jumping/Pointing of beams (100ms)".
- "Vertical steering and compensation of platform movement (±15° Roll/Pitch)".
- An omnidirectional IFF transponder (360°) and Link-16 (360°) antenna functions are fully integrated.
- Supported modes: Mode 1, 2, 3/A, C, S (Elementary and Enhanced Surveillance), ADS-B, Mode 5 Level 1 and 2.

## Specification table (values exact; label pairing is my reading [Y])
| Parameter | Value |
|---|---|
| Antenna gain | "> 22dBi" |
| 3 dB azimuth beamwidth | "less than 8°" |
| Azimuth accuracy | "<0.1° RMS (stationary)" |
| 3 dB elevation beamwidth | ">17°" |
| Sum–Delta notch | ">30dB" |
| SLS | ">9dB below SUM peak" |
| Further antenna channels | IFF Transponder, Link-16 |
| Azimuth coverage | 360° |
| Max. range | ">200NM" |
| Elevation coverage | ">50° (cumulative)" |
| Elevation beams | Vertical Antenna Pointing Diversity |
| Multipath suppression | dynamic elevation beam switching |
| Standards | ICAO Annex 10 Vol III/IV, STANAG 4193 Ed. 3, AIMS17-1000 (compliant); MIL-STD-810H, 461G, AECTP230, 500 (qualified); CE / RED / RoHS / REACH (compliant) |
| System MTBCF | "> 4.500h (MIL-HDBK-217F NU/NS 20°C)" |
| Documentation | IETD ASD 1000D, 2000M |
| Outer diameter | "< 3.700mm" |
| Inner diameter | "> 2.800mm" |
| Height | "< 1000mm" |
| Weight | "<700kg" |
| Cooling | passive convection cooling, no liquids |

## Relevance to us [Y]
- These are the only hard IFF numbers the group publishes. Use them as sanity anchors in the pitch:
  - 200 NM with a 1200 W interrogator;
  - azimuth accuracy below 0.1° RMS;
  - beam re-pointing in 100 ms;
  - roll and pitch compensation of ±15°.
- Sanity check on accuracy: 0.1° at 1 NM gives about 3 m cross-track error (R·δ). That is far too coarse for a flare, but useful for approach sequencing.
- This shows why a cooperative-SSR approach aid needs **range-rate and multilateration**, or a dedicated short-range sensor, close to touchdown.
