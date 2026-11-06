# D_veva_cutts_1999 — Venus Aerobot Multisonde (VEVA): UHF sonde link and X-band DTE table

## Citation
Cutts, J. A., Kerzhanovich, V., Balaram, J. (Bob), Campbell, B., Gershman, R., Greeley, R.,
Hall, J. L., Cameron, J., Klaasen, K., & Hansen, D. M. (1999). *Venus Aerobot Multisonde
Mission.* AIAA Balloon Technology Conference 1999. NTRS 20000052454.
https://ntrs.nasa.gov/api/citations/20000052454/downloads/20000052454.pdf

## What I read
Full paper; Tables 1–2 and comm/navigation text read from rendered pages 6–7.

## Numbers [D-ag, Table 2 p.6]
| Link | Max distance | Tx power | Freq | Tx gain | Rx gain | Data rate |
|---|---|---|---|---|---|---|
| DSN → gondola (uplink) | 1.46e6 km (as printed) | 4 kW | 7.17 GHz | 66.9 dBi | 20 dBi | 125 bps |
| Gondola → DSN (downlink) | — | 153 W (as printed) | 8.4 GHz | 24 dBi | 68.1 dBi | 10 kbps |
| **Sonde → gondola (UHF)** | **200 km** | **1 W** | **400 MHz** | **1 dBi** | **1 dBi** | **500 kbps** |

- Text p.2: sonde–aerobot distance "tens of km"; **100 kbps to 2 Mb/s possible with compact
  low-power UHF (400 MHz) transmitters and omni antennas**.
- Two sondes simultaneously at 500 kbps, receivers 10–15 MHz apart, Viterbi coding (p.6).
- Gondola stores ~300 Mbit per imaging sonde, relays to Earth (p.6).
- X-band gondola antenna 20 cm, Earth pointing accuracy ~5°; control authority 10°/s, residual
  gondola rotation 1°/s, wobble 5° at 30–60 s periods; on-board attitude estimator; sun
  sensor considered for re-acquisition (p.7).
- Navigation: deploy at 60 km; mean wind 0 m/s N/S and 75 m/s E/W, uncertainty 2 m/s N/S,
  10 m/s E/W; dispersion at first target ±14 km N/S, ±72 km E/W; **ranging + phase of the
  gondola signal + altitude → ~10 km position accuracy ("demonstrated on VEGA")** (p.7).
- Table 1: VEGA balloon system 121 kg, floating mass 21 kg; VEVA 94 kg / 63 kg (p.6).
- Envelope options: Mylar bilaminate (23 µm × 23 µm) with Teflon sheath (VEGA heritage "heavy
  Teflon cloth") or polyethylene laminate ("recent tests indicate PE resistant to sulfuric
  acid"); PE density 0.95 g/cc vs TFE 2.15 g/cc (p.6).

## Caveats
"153 W" downlink and "1.46e6 km" distance look odd (Earth–Venus is ≥ 4e7 km); OCR is from the
rendered page, so these are as printed but may be typos in the original. The UHF 1 W / 200 km /
500 kbps row is the useful number for a rotorcraft–relay or rotorcraft–lander link sizing.
