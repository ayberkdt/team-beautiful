"""References for aerokit.fem dynamics and non-linear analysis.

Only bibliographic details the author was confident of are recorded; DOIs and page ranges that
could not be checked are left out. Works shared with other sub-packages (Bathe 2014, Hughes 2000,
Cook et al. 2002, Golub & Van Loan 2013) live in :mod:`aerokit.references._core`.
"""
from aerokit.references import Reference

REFERENCES: tuple[Reference, ...] = (
    # --- structural dynamics ---------------------------------------------------------------------
    Reference("newmark_1959", "N. M. Newmark", 1959, "A method of computation for structural dynamics",
              "Journal of the Engineering Mechanics Division (ASCE) 85(EM3):67-94",
              note="Newmark-beta family; average acceleration beta = 1/4, gamma = 1/2"),
    Reference("hilber_hughes_taylor_1977", "H. M. Hilber, T. J. R. Hughes, R. L. Taylor", 1977,
              "Improved numerical dissipation for time integration algorithms in structural dynamics",
              "Earthquake Engineering and Structural Dynamics 5(3):283-292",
              note="HHT-alpha method, alpha in [-1/3, 0]"),
    Reference("chopra_2012", "A. K. Chopra", 2012,
              "Dynamics of Structures: Theory and Applications to Earthquake Engineering",
              "Prentice Hall, Upper Saddle River NJ", "4th ed.",
              note="SDOF closed forms, piecewise-exact recurrence, Rayleigh damping, modal analysis"),
    Reference("clough_penzien_1993", "R. W. Clough, J. Penzien", 1993, "Dynamics of Structures",
              "McGraw-Hill, New York", "2nd ed.", note="harmonic response, hysteretic damping"),
    # --- non-linear statics and path following ---------------------------------------------------
    Reference("crisfield_1981", "M. A. Crisfield", 1981,
              "A fast incremental/iterative solution procedure that handles \"snap-through\"",
              "Computers & Structures 13(1-3):55-62",
              note="cylindrical arc-length constraint and its root-selection rule"),
    Reference("crisfield_1991", "M. A. Crisfield", 1991,
              "Non-linear Finite Element Analysis of Solids and Structures, Vol. 1: Essentials",
              "Wiley, Chichester", note="shallow two-bar truss, total-Lagrangian truss, arc-length methods"),
    Reference("riks_1979", "E. Riks", 1979, "An incremental approach to the solution of snapping and buckling problems",
              "International Journal of Solids and Structures 15(7):529-551", note="arc-length path following"),
    Reference("bazant_cedolin_1991", "Z. P. Bažant, L. Cedolin", 1991,
              "Stability of Structures: Elastic, Inelastic, Fracture and Damage Theories",
              "Oxford University Press, New York", note="von Mises truss snap-through"),
)
