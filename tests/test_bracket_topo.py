"""aerokit.bracket.topo3d: agreement with the repository's top88-family 3-D code, AM filter adjoint, passive sets."""
import numpy as np

from aerokit.bracket import topo3d as t3
from aerokit.bracket import voxfem as vf
from aerokit.optimization import topology as tp


def test_matches_topology_topopt_density_filter():
    nx, ny, nz = 16, 6, 3
    r0 = tp.topopt(tp.cantilever_3d(nx, ny, nz), 0.3, 1.5, ft=2, max_iter=15)
    m = vf.VoxelMesh(np.ones((nx, ny, nz), bool), 1.0)
    fix = m.nodes_where(lambda X: X[:, 0] == 0)
    fixed = (3 * fix[:, None] + np.arange(3)).ravel()
    tip = m.nodes_where(lambda X: (X[:, 0] == nx) & (X[:, 1] == 0))
    F = np.zeros(m.ndof)
    F[3 * tip + 1] = -1.0 / len(tip)
    r = t3.optimize(m, F, fixed, 0.3, rmin=1.5, projection=False, emin_ratio=1e-9, max_iter=15,
                    solver_kw={"direct_limit": 10**9})
    assert np.isclose(r.compliance[0], r0["compliance"][0], rtol=1e-9)
    assert np.isclose(r.compliance[-1], r0["compliance"][-1], rtol=5e-3)
    xa = tp.Grid3D(nx, ny, nz).vector(r0["xfiz"])
    assert np.abs(xa - r.xphys).max() < 0.02


def test_am_filter_adjoint_matches_finite_differences():
    m = vf.VoxelMesh(np.ones((5, 4, 6), bool), 1.0)
    am = t3.AMFilter3D(m, 2, 1)
    rng = np.random.default_rng(1)
    x = rng.uniform(0.1, 0.9, m.ne)
    w = rng.normal(size=m.ne)
    g = am.backward(x, w)
    e = 1e-6
    for i in range(0, m.ne, 11):
        d = np.zeros(m.ne)
        d[i] = e
        num = (w @ am.forward(x + d) - w @ am.forward(x - d)) / (2 * e)
        assert abs(num - g[i]) < 1e-6 * np.abs(g).max()


def test_am_filter_kills_floating_overhang():
    m = vf.VoxelMesh(np.ones((5, 5, 4), bool), 1.0)
    x = np.zeros(m.ne)
    x[(m.ijk[:, 2] == 3) & (m.ijk[:, 0] == 2) & (m.ijk[:, 1] == 2)] = 1.0     # one solid voxel in the air
    xi = t3.AMFilter3D(m, 2, 1).forward(x)
    assert xi.max() < 0.05
    assert t3.overhang_violations(m, x) == 1


def test_keep_and_volume_and_projection():
    nx, ny, nz = 14, 6, 3
    m = vf.VoxelMesh(np.ones((nx, ny, nz), bool), 1e-3)
    fix = m.nodes_where(lambda X: np.isclose(X[:, 0], 0))
    fixed = (3 * fix[:, None] + np.arange(3)).ravel()
    tip = m.nodes_where(lambda X: np.isclose(X[:, 0], nx * 1e-3))
    F = np.zeros((m.ndof, 2))
    F[3 * tip + 1, 0] = -1.0
    F[3 * tip + 2, 1] = 1.0
    keep = m.ijk[:, 0] == nx - 1
    r = t3.optimize(m, F, fixed, 0.35, keep=keep, rmin=1.5, max_iter=40, beta_every=10, beta_max=8)
    assert np.all(r.xphys[keep] == 1.0)
    assert r.xphys.mean() <= 0.35 + 1e-3
    assert r.compliance[-1] < r.compliance[0]
    assert r.gray() < 25.0
    assert t3.to_grid(m, r.xphys).shape == (nx, ny, nz)


def test_density_filter_rows_sum_and_symmetry():
    s = np.zeros((6, 6, 6), bool)
    s[1:5, 1:5, 1:5] = True
    m = vf.VoxelMesh(s, 1.0)
    H, Hs = t3.density_filter(m, 2.0)
    assert H.shape == (m.ne, m.ne)
    assert np.allclose(np.asarray(H.sum(1)).ravel(), Hs)
    assert np.allclose(H.toarray(), H.toarray().T)


def test_stress_pnorm_adjoint_gradient():
    h = 1e-3
    m = vf.VoxelMesh(np.ones((8, 3, 3), bool), h)
    fix = m.nodes_where(lambda X: np.isclose(X[:, 0], 0))
    fixed = (3 * fix[:, None] + np.arange(3)).ravel()
    tip = m.nodes_where(lambda X: np.isclose(X[:, 0], 8 * h))
    F = np.zeros((m.ndof, 2))
    F[3 * tip + 1, 0] = -50.0 / len(tip)
    F[3 * tip + 2, 1] = 30.0 / len(tip)
    ev = m.ijk[:, 0] <= 6
    xp = np.random.default_rng(0).uniform(0.3, 1.0, m.ne)
    solver = t3._Solver(m, fixed, direct_limit=10**9)
    pn, dpn, mx, _ = t3.stress_pnorm(m, xp, F, fixed, 1e6, ev, solver=solver)
    assert np.all(mx <= pn + 1e-12)                               # the P-norm bounds the maximum from above
    e = 1e-6
    for i in range(0, m.ne, 13):
        d = np.zeros(m.ne)
        d[i] = e
        num = (t3.stress_pnorm(m, xp + d, F, fixed, 1e6, ev, solver=solver)[0]
               - t3.stress_pnorm(m, xp - d, F, fixed, 1e6, ev, solver=solver)[0]) / (2 * e)
        assert np.allclose(num, dpn[:, i], rtol=1e-5, atol=1e-6 * np.abs(dpn).max())


def test_density_snapshots_every_k_iterations_end_with_the_result():
    m = vf.VoxelMesh(np.ones((12, 4, 3), bool), 1e-3)
    fix = m.nodes_where(lambda X: np.isclose(X[:, 0], 0))
    fixed = (3 * fix[:, None] + np.arange(3)).ravel()
    tip = m.nodes_where(lambda X: np.isclose(X[:, 0], 12e-3))
    F = np.zeros((m.ndof, 1))
    F[3 * tip + 1, 0] = -1.0
    r = t3.optimize(m, F, fixed, 0.4, max_iter=12, snapshot_every=5)
    its = [it for it, _ in r.snapshots]
    assert its[:2] == [5, 10] and its[-1] == r.iterations
    assert r.snapshots[-1][1].dtype == np.float16
    assert np.allclose(r.snapshots[-1][1].astype(float), r.xphys, atol=1e-3)
    assert t3.optimize(m, F, fixed, 0.4, max_iter=3).snapshots == []
