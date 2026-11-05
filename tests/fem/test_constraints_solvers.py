"""FEM core: multi-point constraints, load cases, solvers, diagnostics, results and the assembly cache.

Hand calculations (derived in the tests):
- Rigid offset link: a horizontal force P at height e above a cantilever tip equals P plus a moment −eP
  at the tip; Euler-Bernoulli tip response u = PL/EA, θ = ML/EI, v = ML²/2EI (Timoshenko & Gere 1961)
- Inclined roller (normal at 30°) on a triangular truss: moments about the pin give R = P/(2 sin 30°)
- MPC elimination u = T q + g: Cook et al. 2002, Ch. 9
"""
import json
import math

import numpy as np
import scipy.sparse as sp

from aerokit.fem import Model, SingularMatrixError, SolverOptions
from aerokit.fem import solvers
from aerokit.fem.elements.line import Bar, Frame2D
from aerokit.fem.elements.plane import Q4, D_isotropic
from aerokit.fem.mesh import mesh2d
from aerokit.verification import check, check_true, expect_error

E, A, I, L = 200e9, 4e-3, 8e-6, 2.0


def _plate(nx=12, ny=6):
    X, conn, edges = mesh2d.rectangle(2.0, 1.0, nx, ny, "Q4")
    m = Model(X, 2)
    for c in conn:
        m.add(Q4(c, D_isotropic(70e9, 0.3, "stress"), t=0.01))
    for n in mesh2d.edge_nodes(edges["left"]):
        m.fix(n, [0, 1])
    return m, X, edges


# ---------------- multi-point constraints ----------------
def test_tie_equals_merged_node():
    def loads(m, mid):
        m.load(mid, 1, -5e3)
        m.load(mid, 2, 2e3)
        m.load(2, 0, 1e3)
    merged = Model([[0, 0], [L, 0], [2 * L, 0]], 3)
    merged.add(Frame2D(0, 1, E, A, I))
    merged.add(Frame2D(1, 2, E, A, I))
    tied = Model([[0, 0], [L, 0], [2 * L, 0], [L, 0]], 3)
    tied.add(Frame2D(0, 1, E, A, I))
    tied.add(Frame2D(3, 2, E, A, I))
    tied.tie(1, 3, [0, 1, 2])
    for m in (merged, tied):
        m.fix(0, [0, 1, 2])
        m.fix(2, 1)
        loads(m, 1)
    a, b = merged.static(), tied.static()
    ua, ub = a.u.reshape(-1, 3), b.u.reshape(-1, 3)
    scale = np.abs(ua).max()
    check("tie: node displacements equal the merged-node model", np.abs(ub[:3] - ua).max(), 0.0, atol=1e-12 * scale,
          source="Cook et al. 2002 Ch. 9: u_b = u_a eliminated exactly")
    check("tie: the tied node moves with its master", np.abs(ub[3] - ub[1]).max(), 0.0, atol=1e-15 * scale)
    check("tie: support reactions equal", np.abs(b.reaction[[0, 1, 2, 7]] - a.reaction[[0, 1, 2, 7]]).max(), 0.0,
          atol=1e-9 * np.abs(a.reaction).max())


def test_rigid_link_2d_offset():
    P, e = 3e3, 0.25
    m = Model([[0.0, 0.0], [L, 0.0], [L, e]], 3)
    m.add(Frame2D(0, 1, E, A, I))
    m.fix(0, [0, 1, 2])
    m.rigid_link_2d(1, 2)
    m.load(2, 0, P)
    u = m.static().u.reshape(-1, 3)
    M = -e * P                                   # moment of P (at height e) about the tip
    theta = M * L / (E * I)
    check("rigid link: master u = PL/EA", u[1, 0], P * L / (E * A), rtol=1e-12,
          source="hand calculation: offset force = P + moment −eP at the tip")
    check("rigid link: master θ = ML/EI with M = −eP", u[1, 2], theta, rtol=1e-12,
          source="Timoshenko & Gere 1961: cantilever under tip moment")
    check("rigid link: master v = ML²/2EI", u[1, 1], M * L ** 2 / (2 * E * I), rtol=1e-12)
    check("rigid link: slave u = u_m − e θ_m", u[2, 0], P * L / (E * A) - e * theta, rtol=1e-12,
          source="rigid-body kinematics u_s = u_m − (y_s − y_m) θ")
    check("rigid link: slave v = v_m (dx = 0)", u[2, 1], u[1, 1], rtol=1e-12)
    check("rigid link: slave θ = θ_m", u[2, 2], u[1, 2], rtol=1e-12)
    expect_error("rigid_link_2d in a truss (ndof 2) raises", Model([[0, 0], [1, 0]], 2).rigid_link_2d, 0, 1,
                 error=ValueError)


