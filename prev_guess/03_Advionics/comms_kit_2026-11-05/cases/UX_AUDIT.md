# UX gate (ux-yasalari) for the case kit — CLI surfaces only (no HTML is produced by the case kit)

## Kapı 1 · GÖREV BÜTÇESİ (written before the code, 5 Nov 2026)

```
GÖREV BÜTÇESİ — triage.py console output            (yüzey: cli)
Birincil görev(ler)       : 1) see which case matches the real task  2) see what would move               Pareto · Occam
Birincil eylem            : read the ranking; next step printed as ONE command (--apply)                  Von Restorff
Eylem / görünüm           : ≤ 5 · planlanan: 3 flags (--apply, --undo, --keep/--drop as one group)       Hick
Üst düzey gezinti         : ≤ 7 · planlanan: 0                                                             Hick · Miller
Seçenek kümesi            : default = dry run (nothing moves without --apply)                              Seçim Yükü
Form alanı / adım         : 1 positional (task text OR a file path; both accepted)                         Miller · Parkinson
Geri bildirim             : < 400 ms (keyword scoring); --apply prints one line per moved item              Doherty
Stil bütçesi              : no colour; 1 table (≤ 5 columns); last line = result sentence + next command    Benzerlik · Prägnanz
Sisteme yüklenen karmaşıklık : file-vs-text detection, Turkish/English accents folded, keep threshold
                            from JSON, destination folder name from today's date, manifest path printed
```

```
GÖREV BÜTÇESİ — cases/<case>/run.py console output (9 runners, same layout)   (yüzey: cli)
Birincil görev(ler)       : 1) see the 3 key numbers  2) know where result.md / figure went
Birincil eylem            : open outputs/result.md (path printed last)
Eylem / görünüm           : flags --set, --params, --out, --quick, --no-fig (5)                            Hick
Seçenek kümesi            : every number has a default in params.json                                      Seçim Yükü
Geri bildirim             : > 400 ms runs print a start line ("running <case> ...")                        Doherty
Stil bütçesi              : ≤ 8 lines; one aligned "KEY" column; no colour                                 Benzerlik
Sisteme yüklenen karmaşıklık : value types parsed from the JSON default (int/float/bool/list), unknown keys rejected
```

## Kapı 3 · YASA DENETİMİ — triage.py + the nine run.py consoles · 5 Nov 2026 · denetleyici: koşmadı (yüzey: cli, HTML yok)

Sonuç: 20/20 yasa ölçüldü (4 kapsam dışı: işaretçi/kutu/form yok) · 0 HATA · 1 UYARI (gerekçeli) · karar: TESLİM

Measured on: `triage.py task_A_voice.txt` (11 lines, widest 110 columns, 202 ms), `case_2 run.py --quick --no-fig`
(5 lines, 108 columns), `case_5 ... ` (5 lines; was 166 columns → values cut at 77 characters in the console, full
text in result.md → now ≤ 120).

