# Case figures: datawiz set contract and briefs (written before the code, 5 Nov 2026)

All case figures are slide figures (one per case), produced by `cases/<case>/run.py` through
`_common.figure_set(case)`. **Change made during the work:** the first plan was one shared set `cases/cases.seti.json`;
the eighth entity (case 7) hit datawiz's limit ("okabe-ito paletinde boş renk kalmadı (13 varlık)"), so each case now
has its own set `cases/<case>/figures.seti.json` (target `sunum-tam`) — the cases are independent slides and move
with their folder. The shared conventions below are kept by hand (same axis names and units where a quantity
repeats: SNR in C1/C7, time in C2/C4/C6). Audit files sit next to each PNG (`<name>.denetim.txt`).

```
SET SÖZLEŞMESİ — per case, conventions shared
Dergi / hedef      : sunum-tam (all figures)
Varlıklar          : Conservative parser · Naive parser · Detected · False alarm · Truth (grey context)
                     · Shown to pilot · No valid source (shaded band) — fixed colour + line style per entity
Nicelikler         : snr = "Signal-to-noise ratio of the voice channel (dB)" x (cases 1, 7)
                     t = "Time (s)" x (cases 2, 4) · ber = "Bit error rate" x (case 3, log)
Kategori sırası    : comm states always NORMAL, DEGRADED, RX_LOST, TX_LOST, ALTERNATE_AVAILABLE, ALL_COMMS_LOST
Birim yazımı       : "Quantity (unit)"
Ondalık işareti    : "."
Panel harfi        : none (one panel per figure)
```

| Case | FİGÜR BRİFİ (Mesaj · Okur · Hedef · Veri · Karşılaştırma · Biçim · Tema) |
|---|---|
| C1 `C1_voice_wrong_vs_snr` | Mesaj: the conservative parser shows about ten times fewer wrong values than the naive one at every SNR, and pays with SAY AGAIN. Okur: karma (RF/radar jury). Hedef: sunum:sunum-tam. Veri: SNR (dB, nicel) × wrong per 1000 instructions (nicel) × parser (nominal, 2), n = instructions per SNR from params. Karşılaştırma: conservative vs naive at the same SNR. Biçim: line + 95 % Wilson band, direct line-end labels (alt: grouped bars — rejected, SNR is ordered). Tema: set default. |
| C2 `C2_comm_state_timeline` | Mesaj: each comm state appears only with its evidence, and in loss states the display holds only STALE items — nothing new. Okur: karma. Veri: time (s) × state (ordinal, 6) step line. Karşılaştırma: state vs time. Biçim: step line on a categorical y axis (alt: Gantt bars — more ink for the same message). |
| C3 `C3_message_outcome_vs_ber` | Mesaj: as the bit error rate rises, Mode S messages are repaired or rejected, never displayed wrong. Veri: BER (log, nicel) × share of messages (%) × outcome (nominal: intact, repaired, rejected, wrong shown). Biçim: lines with markers, log x, direct labels (alt: stacked area — hides the zero "wrong" line). |
| C4 `C4_par_voice_loss` | Mesaj: the ground radar sees the aircraft well above the glide path; when the voice stops the cockpit shows LOST after ~5 s and never extrapolates. Veri: time (s) × vertical deviation (m): truth line (grey), PAR-measured points, shaded band where the panel shows LOST. Biçim: line + points + band. |
| C5 `C5_gate_deviation_by_source` | Mesaj: without GNSS, the ground radar keeps the 95 % vertical deviation at the gate within the alert limit; the spoofed GNSS does not. Veri: navigation source (nominal, 3–4) × 95th-percentile vertical deviation at the gate (m), n runs from params. Biçim: horizontal dot plot with a reference line at the alert limit (alt: bars — start at 0 anyway; dots used for less ink). |
| C6 `C6_ils_inspection_ddm` | Mesaj: along the drone's mini-approach the inspection receiver tracks the true DDM, and during the injected faults it shows FLAG instead of a centred needle. Veri: time (s) × DDM (nicel): truth line, measured line, shaded FLAG bands. Biçim: line + bands. |
| C7 `C7_readback_alerts_vs_snr` | Mesaj: a readback checker catches most real errors at good SNR, but at low SNR false alarms dominate because real errors are rare. Veri: SNR (dB) × alert rate (%) × kind (detected real error, false alarm). Biçim: two lines with direct labels. |
| C8 `C8_spoof_detection_vs_offset` | Mesaj: the MLAT consistency check flags a spoofed ADS-B position beyond ~X m and almost never flags an honest one. Veri: spoof offset (m) × detection probability (%), false-alarm point at 0 m. Biçim: line with markers + reference line. |
| C9 `C9_uplink_timeout_tradeoff` | Mesaj: a shorter loss timeout alerts faster but raises nuisance "guidance lost" alarms; the timeout must be chosen against the message-loss rate. Veri: message loss probability (log) × probability of at least one nuisance alarm per approach (%) × timeout (nominal, 3). Biçim: lines, log x, direct labels. |

Delivery reports (Kapı 6) are in `cases/UX_AUDIT.md` § Figures after the runs.
