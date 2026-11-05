"""References specific to aerokit.cad (owned by that sub-package)."""
from aerokit.references import Reference

REFERENCES: tuple[Reference, ...] = (
    # --- polyhedral mass properties -----------------------------------------------------------
    Reference("mirtich_1996", "B. Mirtich", 1996, "Fast and accurate computation of polyhedral mass properties",
              "Journal of Graphics Tools 1(2):31-50", doi="10.1080/10867651.1996.10487458",
              note="divergence-theorem reduction of volume integrals to face integrals"),
    Reference("eberly_2002", "D. Eberly", 2002, "Polyhedral Mass Properties (Revisited)",
              "Geometric Tools technical note",
              url="https://www.geometrictools.com/Documentation/PolyhedralMassProperties.pdf",
              note="vectorised subexpressions of the mass-property integrals (section 5 pseudocode)"),
    # --- inside/outside, solid angle ----------------------------------------------------------
    Reference("vanoosterom_strackee_1983", "A. van Oosterom, J. Strackee", 1983, "The solid angle of a plane triangle",
              "IEEE Transactions on Biomedical Engineering BME-30(2):125-126", doi="10.1109/TBME.1983.325207",
              note="closed-form tan(Omega/2) of the solid angle subtended by a triangle"),
    Reference("jacobson_kavan_2013", "A. Jacobson, L. Kavan, O. Sorkine-Hornung", 2013,
              "Robust inside-outside segmentation using generalized winding numbers",
              "ACM Transactions on Graphics 32(4) (Proc. SIGGRAPH 2013)", doi="10.1145/2461912.2461916",
              note="generalized winding number w(p) = sum of solid angles / 4 pi"),
    Reference("hormann_agathos_2001", "K. Hormann, A. Agathos", 2001,
              "The point in polygon problem for arbitrary polygons", "Computational Geometry 20(3):131-144",
              doi="10.1016/S0925-7721(01)00012-8", note="even-odd (crossing) rule"),
    # --- mesh processing, rasterisation, polygon moments --------------------------------------
    Reference("botsch_kobbelt_2010", "M. Botsch, L. Kobbelt, M. Pauly, P. Alliez, B. Lévy", 2010,
              "Polygon Mesh Processing", "A K Peters, Natick MA",
              note="half-edge topology, manifoldness, consistent orientation, mesh repair"),
    Reference("pineda_1988", "J. Pineda", 1988, "A parallel algorithm for polygon rasterization",
              "Computer Graphics (Proc. SIGGRAPH '88) 22(4):17-20",
              note="edge-function inside test for triangle rasterisation"),
    Reference("steger_1996", "C. Steger", 1996, "On the calculation of arbitrary moments of polygons",
              "Technical Report FGBV-96-05, Technische Universität München",
              note="closed-form polygon area moments via Green's theorem"),
    Reference("wadell_1935", "H. Wadell", 1935, "Volume, shape, and roundness of quartz particles",
              "Journal of Geology 43(3):250-280", doi="10.1086/624298", note="sphericity definition"),
    # --- file formats -------------------------------------------------------------------------
    Reference("3dsystems_1989", "3D Systems, Inc.", 1989, "StereoLithography Interface Specification",
              "3D Systems, Inc.",
              note="STL: ASCII 'solid' grammar; binary 80-byte header + uint32 count + 50 bytes per facet"),
    Reference("turk_1994", "G. Turk", 1994, "The PLY polygon file format", "Stanford University",
              note="PLY header grammar, ASCII and binary (little/big-endian) bodies"),
    Reference("autodesk_2011", "Autodesk, Inc.", 2011, "AutoCAD 2012 DXF Reference", "Autodesk, Inc., San Rafael CA",
              note="group-code/value pairs; LINE, LWPOLYLINE, POLYLINE, CIRCLE, ARC, SPLINE entities; "
                   "bulge = tan(theta/4)"),
)
