# Case 4 — PAR talk-down: ground radar measures, guidance reaches the pilot by voice

**Task wording that triggers it:** "precision approach radar", "talk-down", "GCA", "ground radar guides the aircraft
on final", "voice guidance", "glide path deviation". Spoiler fit: fits *every* word — radar expertise, approach
guidance, voice, translate (radar deviation → phrase → display), "if communication is lost" (doc 24 H7).

**Concept (5 lines)**
1. PAR measures the aircraft every ≤ 1 s (Annex 10 accuracy via ENRI: el 6 m / 0.4 % R + 10 % offset, az 9 m / 0.6 % R).
2. A talk-down generator turns measurements into standard phrases every ~5 s ("slightly above glidepath, on course").
3. Cockpit side: phrase → display classes (GP / CRS), unheard words stay "?" — classes, never invented numbers.
4. Voice lost > ~5 s → panel shows **PAR GUIDANCE LOST**, needle removed; crew applies the lost-comm instruction
   given before final. The same deviation could go up as data (case 9).
5. The independent ground radar exposes a biased on-board source (the aircraft flies 25 m high).

**Three numbers** (`outputs/result.md`)
- 20 heard calls: PAR mean **+8.1 m** vs truth **+10.1 m**, RMS error **7.6 m** (the aircraft drifts high on its bias).
- Voice stops at 100 s → LOST at **101 s**, 6 s after the last heard call (rule > 5 s, [A] FAA JO 7110.65 summaries).
- **0** values shown after LOST (never extrapolated).

**What the jury wants to hear:** PAR accuracy vs range (angle error × range), update rate, why elevation is the hard
axis (multipath), NGSP processing is fitted to precision-approach radars (S_intersoft_ngsp_*), SkyRF / RFX474 for
PAR verification (S_intersoft_rass_catalogue).

**Risks / limits:** the 5 s figures rest on search summaries only (FAA pages refused) — say "about 5 s"; talk-down
class boundaries are [Y]; Annex 10 itself not read.

**Mentor questions:** Is the guidance itself radar-based (PAR)? Voice only, or may we uplink data? Manned aircraft or
UAS? What must happen when the voice stops on short final?

**Run:** `python 03_Advionics/cases/case_4_par_talkdown/run.py [--set voice_lost_at_s=80] [--set lost_after_s=6]`
· report §5b/§5c and F7 in `outputs/`. Reuses `atc.par`, `aerokit.approach`.
