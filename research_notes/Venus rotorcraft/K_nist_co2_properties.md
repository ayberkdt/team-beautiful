# NIST Chemistry WebBook — CO₂ and N₂ thermophysical data (read by the Venus session itself, 4 Nov 2026 ~16:30 UTC+3)

Tag: **[D]** — read in this session with WebFetch from the NIST pages below (the fetch tool returns the page as
markdown through a summariser; the tables are self-consistent: ρ at 300 K, 0.05 MPa = 0.88434 vs ideal gas 0.8822 kg/m³,
0.24 % real-gas effect).

## Sources

1. NIST Chemistry WebBook, SRD 69, Carbon dioxide, gas-phase thermochemistry (Shomate equation; Chase 1998, NIST-JANAF).
   <https://webbook.nist.gov/cgi/cbook.cgi?ID=C124389&Mask=1>
2. NIST Chemistry WebBook, Nitrogen, gas-phase thermochemistry. <https://webbook.nist.gov/cgi/cbook.cgi?ID=C7727379&Mask=1>
3. NIST Chemistry WebBook, Thermophysical properties of fluid systems (Lemmon, McLinden, Friend), CO₂ isobars
   0.05 MPa (250–350 K) and 0.1 MPa (225–400 K). URL pattern `https://webbook.nist.gov/cgi/fluid.cgi?P=0.1&TLow=225&THigh=400&TInc=25&...&ID=C124389&Type=IsoBar`.

## Shomate coefficients, Cp° = A + B t + C t² + D t³ + E/t², t = T/1000 [J/(mol K)]

| Species, range | A | B | C | D | E |
|---|---|---|---|---|---|
| CO₂, 298–1200 K | 24.99735 | 55.18696 | −33.69137 | 7.948387 | −0.136638 |
| CO₂, 1200–6000 K | 58.16639 | 2.720074 | −0.492289 | 0.038844 | −6.447293 |
| N₂, 100–500 K | 28.98641 | 1.853978 | −9.647459 | 16.63537 | 0.000117 |

Caveat: the CO₂ fit starts at 298 K; at 60 km (≈263 K) it is extrapolated by 35 K. The NIST fluid tables below cover it.

## CO₂ at 0.1 MPa (1 bar), vapour

| T [K] | ρ [kg/m³] | Cp [J/mol K] | Cv [J/mol K] | a [m/s] | μ [µPa s] | k [W/m K] |
|---|---|---|---|---|---|---|
| 225 | 2.3828 | 34.511 | 25.685 | 235.93 | 11.353 | 0.011302 |
| 250 | 2.1363 | 35.428 | 26.766 | 247.79 | 12.581 | 0.013051 |
| 275 | 1.9374 | 36.462 | 27.897 | 258.89 | 13.799 | 0.014881 |
| 300 | 1.7730 | 37.520 | 29.016 | 269.39 | 15.003 | 0.016774 |
| 325 | 1.6348 | 38.561 | 30.099 | 279.42 | 16.191 | 0.018714 |
| 350 | 1.5167 | 39.566 | 31.134 | 289.04 | 17.359 | 0.020691 |
| 375 | 1.4147 | 40.528 | 32.118 | 298.31 | 18.508 | 0.022695 |
| 400 | 1.3257 | 41.446 | 33.051 | 307.28 | 19.635 | 0.024718 |

## CO₂ at 0.05 MPa (0.5 bar)

| T [K] | ρ | Cp | Cv | a | μ | k |
|---|---|---|---|---|---|---|
| 250 | 1.0634 | 35.130 | 26.644 | 248.44 | 12.581 | 0.013019 |
| 275 | 0.96552 | 36.257 | 27.818 | 259.37 | 13.796 | 0.014852 |
| 300 | 0.88434 | 37.372 | 28.964 | 269.77 | 14.998 | 0.016746 |
| 325 | 0.81585 | 38.449 | 30.062 | 279.71 | 16.185 | 0.018689 |
| 350 | 0.75726 | 39.480 | 31.107 | 289.27 | 17.353 | 0.020667 |

What we use: viscosity and conductivity are pressure-independent to < 0.1 % between 0.5 and 1 bar → `aerokit.venus.gas`
interpolates the 1-bar μ(T), k(T) columns. Speed of sound: pressure effect 0.14 % at 300 K. The 3.5 % N₂ is added by
ideal-gas mixing of Cp (Shomate) — an approximation [Y]; its effect on μ is neglected (< 1 % expected [Y], not verified).
