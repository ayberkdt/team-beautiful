# R0 · NASA Fault Tree Handbook with Aerospace Applications (v1.1, Aug 2002)

- **Source:** Stamatelatos M., Vesely W. (lead), Dugan J., Fragola J., Minarick J., Railsback J. *Fault Tree Handbook with Aerospace
  Applications*, Version 1.1, NASA Office of Safety and Mission Assurance, August 2002.
  https://extapps.ksc.nasa.gov/reliability/Documents/Fault_Tree_Handbook_with_Aerospace_Applications_August_2002.pdf
  (downloaded to `D:\tmp_ideathon\easa\dl\std\nasa_fth.pdf`, 1 343 797 bytes).
- **Read by:** main EASA session, 4 Nov 2026 16:05–16:10 (UTC+3); only the sections below (not the whole 218 pages).
- Page numbers below: "doc p." = page number printed in the handbook; "PDF p." = PDF page.

| What the code uses | Where | Tag |
|---|---|---|
| Top event ≈ sum of minimal-cut-set probabilities ("rare event approximation"), accurate for basic-event probabilities < 0.1; a cut set probability = product of its basic-event probabilities | §7.1, doc p. 83 (PDF p. 96) | [D] |
| Inclusion–exclusion for union of events (Eq. B.5–B.7); rare-event approx. Eq. B.8 within ~10 %, conservative, when P(Ei) < 0.1 | App. B, PDF p. 185 | [D] |
| Unavailability of a **standby (periodically tested) component**: q = ½λsT / (1 + ½λsT) ≈ ½λsT (Eq. 7.6), T = test interval | §7.1, doc p. 86 (PDF p. 99) | [D] |
| Operating component unavailability q = λτ/(1+λτ) ≈ λτ (Eq. 7.5), τ = mean repair time | same | [D] |
| Importance measures: Fussell-Vesely (contribution of cut sets containing the event), Risk Reduction Worth (top with event prob. = 0), Risk Achievement Worth (top with event prob. = 1), Birnbaum BM = P(top | 1) − P(top | 0) = RAW + RRW on the interval scale | §7, doc p. 90–91 (PDF p. 103–104) | [D] |

Use in `aerokit.canopy.fta`: exact independent-event gate algebra (AND = ∏p, OR = 1 − ∏(1 − p)), the rare-event sum for cut
sets, ½λT latent-failure unavailability for a sensor checked at each pre-flight self-test / maintenance functional test, and the four
importance measures.

NOT read: MIL-STD-1629A (two download attempts from everyspec.com returned an HTML error page; ReliaWiki returned HTTP 403) — the FMEA in
this work therefore does **not** claim MIL-STD-1629A criticality numbers.