def test_inclined_roller_reactions():
    P, h, th = 1e4, 1.5, math.radians(30.0)
    m = Model([[0.0, 0.0], [L, 0.0], [L / 2, h]], 2)
    for i, j in ((0, 1), (1, 2), (0, 2)):
        m.add(Bar(i, j, E, A))
    m.fix(0, [0, 1])
    m.add_mpc({(1, 0): math.cos(th), (1, 1): math.sin(th)})          # roller: n·u = 0, n at 30°
    m.load(2, 1, -P)
    r = m.static()
    R = P / (2 * math.sin(th))
    check("inclined roller: reaction along the normal R = P/(2 sin 30°) (x component)", r.reaction[2], R * math.cos(th),
          rtol=1e-10, source="statics: moments about the pin")
    check("inclined roller: reaction y component", r.reaction[3], R * math.sin(th), rtol=1e-10)
    check("inclined roller: pin reaction Ax = −R cos 30°", r.reaction[0], -R * math.cos(th), rtol=1e-10)
    check("inclined roller: pin reaction Ay = P − R sin 30°", r.reaction[1], P - R * math.sin(th), rtol=1e-10)
    check("inclined roller: constraint n·u = 0 satisfied", math.cos(th) * r.u[2] + math.sin(th) * r.u[3], 0.0,
          atol=1e-15 * np.abs(r.u).max())
    check_true("inclined roller: the node slides along the incline", abs(r.u[2]) > 1e-9 * abs(r.u).max())


def test_mpc_errors():
    m = Model([[0, 0], [1, 0], [2, 0]], 2)
    m.add(Bar(0, 1, E, A))
    m.add(Bar(1, 2, E, A))
    m.fix(0, [0, 1])
    m.add_mpc([(1, 0, 1.0), (2, 0, -1.0)])
    m.add_mpc([(2, 0, 1.0), (1, 0, -1.0)])
    m.fix(1, 1)
    m.fix(2, 1)
    m.load(2, 0, 1.0)
    expect_error("circular MPC chain raises ValueError", m.static, error=ValueError)
    try:
        m.static()
        message = ""
    except ValueError as exc:
        message = str(exc)
    check_true("circular MPC message lists the chain", "circular" in message and "node 1 dof 0" in message, message)
    m2 = Model([[0, 0], [1, 0]], 2)
    m2.add(Bar(0, 1, E, A))
    m2.add_mpc([(1, 1, 1.0), (1, 0, -0.5)])
    expect_error("fixing an MPC-dependent DOF raises", m2.fix, 1, 1, error=ValueError)
    m2.fix(0, 0)
    expect_error("an MPC on a prescribed DOF raises", m2.add_mpc, [(0, 0, 1.0), (1, 0, 1.0)], error=ValueError)
    expect_error("zero dependent coefficient raises", m2.add_mpc, [(0, 1, 0.0), (1, 0, 1.0)], error=ValueError)


