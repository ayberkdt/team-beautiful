"""Structural and design optimization.

Modules (each is imported separately; this package loads none of them by itself):

sizing
    Truss/frame cross-section sizing: analytic sensitivities (direct and adjoint), fully stressed
    design, optimality criterion, SLSQP, KKT audit and classic benchmark problems.
topology
    SIMP compliance topology optimization (top88-style, OC and MMA, density/sensitivity filters,
    Heaviside projection, 2-D and 3-D grids).
design
    Design-level tools: constraint diagram optimum, design carpet, wing-box and tube minimum-mass
    sizing, parametric scans, Pareto sorting, sensitivities, Monte Carlo and FORM reliability.
laminate
    Composite laminate stacking-sequence optimization and lamination parameters.
"""
