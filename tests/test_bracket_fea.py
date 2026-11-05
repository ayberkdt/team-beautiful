"""aerokit.bracket.voxfem: element matrices, patch test, cantilever benchmark, solver agreement."""
import numpy as np
import pytest

from aerokit.bracket import voxfem as vf
from aerokit.optimization.topology import ke_h8


def _block(shape, h=1e-3):
    return vf.VoxelMesh(np.ones(shape, bool), h)


def test_h8_matches_topology_ke():
    K, R = vf.ke_unit(0.3, "H8")
    assert R is None
    assert np.allclose(K, ke_h8(0.3), atol=1e-14)


@pytest.mark.parametrize("element", ["H8", "H8IM"])
def test_element_symmetric_six_rigid_modes(element):
    K, _ = vf.ke_unit(0.3, element)
    assert np.allclose(K, K.T)
    w = np.linalg.eigvalsh(K)
    assert np.sum(np.abs(w) < 1e-10 * w.max()) == 6
    assert w.min() > -1e-10


@pytest.mark.parametrize("element", ["H8", "H8IM"])
def test_patch_uniform_tension_exact(element):
    h, E, nu, sig = 1e-3, 200e9, 0.3, 100e6
    m = _block((4, 3, 5), h)
    L = 5 * h
    top = m.nodes_where(lambda X: np.isclose(X[:, 2], L))
    bot = m.nodes_where(lambda X: np.isclose(X[:, 2], 0))
    A = np.zeros(m.nn)
    for e in np.flatnonzero(m.ijk[:, 2] == 4):
        for n in m.conn[e]:
            if np.isclose(m.X[n, 2], L):
                A[n] += h * h / 4
    F = np.zeros(m.ndof)
    F[3 * np.arange(m.nn) + 2] = sig * A
    o = m.nodes_where(lambda X: np.all(np.isclose(X, 0), axis=1))[0]
    o2 = m.nodes_where(lambda X: np.isclose(X[:, 0], 4 * h) & np.isclose(X[:, 1], 0) & np.isclose(X[:, 2], 0))[0]
    fixed = np.r_[3 * bot + 2, 3 * o, 3 * o + 1, 3 * o2 + 1]
    r = vf.static(m, E, nu, F, fixed, element=element, method="direct")[0]
    assert np.allclose(r.stress_node[:, 2], sig, rtol=1e-9)
    assert np.allclose(r.stress_node[:, :2], 0, atol=1e-6 * sig)
    assert np.allclose(r.U[3 * top + 2], sig * L / E, rtol=1e-9)
    assert np.allclose(r.reaction[2], -sig * 4 * 3 * h * h, rtol=1e-9)


def _cantilever(element, n):
    E, nu, P = 200e9, 0.3, 1000.0
    Lx, b, t = 100e-3, 10e-3, 10e-3
    h = t / n
    m = _block((round(Lx / h), n, n), h)
    fix = m.nodes_where(lambda X: np.isclose(X[:, 0], 0))
    fixed = (3 * fix[:, None] + np.arange(3)).ravel()
    tip = m.nodes_where(lambda X: np.isclose(X[:, 0], Lx))
    F = np.zeros(m.ndof)
    F[3 * tip + 2] = -P / len(tip)
    r = vf.static(m, E, nu, F, fixed, element=element, method="direct")[0]
    I = b * t ** 3 / 12
    G = E / 2 / (1 + nu)
    timo = P * Lx ** 3 / (3 * E * I) + P * Lx / (5 / 6 * G * b * t)       # Timoshenko beam, kappa = 5/6
    return -r.U[3 * tip + 2].mean() / timo


def test_cantilever_h8im_within_two_percent_even_one_voxel_thick():
    # [K] 2026-11-04: 0.9855 (n=1), 0.9867 (n=2); the clamped root (Poisson restrained) stiffens by ~1 %
    for n in (1, 2):
        assert 0.97 < _cantilever("H8IM", n) < 1.0


