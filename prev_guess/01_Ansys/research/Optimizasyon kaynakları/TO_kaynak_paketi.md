# Density-based topology optimisation: source pack for 5–6 Nov 2026

Compiled 2026-11-03. Covers our Python SIMP code (`src/aerokit/optimization/`) and Ansys Mechanical/Discovery.

**Tags.** **[D]** = I read this in the primary source in this session, and the page or equation number is given. **[S]** = I read it in a secondary source in this session, which is named. **[Y]** = my own judgement or arithmetic. **NOT FOUND** = I could not read it this session, so no formula is given.
Equations are copied as printed, with typos kept and flagged. Symbols follow each source.

## Access log (what was and was not readable)

| Source | Status this session | Where read |
|---|---|---|
| Andreassen et al. 2011 (top88) | [D] read, author preprint dated 27 Oct 2010 | lirias.kuleuven.be/retrieve/225946 |
| Ferrari & Sigmund 2020 (top99neo) | [D] read, arXiv 2005.05436v2 | arxiv.org/pdf/2005.05436 |
| Guest, Prévost & Belytschko 2004 | **NOT FOUND**, no open copy (Princeton record only) | formula seen only as reproduced in top88 and Lazarov 2016 [S] |
| Wang, Lazarov & Sigmund 2011 | **NOT FOUND**, DTU Orbit record without file | content via Qian & Sigmund 2013 and Lazarov 2016 [S] |
| Qian & Sigmund 2013 (length-scale formula) | [D] read, author preprint | cdm.me.wisc.edu/pub/ActuatorCMAME.pdf |
| Lazarov, Wang & Sigmund 2016 (review) | [D] read, DTU Orbit postprint | backend.orbit.dtu.dk/ws/files/140201797/main.pdf |
| Le, Norato, Bruns, Ha & Tortorelli 2010 | **NOT FOUND**, Springer paywall | described in Holmberg 2013 and in the Ansys guide [S] |
| Holmberg, Torstenfelt & Klarbring 2013 | [D] read, LiU post-print | diva-portal.org/smash/get/diva2:601666/FULLTEXT02.pdf |
| Duysinx & Bendsøe 1998 | **NOT FOUND**, ORBi "request a copy" only | — |
| Du & Olhoff 2007 | **NOT FOUND**, paywall | interpolation via Yaghoobi & Hassani 2017 and pymoto [S] |
| Pedersen 2000 | **NOT FOUND** | — |
| Langelaar 2017 SMO 55:871 (2D AM filter) | [D] read, open access | link.springer.com/content/pdf/10.1007/s00158-016-1522-2.pdf |
| Langelaar 2016 AM 12:60 (3D) | **NOT FOUND**. repository.tudelft.nl refused the connection; research.tudelft.nl served a Cloudflare challenge / 403 (not bypassed) | — |
| Gaynor & Guest 2016 | **NOT FOUND** | — |
| Huang & Xie 2007/2010 (BESO) | **NOT FOUND** | BESO steps via Wang, Liu & Wen, arXiv 1908.07157 [S] |
| Allaire, Jouve & Toader 2004 JCP | **NOT FOUND**. HAL served an Anubis bot challenge (not bypassed) | same authors' 2002 C. R. Acad. Sci. note read [D] (giref.ulaval.ca mirror) |
| Wang, Wang & Guo 2003 | **NOT FOUND** | — |
| Sigmund 2007 (M_nd) | **NOT FOUND** (primary) | formula via Lazarov 2016 eq. (30) and top99neo §3.3 [S] |
| Ansys Mechanical Structural Optimization Guide 2025 R1 | [D] read, public PDF | ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/pdf/Structural_Optimization_in_Mechanical.pdf |
| Ansys Discovery help | **NOT FOUND**, not located | — |

The guide is for **2025 R1**. If the event machines run 2026 R1, check each default on screen [Y].

---

## Summary table: what each topic gives you and where our code stands

Topics are in the order of the brief. "Our code" was read on 2026-11-03 in `src/aerokit/optimization/topology.py`, `am_filter.py` and `topo_mapped.py`. A grep of `src/` for `tanh|robust|pnorm|eroded|dilated|Neumann` found no matches in TO code.

| # | Topic | Key formula | Default parameters (source) | Our code | Tag |
|---|---|---|---|---|---|
| 1 | Modified SIMP, top88 | $E_e=E_{\min}+x_e^p(E_0-E_{\min})$; density filter $\tilde x_e=\sum H_{ei}x_i/\sum H_{ei}$, $H_{ei}=\max(0,r_{\min}-\Delta(e,i))$; OC with $\eta=1/2$ | p = 3, Emin = 1e-9, move 0.2, stop max\|Δx\| < 0.01, γ = 1e-3, rmin = 0.04·width (top88) | **Implemented**: ft 0/1/2/3, OC and MMA, Emin 1e-9, move 0.2, tol 0.01 | [D] |
| 2 | top99neo | $\mathcal H=\frac{\tanh(\beta\eta)+\tanh(\beta(\tilde x-\eta))}{\tanh(\beta\eta)+\tanh(\beta(1-\eta))}$; η* from a Newton solve so that V(x̂)=V(x̃) | `top99neo(300,100,0.5,3,8.75,3,'N',0.5,2,0.2,500)`; penalCnt {1,3,25,0.25}, betaCnt {1,2,25,2}; stop ‖Δx̂‖/√m < 1e-6 | **Missing**: tanh/η projection, volume-preserving η, continuation on p, Neumann filter BC | [D] |
| 3 | Heaviside projection, robust design, length scale | eroded/blueprint/dilated thresholds 1−η, 0.5, η; $b/R=2\sqrt{\eta_e-1/2}$ for $\eta_e\in[0.5,0.75]$ | η = 0.25 gives b = R; β = 1 doubled every 50 iterations up to 128; volume constraint on the dilated design | **Partial**: only the Guest-type exponential projection (ft = 3); no robust formulation | [D] Qian & Sigmund; [S] Wang 2011 |
| 4 | Stress-constrained TO | $\sigma^{PN}_i=\big(\frac1{N_i}\sum_{a\in\Omega_i}(\sigma^{vM}_a)^p\big)^{1/p}$; $\boldsymbol\sigma_a=\eta_S(\rho_e)\hat{\boldsymbol\sigma}_a$, $\eta_S=\rho_e^{1/2}$ | p = 8 (Holmberg), q = 3; Deng et al. use q = 0.5, p = 10; Ansys recommends convergence accuracy 0.05 % | **Missing** in TO | [D] Holmberg; Le 2010 [S]; Duysinx 1998 NOT FOUND |
| 5 | Eigenfrequency TO | modified mass: $M_e=x_eM^0_e$ for $x_e\ge0.1$, $(c_1x_e^6+c_2x_e^7)M^0_e$ for $x_e\le0.1$ | c1 = 6e5, c2 = −5e6; p = 3, q = 1 | **Missing** (eigensolvers exist in `fem/solvers.py`, not wired to TO) | [S]; Pedersen NOT FOUND |
| 6 | AM overhang filter | $\xi_{(i,j)}=\mathrm{smin}(x_{(i,j)},\Xi_{(i,j)})$; $\Xi=\mathrm{smax}$ of 3 supports; $Q=P+\log n_S/\log\xi_0$ | ε = 1e-4, P = 40, ξ0 = 0.5; OC move ≈ 0.05; MMA recommended | **Implemented (2D)**, but defaults P = 80, ε = 1e-3 differ from Langelaar | [D] 2017; 3D paper NOT FOUND |
| 7 | BESO and level set | BESO: $\alpha_i=(\alpha_i^k+\alpha_i^{k-1})/2$, $V_{k+1}=V_k(1\pm ER)$; level set: $\partial_t\psi-v\lvert\nabla\psi\rvert=0$ | ER = 1 % (example) | **Missing** (not needed: use Ansys) | [S] BESO; [D] Allaire 2002 |
| 8 | Ansys practice | stop when $\lvert(f(\rho_i)-f(\rho_{i-1}))/f(\rho_i)\rvert\le\epsilon$ on 3 successive iterations; penalty $\rho^{3}$ | 500 iterations, 0.1 %, min density 0.001, penalty 3, retained threshold 0.5, percent to retain 50, min member size 2.5 × element (density-based), overhang 45° (27–60°) | **Implemented**: `gray_measure` = M_nd | [D] Ansys 2025 R1 |

