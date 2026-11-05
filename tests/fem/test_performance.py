"""Vectorized (batch) assembly: must give exactly the same K as the element loop, and be faster."""
import math
import time

import numpy as np

from aerokit.fem import Model
from aerokit.fem.mesh import mesh2d
from aerokit.fem.mesh import mesh3d
from aerokit.fem.elements.plane import T3, Q4, QM6, Q8, D_isotropic, D_orthotropic
from aerokit.fem.elements.solid import T4, T10, H8, D_isotropic3d
from aerokit.verification import check, check_true


def _K_both_paths(m):
    m.batch_assembly = True
    A = m.K().toarray()
    m.batch_assembly = False
    B = m.K().toarray()
    m.batch_assembly = True
    return A, B


def _distorted_mesh(kind, n=6):
    X, conn, _ = mesh2d.mapped_mesh(lambda s, t: (s + 0.15 * math.sin(3 * t), t + 0.1 * math.sin(2 * s)),
                                    n, n, kind)
    return X, conn


def test_batch_2d_equality():
    cases = [("T3 stress", T3, "stress", D_isotropic(70e9, 0.3, "stress")),
                ("Q4 stress", Q4, "stress", D_isotropic(70e9, 0.3, "stress")),
                ("Q8 strain", Q8, "strain", D_isotropic(70e9, 0.3, "strain")),
                ("Q4 orthotropic", Q4, "stress", D_orthotropic(140e9, 10e9, 0.3, 5e9, 30.0))]
    for name, class_, formulation, D in cases:
        X, conn = _distorted_mesh("T3" if class_ is T3 else ("Q8" if class_ is Q8 else "Q4"))
        m = Model(X, 2)
        for c in conn:
            m.add(class_(c, D, format=formulation, t=0.01))
        A, B = _K_both_paths(m)
        check(f"batch K = loop K ({name}, distorted mesh)", np.abs(A - B).max() / np.abs(B).max(), 0.0, atol=1e-13)
    # axisymmetric (shifted so that x ≥ 0.1)
    for name, class_, kind in (("Q8 axisymmetric", Q8, "Q8"), ("T3 axisymmetric", T3, "T3")):
        X, conn = _distorted_mesh(kind)
        X[:, 0] += 0.3
        m = Model(X, 2)
        for c in conn:
            m.add(class_(c, D_isotropic(70e9, 0.3, "axisymmetric"), format="axisymmetric"))
        A, B = _K_both_paths(m)
        check(f"batch K = loop K ({name})", np.abs(A - B).max() / np.abs(B).max(), 0.0, atol=1e-13)


def test_batch_mixed_model():
    """Different materials and QM6 (which has no batch path) in the same model: grouping must be correct."""
    X, conn = _distorted_mesh("Q4", n=8)
    m = Model(X, 2)
    D1, D2 = D_isotropic(70e9, 0.3, "stress"), D_isotropic(200e9, 0.28, "stress")
    for i, c in enumerate(conn):
        if i % 3 == 0:
            m.add(QM6(c, D1))
        elif i % 3 == 1:
            m.add(Q4(c, D2, t=0.02))
        else:
            m.add(Q4(c, D1, t=0.01))
    A, B = _K_both_paths(m)
    check("batch K = loop K (mixed materials + QM6)", np.abs(A - B).max() / np.abs(B).max(), 0.0, atol=1e-13)


def test_batch_3d_equality_and_speed():
    D = D_isotropic3d(70e9, 0.3)
    rng = np.random.default_rng(3)
    for kind, class_ in (("T4", T4), ("T10", T10), ("H8", H8)):
        X, el = mesh3d.box(1.0, 0.5, 0.4, 4, 3, 2, kind)
        inner = [i for i, p in enumerate(X) if np.all((p > 1e-9) & (p < np.array([1, 0.5, 0.4]) - 1e-9))]
        if kind != "T10":
            X[inner] += rng.uniform(-0.02, 0.02, (len(inner), 3))
        m = Model(X, 3)
        for e in el:
            m.add(class_(e, D))
        A, B = _K_both_paths(m)
        check(f"batch K = loop K ({kind})", np.abs(A - B).max() / np.abs(B).max(), 0.0, atol=1e-13)
    X, el = mesh3d.box(1.0, 0.2, 0.2, 20, 4, 4, "T10")
    m = Model(X, 3)
    for e in el:
        m.add(T10(e, D))
    t0 = time.perf_counter()
    m.batch_assembly = False
    m.K()
    t_loop = time.perf_counter() - t0
    t0 = time.perf_counter()
    m.batch_assembly = True
    m.K()
    t_batch = time.perf_counter() - t0
    check_true(f"batch assembly at least 3× faster than the loop on {len(el)} T10 elements", t_loop / t_batch > 3,
          f"loop {t_loop:.2f} s, batch {t_batch:.2f} s, speed-up {t_loop / t_batch:.1f}×")
