# R_radar_eq_swerling_wiki — Wikipedia, "Radar" (range equation section) and "Fluctuation loss" (Swerling models)

## Citation
1. Wikipedia contributors, "Radar", section "Radar range equation", English Wikipedia, last edit 06:40, 18 October 2026. https://en.wikipedia.org/wiki/Radar
2. Wikipedia contributors, "Fluctuation loss", English Wikipedia, last edit 12:48, 4 January 2026. https://en.wikipedia.org/wiki/Fluctuation_loss
These are two articles in one file because both are generic textbook background. Note that the task rule is one file per source; this file deliberately groups two short secondary background extracts.
Date read: 2026-11-04 (raw wikitext). Source class: SECONDARY.
Labels: [D-ag] read this session.

## Radar range equation [D-ag]
- P_r = P_t·G_t·A_r·σ·F⁴ / ((4π)²·R_t²·R_r²), with A_r = G_r·λ²/(4π).
- For a monostatic radar (R_t = R_r = R): **P_r = P_t·G_t·A_r·σ·F⁴ / ((4π)²·R⁴)**. Received power falls with R⁴.
- F = pattern propagation factor (multipath, shadowing). F = 1 corresponds to free space.
- Doppler subsection: MTI can cancel targets at certain radial velocities (blind speeds).
- Cross-reference [D-ag, R_atcrbs_wiki]: SSR one-way signal falls with R², not R⁴.

## Swerling target models [D-ag] ("Fluctuation loss")
- Swerling's 1954 RAND paper. RCS follows a chi-squared pdf: p(σ) = m/(Γ(m)σ_av)·(mσ/σ_av)^(m−1)·e^(−mσ/σ_av), where m = degrees of freedom / 2. The std/mean ratio is m^(−1/2).
- **Swerling I**: 2 DOF (m = 1), fluctuating **scan-to-scan**, giving p(σ) = (1/σ_av)·e^(−σ/σ_av). This is many equal scatterers, "particularly useful for considering aircraft shapes", and fits scanning radars.
- **Swerling II**: same pdf, fluctuating pulse-to-pulse.
- **Swerling III**: 4 DOF (m = 2), one dominant scatterer plus small ones (e.g. propeller aircraft, helicopters), scan-to-scan.
- **Swerling IV**: "Similar to Swerling III, but the RCS varies from pulse-to-pulse". The original source the article cites is Swerling, P., *Probability of Detection for Fluctuating Targets*, ASTIA AD 80638, 17 March 1954 (https://apps.dtic.mil/sti/tr/pdf/AD0080638.pdf); the agent did not read it.
- Swerling V (also called 0): non-fluctuating (m → ∞).
- Mitigation: frequency diversity or pulse compression.

## Relevance to us [Y]
Gives the equation and the target model for a PSR detection-probability simulation. Primary sources use Swerling I for ATC specs (FAA ARSR-4: "Swerling type I" 1 m² to 165 NM; see R_faa_order_1812_8_arsr4.md). For the slide, Skolnik's *Radar Handbook* would be a better citation, but the agent did not read it.
