# R_alpha_beta_wiki — Wikipedia, "Alpha beta filter"

## Citation
Wikipedia contributors, "Alpha beta filter", English Wikipedia, last edit 00:37, 4 October 2026. URL: https://en.wikipedia.org/wiki/Alpha_beta_filter (raw wikitext read).
Date read: 2026-11-04. Source class: SECONDARY; banner "Confusing" (2009). It cites Brookner, *Tracking and Kalman Filtering Made Easy* (Wiley 1998), and Asquith 1969 (AD 859332) for the stability bounds.
Labels: [D-ag] read this session.

## Facts [D-ag] (section "Filter equations")
- Also called the f-g or g-h filter. It needs no detailed system model. The state is position x and velocity v.
- Predict: (1) x̂_k = x̂_{k−1} + ΔT·v̂_{k−1}; (2) v̂_k = v̂_{k−1}.
- Residual: (3) r_k = x_k − x̂_k.
- Correct: (4) x̂_k += α·r_k; (5) v̂_k += (β/ΔT)·r_k.
- Stability: 0 < α < 1 and 0 < β ≤ 2. Noise is suppressed only if 0 < β < 1.
- Large gains respond fast; small gains suppress noise. Gains are typically tuned by experiment.

## Relevance to us [Y]
This is the legacy, simplest ATC tracker baseline (fixed gains) to compare against Kalman and IMM (R_blom_imm_atc.md). With a radar update ΔT = 4–5 s (terminal) or 12 s (en route), it shows clearly why fixed gains lag in turns, motivating IMM. The equations here are enough to code the baseline.
