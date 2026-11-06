# Case 3 — Radar / RF signal → plots → tracks → ASTERIX → display

**Task wording that triggers it:** "primary / secondary radar", "Mode S", "transponder", "ADS-B", "plots and tracks",
"air situation display", "ASTERIX", "clutter", "translate the radar signal". Spoiler fit: "Advionics → Radar
Expertise", "translate signal"; the sponsor sells radar test, monitoring and ASTERIX conversion (S_00_summary).

**Concept (5 lines)**
1. SSR: interrogation mode from P1–P3 spacing (8 µs A / 21 µs C), reply bracket F1–F2 20.3 µs, FRUIT, garble flags;
   a code is validated only when ≥ 2 replies agree.
2. Mode S / ADS-B: CRC-24, single-bit repair by syndrome, CPR position, velocity, identification (20/20 book vectors).
3. PSR: I/Q chain MTI / MTD / CA-CFAR / clutter map → plots; Swerling-1 Pd budget.
4. IMM tracker (ARTAS-like design) → tracks → ASTERIX CAT048 (radar) / CAT021 (ADS-B) → scope labels, 7600 alert.
5. Rule as in voice: a rejected message never reaches the display; the track coasts, nothing is invented.

**Three numbers** (`outputs/result.md`)
- **0 of 18 000** Mode S messages reached the display with wrong content over BER 1e-4…3e-2 (95 % upper bound 0.02 %).
- At BER 1e-3: **99.1 %** reach the display (9.3 % repaired, 0.9 % rejected).
- PSR Pd 0.9 (Swerling 1, illustrative S-band budget [Y]) at **24.8 NM (2 m²) / 37.1 NM (10 m²)**; full chain
  KPIs: PSR Pd 0.934/scan, SSR Pd 1.000, false PSR plots 3.0/scan (EUROCONTROL 1997: > 0.90, < 20).

**What the jury wants to hear:** Pd, Pfa, false/split/reflected plots, code correctness, bias + random error,
update rate, latency — RASS/SMS vocabulary; verification by RES/RTG injection and radar-vs-ADS-B comparison;
ASTERIX as the interface (CAT048/021/062, Cat253 control).

**Risks / limits:** radar parameters and scene are [Y]; bit errors independent (real FRUIT/garble are bursty);
3+ bit errors only characterised statistically; ASTERIX CAT021 from a rendering, not the EUROCONTROL PDF.

**Mentor questions:** Ground display (controller) or cockpit (TIS-B/ADS-B In)? PSR, SSR, Mode S, ADS-B, or all? Which
KPI matters to you most? Do you expect an ASTERIX output or just a picture?

**Run:** `python 03_Advionics/cases/case_3_radar_signal_to_display/run.py [--quick] [--set bers=[0.001,0.01]]`
· demo: `outputs/scope_demo.html` · deeper study: `scripts/atc_day.py --psr`. Reuses `atc.translate`, `modes`,
`modeac`, `asterix`, `radar`, `traffic`.
