# C_grip2018 — Guidance and Control for a Mars Helicopter (AIAA 2018-1849)

## Citation
Grip, H. F.; Scharf, D. P.; Malpica, C.; Johnson, W.; Mandić, M.; Singh, G.; Young, L. (2018). *Guidance and Control for a Mars Helicopter.* AIAA Guidance, Navigation, and Control Conference, AIAA SciTech Forum 2018. AIAA 2018-1849. DOI: 10.2514/6.2018-1849.
PDF: https://rotorcraft.arc.nasa.gov/Publications/files/Grip_AIAA2018_1849.pdf

Related paper not obtained: Grip et al. 2019, *Flight Control System for NASA's Mars Helicopter*, AIAA SciTech 2019 (AIAA 2019-1289). The JPL copy https://dartslab.jpl.nasa.gov/References/pdf/2019-mars-heli.pdf returned an HTML page to curl, so I did not read it. **Nothing in this file is taken from the 2019 paper.**

## What was read
Full text, 22 pages (pypdf), with focus on sections II (vehicle), III (requirements), V-D (gusts) and IX (control design).

Tag: [D-ag] read in this paper. [derived] my arithmetic.

## Numbers [D-ag]
| Item | Value | Location |
|---|---|---|
| Gross mass | < 1.8 kg, "a substantial portion" is batteries | Sec. II, p. 3 |
| Rotor speed | constant, up to 2800 RPM, chosen by atmospheric density on the day. RPM is **not** used for control | Sec. II-A, p. 3 |
| Collective range | 22° per rotor | p. 3-4 |
| Cyclic range | ±10° on both rotors | p. 4 |
| Control mapping | heave = symmetric collective; yaw = differential collective; roll/pitch = cyclic; translation via attitude | p. 4 |
| Navigation | MEMS IMU (propagation) + low-res downward camera + laser rangefinder (height and velocity), fused to limit drift | Sec. II-B, p. 4 |
| Density envelope | 0.014-0.02 kg/m³ | Sec. III, p. 5 |
| Thrust margin | **at least 40 % above hover thrust before stall**, across that density range | Sec. III, p. 5 |
| Wind limits | horizontal 9 m/s, vertical 2 m/s, gust component max 3.5 m/s | Sec. III, p. 5 |
| Airspeed limits | 10 m/s horizontal, 3 m/s vertical | Sec. III, p. 5 |
| Chamber gust design case | 5 m/s step in airspeed; requirement of max 2 m displacement for a 5 m/s gust | Sec. III p. 5; Sec. IX |
| Rotor inflow (hover) | approx. **10 m/s** | Sec. V-D |
| Flap frequency | rotating flap frequency ~80-90 Hz (deliberately stiff) | Sec. V-C |
| Stiff-rotor drawback | higher gust sensitivity; open-loop unstable hover modes (four unstable modes in the linear model) | Sec. V-D, VII-A |
| GNC loop rate | 500 Hz, triggered by IMU | Sec. IX |
| Delays assumed | 1 ms (half sample) + 4 ms latency bound + 2.9 ms gyro FIR + 5.8 ms accelerometer FIR | Sec. IX |
| Servo model | 2nd order, 12 Hz bandwidth, 85 % damping | Sec. IX |
| Heave loop | crossover 1.2 Hz, margins 15.5 dB / 60° | Sec. IX |
| Yaw loop | crossover 1.9 Hz, margins 10.2 dB / 58° (Bode step) | Sec. IX |
| Pitch inner loop | crossover 2.6 Hz, 9.3 dB / 60° | Sec. IX |
| Translational outer loop | crossover 0.3 Hz, 15.6 dB / 56° | Sec. IX |
| Margin boxes on Nichols charts | inner 6 dB / 30°, outer 10 dB / 60° | Fig. 16 caption |
| Reduced-order model | matches the high-order model up to ~10 Hz; 9 states [u v w φ θ ψ p q r] | Sec. VII |
| Flight phases | spin-up, takeoff prep, open-loop takeoff "a few centimeters", climb, hover/translate, descent, landing with no closed-loop at a few cm, spin-down | Sec. IV |

## Caveats
- These are 2016-2017 demonstration-vehicle numbers. The flight vehicle evolved (see C_ingenuity_jpl).
- Venus relevance: at ρ ≈ 0.5-1.6 kg/m³ (about 30-90× Mars density) blade flap damping (Lock number) is Earth-like, so the "stiff blade to move weakly damped flap modes" driver specific to Mars goes away. This is my inference, not from the paper.
