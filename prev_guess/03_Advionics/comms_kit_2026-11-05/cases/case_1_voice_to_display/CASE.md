# Case 1 — ATC voice → text → structured clearance → cockpit display

**Task wording that triggers it:** "translate the controller's voice / radio message", "speech recognition",
"transcribe", "voice to text", "display the clearance in the cockpit", "phraseology". Spoiler fit: "translate signal",
"[voice] sinyal display'e nasıl ulaşır", speaker used *voice, radio, translate* (organiser note).

**Concept (5 lines)**
1. VHF AM audio (300–3400 Hz, 25 kHz; 350–2500 Hz, 8.33 kHz) → audio monitor (SNR, clipping, dropout).
2. Recogniser → words + confidences + n-best (any ASR; demo: Windows SAPI, word-error model for sweeps).
3. Parser → callsign, heading, level, speed, squawk, frequency, QNH, runway; each field CONFIRMED / LOW_CONFIDENCE /
   AMBIGUOUS / NOT_RECEIVED / INVALID — an unsure digit is masked (`2?0`), never guessed.
4. Context checks catch what confidence cannot: runway exists at the destination, octal squawk, valid 8.33 channel,
   climb/descend direction.
5. Advisory panel: only received items, with source and age; pilot confirms by ear / readback. Never to the autopilot.

**Three numbers we can show** (`outputs/result.md`, word-error model, all parameters [Y])
- Wrong values shown per 1000 instructions at SNR ≥ 21 dB: **conservative 5–14 vs naive 30–53** (×4.2 fewer).
- Price: at SNR ≤ 9 dB the conservative parser withholds **99–100 %** (SAY AGAIN) instead of guessing.
- Real recogniser (doc 24 §7, `atc_day.py --asr`): SAPI heard runway 25R as **35R at confidence 0.99** — caught by the
  runway check, 0 wrong values at every SNR.

**What the jury (radar/RF people) wants to hear**
- The chain in their language: signal quality (SNR) → detection (recognition) → validation → display, with error
  rates per stage, like Pd/Pfa. "Wrong-but-confident" is their "false plot".
- Literature anchors (A_00_summary): VHF ATC audio 20–25 % WER at 10–15 dB; zero-shot Whisper ~79 % WER on ATCO2;
  surveillance-boosted callsigns 41.3 → 69.7 % (A_Nigmatulina2021).
- Verification plan: recorded ATC speech per recogniser, threshold calibration curve (F5), shadow mode.

**Risks / limits:** word-error model is ours [Y]; no recorded ATC corpus used (licences unchecked); SAPI is a desktop
recogniser; display text from ASR is itself a translation (inverse text normalisation broke a callsign once);
voice watch must stay (SERA.8035).

**Mentor questions:** Is "translate" speech→text or RF→picture? Display for pilot, controller or both? Which
phraseology/language? Is a real recogniser expected or a concept? Success metric: accuracy, latency, safety argument?

**Run:** `python 03_Advionics/cases/case_1_voice_to_display/run.py [--quick] [--set snr_db=[30,20,10]]`
· live speech: `python 03_Advionics/scripts/atc_live.py "beetle one two three cleared ils approach runway two five right" --snr 15`
· demo page: `03_Advionics/outputs/cockpit_demo.html`. Reuses `aerokit.atc.translate`, `clearance`, `channel`, `commhealth`.
