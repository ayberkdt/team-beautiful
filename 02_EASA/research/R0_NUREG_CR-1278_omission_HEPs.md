# R0 · Swain & Guttmann, NUREG/CR-1278 (THERP handbook) — omission error probabilities

- **Source:** Swain, A. D.; Guttmann, H. E. *Handbook of Human Reliability Analysis with Emphasis on Nuclear Power Plant
  Applications*, NUREG/CR-1278 (SAND80-0200), US NRC, August 1983 (OSTI copy downloaded by subagent R6 to
  `D:\tmp_ideathon\easa\dl\hf2\nureg_cr1278.pdf`; see `R6_hf_full_texts.md` for the URL).
- **Read by:** main session, 4 Nov 2026 (round 2), Table 20-7 and the Ch. 6 explanation of Table 15-3 only. Tags [D].

## Table 20-7 (from Table 15-3): errors of omission per item of instruction when written procedures are specified

| Item | Condition | HEP | EF |
|---|---|---|---|
| 1 | Checkoff used correctly, short list (< 10 items) | 0.001 | 3 |
| 2 | Checkoff used correctly, long list (> 10 items) | 0.003 | 3 |
| 3 | No checkoff (or used incorrectly), short list | 0.003 | 3 |
| 4 | No checkoff (or used incorrectly), long list | 0.01 | 3 |
| 5 | Written procedures available and should be used, but are not used | 0.05 | 5 |

- The estimates assume zero dependence between items (table footnote).
- Ch. 6: "the absolute values for each entry in Table 15-3 are based on judgment"; the relative differences "seem
  psychologically sound". Table 16-1: probability 0.01 that plant policies are ignored; a checklist "will be used properly only
  one-half of the time" (the estimate behind the 0.5 used in Table 16-1).

## Use in the study [Y]

- The hazard "handle released but not pulled fully aft" is an omission of one procedure step. Its per-flight rate is taken as
  **1e-3 central** (THERP item 1). The sweep runs **1e-4 … 5e-2** (item 5, procedure not used). Nuclear-plant values transfer
  to cockpit checklists only by analogy; the airline observations in R6 (Dismukes & Berman 2010: 42 omitted or incorrect
  checklist items in 60 flights) [D-ag] are of the same order.
- This is a per-step omission rate. Whether the pilot's **check** then catches the partial lock is a separate parameter
  (`p_pilot_miss`); AAIB p. 20 found no visible difference at the frame, so that check is weak.
