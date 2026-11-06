# D_vega_balloon_tda1986 — VEGA balloon direct-to-Earth link and VLBI tracking

## Citation
Stelzried, C. T., Preston, R. A., Hildebrand, C. E., Wilcher, J. H., & Ellis, J. (1986).
*The Venus Balloon Project.* JPL TDA Progress Report 42-85 (Jan–Mar 1986), pp. 191–198.
NTRS 19860018820. https://ntrs.nasa.gov/api/citations/19860018820/downloads/19860018820.pdf
Also skimmed: Jurgens, R. F. & Divsalar, D. (1985). *A Proposed Technique for the Venus Balloon
Telemetry and Doppler Frequency Recovery.* JPL Publication 85-68, NTRS 19860005863.

## What I read
TDA report full text (8 pp.). JPL 85-68 grepped only (microfiche scan, partly illegible).

## Numbers [D-ag, TDA 42-85]
- Two balloons released 11 and 15 June 1985; float **~54 km**; travelled about one-third of
  the way around Venus in **46-hour** lifetimes.
- **Carrier 1667.914 MHz (L-band)**; primary telemetry **4 bit/s** (Science abstract via search
  also mentions 1 or 4 bit/s on a subcarrier [A]).
- **Radiated power ≈ 4.5 W**, left-circular polarisation; balloon omni antenna gain **−3 to 0 dB**
  (max near sub-Earth point, min near limb); VEGA bus antenna peak gain 10 dB; bus and balloon
  transmitters identical.
- DSN 64-m reception: cooled FET LNAs, 18 MHz RF bandwidth, zenith noise temp ~30 K; received
  balloon carrier power **−165 to −162 dBm**.
- ~95 % of telemetry decoded.
- VLBI: 20 radio observatories (15 CNES network incl. DSN 64-m + 5 Soviet); differential VLBI
  balloon vs bus; ≥ 3 simultaneous stations needed; coverage ~22 h/day.
- **Accuracy goals 15 km position, 1 m/s velocity**; VEGA 1 met them throughout; VEGA 2 position
  error exceeded goal after ~30 h, max < 24 km.
- Altitude from in-situ pressure measurement.

## Other VEGA facts (secondary) [A]
- Envelope 3.4 m diameter, Teflon-coated fabric (search snippet, newspaceeconomy.ca; Science
  1986 abstract not opened). VEVA paper (D_veva_cutts_1999.md) calls it "heavy Teflon cloth"
  and gives VEGA balloon system 121 kg, floating mass 21 kg [D-ag in that paper].

## Caveats
Direct-to-Earth at 4 bit/s required the world's largest antennas — not a model for a
rotorcraft data link; relevant as a navigation-by-radio precedent.
