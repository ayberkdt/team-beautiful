# E_15 — Chen 1989: survey of nonuniform inflow models (Pitt–Peters dynamic inflow)

- **Citation:** Chen, R. T. N. (1989), "A Survey of Nonuniform Inflow Models for Rotorcraft Flight Dynamics and Control
  Applications", NASA TM-102219 / 15th European Rotorcraft Forum, Amsterdam, paper 64 (Vertica 14(2), 1990).
- **URL:** NLR ERF repository `https://dspace-erf.nlr.nl/bitstreams/a3c6a048-31d2-4895-a7c2-5a0a31909de2/download`,
  accessed 2026-11-05; local `D:\tmp_ideathon\venus_research\pdf\chen1989.pdf`. Read level: dynamic-inflow section and
  summary (pdftotext; equation layout partly garbled) **[D]**.

## Values [D]
- Three-state Pitt–Peters model: M dλ/dt + L⁻¹ λ = forcing; apparent-mass matrix **M = diag(8/(3π), 16/(45π), 16/(45π))**;
  M11 = 128/(75π) suggested for twisted blades, but recent studies found 8/(3π) correlates better with flight data.
- Time-constant matrix in hover: **[τ]_hover = (1/v0) · diag(4/(3π), 16/(45π), 16/(45π))** (nondimensional; v0 = mean
  inflow ratio). Rigid-wake assumption doubles the moment-related time constants — an unresolved "factor of two".
- Summary: "the Pitt/Peters first-harmonic inflow model works well overall" against test data at advance ratios
  0.15–0.30 out of ground effect.

## VESPER numbers [K]
Dimensional hover time constant τ0 = (4/(3π)) · R / v_h = 0.424 × 1.3 m / 2.59 m/s ≈ **0.21 s** (55 km). This is short
compared with the ~0.3 s rpm response (sim_params) and the 0.1 s collective actuator, so a 3-state Pitt–Peters model
is cheap and adequate; a static (quasi-steady) inflow would hide only ~0.2 s of lag.
