# R_icao_suricg7_ip14_wam — ICAO APAC SURICG/7 IP/14 (China): WAM test for final approach monitoring

## Citation
ICAO Asia/Pacific, Seventh Meeting of the Surveillance Implementation Coordination Group (SURICG/7), Information Paper IP/14, Agenda Item 8a, *Introduction to the Test of the WAM Technology in the Final Approach Monitoring*, presented by China (ATMB of CAAC). Video teleconference, 24–27 May 2022. 7 pages.
URL: https://www.icao.int/sites/default/files/APAC/Meetings/2022/2022%20SURICG-7/4-Information%20Papers/IP14_CHN-AI.8a-Introduction-to-the-Test-of-the-WAM-Technology-in-the-Final-Approach-Monitoring-v2.pdf
Date read: 2026-11-04 (PDF text extracted with PyMuPDF; pp.1–5 read).
Source class: a State information paper to an ICAO meeting. It reports **measured** values from one test campaign, not a specification. Its Appendix quotes **ED-142** metric definitions (ED-142 itself is paywalled and was not read).
Labels: [D-ag] read this session.

## Facts [D-ag]
- §1–2 (p.1): tests ran 2020–2021 at Chengdu Shuangliu. The WAM was **passive** (no transmitter) and used Mode S downlinks triggered by a nearby Mode S interrogator. It had 5 receivers around the extended runway centrelines plus 9 receivers from the airport MLAT, and a central processor doing TDOA.
- §2.3 (p.2): checked against CAAC spec MH/T 4037. The flight check used an RTK-referenced aircraft.
- **§3.2 (p.2), horizontal accuracy vs RTK: "WAM is about 6-7 meters", "ADS-B is about 20 meters", "Mode S radar is about 200 meters".**
- §3.3 (p.3): probability of position detection = 99.8 %. Probability of false detection < 10⁻³, where false means a deviation > 2100 m (5 NM interval) or > 1690 m (3 NM interval).
- §4 (p.3): place sites with good visibility on both sides of the extended centreline. Site selection balances GDOP, O&M cost and difficulty.
- Appendix 1 (p.4), quoting ED-142 §6.4.5: horizontal position accuracy is "expressed as a Root Mean Square (RMS) of an absolute distance error": dr_i = √(eX_i² + eY_i²), RMS = √(Σdr_i²/N).
- Appendix 2 (p.4), quoting ED-142 §6.4.1: PD = D/E × 100, with E = t_c/UI (expected update intervals) and D = update intervals with at least one report.
- Appendix 3 (p.4–5), quoting ED-142 §6.4.2: PFD = count(dr > de)/N × 100, with de = 1690 m (3 NM) or 2100 m (5 NM).
- Appendix 4 (p.5), quoting ED-142 §6.4.3: probability of code detection per update interval (Mode S address, Mode A, Mode C).

## Relevance to us [Y]
This is a real-world, final-approach-specific comparison: WAM 6–7 m, ADS-B ~20 m, Mode S radar ~200 m. It makes the argument for an approach-guidance concept that fuses WAM/ADS-B rather than relying on SSR alone. The ED-142 metric formulas (RMS, PD, PFD) can be implemented directly in our evaluation script.
