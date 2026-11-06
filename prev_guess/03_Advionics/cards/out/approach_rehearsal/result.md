# Advionics rehearsal: GNSS-independent ground-radar approach guidance

Rehearsal card. Runway position is synthetic; sensor sigmas, transponder power and antenna gains are ASSUMPTIONS to be replaced by the challenge's own numbers.

## Gate accuracy and integrity at 200 ft (200 runs per source)

Protection level = K·σ + |bias| with K = 5.33 (integrity risk 1e-07); LPV-200 limits HAL 40 m, VAL 35 m.

| Navigation source | Vertical mean (m) | Vertical P95 (m) | Lateral P95 (m) | VPL (m) | HPL (m) | Inside limits |
|---|---:|---:|---:|---:|---:|---|
| Ground radar 0.1 deg | 0.7 | 1.9 | 1.8 | 11.2 | 11.2 | yes |
| SBAS LPV-like | 0.9 | 2.8 | 1.7 | 8.0 | 5.3 | yes |
| Ground radar 0.3 deg | 0.9 | 4.1 | 5.9 | 33.5 | 33.5 | yes |
| Baro-VNAV at ISA-30 K | -5.2 | 7.6 | 5.1 | 17.1 | 16.0 | yes |
| Vision/INS 2 % of range | 1.7 | 24.0 | 28.4 | 127.8 | 127.8 | no |

## Spoofing ramp against a dissimilar monitor

Ramp [0.0, 0.0, -1.0] m/s from t = 20 s. Thresholds (along, cross, vertical) 14.0, 10.3, 11.4 m. Alarm after 14.4 s at 671 ft; largest undetected error 13.5 m (bound 19.3 m).
With the monitor the aircraft is -1.0 m from the path at the gate.
Without it the aircraft ends +68 m from the path and never descends below 222 ft before the glide-path intercept.

## Transponder-reply link and monopulse angle noise

ASSUMED values: transponder reply power, antenna gains, receiver bandwidth and noise figure

| Range (NM) | Received (dBm) | SNR (dB) | Angle σ (°) | Position σ (m) |
|---:|---:|---:|---:|---:|
| 10.0 | -48 | 53 | 0.0018 | 0.58 |
| 5.0 | -42 | 59 | 0.00090 | 0.15 |
| 2.0 | -34 | 67 | 0.00036 | 0.023 |
| 0.6 | -23 | 78 | 0.00011 | 0.0021 |

Thermal noise is not the limit: a cooperative reply gives at least 53 dB SNR here, so the angle accuracy of a real installation is set by calibration bias, multipath near the ground and the reply's pulse timing. Treat the angle σ in the Monte Carlo as that bias/multipath budget.

## Autoland on fused navigation (EKF: GNSS + ground radar + baro + radio altimeter, IMU-driven)

| Scenario | Landed | In touchdown box | Touchdown (m past thr.) | Sink at touchdown (m/s) | GNSS excluded | Honest sensor excluded |
|---|---:|---:|---|---:|---:|---:|
| Fault-free, all sensors | 100 % | 100 % | 354 ± 5 | 1.1 | 0 % | 0 % |
| GNSS spoof, solution-separation FDE | 100 % | 100 % | 354 ± 6 | 1.1 | 100 % | 0 % |
| GNSS spoof, innovation FDE | 10 % | 10 % | 357 ± 1 | 1.1 | 10 % | 90 % |
| No GNSS, cold baro | 100 % | 100 % | 356 ± 6 | 1.1 | 0 % | 0 % |

Innovation gating can exclude the honest sensors when a precise source drifts slowly (it drags the estimate with it); the solution-separation bank tests whole solutions with one sensor left out and excludes the faulty one.

Model results with the card's stated sensor parameters, not equipment data. Multipath near the ground, datalink latency and wrong-aircraft association are not modelled.