---

## 1. SIMP basics and top88

**Source.** E. Andreassen, A. Clausen, M. Schevenels, B. S. Lazarov, O. Sigmund, *Efficient topology optimization in MATLAB using 88 lines of code*, Struct Multidisc Optim 43:1–16 (2011), DOI 10.1007/s00158-010-0594-7. I read the author preprint dated 27 Oct 2010 (LIRIAS, https://lirias.kuleuven.be/retrieve/225946). Page numbers below are **preprint** pages. Code: https://www.topopt.mek.dtu.dk/apps-and-software/efficient-topology-optimization-in-matlab, which also serves `top88.m`, `top82.m`, `top71.m` and `top110.m`. **[D]**

### Equations (preprint p. 3–4, 8–11)

- (1) $E_e(x_e)=E_{\min}+x_e^p(E_0-E_{\min}),\quad x_e\in[0,1]$. "typically p = 3"; Emin is "a very small stiffness assigned to void regions".
- (2) $\min_x c(\mathbf x)=\mathbf U^T\mathbf K\mathbf U=\sum_{e=1}^N E_e(x_e)\mathbf u_e^T\mathbf k_0\mathbf u_e$ s.t. $V(\mathbf x)/V_0=f$, $\mathbf{KU}=\mathbf F$, $\mathbf 0\le\mathbf x\le\mathbf 1$.
- (3) OC update as printed:
  $x_e^{new}=\begin{cases}\max(0,x_e-m) & \text{if } x_eB_e^\eta\le\max(0,x_e-m)\\ \min(1,x_e+m) & \text{if } x_eB_e^\eta\ge\min(1,x_e-m)\\ x_eB_e^\eta & \text{otherwise}\end{cases}$
  Here m is the move limit and η = 1/2 is the damping coefficient.
  **Typo in the preprint**: the second condition reads "min(1, x_e − m)". The code implements `min(x+move, ...)`, i.e. $x_e+m$.
- (4) $B_e=\dfrac{-\partial c/\partial x_e}{\lambda\,\partial V/\partial x_e}$. λ is found by bisection.
- (5) $\partial c/\partial x_e=-p\,x_e^{p-1}(E_0-E_{\min})\mathbf u_e^T\mathbf k_0\mathbf u$. Read the last vector as $\mathbf u_e$; the preprint omits the subscript. (6) $\partial V/\partial x_e=1$ (unit element volume).
- (7) Sensitivity filter: $\widehat{\dfrac{\partial c}{\partial x_e}}=\dfrac{1}{\max(\gamma,x_e)\sum_{i\in N_e}H_{ei}}\sum_{i\in N_e}H_{ei}x_i\dfrac{\partial c}{\partial x_i}$, with γ = 10⁻³.
- (8) $H_{ei}=\max(0,r_{\min}-\Delta(e,i))$. $N_e$ is the set of elements whose centre-to-centre distance to e is less than rmin.
- (9) Density filter: $\tilde x_e=\dfrac{1}{\sum_{i\in N_e}H_{ei}}\sum_{i\in N_e}H_{ei}x_i$. x are the design variables, x̃ the "physical densities".
- (10) $\dfrac{\partial\psi}{\partial x_j}=\sum_{e\in N_j}\dfrac{\partial\psi}{\partial\tilde x_e}\dfrac{\partial\tilde x_e}{\partial x_j}=\sum_{e\in N_j}\dfrac{1}{\sum_{i\in N_e}H_{ei}}H_{je}\dfrac{\partial\psi}{\partial\tilde x_e}$, with ψ = c or V.
- (15)–(17) PDE (Helmholtz) filter: $-R_{\min}^2\nabla^2\tilde\psi+\tilde\psi=\psi$ with $\partial\tilde\psi/\partial n=0$, and **$R_{\min}=r_{\min}/(2\sqrt3)$**.
- (21) Heaviside projection (Guest-type, as used in top88): $\bar x_e=1-e^{-\beta\tilde x_e}+\tilde x_e e^{-\beta}$. (23) $\partial\bar x_e/\partial\tilde x_e=\beta e^{-\beta\tilde x_e}+e^{-\beta}$. Code: `xPhys = 1-exp(-beta*xTilde)+xTilde*exp(-beta)`.

### Parameters as printed (code appendix and §3.4, §5.4)

- `E0 = 1`, `Emin = 1e-9`, `nu = 0.3`.
- OC: `l1 = 0; l2 = 1e9; move = 0.2`, `while (l2-l1)/(l1+l2) > 1e-3`, `xnew = max(0,max(x-move,min(1,min(x+move,x.*sqrt(-dc./dv/lmid)))))`.
- The volume test uses physical densities: `sum(xPhys(:)) > volfrac*nelx*nely`.
- Stop: `while change > 0.01`, where `change = max(abs(xnew(:)-x(:)))` (L∞ norm on the design variables).
- §3.4: MBB with volfrac 0.5 and p = 3; "rmin equals 0.04 times the width … i.e. 2.4, 6, and 16" for meshes 60×20, 150×50 and 300×100. **Inconsistent as printed**: 0.04 × 300 = 12, not 16 [Y].
- §5.4 Heaviside: β from 1 to 512, "doubling its value every 50 iterations or when the change … becomes less than 0.01". rmin is reduced to 0.03 × width.

### Validation targets (numbers printed in the paper; use them to test our port)

| Case (call) | Mesh | Compliance c (printed) |
|---|---|---|
| Fig. 3, sensitivity filter, ft = 1, rmin = 0.04·nelx | 60×20 / 150×50 / 300×100 | 216.81 / 219.52 / 222.29 |
| Fig. 3, density filter, ft = 2 | same | 233.71 / 235.73 / 238.31 |
| Fig. 4, PDE sensitivity filter | same | 218.79 / 217.88 / 219.44 |
| Fig. 4, PDE density filter | same | 237.60 / 235.36 / 236.62 |
| Fig. 8, Heaviside, rmin = 0.03·nelx | same | 189.14 / 191.49 / 193.24 |

Other calls given in the paper: `top88(60,20,0.5,3,1.5,1)` (reproduces the 99-line result), `top88(160,100,0.4,3,6,1)` (short cantilever), `top88(150,150,0.4,3,6,1)` (two load cases), `top88(150,100,0.5,3,5,1)` (passive hole).

### Pitfalls

- Show x̃ (`xPhys`), not x, as the result (p. 4). [D]
- With the density filter, dv is not uniform, so it must stay in the OC update (§3.3). [D]
- A non-volume-preserving filter (Heaviside) needs the volume constraint on physical densities. The initial design then violates volume, and OC corrects it (§3.3, §5.4). [D]
- The sensitivity filter (7) is heuristic: its gradient is not the true gradient. Our code docstring says the same.
- Heaviside "cannot be directly applied with the PDE filter". It also gives a minimum length scale on solid only and "does not prevent the occurrence of very small holes" (§5.4). [D]
- Wrong mesh/rmin units: rmin is in element sizes (§3). [D]

---

## 2. top99neo / top3D125 (Ferrari & Sigmund 2020)

**Source.** F. Ferrari, O. Sigmund, *A new generation 99 line Matlab code for compliance topology optimization and its extension to 3D*. I read arXiv:2005.05436v2 (28 Jul 2020), marked "Accepted paper, to appear soon in Structural and Multidisciplinary Optimization". **Final volume, pages and DOI were not read this session.** Code page: https://www.topopt.mek.dtu.dk/apps-and-software/new-99-line-topology-optimization-code-written-in-matlab, which serves `top99neo.m` and `top3d125.m`. **[D]**

### Equations (arXiv p. 2–3, 6–8)

- (1) Relaxed Heaviside projection: $\mathcal H(\tilde x_e,\eta,\beta)=\dfrac{\tanh(\beta\eta)+\tanh(\beta(\tilde x_e-\eta))}{\tanh(\beta\eta)+\tanh(\beta(1-\eta))}$, with threshold η and sharpness β. It is attributed to Wang et al. (2011).
- (2) $H(x_e,r_{\min}):=\dfrac{\sum_{i\in N_e}h_{e,i}x_i}{\sum_{i\in N_e}h_{e,i}}$, with $N_e=\{i\,|\,\mathrm{dist}(\Omega_i,\Omega_e)\le r_{\min}\}$ and $h_{e,i}=\max(0,r_{\min}-\mathrm{dist}(\Omega_i,\Omega_e))$.
- (4) $V(\hat x)=\sum_e|\Omega_e|\hat x_e=\frac1m\big(m_{P_1}+\sum_{e\in A}\hat x_e\big)\le f$. Passive solid elements count toward volume.
- (6) $E(\hat x_e)=E_{\min}+\hat x_e^p(E_0-E_{\min})$.
- (8) Back-filtering: $\nabla_x c=\nabla_{\tilde x}\mathcal H\odot(H^T\nabla_{\hat x}c)$.
- (9) $\nabla_{\tilde x}\mathcal H=\beta\dfrac{1-\tanh(\beta(\tilde x-\eta))^2}{\tanh(\beta\eta)+\tanh(\beta(1-\eta))}$.
- (10)–(11) OC: $x_{k+1,e}=\delta_-$ if $\mathcal F<\delta_-$; $\delta_+$ if $\mathcal F>\delta_+$; $\mathcal F_{k,e}$ otherwise. Here $\delta_\mp=\max(0,x_{k,e}\mp\mu)$ / $\min(1,x_{k,e}+\mu)$ and $\mathcal F_{k,e}=x_{k,e}\big(-\partial_ec_k/(\tilde\lambda_k\partial_eV_k)\big)^{1/2}$.
- (17) Volume-preserving threshold: $\eta_k^*=\arg\min_{\eta\in[0,1]}|V(\hat x_k(\eta))-V(\tilde x_k)|$, solved by Newton from the previous η. "Generally $\eta_k^*\in[0.4,0.52]$", converging in 1–2 Newton iterations (§3.2).
- (19) Upper bound for the multiplier, used to bracket the bisection: $\lambda_k^\#=\Big(\frac{1}{mf}\sum_e x_{k,e}\big(-\partial_ec_k/\partial_eV_k\big)^{1/2}\Big)^2$. Initial bracket $[0,\lambda^\#]$ instead of $[0,10^9]$ cuts the number of bisections by about 50 %.
- Non-discreteness (§3.3): $m_{ND}=100\times4\hat{\mathbf x}^T(1-\hat{\mathbf x})/m$. Hats are inferred because the glyphs were lost in extraction; Lazarov 2016 eq. (30) gives the same form [S].

### What changes relative to top88

| Item | top88 | top99neo (code listing, arXiv) |
|---|---|---|
| Filter | sparse H built with loops, or `conv2` (zero-Dirichlet only) | `imfilter(...,h,bcF)`, where `ftBC='N'` sets `bcF='symmetric'` (zero-Neumann) and `'D'` sets 0 |
| Projection | exponential Heaviside (ft = 3 variant) | tanh with η; ft = 2 keeps η fixed, ft = 3 computes volume-preserving η* (Newton, tolerance 1e-6) |
| Continuation | β doubled every 50 iterations (Heaviside variant only) | `penalCnt = {1, 3, 25, 0.25}`, `betaCnt = {1, 2, 25, 2}` = {istart, maxPar, isteps, deltaPar} |
| OC bisection | [0, 1e9], tolerance 1e-3 | `l = [0, mean(ocP)/volfrac]`, `while (l(2)-l(1))/(l(2)+l(1)) > 1e-4` |
| Stop | max\|Δx\| < 0.01 | `while ch > 1e-6 && loop < maxit`, `ch = norm(xPhys-xOld)./sqrt(nEl)` |
| Assembly | full `sparse` | lower triangle only, `fsparse` (stenglib), int32 indices |

Example calls on the DTU page: `top99neo(300,100,0.5,3,8.75,3,'N',0.5,2,0.2,500)` and `top3D125(24,12,12,0.12,3,sqrt(3),1,'N',0.5,1,0.2,100)`. Argument order: nelx, nely, volfrac, penal, rmin, ft, ftBC, eta, beta, move, maxit. Paper default test: 300×100, f = 0.5, rmin = 8.75, E1 = 1, Emin = 1e-9, ν = 0.3.

### Table 2 of the paper (MBB, convergence comparison, as printed)

T1: density filter, p = 3. T2: projection, η from (17), β = 2. T3: as T2 plus betaCnt {250,16,25,2} and penalCnt {50,3,25,0.25}. T4: as T2 on 600×200. PAE = periodic Anderson extrapolation, with q = 4, mr = 4, start q0 = 20 (T1–T2) or 500 (T3–T4), damping 0.9 on non-accelerated steps. Stop: ‖r‖₂/√m < 1e-6.

| Test | it. | c | Δc | ‖r‖₂/√m | m_ND |
|---|---|---|---|---|---|
| T1 | 2500 | 252.7 | 4.2e-8 | 1.03e-5 | 0.025 |
| T1-PAE | 828 | 258.9 | 4.2e-10 | 9.95e-7 | 0.021 |
| T2 | 2500 | 246.1 | 5.1e-8 | 3.21e-5 | 0.023 |
| T2-PAE | 352 | 253.9 | 6.2e-9 | 9.97e-7 | 0.014 |
| T3 | 2500 | 199.6 | 1.1e-4 | 1.91e-3 | 0.014 |
| T3-PAE | 752 | 197.5 | 3.7e-8 | 8.72e-7 | 0.007 |
| T4 | 2500 | 191.8 | 2.0e-7 | 3.21e-5 | 0.006 |
| T4-PAE | 818 | 192.1 | 2.5e-7 | 9.97e-7 | 0.001 |

The m_ND column is printed without the ×100 scale it uses in the text.

### Pitfalls

- **Continuation is off in the default call.** With `penal = 3` and `beta = 2` as inputs, `maxPar` (3 and 2) is already reached, so `cnt()` adds nothing. To get continuation, start p at 1 and set maxPar higher, as in T3 [Y, read from the listing logic].
- ft = 2 with fixed η and the volume constraint on x: V(x̂) > f if η < 0.5 and V(x̂) < f if η > 0.5. The paper gives replacement bisection lines that evaluate the volume on the projected field (§3.2). [D]
- Filter BC matters. On the 3D cantilever (48×24×24, f = 0.12, rmin = 3, 100 iterations), Neumann gives c = 3993.7 and Dirichlet gives c = 4074.3, "clearly a worse local minimum" (§4, Fig. 8). [D] Our `filter_matrix` (row-sum normalisation, like top88) is the zero-padding case, i.e. the paper's 'D' [Y].
- In the arXiv v2 listing, the 2D code computes `imfilter(x)./Hs` and back-filters `imfilter(dc./dHs)`, while the 3D code computes `imfilter(x./Hs)` and `imfilter(dc)./dHs`. The two agree only where Hs is constant, which holds with 'N' (symmetric padding). With 'D' the 3D order is not eq. (2) [Y]. Port the 2D order.
- Its stopping rule (‖Δx̂‖₂/√m) is not top88's (max\|Δx\|). Do not compare iteration counts across codes. [D]

---

## 3. Heaviside projection, robust formulation, minimum length scale

### 3a. Projection functions

- Guest, Prévost & Belytschko 2004 (IJNME): primary **NOT FOUND**. As reproduced in Lazarov et al. 2016 eq. (16)–(18) [S]: $\bar{\bar\rho}=H(\tilde\rho)$, $H(\tilde\rho)\approx1-\exp(-\beta\tilde\rho)+\tilde\rho\exp(-\beta)$. For length scale on void use $\bar{\bar\rho}=1-H(1-\tilde\rho)$. Top88 notes that Guest et al. "include an extra term" for the lower bound, which modified SIMP makes unnecessary [S].
- Intermediate-threshold tanh projection, attributed to Wang, Lazarov & Sigmund 2011 (primary **NOT FOUND**). Printed identically in top99neo eq. (1) [D], Lazarov 2016 eq. (23) [D] and Qian & Sigmund 2013 eq. (25) [D]:
  $\bar{\tilde\rho}_i=\dfrac{\tanh(\beta\eta)+\tanh(\beta(\tilde\rho_i-\eta))}{\tanh(\beta\eta)+\tanh(\beta(1-\eta))}$.
  Qian & Sigmund p. 8: "For η = 0, the projection corresponds to the original Heaviside projection concept [18], for η = 1 we have the modified Heaviside projection concept [16] and for η = 1/2 we have the volume preserving projection concept [19]." [D]

### 3b. Robust (eroded / intermediate / dilated) formulation

- Qian & Sigmund 2013, preprint p. 8 [D]: "η is substituted with the three values 1 − η, 0.5, η with η ∈ [0, 0.5], denoting the eroded, the blue-print and the dilated realization". β is "initialized to 1 and then doubled every 50th iteration until it reaches 128". Convergence (numerical results section): maximum density change < 0.01 and β ≥ 128. Volume constraint "imposed on the dilated design". Examples use R = 6.3h and 8.4h with η = 0.25.
- Lazarov, Wang & Sigmund 2016, Arch Appl Mech 86:189–218, DOI 10.1007/s00419-015-1106-4, eq. (37), p. 22 [D]:
  $\min_\rho\max\{J_e,J_d\}$ s.t. $\mathbf K(\rho,\eta_d)\mathbf u_d=\mathbf f$, $\mathbf K(\rho,\eta_e)\mathbf u_e=\mathbf f$, $V(\rho,\eta_d)\le V^*$, $0\le\rho\le1$.
  For compliant mechanisms the worst case is the most eroded or the most dilated design, so dropping the blueprint "can save around a third of the computational time". Examples use η ∈ [0.35, 0.65] (p. 23).
  Length scale is "guaranteed only if the designed topology does not change for all possible realizations" (p. 23).
- Wang, Lazarov & Sigmund 2011, SMO 43:767–784, DOI 10.1007/s00158-010-0602-y (DTU Orbit lists a 2022 correction, DOI 10.1007/s00158-022-03326-6): primary **NOT FOUND**. Do not attribute exact equations to it from this pack.

### 3c. Filter radius → minimum member size (explicit rule)

**Source.** X. Qian, O. Sigmund, *Topological design of electromechanical actuators with robustness toward over- and under-etching*, author preprint, Appendix (p. 23–25), https://cdm.me.wisc.edu/pub/ActuatorCMAME.pdf. Published in CMAME (2013). **Volume, pages and DOI were not read in the preprint this session.** **[D]**

Assumptions (p. 23–24): the three realisations have the same topology; the filter is the 1D normalised hat $w_h=\frac1R(1-\frac{|x|}{R})$ on [−R, R]; b is the minimum width of the intermediate (blueprint) design.

- (27) $\tilde\rho(x_{p,1})=\int_{-h/2}^{h/2}\frac1R\big(1-\frac{|x|}{R}\big)dx=\eta_e$.
- **(29)** $\dfrac bR=\begin{cases}2-2\sqrt{1-\eta_e}, & \eta_e\in[0.75,1]\\ 2\sqrt{\eta_e-1/2}, & \eta_e\in[0.5,0.75]\end{cases}$
- **(30)** $\eta_e=\begin{cases}\frac14(b/R)^2+\frac12, & b/R\in[0,1]\\ -\frac14(b/R)^2+b/R, & b/R\in[1,2]\\ 1, & b/R\in[2,\infty)\end{cases}$

The prediction matched computed hinge and gap widths within 1 % (inverter) and 1.6 % (gripper) after round-off (numerical results, Tables 1–2).

Worked values from (29) [Y, arithmetic]:

| η (dilated) | η_e = 1 − η | b/R |
|---|---|---|
| 0.40 | 0.60 | 0.63 |
| 0.30 | 0.70 | 0.89 |
| 0.25 | 0.75 | 1.00 |
| 0.20 | 0.80 | 1.11 |
| 0.10 | 0.90 | 1.37 |

Recipe [Y]: choose η_e = 0.75, then rmin (cone radius, in elements) = target minimum member width / element size. Use at least 3 elements across the radius so the hat filter is resolved. For the PDE filter use $R_{\min}=r_{\min}/(2\sqrt3)$ (top88 eq. 17) [D].

Pitfalls: (29) is 1D with a hat kernel. For the Helmholtz filter it "follow[s] the predicted value reasonably well" (Table 1 discussion) [D]. A plain single-field η = 0.5 projection gives **no** length scale on either phase (Fig. 2 discussion) [D].

---

## 4. Stress-constrained TO

### 4a. Holmberg, Torstenfelt & Klarbring 2013 (clustered P-norm) [D]

**Source.** E. Holmberg, B. Torstenfelt, A. Klarbring, *Stress constrained topology optimization*, SMO 48(1):33–47 (2013), DOI 10.1007/s00158-012-0880-7. I read the LiU post-print, https://www.diva-portal.org/smash/get/diva2:601666/FULLTEXT02.pdf. Page numbers are journal pages printed on the post-print.

- (P1) $\min_x\sum_e m_e\rho_e(x)$ s.t. $\sigma_i^{PN}(x)\le\bar\sigma$, $i=1..n_c$, and $\underline x_e\le x_e\le\bar x_e$, with $\underline x_e=\epsilon$ small (p. 3). (P2): minimise $\frac12F^Tu$ with stress and mass constraints.
- Filter (p. 4): $\rho_e(x)=\sum_{j\in\Omega_e}w_jx_j/\sum_{j\in\Omega_e}w_j$, cone weight $w_j=(r_0-r_j)/r_0$. Stiffness: $\eta_K(\rho_e)=\rho_e^q$, "**q = 3**".
- (3)–(4) Stress penalisation (p. 5): $\boldsymbol\sigma_a(x)=\eta_S(\rho_e(x))\hat{\boldsymbol\sigma}_a(x)$, $\hat{\boldsymbol\sigma}_a=EB_au$, and **$\eta_S(\rho_e)=(\rho_e)^{1/2}$**. This is "the penalization in [7] [Bruggi] … with a specific choice of the exponent, as suggested in [20] [Le et al.]", and gives $\lim_{\rho_e\to0}\boldsymbol\sigma_a=\mathbf 0$, hence no singularity.
- (5) $\sigma_a^{vM}=(\sigma_{ax}^2+\sigma_{ay}^2+\sigma_{az}^2-\sigma_{ax}\sigma_{ay}-\sigma_{ay}\sigma_{az}-\sigma_{az}\sigma_{ax}+3\tau_{axy}^2+3\tau_{ayz}^2+3\tau_{azx}^2)^{1/2}$.
- **(6)** $\sigma_i^{PN}(x)=\Big(\dfrac1{N_i}\sum_{a\in\Omega_i}(\sigma_a^{vM}(x))^p\Big)^{1/p}$, with $N_i$ the number of points in cluster i.
- Bounds (p. 6): $\big(\frac1{N_i}\sum(\sigma^{vM}_a)^p\big)^{1/p}\le\max_{a\in\Omega_i}\sigma^{vM}_a\le\big(\sum(\sigma^{vM}_a)^p\big)^{1/p}$, so the true maximum is below $N_i^{1/p}\bar\sigma$.
- Scaled constraint actually used (p. 6): $\Big(\dfrac1{N_i}\sum_{a\in\Omega_i}\big(\sigma_a^{vM}/\bar\sigma\big)^p\Big)^{1/p}\le1$.
- **p = 8** in all examples (p. 6): "numerical problems are … experienced for too high values of p; … p = 1 gives the mean stress".
- Clustering (§6): "stress level" (sort descending, consecutive blocks of $n_e/n_c$) or "distributed" (round-robin). Re-clustering every iteration, every 50th, or never all converged; every iteration gives small oscillations.
- Sensitivities (§7):
  - $\dfrac{\partial\sigma_i^{PN}}{\partial\sigma_a^{vM}}=\Big(\frac1{N_i}\sum(\sigma_a^{vM})^p\Big)^{\frac1p-1}\frac1{N_i}(\sigma_a^{vM})^{p-1}$.
  - $\partial\sigma^{vM}_a/\partial\sigma_{ax}=\frac{1}{2\sigma^{vM}_a}(2\sigma_{ax}-\sigma_{ay}-\sigma_{az})$ (cyclic), and $\partial\sigma^{vM}_a/\partial\tau_{axy}=\frac{3}{\sigma^{vM}_a}\tau_{axy}$ (cyclic).
  - (12) $\dfrac{\partial\boldsymbol\sigma_a}{\partial x_b}=\dfrac{\partial\eta_S}{\partial\rho_e}\dfrac{\partial\rho_e}{\partial x_b}EB_au+\eta_S EB_a\dfrac{\partial u}{\partial x_b}$.
  - Adjoint: $K\boldsymbol\lambda_i=\sum_{a\in\Omega_i}\dfrac{\partial\sigma_i^{PN}}{\partial\sigma_a^{vM}}B_a^TE^T\dfrac{\partial\sigma^{vM}_a}{\partial\boldsymbol\sigma_a}$.
  - Final gradient: $\dfrac{\partial\sigma_i^{PN}}{\partial x_b}=\sum_{a\in\Omega_i}\dfrac{\partial\sigma_i^{PN}}{\partial\sigma_a^{vM}}\Big(\dfrac{\partial\sigma_a^{vM}}{\partial\boldsymbol\sigma_a}\Big)^T\dfrac{\partial\eta_S}{\partial\rho_e}\dfrac{\partial\rho_e}{\partial x_b}EB_au-\eta_S\boldsymbol\lambda_i^T\Big[\sum_{r}\dfrac{\partial K}{\partial\rho_r}\dfrac{\partial\rho_r}{\partial x_b}u\Big]$ (p. 8–9).
- Practical (p. 9–10): stress is evaluated at the element centroid (Q4). Exclude the elements under the load from the design space. Filter radius r₀ = 1.5 element sizes (L-beam) and 2 in a later example. The filter makes members thicker than about 2 r₀, so the element size must suit the stress limit and the radius. Initial ρ = 0.5. MMA is the optimiser.

### 4b. Le, Norato, Bruns, Ha & Tortorelli 2010: primary NOT FOUND

SMO 41(4):605–620, DOI 10.1007/s00158-009-0440-y (paywalled). What I read about it, all **[S]**:
- Holmberg p. 6: Le et al. "use an elemental scale factor based on the volume of element a, instead of the 1/N_i-term", and "scale the current values with respect to stress values from the previous iteration". Exponent 1/2 for the stress interpolation "as suggested in [20]".
- Ansys guide 2025 R1 p. 113 (pdf p. 121): "In Le, the normalized maximum approximation … instead of using a fixed factor an adaptive factor $c_i$ is introduced. In each iteration i the factor $c_i$ is modified … $\lim_{i\to\infty}c_i\|\sigma^i_S\|_p=\|\sigma^i_S\|_\infty$".
- The exact update formula for c is **NOT FOUND**. Do not code it from memory.

### 4c. Duysinx & Bendsøe 1998 (ε-relaxation): primary NOT FOUND

IJNME 43:1453–1478 (ORBi record, request-a-copy only). The ε-relaxed constraint formula is **NOT FOUND**. Holmberg only states that ε-relaxation (Cheng & Guo) "is used in stress constrained problems by Duysinx and Bendsøe" and opens the hole of their Fig. 1 example. The "qp" form below is from a secondary source.

### 4d. Relaxed stress σ = x^q σ₀ (secondary) [S]

H. Deng, P. S. Vulimiri, A. C. To, *An efficient 146-line 3D sensitivity analysis code of stress-based topology optimization written in MATLAB*, arXiv:2104.01210, eq. (1)–(9), p. 3–4:
- $D_i=x_i^{pl}D_0$ and $\boldsymbol\sigma_i=D_0B_iu_i$.
- $\hat{\boldsymbol\sigma}_i(x_i)=\eta(x_i)\boldsymbol\sigma_i$, $\eta(x_i)=(x_i)^q$, with q "a non-negative stress relaxation parameter".
- $\sigma_{PN}=\big(\sum_{i}\hat\sigma_{vm,i}^p\big)^{1/p}\ge\max\hat\sigma_{vm}$.
- Values used: pl = 3, q = 0.5, p = 10 (stress minimisation), p = 8 (finite-difference check). "ill-conditioned and cause severe oscillations … if … p is too great (p > 30)".

### Recommended settings for the day [Y, from the above]

| Setting | Value |
|---|---|
| Stiffness penalty p | 3 |
| Stress relaxation exponent | 0.5 |
| P-norm exponent | 8–10; do not exceed about 30 |
| Normalisation | normalise by $\bar\sigma$; with a fixed $1/N^{1/p}$ factor, expect the true maximum to overshoot |
| Load region | exclude elements under loads (Ansys and Holmberg agree) |
| Ansys convergence accuracy | 0.05 % for mass minimisation with von Mises constraints (guide p. 9, note) [D] |

---

## 5. Frequency / eigenvalue TO

- Du & Olhoff 2007, SMO 34(2):91–110, DOI 10.1007/s00158-007-0101-y: primary **NOT FOUND**.
- Pedersen 2000, SMO 20:2–11: primary **NOT FOUND**. Its modified interpolation is therefore not given here.

**Modified mass interpolation "following Du and Olhoff"**, as printed in N. Yaghoobi, B. Hassani, Int J Optim Civil Eng 7(1):1–12 (2017), eq. (2), (3), (6), p. 3–4 (https://cefsse.iust.ac.ir/ijoce/article-1-280-en.pdf) **[S]**:
- $\mathbf E_e=x_e^p\mathbf E_e^0$ ("p … usually 3"), $\mathbf M_e=x_e^q\mathbf M_e^0$ ("usually q = 1").
- (6) $\mathbf M_e(x_e)=\begin{cases}x_e\mathbf M_e^0, & x_e\ge0.1\\(c_1x_e^6+c_2x_e^7)\mathbf M_e^0, & x_e\le0.1\end{cases}$, with $c_1=6\times10^5$, $c_2=-5\times10^6$ "enforc[ing] the C⁰ and C¹ continuity at x_e = 0.1".
- Check [Y]: $c_1(0.1)^6+c_2(0.1)^7=0.6-0.5=0.1$ and $6c_1(0.1)^5+7c_2(0.1)^6=36-35=1$. Both are correct.
- Problem (8): max–min of $\omega_i^2$ with $\mathbf u_i^T\mathbf M\mathbf u_j=\delta_{ij}$ and a volume constraint. Bound formulation solved with MMA.

**A different variant in code**: pymoto docs, "Eigenfrequency maximization" example, read via WebFetch (https://pymoto.readthedocs.io/en/stable/auto_examples/topology_optimization/ex_eigenfrequency.html) **[S]**:
- "Two-range material interpolation based on Du and Olhoff's paper": mass $=\rho x^{p_1}$ for $x\ge t$ and $\rho x^{p_0}/t^{(p_0-p_1)}$ for $x<t$.
- Defaults t = 0.1, p0 = 6, p1 = 1. This is C⁰ only. Stiffness $E(x_{\min}+(1-x_{\min})x^3)$, x_min = 1e-9.
- Objective: sum of reciprocals of the 3 lowest eigenvalues, scaled by 100 for MMA. Filter radius 2.0, volfrac 0.5.
- The two secondary sources disagree on the form below 0.1. Pick one and state it.

**Why localized modes occur** (Olhoff & Du 2016, SMO 54:1113–1141, open-access CC BY, https://vbn.aau.dk/ws/files/266147618/s00158_016_1574_3.pdf, §2.1–2.2, p. 1116–1117) **[D]**:
- SIMP for single-material vibrating structures "may lead to the occurrence of spurious, localized vibration modes". The paper points to Pedersen (2000), Tcherniak (2002) and Du & Olhoff (2007b) for elimination methods.
- In bi-material design with equal specific stiffness $E^{*2}/\gamma_m^{*2}=E^{*1}/\gamma_m^{*1}$, localized modes "may be avoided".
- "a pertinent value of the power q is 1 in design for maximization of eigenfrequencies".

**Ansys Mechanical** (guide 2025 R1 p. 111–112, pdf p. 120) **[D]**:
- Frequency can be the objective (single or weighted) or a constraint with lower and upper bounds.
- "all of the repeating frequencies are optimized simultaneously". "there is no tracking with respect to the initial mode shape".
- Multiple eigenvalues are handled with a special sensitivity (Seyranian et al. 1994).
- The OC solver "should not be used for a Modal Analysis". Pre-stressed modal and damping are not supported (p. 109–110).

Pitfalls [Y]: maximise the lowest eigenvalue with a bound formulation, not ω₁ alone, because modes switch. Check that the final first mode is global, not confined to grey regions.

---

## 6. AM overhang filter

**Correction to the brief** [D, Langelaar 2017 p. 872]: the **2D** filter is in SMO 2017 ("For clarity we limit the discussion to the 2D case … The extension to 3D … will be discussed elsewhere (Langelaar 2016)"). The **3D** version is the Additive Manufacturing 2016 paper.

**Source.** M. Langelaar, *An additive manufacturing filter for topology optimization of print-ready designs*, Struct Multidisc Optim 55:871–883 (2017), DOI 10.1007/s00158-016-1522-2, open access. **[D]**

### Model (p. 872–873)

- (1) $\xi_{(i,j)}=\min\big(x_{(i,j)},\Xi_{(i,j)}\big)$, where x is the blueprint and ξ the printed density.
- (2) $\Xi_{(i,j)}=\max\big(\xi_{(i-1,j-1)},\xi_{(i-1,j)},\xi_{(i-1,j+1)}\big)$, with layer i = 1 on the base plate printed as designed. The supporting region is three elements (45° rule); "In 3D, one may use a support region of 5 or 9 elements". At domain boundaries the region has 2 elements.
- (3) $\mathrm{smin}(x,\Xi)\equiv\frac12\Big(x+\Xi-\big((x-\Xi)^2+\varepsilon\big)^{1/2}+\sqrt\varepsilon\Big)$
- (4) $\mathrm{smax}(\xi_1,\xi_2,\xi_3)\equiv\big(\sum_{k=1}^{n_S}\xi_k^P\big)^{1/P}$. This overestimates for equal inputs, so it is redefined as
- (5) $\mathrm{smax}(\xi_1,\xi_2,\xi_3)\equiv\big(\sum_{k=1}^{n_S}\xi_k^P\big)^{1/Q}$ with $Q\le P$
- (6) **$Q=P+\dfrac{\log n_S}{\log\xi_0}$**, which gives zero overshoot for uniform layers at density ξ₀. "we choose ξ₀ = 0.5 as default value".
- (7)–(8) $\xi_{(i,j)}=\mathrm{smin}(x_{(i,j)},\Xi_{(i,j)})$, $\Xi_{(i,j)}=\mathrm{smax}(\xi_{(i-1,j-1)},\xi_{(i-1,j)},\xi_{(i-1,j+1)})$.
- **Defaults (p. 875): ε = 10⁻⁴, P = 40, ξ₀ = 0.5.** Worked Q [Y]: $Q=40+\ln3/\ln0.5=40-1.585=38.415$ (for n_S = 2 at a boundary: 39.0).

### Sensitivities (p. 874, eq. 9–14)

- (10) $\xi_i=\mathrm{smin}(x_i,\xi_{i-1})=\check s(x_i,\xi_{i-1})$, with layer indices and $\xi_1=\check s_1\equiv x_1$.
- (11) $\tilde f_p=f_p(\xi(x))+\sum_{i=1}^{n_i}\lambda_i^T(\check s(x_i,\xi_{i-1})-\xi_i)$.
- (13) Backward (top layer down) recursion:
  $\lambda_j^T=\dfrac{\partial f_p}{\partial\xi_j}+\lambda_{j+1}^T\dfrac{\partial\check s_{j+1}}{\partial\xi_j}$ for $1\le j<n_i$, and $\lambda_{n_i}^T=\dfrac{\partial f_p}{\partial\xi_{n_i}}$.
  Then $\dfrac{\partial f_p}{\partial x_j}=\lambda_j^T\dfrac{\partial\check s_j}{\partial x_j}$.
- $\dfrac{\partial\check s(x,\Xi)}{\partial x}=\frac12\big(1-(x-\Xi)((x-\Xi)^2+\varepsilon)^{-1/2}\big)$, $\dfrac{\partial\check s}{\partial\Xi}=\frac12\big(1+(x-\Xi)((x-\Xi)^2+\varepsilon)^{-1/2}\big)$, $\dfrac{\partial\check s}{\partial\xi}=\dfrac{\partial\check s}{\partial\Xi}\dfrac{\partial\Xi}{\partial\xi}$.
- (14) $\dfrac{\partial\Xi(\xi_1,\xi_2,\xi_3)}{\partial\xi_i}=\dfrac{P\xi_i^{P-1}}{Q}\Big(\sum_{k=1}^{n_S}\xi_k^P\Big)^{1/Q-1}$.
- (15)–(16) Chain with the density filter: $\partial f_p/\partial x=(\partial f_p/\partial\xi)(\partial\xi/\partial\tilde x)(\partial\tilde x/\partial x)$. "the AM filter should typically be the last in the chain".

### Integration into top88 (Appendix "Use of AMfilter.m") [D]

- Call `xPrint = AMfilter(xPhys, baseplate)` (baseplate N/E/S/W/X) and `[xPrint,df1,df2,..] = AMfilter(xPhys,baseplate,df1,df2,..)`.
- Replace xPhys with xPrint in lines 54, 59 and 60. Transform dc and dv before filtering.
- **Reduce the OC move limit to e.g. 0.05.** Apply the filter inside the OC loop.
- Prefer density filtering; with sensitivity filtering, also filter dv. "Use of MMA is recommended".
- `AMfilter.m` is supplementary material of the article, per the paper; I did not download it.

### Our code vs Langelaar

`am_filter.py` implements the same smin (3), smax (5) and Q (6). Its docstring says "the original equations were not read". They now match the printed equations.
**Defaults differ**: ours P = 80, ε = 1e-3 (taken from a CILAMCE 2024 study) vs Langelaar ε = 1e-4, P = 40. The 3D filter is not implemented. [D, read in our source]

### Other sources

- Langelaar 2016, *Topology optimization of 3D self-supporting structures for additive manufacturing*, Additive Manufacturing 12 Part A:60–70, DOI 10.1016/j.addma.2016.06.010: **NOT FOUND**. The 3D support stencil, P/ε values and 3D sensitivity are therefore not given.
- Gaynor & Guest 2016, SMO 54:1157–1172, DOI 10.1007/s00158-016-1551-x: **NOT FOUND**. Langelaar 2017 p. 872 summarises Gaynor & Guest (2014): a wedge-shaped filter where "intermediate density material can readily be used by the optimizer to support fully dense structures" [S].
- Ansys (guide Table 4.1/4.2, pdf p. 193) [D]: the density-based and mixable-density overhang constraint "is based on filtering techniques [16]", where [16] = Langelaar 2016 (AM 12). Level set uses Allaire et al. 2017 (JCP 351). Setup: Build Direction (default +Z) and Overhang Angle (default 45°). For density-based, keep the angle **between 27° and 60°** (Manufacturing Constraint, AM Overhang note).

---

## 7. BESO and level-set methods

**BESO (Huang & Xie 2007, FEAD 43:1039–1049, DOI 10.1016/j.finel.2007.06.006): primary NOT FOUND.** Steps as described in H. Wang, J. Liu, G. Wen, arXiv:1908.07157, §4.4, p. 10–11 **[S]**:
1. Elements are discrete 0/1 (soft-kill: void = ρ_min).
2. Sensitivity numbers are filtered, then averaged with history: $\alpha_i=(\alpha_i^k+\alpha_i^{k-1})/2$ (eq. 21).
3. Target volume: $V_{k+1}=V_k(1\pm ER)$, where ER is the evolutionary volume ratio (1 % in their MBB example).
4. Solids with $\alpha_i\le\alpha_{del}^{th}$ switch to 0; voids with $\alpha_i>\alpha_{add}^{th}$ switch to 1.
5. Stop when the volume is reached and $\big|\sum_{i=1}^M(C_{k-i+1}-C_{k-M-i+1})\big|/\sum_{i=1}^MC_{k-i+1}\le\tau$ (eq. 22).

Use it as a concept only [Y]: designs are crisp but the volume path is user-set, and the method is not in Ansys Mechanical's list (density, level set, mixable density, lattice, shape, topography; guide intro, "Optimization Methods") [D].

**Level set (Allaire, Jouve & Toader).** The JCP 2004 paper (194:363–393, DOI 10.1016/j.jcp.2003.09.032) was **not read**. The same authors' C. R. Acad. Sci. Paris 2002 note, *A level-set method for shape optimization*, p. 3–4, was read **[D]**:
- Shape Ω ⊂ Q with ψ < 0 in Ω, ψ = 0 on ∂Ω∩Q and ψ > 0 in Q∖Ω.
- Minimise $J(\Omega)+\ell\int_\Omega dx$. For compliance the shape derivative gives the velocity $v=2\big[\frac{\partial(g\cdot u)}{\partial n}+Hg\cdot u\big]-Ae(u)\cdot e(u)$.
- ψ is transported by the Hamilton–Jacobi equation $\partial\psi/\partial t-v|\nabla\psi|=0$ (eq. 7), using upwind differences on a fixed mesh.
- Void is a weak material $B=10^{-3}A$. A step is accepted when $J(\Omega_{k+1})+\ell|\Omega_{k+1}|\le J(\Omega_k)+\ell|\Omega_k|$.
- Topology changes only by boundaries merging; holes are not nucleated in this 2002 scheme [Y, from the algorithm].
- Wang, Wang & Guo 2003 (CMAME 192:227–246): **NOT FOUND**.

**When Ansys's level-set option differs from density** (guide 2025 R1) **[D]**:

| Aspect | Level set (Ansys) | Density-based / mixable density (Ansys) |
|---|---|---|
| Representation | "directly deals with the boundary of the shape … unambiguous solution" (guide intro) | SIMP pseudo-densities; mixable density is the default Optimization Type and "delivers smoother results" (§2 Optimization Type; §3.2.3, p. 119) |
| Elements | only 3D elements (p. 114) | density-based supports solid, shell and plane; mixable density supports solid only (p. 109, p. 120) |
| Retained threshold | "not relevant" (Topology Density Tracker section) | default 0.5, range 0.01–0.99 |
| Member size | Min/Max default Free; mesh so that the size is greater than 4 × element average size, and the tool raises a limit that is too small to four element sizes | density-based minimum: Program Controlled = **2.5 × mesh element size**; mixable density has no Max or Gap |
| Mesh advice | uniform fine mesh; if features are one element thick, refine (p. 118) | — |
| Overhang basis | Allaire et al. 2017 (JCP 351) | Langelaar 2016 filter |
| Responses / solver | geometric (mass, volume, CoG, inertia), compliance, displacement and reaction-force criteria, frequency (ranking must not change), stress (best-practice note p. 118) | SCP (MMA-type) by default; OC only for compliance + volume/mass |

Practical choice [Y]: use density-based or mixable density for quick concepts and stress/frequency work. Use level set when you need a crisp boundary on a 3D solid mesh with member-size control.

---

## 8. Practical guidance: convergence, greyness, interpretation, Ansys settings

### Convergence criteria (all [D])

| Code | Criterion | Default |
|---|---|---|
| top88 | max\|x_new − x\| ≤ 0.01 on design variables | 0.01 |
| top99neo | ‖x̂_k − x̂_{k−1}‖₂/√m ≤ 1e-6, or maxit | 1e-6, maxit as passed |
| Robust (Qian & Sigmund) | max density change < 0.01 and β ≥ 128 | — |
| Ansys density-based (pdf p. 121) | $\big\lvert\frac{f(\rho_i)-f(\rho_{i-1})}{f(\rho_i)}\big\rvert\le\epsilon$ for three successive iterations; constraints within 0.1 % of bound | Convergence Accuracy 0.1 % (≤ 2 allowed); Maximum Number of Iterations 500 |

Ansys warns that the relaxed criterion "might terminate too early … rerun with a smaller tolerance" (p. 113) [D].

### Greyness (measure of non-discreteness)

$M_{nd}=\dfrac{\sum_1^N4\bar\rho_i(1-\bar\rho_i)}{N}\cdot100\%$, from Lazarov 2016 eq. (30), citing [124] = Sigmund 2007 **[S]**. Sigmund 2007 (SMO 33:401–424) primary was **not read**.
Reference values: 0 % is black and white, 100 % is all 0.5. top99neo Table 2 reaches m_ND ≈ 0.001–0.025 (fraction). Our `gray_measure()` implements exactly this formula [D, our code].

### Interpretation and reconstruction

- Report the physical field (x̃ or x̂), never x (top88 p. 4). [D]
- Check M_nd before thresholding. A threshold changes volume: in Ansys, Percent to Retain is an **equality** constraint for density-based (p. 42), and the Retained Threshold slider (default 0.5) changes the reported Final Volume/Mass (p. 63). [D]
- Ansys colour bands: Remove 0–0.4, Marginal 0.4–0.6, Keep > 0.6 (p. 64). [D]
- Reconstruction: a **Smoothing** object generates an STL (not on Linux). Design validation (Geometry or Model) needs a Smoothing object with Export Model = Yes, and Mechanical creates a .pmdb for the downstream system (p. 62, p. 82–88). [D]
- Re-analyse the smoothed geometry with the real loads. Compare compliance and stress to the TO result. A density result with grey hinges or one-element members means a coarse mesh or a small rmin [Y].

### Ansys Mechanical 2025 R1 defaults (Structural Optimization Guide, p. 8–12, 42, 53–54) [D]

| Setting | Default / rule |
|---|---|
| Optimization Type | Topology Optimization – **Mixable Density (default)**; Density Based is listed separately ("Select the Optimization Type") |
| Maximum Number of Iterations | 500 |
| Minimum Normalized Density | 0.001 (between 0 and 1) |
| Convergence Accuracy | 0.1 % (≤ 2); 0.05 % recommended for mass/volume minimisation with stress constraints |
| Initial Volume Fraction | program-chosen from objectives and constraints |
| Penalty Factor (Stiffness) | 3; stiffness scaled by "Pseudo Density^Penalty Factor (Stiffness)" |
| Filter (density-based only) | Non-Linear (Program Controlled default) or Linear. Linear is faster but "may prefer placing material on the boundary". Exclude load areas. |
| Solver Type | Program Controlled = Sequential Convex Programming (MMA extension with merit-function line search). OC only for compliance with volume/mass and min member size. |
| Response constraint Mass/Volume | Percent to Retain 50 (1–99); Range Min/Max 50/50 |
| Member Size, density-based | Minimum Program Controlled = 2.5 × mesh element size; Max Manual |
| Exclusion Thickness (level set, mixable, shape) | 2 × average element size |
| AM Overhang | build +Z, 45°, keep 27°–60° (density-based) |
| Retained Threshold (result) | 0.5 (0.01–0.99) |
| Stress clustering | p-norm clusters. Earlier releases used Holmberg's fixed $1/\sqrt[p]{n_S}$ factor; the current option uses Le's adaptive $c_i$ (p. 112–113) |

**Ansys Discovery** topology settings (defaults, member size, smoothing) were **NOT FOUND**: no Discovery help page was read. Verify on screen on the day.

### Day-of choices [Y]

1. Volume or mass target: start at the Percent to Retain the brief implies, then sweep (30/40/50).
2. Mesh at least 4 elements across the thinnest expected member. Keep min member size at the 2.5 × element default unless the AM process needs more.
3. Exclude the load and support faces.
4. For stress, use Convergence Accuracy 0.05 % and a stiffness constraint alongside (the level-set note on p. 118 warns that a void design minimises stress).
5. Validate every design in a downstream static system.

---

## Open educational codes and tutorials

| Code / resource | URL | Good for | Checked this session |
|---|---|---|---|
| top88 (plus top71/top82/top110) | https://www.topopt.mek.dtu.dk/apps-and-software/efficient-topology-optimization-in-matlab | reference implementation for our port; validation numbers in §1 | page 200, `.m` links present |
| top99neo / top3D125 | https://www.topopt.mek.dtu.dk/apps-and-software/new-99-line-topology-optimization-code-written-in-matlab | tanh projection, η*, continuation, Neumann filter, 3D | page 200, `.m` links and example calls read |
| DTU Python TO codes | https://www.topopt.mek.dtu.dk/apps-and-software/topology-optimization-codes-written-in-python | Python counterpart of top88 (numpy/scipy, CVXOPT variant) | search result only, not opened |
| AMfilter.m (Langelaar 2017 ESM) | https://doi.org/10.1007/s00158-016-1522-2 | 2D overhang filter for 88-line code, top88 integration recipe | stated in paper; ESM not downloaded |
| top3d (Liu & Tovar 2014) | https://top3d.app/ | 3D SIMP MATLAB code and tutorials | page 200 (title "top3d"); content not read |
| 146-line 3D stress sensitivity (Deng, Vulimiri, To) | https://arxiv.org/abs/2104.01210 | p-norm stress adjoint with finite-difference check, q = 0.5 relaxation | read (§4d) |
| pymoto eigenfrequency example | https://pymoto.readthedocs.io/en/stable/auto_examples/topology_optimization/ex_eigenfrequency.html | Python eigenfrequency TO with Du–Olhoff-type two-range mass | read via WebFetch |
| GCMMA-MMA-Python (Deetman) | https://github.com/arjendeetman/GCMMA-MMA-Python | MMA/GCMMA in Python, which our `mma_*` routines follow | page 200 |
| topoptlab (Hiemer) | https://pypi.org/project/topoptlab/ | pip package collecting published MATLAB scripts in Python (SIMP, RAMP, OC, MMA) | search result only |
| PolyTop (Talischi, Paulino, Pereira, Menezes 2012, SMO 45:329–357) | https://collaborate.princeton.edu/en/publications/polytop-a-matlab-implementation-of-a-general-topology-optimizatio/ | polygonal meshes, modular TO | record only; download page not verified |

- scikit-topopt: **NOT FOUND** (not located).
- github.com/williamhunter/topopt returned 404.
- The "MATLAB TopOpt DTU app" page was **not found** on the DTU apps listing I fetched.

---

## Our-code to-do list implied by this pack [Y]

1. Add the tanh projection with η and the top99neo η* Newton step (eq. 1, 9, 17, 18), with continuation on p and β.
2. Add a Neumann (symmetric-padding) filter option, and compare against the 3D figures in §2.
3. Add a robust option (eroded/dilated, max{J_e, J_d}, volume on dilated). Size rmin with Qian–Sigmund (29).
4. Expose the AM filter defaults and switch them to Langelaar's ε = 1e-4, P = 40 (or document why 80/1e-3). Use move 0.05 with OC.
5. Stress: Holmberg P-norm with ρ^{1/2} relaxation, p = 8, clusters. The adjoint is in §4a.
6. Regression tests against the top88 compliance table in §1.