# ---------------- load cases and solvers ----------------
def test_multiple_load_cases_and_cg():
    m, X, edges = _plate()
    F1 = mesh2d.edge_load(X, edges["right"], traction=lambda x, y: (1e6, 0.0), t=0.01)
    F2 = mesh2d.edge_load(X, edges["right"], traction=lambda x, y: (0.0, -2e5), t=0.01)
    F3 = mesh2d.edge_load(X, edges["upper"], pressure=1e5, t=0.01)
    many = m.static(F=np.column_stack([F1, F2, F3]))
    for k, F in enumerate((F1, F2, F3)):
        one = m.static(F=F)
        check(f"load case {k + 1}: F matrix column equals a separate solve", np.abs(many.u[:, k] - one.u).max(), 0.0,
              atol=1e-12 * np.abs(one.u).max(), source="one factorisation, several right-hand sides")
        check(f"load case {k + 1}: strain energy per case", many.energy[k], one.energy, rtol=1e-10)
    direct = m.static(F=F2)
    for pre in ("jacobi", "ilu"):
        cg = m.static(F=F2, options=SolverOptions(method="cg", preconditioner=pre, rtol=1e-12))
        check(f"PCG ({pre}) equals the direct solution", np.abs(cg.u - direct.u).max() / np.abs(direct.u).max(), 0.0,
              atol=1e-8, source="Saad 2003 Alg. 9.1")
        check_true(f"PCG ({pre}) reports its iterations", cg.solver is not None and cg.solver.iterations > 0
                   and cg.solver.method == "cg")
    check_true("direct solver reports method 'direct'", direct.solver is not None and direct.solver.method == "direct")


def test_singular_model_diagnostics():
    m = Model([[0, 0], [1, 0], [2, 0], [3, 3]], 2)       # node 3 is not connected
    m.add(Bar(0, 1, E, A))
    m.add(Bar(1, 2, E, A))                               # collinear bars: no lateral stiffness at nodes 1, 2
    m.fix(0, [0, 1])
    m.load(2, 0, 1e3)
    expect_error("mechanism raises SingularMatrixError", m.static, error=SingularMatrixError)
    try:
        m.static()
        message = ""
    except SingularMatrixError as exc:
        message = str(exc)
    for name in ("node 1 dof 1", "node 2 dof 1", "node 3 dof 0", "node 3 dof 1"):
        check_true(f"singular message names '{name}'", name in message, message)
    check_true("SingularMatrixError is a ValueError", issubclass(SingularMatrixError, ValueError))


def test_condition_estimate():
    m, _, _ = _plate(4, 2)
    est = m.condition_estimate()
    K = m.K().toarray()
    free = np.setdiff1d(np.arange(m.n_dof), [m.dof(n, d) for n in range(m.n_node) if m.X[n, 0] == 0 for d in (0, 1)])
    exact = np.linalg.cond(K[np.ix_(free, free)], 1)
    check_true("condition_estimate within a factor 3 of numpy.linalg.cond(K, 1)", exact / 3 <= est <= 3 * exact,
               f"estimate {est:.4e}, exact {exact:.4e}", source="Higham & Tisseur 2000 block 1-norm estimator")
    check_true("condition estimate never exceeds the exact 1-norm condition (lower bound)", est <= exact * (1 + 1e-9),
               f"{est:.6e} vs {exact:.6e}")


# ---------------- results ----------------
def test_results_mapping_and_json():
    m, X, edges = _plate(4, 2)
    m.F += mesh2d.edge_load(X, edges["right"], traction=lambda x, y: (1e6, 0.0), t=0.01)
    r = m.static()
    check_true("StaticResult: r['u'] is r.u", r["u"] is r.u)
    check_true("StaticResult: keys", list(r) == ["u", "reaction", "energy", "residual", "solver"], str(list(r)))
    check_true("StaticResult: dict(r) works", dict(r)["energy"] == r.energy)
    expect_error("unknown key raises KeyError", r.__getitem__, "nope", error=KeyError)
    d = r.to_dict()
    text = json.dumps(d)
    check_true("StaticResult.to_dict() is JSON serialisable (nested SolverInfo included)",
               isinstance(text, str) and isinstance(d["solver"], dict) and d["solver"]["method"] == "direct")
    for e in m.elements:
        e.rho = 2700.0
    mr = m.modal(3)
    check_true("ModalResult: mapping access and JSON", mr["f"] is mr.f and isinstance(json.dumps(mr.to_dict()), str))


