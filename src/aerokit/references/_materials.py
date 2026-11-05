"""References specific to aerokit.materials (owned by that sub-package)."""
from aerokit.references import Reference

REFERENCES: tuple[Reference, ...] = (
    # Bibliographic details as printed on PDF pages 1-2 and in the running header of
    # references/materials/ncamp-ncp-rp-2013-015/cmh17-generic-basis-8552-im7-revA.pdf.
    Reference("ncamp_2013_8552_im7", "E. Clarkson", 2013,
              "A Comparison of Equivalence Criteria and Basis Values for HEXCEL 8552 IM7 Unidirectional Tape "
              "computed from the NCAMP shared database",
              "National Center for Advanced Materials Performance (NCAMP), National Institute for Aviation "
              "Research, Wichita State University, Wichita KS",
              "NCAMP Report NCP-RP-2013-015 Rev A, Oct 31, 2013",
              note="IM7/8552 generic, pooled and qualification B-/A-basis strengths (generic values not approved "
                   "by CMH-17)"),
    Reference("uiuc_me598_2020_selection", "University of Illinois Urbana-Champaign, ME 598", 2020,
              "Materials properties and selection (lecture 4)", "Grainger College of Engineering",
              "Spring 2020 slides, after M. Ashby, Materials Selection in Mechanical Design",
              url="https://courses.grainger.illinois.edu/me598dm/sp2020/4.selection.pdf",
              note="read 2026-11-01 (PDF text): strong tie m = SLFρ/σ_YS (p. 16), stiff tie m = SFL²ρ/(δE) (p. 22), "
                   "strong cantilever m ∝ ρ/σ_YS^(2/3) (p. 26), E^(1/2)/cost (p. 31)"),
    Reference("useful_numbers_env", "Polybags Ltd (compiler)", 2017, "Useful numbers for environmental studies",
              "polybags.co.uk", "12 pages; tables cite M. F. Ashby, Materials and the Environment, 2nd ed., "
              "Butterworth-Heinemann 2013, with page numbers",
              url="https://polybags.co.uk/environmentally-friendly/useful-numbers-for-environmental-studies.pdf",
              note="read 2026-11-01 (PDF text, pp. 1-11): family embodied energy / CO2 / recycle fraction; shaping "
                   "energies (Ashby p. 133). Secondary reproduction: Ashby 2013 itself was not read"),
)