| #  | Yasa             | Ölçüm (sayı/gözlem) | Eşik | Durum | Gerekçe (yalnız UYARI) |
|----|------------------|---------------------|------|-------|------------------------|
| 1  | Hick             | triage: 4 visible flags (--apply, --undo, --keep, --drop; 3 test-only flags hidden); run.py: 5 flags | ≤ 5 | geçti | |
| 2  | Fitts            | kapsam dışı: CLI, no pointer targets | — | kapsam dışı | |
| 3  | Jakob            | argparse conventions: positional + `--flag`, `--help`, `NAME=VALUE` like `-D`/`--set` in common tools | 0 sapma | geçti | |
| 4  | Seçim Yükü       | default = dry run; every parameter has a JSON default; keep threshold from JSON | varsayılan işaretli | geçti | |
| 5  | Yakınlık         | triage: header + 9 rows contiguous, result line directly after; run.py: 3 key lines + figure line contiguous | gruplu | geçti | |
| 6  | Benzerlik        | one fixed-width layout per tool (triage columns 2/36/6/4/≤60; run.py label column 40); no colour | 1 stil | geçti | |
| 7  | Tekdüze Bağlılık | 1 table per output | ≤ 1 | geçti | |
| 8  | Ortak Bölge      | kapsam dışı: no boxes / frames in a console | — | kapsam dışı | |
| 9  | Prägnanz         | no ASCII art, no colour codes, no decorations | 0 süs | geçti | |
| 10 | Von Restorff     | the only "action" text is the last line ("next: same command + --apply" / "open <result.md>") | 1 vurgu | geçti | |
| 11 | Miller           | triage table 5 columns, 9 rows (one per case, ranked) | ≤ 7 sütun | UYARI | 9 rows > 7: all cases must stay visible to override the decision; the keep column carries the decision |
| 12 | Sıra Konumu      | first row = top case; last line = result + next command | birincil görev ilk/son | geçti | |
| 13 | Doherty          | triage 202 ms (measured); runners 2–18 s full: first line "running <case> ..." printed before work | < 400 ms ya da gösterge | geçti | |
| 14 | Zeigarnik        | dry run names the next step; `--apply` prints one line per moved item + the undo command | ≥ 3 adımda gösterge | geçti | |
| 15 | Zirve-Son        | last line is a result sentence with counts (35 would move, 19 stay) and the next command | 1 sonuç satırı | geçti | |
| 16 | Parkinson        | 1 required positional (triage); 0 required (run.py) | ≤ %50 zorunlu | geçti | |
| 17 | Tesler           | file-vs-text detected; accents/Turkish folded; destination folder from the date, never reused (`_2`); value types from JSON | her girdiye gerekçe | geçti | |
| 18 | Postel           | accepts text or a .txt/.md path, BOM files, upper/lower case, `--set x=[1,2]` JSON or plain text | normalizasyon | geçti | |
| 19 | Occam            | triage 11 lines; run.py 5–6 lines (budget ≤ 8) | ≤ bütçe | geçti | |
| 20 | Pareto           | the top 3 lines answer task 1 (which case, why: matched words) | ≥ %60 | geçti | |

Riskler: long matched-word lists are cut at 60 characters in the console (full list in `triage_plan.md`); a terminal
narrower than 110 columns wraps the table.

## Figures — datawiz Kapı 5–6 delivery (full runs, 5 Nov 2026)

| Figure | Audit (`.denetim.txt`) | Eye check (PNG opened) |
|---|---|---|
| C1_voice_wrong_vs_snr | 0 HATA · 0 UYARI · 1 BİLGİ | Wilson bands, direct labels, no overlap |
| C2_comm_state_timeline | 0 HATA · 0 UYARI · 2 BİLGİ | six state names readable; categorical y axis (BİLGİ: no unit — intended) |
| C3_message_outcome_vs_ber | 0 HATA · 0 UYARI · 1 BİLGİ | first version: x axis ran to an empty 10⁻¹ decade and "Wrong shown" sat on the axis → xlim + ylim −6 fixed; earlier HATA (ASCII minus in log ticks) fixed with superscript ticks |
| C4_par_voice_loss | 0 HATA · 0 UYARI · 1 BİLGİ | two earlier HATA fixed (annotation over a label; legend pushing the y title off the figure) → direct text labels |
| C5_gate_deviation_by_source | 0 HATA · 0 UYARI · 1 BİLGİ | dot plot with the 35 m alert-limit line; labels clear |
| C6_ils_inspection_ddm | 0 HATA · 0 UYARI · 1 BİLGİ | earlier HATA: yellow 1.26:1 → explicit purple; label crossings → background halo |
| C7_readback_alerts_vs_snr | 0 HATA · 0 UYARI · 2 BİLGİ | label shortened to "False alarms" (wider plot area); BİLGİ asks to name the band: 95 % Wilson, n in result.md |
| C8_spoof_detection_vs_offset | 0 HATA · 0 UYARI · 2 BİLGİ | 95 % Wilson band, n = 600 per offset (result.md) |
| C9_uplink_timeout_tradeoff | 0 HATA · 0 UYARI · 2 BİLGİ | empty 10⁰ decade removed; three labels separated |

Captions for slides: the bands in C1/C7/C8 are 95 % Wilson intervals; n per point is in each `result.md`.
