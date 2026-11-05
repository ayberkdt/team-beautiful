"""aerokit.bracket.stress3d: gradient of the clustered P-norms (with projection) and the L-beam set-up."""
import numpy as np
import pytest

from aerokit.bracket import stress3d as s3
from aerokit.bracket import topo3d as t3
from aerokit.bracket import voxfem as vf


@pytest.mark.parametrize("projection", [False, True])
def test_response_gradient_matches_finite_differences(projection):
    h = 1e-3
    m = vf.VoxelMesh(np.ones((8, 3, 3), bool), h)
    fix = m.nodes_where(lambda X: np.isclose(X[:, 0], 0))
    fixed = (3 * fix[:, None] + np.arange(3)).ravel()
    tip = m.nodes_where(lambda X: np.isclose(X[:, 0], 8 * h))
    F = np.zeros((m.ndof, 2))
    F[3 * tip + 1, 0] = -50.0 / len(tip)
    F[3 * tip + 2, 1] = 30.0 / len(tip)
    keep = m.ijk[:, 0] == 7
    free = ~keep
    KE, _ = vf.ke_unit(0.3, "H8IM")
    H, Hs = t3.density_filter(m, 1.5)
    ctx = s3._Ctx(m, F, KE, H, Hs, H.T.tocsr(), keep, free, free.copy(), np.ones(m.ne),
                  t3._Solver(m, fixed, direct_limit=10**9), 1e6, 3.0, 0.5, 8.0, 1, 1e-6, "H8IM", 0.3, projection, 0.5)
    x = np.where(keep, 1.0, np.random.default_rng(2).uniform(0.3, 0.9, m.ne))
    beta = 4.0
    f0, g, df0, dg, _, _ = s3._response(ctx, x, beta)
    assert g.shape == (2,)
    idx = np.flatnonzero(free)
    e = 1e-6
    for j in range(0, idx.size, 9):
        d = np.zeros(m.ne)
        d[idx[j]] = e
        gp = s3._response(ctx, x + d, beta)
        gm = s3._response(ctx, x - d, beta)
        assert np.allclose((gp[1] - gm[1]) / (2 * e), dg[:, j], rtol=1e-4, atol=1e-6 * np.abs(dg).max())
        assert (gp[0] - gm[0]) / (2 * e) == pytest.approx(df0[j], rel=1e-5, abs=1e-9)


def test_l_beam_setup_matches_holmberg():
    mesh, F, fixed, keep, ev = s3.l_beam(20)
    assert mesh.ne == 20 * 20 - 12 * 12
    assert keep.sum() == 6 and not ev[keep].any()
    assert F.sum() == pytest.approx(-1500.0 * (0.2 / 20) / 1e-3)      # 1 mm beam → h-thick slab


def test_grey_measure():
    assert s3.grey_measure(np.array([0.0, 1.0])) == 0.0
    assert s3.grey_measure(np.full(4, 0.5)) == pytest.approx(100.0)


def test_verified_rounds_lower_the_working_limit_on_overshoot():
    h = 1e-3
    m = vf.VoxelMesh(np.ones((14, 5, 3), bool), h)
    fix = m.nodes_where(lambda X: np.isclose(X[:, 0], 0))
    fixed = (3 * fix[:, None] + np.arange(3)).ravel()
    tip = m.nodes_where(lambda X: np.isclose(X[:, 0], 14 * h))
    F = np.zeros(m.ndof)
    F[3 * tip + 1] = -60.0 / len(tip)
    keep = m.ijk[:, 0] >= 13
    ev = ~keep & (m.ijk[:, 0] >= 1)
    r = s3.optimize_stress_verified(m, F, fixed, 200e6, evaluate=ev, keep=keep, max_iter=30, rounds=1,
                                    round_iters=10, beta_start=10, beta_every=5, n_clusters=3,
                                    solver_kw={"direct_limit": 10**9})
    log = r["rounds_log"]
    assert 1 <= len(log) <= 2 and log[0]["sigma_eff_Pa"] == 200e6
    if len(log) == 2:                                    # overshoot measured → limit lowered by that factor
        assert log[1]["sigma_eff_Pa"] == pytest.approx(200e6 / log[0]["threshold_true_ratio"])
    assert r["verified"] == (log[-1]["threshold_true_ratio"] <= 1.02)
    assert r["grey_percent"] < 50.0