def test_cantilever_h8_locks_and_converges():
    # [K]: 0.643 (n=1), 0.869 (n=2), 0.957 (n=4) - shear locking of the plain trilinear brick
    r1, r2 = _cantilever("H8", 1), _cantilever("H8", 2)
    assert r1 < 0.7 < r2 < 0.9


def test_solvers_agree():
    m = _block((12, 4, 4), 1e-3)
    KE, _ = vf.ke_unit(0.3, "H8IM")
    K = m.stiffness(KE, 200e9 * m.h)
    fix = m.nodes_where(lambda X: np.isclose(X[:, 0], 0))
    fixed = (3 * fix[:, None] + np.arange(3)).ravel()
    F = np.zeros(m.ndof)
    tip = m.nodes_where(lambda X: np.isclose(X[:, 0], 12e-3))
    F[3 * tip + 1] = 10.0
    Ud, _ = vf.solve(K, F, fixed, m.X, method="direct")
    Uc, info = vf.solve(K, F, fixed, m.X, method="cg", tol=1e-12)
    assert np.allclose(Ud, Uc, rtol=1e-6, atol=1e-12 * np.abs(Ud).max())
    if vf.pardiso_module():
        Up, _ = vf.solve(K, F, fixed, m.X, method="pardiso")
        assert np.allclose(Ud, Up, rtol=1e-8, atol=1e-14)


def test_stiffness_scales_with_E_and_h():
    m1, m2 = _block((3, 2, 2), 1e-3), _block((3, 2, 2), 2e-3)
    KE, _ = vf.ke_unit(0.3, "H8")
    K1, K2 = m1.stiffness(KE, 1e9 * m1.h), m2.stiffness(KE, 1e9 * m2.h)
    assert np.allclose(K2.toarray(), 2 * K1.toarray())


def test_von_mises_uniaxial_and_shear():
    assert np.isclose(vf.von_mises(np.array([5.0, 0, 0, 0, 0, 0])), 5.0)
    assert np.isclose(vf.von_mises(np.array([0, 0, 0, 0, 0, 2.0])), 2 * np.sqrt(3))


@pytest.mark.parametrize("element", ["H8", "H8IM"])
def test_thermal_free_expansion_and_clamped_bar(element):
    E, nu, a, dT, h = 200e9, 0.3, 1.2e-5, 278.0, 1e-3
    m = _block((6, 3, 4), h)
    o = m.nodes_where(lambda X: np.all(np.isclose(X, 0), axis=1))[0]
    ox = m.nodes_where(lambda X: np.isclose(X[:, 0], 6 * h) & np.isclose(X[:, 1], 0) & np.isclose(X[:, 2], 0))[0]
    oy = m.nodes_where(lambda X: np.isclose(X[:, 0], 0) & np.isclose(X[:, 1], 3 * h) & np.isclose(X[:, 2], 0))[0]
    fixed = np.r_[3 * o, 3 * o + 1, 3 * o + 2, 3 * ox + 1, 3 * ox + 2, 3 * oy + 2]
    r = vf.static(m, E, nu, np.zeros(m.ndof), fixed, element=element, thermal_strain=a * dT, method="direct")[0]
    assert np.abs(r.stress_node).max() < 1e-3                      # free expansion: no stress
    assert r.U[3 * ox] == pytest.approx(a * dT * 6 * h, rel=1e-9)
    m = _block((40, 2, 2), h)
    ends = m.nodes_where(lambda X: np.isclose(X[:, 0], 0) | np.isclose(X[:, 0], 40 * h))
    r = vf.static(m, E, nu, np.zeros(m.ndof), (3 * ends[:, None] + np.arange(3)).ravel(), element=element,
                  thermal_strain=a * dT, method="direct")[0]
    mid = np.isclose(m.X[:, 0], 20 * h)
    assert r.stress_node[mid, 0].mean() / (-E * a * dT) == pytest.approx(1.0, abs=0.03)   # [K] 1.024 / 1.021
