# D_delaune_2021_ingenuity_nav — Ingenuity navigation sensors, architecture and drift

## Citation
Delaune, J. (NASA JPL Aerial Mobility Group) (2021). *Vision-Based Navigation for Mars
Helicopters: Ingenuity & Mars Science Helicopter.* Seminar slides, ETH–UZH, 2 Dec 2021 (73 pp.).
https://rpg.ifi.uzh.ch/docs/teaching/2021/NASA-JPL-seminar.pdf
(Underlying paper: Bayard, D. S. et al. 2019, "Vision-based navigation for the NASA Mars
helicopter", AIAA SciTech 2019 — not read.)

## What I read
Text extraction; slides 27–36 (sensors, architecture, flight performance) and 44–52 (MSH).

## Numbers [D-ag]
- Sensors: nadir nav camera (OmniVision OV7251, 640×480, FOV 133°×100°, 3.6 mrad/pixel,
  > 30 Hz); lidar altimeter (LRF) 50 Hz; IMU accel 1600 Hz / gyro 3200 Hz, downsampled to 500 Hz;
  inclinometer for pre-flight roll/pitch calibration only (slides 27–28).
- Estimator: MAVeN, simple **21-state EKF**; vision on 1 core of a 2.1 GHz Qualcomm Snapdragon;
  flight control on lock-step redundant R5 cores; FPGA rad-hard; all fault responses "land now"
  (slide 28).
- Feature tracking: FAST corners, 28 highest-contrast features in each of 9 tiles; ground
  assumed planar ("LRF + globally-flat terrain") (slides 30–44).
- **Performance: tech-demo flights ~1–2 % position drift; scouting flights ~2–6 %, worst 6 %
  (Flight 9 over sloped terrain); drift mainly cross-track** (slides 35–36, from HiRISE
  reconstructions).
- Map-based localisation (SIFT etc.) was research for the Mars Science Helicopter, not used on
  Ingenuity's flights (slide 51).

## Relevance to Venus 50–60 km (mine)
Ingenuity's navigation is terrain-relative visual-inertial odometry; at 50–60 km on Venus the
surface is not visible at visible wavelengths and the cloud deck has no stable features, so this
architecture does not transfer. What transfers: IMU + EKF, lidar-like ranging only near objects,
"land/hold now" fault logic. Absolute position must come from radio (Doppler/ranging to the
orbiter or Earth, VLBI as on VEGA — see D_vega_balloon_tda1986.md, D_veva_cutts_1999.md) and
altitude from pressure (VEGA practice). VAPS 2018 says Sun direction better than 10° may be
impractical inside the clouds and Venus has no global magnetic field (D_vaps_2018.md).

## Caveats
Slides, not a paper; drift figures are percent of distance flown (flights of roughly
100–450 m in the rows I read).
