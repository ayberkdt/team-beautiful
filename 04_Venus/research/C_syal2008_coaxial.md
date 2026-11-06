# C_syal2008_coaxial — Coaxial momentum and BEMT interference factors with Harrington validation (Leishman group)

## Citation
Syal, Monica (2008). *Contributions to the Aerodynamic Optimization of a Coaxial Rotor System.* M.S. Thesis, Department of Aerospace Engineering, University of Maryland, College Park (advisor J. G. Leishman). UMD DRUM: https://drum.lib.umd.edu/bitstream/1903/8792/1/umi-umd-5812.pdf

**Why this source:** the requested Leishman & Ananthan (2008) JAHS paper *An Optimum Coaxial Rotor System for Axial Flight* was not freely available (searches found only the 2006 AHS Forum version on Issuu and the VTOL store). This thesis from the same group derives the same coaxial momentum-theory interference factors and validates BEMT against Harrington. **Nothing here is read from the JAHS paper itself.**

## What was read
pypdf text of Chapter 2 (Sec. 2.1, Table 2.1 and Eqs. 2.13-2.16) and Chapter 4 (Sec. 4.1, Eqs. 4.1-4.6, Fig. 4.1 labels). This PDF's text layer uses a shifted font: digits and some capitals are encoded +32 code points (Q = 1, R = 2, S = 3, T = 4, U = 5, V = 6, W = 7, X = 8, Y = 9, P = 0, N = "."). I decoded the numbers by hand. For example, the coplanar case reads "QNTQTR" = 1.4142 = √2, which checks the decoding. Figures were not viewed.

Tag: [D-ag] read in this thesis (decoded). [derived] mine.

## Interference-induced power factor κ_int = (P_i)coax / (2·(P_i)isolated) — Table 2.1 [D-ag, decoded]
| Case | Condition | κ_int |
|---|---|---|
| 1 | rotors coplanar, equal thrust | 1.4142 (= √2) |
| 2 | coplanar, balanced torque | 1.4142 |
| 3 | lower rotor in fully developed (contracted) slipstream of upper, equal thrust | **1.2808** |
| 4a | as 3, torque balance, compared with isolated rotors each at T/2 | **1.2810** |
| 4b | as 3, torque balance, isolated rotors at T_u and T_l respectively | **1.2657** (minimum) |
- Case 4a text: at torque balance P_u = P_l, and T_u/T_l decodes to 1.4375. That value is flagged for re-check because the digits are hard to decode cleanly.
- Text: as spacing increases the interference losses fall; the minimum κ_int (~1.266) occurs with the lower rotor in the fully developed slipstream.
- **"1.16" (from the task brief) does not appear in Coleman 1997 or in the parts of this thesis I read.** Do not cite 1.16 without finding its source.

## Harrington validation (Ch. 4) [D-ag, decoded]
- Fig. 4.1 schematic: Harrington Rotor 1 blade 3.81 m (radius) with chords 0.287 m (root) and 0.11 m (tip); Rotor 2 with 0.457 m chord. These match my digitization of Harrington Fig. 1 (C_harrington1951: c ≈ 11.36 in = 0.289 m at r = 20 in; tip ≈ 4.3-4.4 in ≈ 0.11 m; rotor 2 18 in = 0.457 m). This suggests the blade starts at r ≈ 20 in for rotor 1 [derived, consistent but not stated].
- Eq. 4.1 (single rotor, modified momentum theory): C_P = κ C_T^{3/2}/√2 + σ C_d0/8.
- Eq. 4.3 (coax): C_P = κ_int κ C_W^{3/2}/√2 + σ C_d0/8, using **κ_int = 1.28** for Harrington.
- Eq. 4.4: C_d = C_d0 + d1 α + d2 α², with **d1 = 0.021, d2 = 0.65** "based on NACA 0012 airfoil section measurements".
- BEMT with Prandtl tip loss: the single-rotor induced power factor is **κ ≈ 1.1**. For the Harrington Rotor 1 coax, total κ varies **1.34-1.38** over the normal C_T/σ range, which implies **κ_int ≈ 1.26**, "consistent with the results from the SMT".
- Conclusion stated: SMT and BEMT power polars are in reasonably good agreement with Harrington. BEMT is better than SMT, and the free-vortex method is in good agreement.

## Use in our BEMT validation (my suggestion)
- A single-rotor BEMT should reproduce Harrington single-rotor FM_max ≈ 0.615 (C_harrington1951) with κ ≈ 1.1.
- A coaxial BEMT should give total induced factor ≈ 1.3-1.4 for rotor 1, or equivalently κ_int ≈ 1.26-1.28 on top of single-rotor κ.
