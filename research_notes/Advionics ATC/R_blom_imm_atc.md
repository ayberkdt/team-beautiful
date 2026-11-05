# R_blom_imm_atc — Blom, Yang, Bar-Shalom, "IMM Estimator in Multisensor Multitarget Tracking for Air Traffic Control and Autonomous Driving"

## Citation
H. A. P. Blom, K. Yang, Y. Bar-Shalom, "IMM Estimator in Multisensor Multitarget Tracking for Air Traffic Control and Autonomous Driving". A 2-page short paper hosted by TU Delft (file name suggests IEEE Aerospace and Electronic Systems Magazine, "IEEE_AESM_IMM"). The extracted text shows no publication year or volume; it cites items up to 2020.
URL: https://filelist.tudelft.nl/LR/Organisatie/Afdelingen/Department_of_Control_and_Operations/ATO/News/IEEE_AESM_IMM%20%283%29.pdf
Date read: 2026-11-04. Read in full (2 pages, PyMuPDF text).
Source class: PRIMARY-ish (written by the IMM inventors, including ARTAS history). The foundational paper itself was **not read**: Blom & Bar-Shalom, "The Interacting Multiple Model Algorithm for Systems with Markovian Switching Coefficients", IEEE Trans. Automatic Control, vol. 33, pp. 780–783, 1988 (as cited in ref [2] of this paper; DOI 10.1109/9.1299 per search snippet [A]).
Labels: [D-ag] read this session; [A] snippet only.

## Facts [D-ag]
- §I: the model is a Markov jump linear Gaussian system, x_t = A(θ_t)x_{t−1} + B(θ_t)w_t, y_t = F(θ_t)x_t + G(θ_t)v_t, where θ_t is a hidden Markov chain with switching probabilities Π_ij. The optimal estimator needs a number of Kalman filters that grows exponentially. **IMM uses N Kalman filters (one per mode)**, with interaction/mixing at the start of each cycle and mode probabilities plus a combined mean and covariance at the end. Ref [1] proves the mixing equations are exact.
- Kalman filters for kinematic models are low-pass. Small noise gain B means low bandwidth (near-constant velocity); large B means high bandwidth (manoeuvre).
- §II (ATC): IMM track maintenance showed "remarkably good performance" on simulated and live primary-radar data (ref [6], Blom 1984, Int. Conf. on Radar, Paris). The modes were **uniform motion, speed change, right turn, left turn**. Outliers, false measurements and missing identities were handled by **PDA**.
- NLR's results "motivated EUROCONTROL to start the development" of **ARTAS (Air traffic management suRveillance Tracker and Server)**. The first version fused multiple PSRs and SSRs, with an architecture "largely based on the IMM inspired design" of ref [7] (Blom, Hogendoorn, van Doorn, in Bar-Shalom (ed.), *Multitarget-Multisensor Tracking*, vol. II, Artech House 1992, pp. 31–63).
- ARTAS entered operational use around the mid-1990s ("Halfway the ninetees"). Later PDA was replaced by **Joint PDA that avoids track coalescence** (ref [8], Blom & Bloem, IEEE TAC 45, 2000, pp. 247–259). Fusion was extended to Mode S, ADS, WAM and SMR, all "within the IMM centered design".
- ARTAS is operational in 43 EUROCONTROL member states and elsewhere, including the USA. Current work includes drone tracking.
- Standard textbook (ref [3]): Bar-Shalom, Li, Kirubarajan, *Estimation with Applications to Tracking and Navigation*, Wiley 2001.

## Relevance to us [Y]
This closes the gap left by the ARTAS product page (R_eurocontrol_artas_asterix.md): the inventors state that the first ARTAS architecture was "largely based on the IMM inspired design" of NLR's work, with PDA later replaced by JPDA. The four modes (uniform motion, speed change, right/left turn) belong to that earlier NLR IMM research, not to a published ARTAS specification (corrected after audit 2026-11-04). For our approach tracker, a 2–4 mode IMM (CV plus turn / speed-change) with JPDA is the defensible "industry-standard" baseline; a plain alpha-beta filter is the legacy comparison. Cite both papers on the slide.