# ---------------- eigen solvers ----------------
def test_sparse_and_dense_eigen_agree():
    # Q4 plate (well-conditioned pencil; a slender Frame2D beam has κ(K)κ(M) ≈ 1e12 and the dense
    # LAPACK lowest eigenvalue is then only good to ~4e-8, measured)
    m, _, _ = _plate(10, 5)
    for e in m.elements:
        e.rho = 2700.0
    K, M = m.K(), m.M()
    free = np.setdiff1d(np.arange(m.n_dof), [m.dof(n, d) for n in range(m.n_node) if m.X[n, 0] == 0 for d in (0, 1)])
    Kr, Mr = K[free][:, free], M[free][:, free]
    for which, (Aop, Bop) in (("SM", (Kr, Mr)), ("LA", (Mr, Kr))):
        wd, Vd = solvers.generalized_eigh(Aop, Bop, 6, which=which)
        ws, Vs = solvers.generalized_eigh(sp.csr_matrix(Aop), sp.csr_matrix(Bop), 6, which=which, dense_limit=0)
        check(f"eigen {which}: ARPACK eigenvalues = LAPACK", np.abs(ws / wd - 1).max(), 0.0, atol=1e-9,
              source="scipy eigsh (shift-invert / LA) vs eigh")
        overlap = np.abs(np.einsum("ij,ik,kj->j", Vs, Bop.toarray(), Vd))
        check(f"eigen {which}: B-orthonormal eigenvectors agree up to sign", np.abs(overlap - 1).max(), 0.0, atol=1e-7)


# ---------------- assembly cache ----------------
def _fresh_K(X, conn, props):
    m = Model(X, 2)
    for c, (Ei, t) in zip(conn, props, strict=True):
        m.add(Q4(c, D_isotropic(Ei, 0.3, "stress"), t=t))
    return m.K()


def test_assembly_cache_is_never_stale():
    X, conn, _ = mesh2d.rectangle(1.0, 1.0, 4, 4, "Q4")
    m = Model(X, 2)
    for c in conn:
        m.add(Q4(c, D_isotropic(70e9, 0.3, "stress"), t=0.01))
    K0 = m.K()
    props = [(70e9, 0.01)] * len(conn)
    check("cache: first assembly equals a fresh model", abs(K0 - _fresh_K(X, conn, props)).max(), 0.0, atol=0.0)
    # modify one element's property in place
    m.elements[5].t = 0.02
    props[5] = (70e9, 0.02)
    K1 = m.K()
    check("cache: K after changing an element thickness equals a fresh model",
          abs(K1 - _fresh_K(X, conn, props)).max() / abs(K1).max(), 0.0, atol=1e-15)
    check_true("cache: the modification is visible", abs(K1 - K0).max() > 0)
    # replace the element list by a different connectivity of the same length (T3 pairs swapped diagonal)
    rng = np.random.default_rng(1)
    perm = rng.permutation(len(conn))
    conn2 = [[c[1], c[2], c[3], c[0]] for c in (conn[i] for i in perm)]     # rotated node order, shuffled
    props2 = [(70e9 * (1 + 0.1 * i), 0.01) for i in range(len(conn2))]
    m.elements = [Q4(c, D_isotropic(Ei, 0.3, "stress"), t=t) for c, (Ei, t) in zip(conn2, props2, strict=True)]
    K2 = m.K()
    check("cache: K after replacing model.elements equals a fresh model",
          abs(K2 - _fresh_K(X, conn2, props2)).max() / abs(K2).max(), 0.0, atol=1e-15)
    m.batch_assembly = False
    check("cache: element loop equals batched assembly", abs(m.K() - K2).max() / abs(K2).max(), 0.0, atol=1e-14)
