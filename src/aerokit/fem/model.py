"""FEM core: model definition, constraints, sparse assembly and the analysis drivers.

DOF numbering
    global = node · ndof + local. Every node carries the same ``ndof``, fixed by the element
    family (2-D truss: 2, plane continuum: 2, 2-D frame: 3, Mindlin plate: 3, 3-D frame: 6,
    3-D solid: 3, heat conduction: 1).

Element protocol (see :mod:`aerokit.fem.elements`)
    ``nodes``                 node indices
    ``ndof``                  DOFs per node (must equal the model's)
    ``k(X)``                  stiffness in global axes
    ``m(X, lumped=False)``    consistent or lumped mass
    ``kg(X, ue)``             geometric stiffness from the element pre-load solution ``ue``
    ``stress(X, ue)``         result dictionary
    ``body_force(X)``         (optional) equivalent nodal loads
    ``batch_key()`` / ``k_batch(X, els)``  (optional) vectorised stiffness of identical elements

Constraints
    * single-point (Dirichlet) constraints, :meth:`Model.fix`;
    * linear multi-point constraints ``Σ cᵢ uᵢ = r`` (:meth:`Model.add_mpc`, :meth:`Model.tie`,
      :meth:`Model.rigid_link_2d`), eliminated with the master-slave transformation
      ``u = T q + g`` so that the reduced stiffness ``Tᵀ K T`` stays symmetric positive definite
      [cook_2002]_ (Ch. 9).

Performance
    Identical elements are integrated in one vectorised BLAS call, and the COO→CSR assembly
    pattern is cached: re-assembly with new element values (optimisation loops, Newton steps)
    costs one ``bincount`` instead of a sort.

Units SI; tension positive.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any

import numpy as np
import scipy.sparse as sp

from aerokit.fem import solvers
from aerokit.fem.results import BucklingResult, ModalResult, StaticResult
from aerokit.references import cite

__all__ = ["Model"]


class _Pattern:
    """Cached COO → CSR scatter map for a fixed sparsity pattern."""

    def __init__(self, rows: np.ndarray, cols: np.ndarray, n: int) -> None:
        lin = rows.astype(np.int64) * n + cols
        uniq, self.inverse = np.unique(lin, return_inverse=True)
        self.indices = (uniq % n).astype(np.int32)
        r = uniq // n
        self.indptr = np.zeros(n + 1, dtype=np.int64)
        np.add.at(self.indptr, r + 1, 1)
        np.cumsum(self.indptr, out=self.indptr)
        self.n, self.nnz = n, uniq.size

    def assemble(self, data: np.ndarray) -> sp.csr_matrix:
        values = np.bincount(self.inverse, weights=data, minlength=self.nnz)
        return sp.csr_matrix((values, self.indices, self.indptr), shape=(self.n, self.n))


class Model:
    """Finite-element model: nodes, elements, loads, constraints and analyses.

    Parameters
    ----------
    nodes : array_like, shape (n_node, 2) or (n_node, 3)
        Nodal coordinates [m].
    ndof : int
        DOFs per node.

    Examples
    --------
    >>> from aerokit.fem import Model
    >>> from aerokit.fem.elements.line import Bar
    >>> m = Model([[0.0, 0.0], [1.0, 0.0]], ndof=2)
    >>> _ = m.add(Bar(0, 1, E=70e9, A=1e-4))
    >>> m.fix(0, [0, 1]); m.fix(1, [1]); m.load(1, 0, 1e3)
    >>> round(m.static().u[2] * 1e6, 4)          # PL/EA in µm
    0.1429
    """

    batch_assembly: bool = True     # vectorise identical elements (False: plain element loop)

    def __init__(self, nodes: Any, ndof: int) -> None:
        X = np.asarray(nodes, dtype=float)
        if X.ndim != 2 or X.shape[1] not in (2, 3):
            raise ValueError("node coordinates must have shape (n, 2) or (n, 3)")
        if not np.all(np.isfinite(X)):
            raise ValueError("node coordinates must be finite")
        if int(ndof) < 1:
            raise ValueError("ndof must be a positive integer")
        self.X = X
        self.ndof = int(ndof)
        self.elements: list[Any] = []
        self.F = np.zeros(self.n_dof)
        self._fixed: dict[int, float] = {}                  # global DOF → prescribed value
        self._mpc: dict[int, tuple[dict[int, float], float]] = {}   # slave → ({master: coef}, offset)
        self._patterns: dict[Any, tuple[np.ndarray, np.ndarray, _Pattern]] = {}
        self.solver_options = solvers.SolverOptions()

    # ------------------------------------------------------------------ definition
    @property
    def n_node(self) -> int:
        """Number of nodes."""
        return int(self.X.shape[0])

    @property
    def n_dof(self) -> int:
        """Total number of DOFs."""
        return self.n_node * self.ndof

    def dof(self, node: int, local: int) -> int:
        """Global DOF index of ``(node, local)``."""
        if not 0 <= int(local) < self.ndof:
            raise ValueError(f"invalid local DOF {local} (ndof = {self.ndof})")
        if not 0 <= int(node) < self.n_node:
            raise ValueError(f"invalid node {node} (model has {self.n_node} nodes)")
        return int(node) * self.ndof + int(local)

    def dof_label(self, i: int) -> str:
        """Readable name of global DOF ``i``."""
        return f"node {i // self.ndof} dof {i % self.ndof}"

    def add(self, element: Any) -> Any:
        """Add an element and return it."""
        if element.ndof != self.ndof:
            raise ValueError(f"element needs {element.ndof} DOFs per node, model has {self.ndof}")
        if len(element.nodes) == 0 or max(element.nodes) >= self.n_node or min(element.nodes) < 0:
            raise ValueError("element is connected to a node that does not exist")
        if len(set(element.nodes)) != len(element.nodes):
            raise ValueError("element connects the same node twice")
        self.elements.append(element)
        self._patterns.clear()
        return element

    def fix(self, node: int, local_dofs: int | Iterable[int], value: float = 0.0) -> None:
        """Prescribe the given local DOFs of ``node`` (``value ≠ 0``: enforced displacement)."""
        for y in np.atleast_1d(np.asarray(local_dofs, dtype=int)):
            i = self.dof(node, int(y))
            if i in self._mpc:
                raise ValueError(f"{self.dof_label(i)} is already a dependent DOF of a constraint")
            if not np.isfinite(value):
                raise ValueError("prescribed value must be finite")
            self._fixed[i] = float(value)

    def load(self, node: int, local: int, value: float) -> None:
        """Add a nodal force/moment."""
        if not np.isfinite(value):
            raise ValueError("load must be finite")
        self.F[self.dof(node, local)] += value

    def add_mpc(self, terms: Mapping[tuple[int, int], float] | Sequence[tuple[int, int, float]],
                rhs: float = 0.0) -> int:
        """Add the linear constraint ``Σ c·u(node, local) = rhs``.

        The DOF of the **first** term becomes the dependent (eliminated) DOF; it must not be
        prescribed or already dependent. Returns its global index.
        """
        items = list(terms.items()) if isinstance(terms, Mapping) else [((n, l), c) for n, l, c in terms]
        if not items:
            raise ValueError("an MPC needs at least one term")
        (n0, l0), c0 = items[0]
        s = self.dof(n0, l0)
        if c0 == 0 or not np.isfinite(c0):
            raise ValueError("the dependent DOF coefficient must be finite and non-zero")
        if s in self._fixed or s in self._mpc:
            raise ValueError(f"{self.dof_label(s)} is already constrained")
        masters: dict[int, float] = {}
        for (n, l), c in items[1:]:
            j = self.dof(n, l)
            if j == s:
                raise ValueError("dependent DOF appears twice in the MPC")
            masters[j] = masters.get(j, 0.0) - float(c) / c0
        self._mpc[s] = (masters, float(rhs) / c0)
        return s

    def tie(self, node_a: int, node_b: int, local_dofs: Iterable[int]) -> None:
        """Make the listed DOFs of ``node_b`` equal to those of ``node_a``."""
        for y in local_dofs:
            self.add_mpc([(node_b, y, 1.0), (node_a, y, -1.0)])

    def rigid_link_2d(self, master: int, slave: int) -> None:
        """Rigid offset link in a 2-D frame model (ndof = 3: u, v, θ)."""
        if self.ndof != 3 or self.X.shape[1] != 2:
            raise ValueError("rigid_link_2d needs a 2-D model with ndof = 3")
        dx, dy = self.X[slave] - self.X[master]
        self.add_mpc([(slave, 0, 1.0), (master, 0, -1.0), (master, 2, dy)])
        self.add_mpc([(slave, 1, 1.0), (master, 1, -1.0), (master, 2, -dx)])
        self.add_mpc([(slave, 2, 1.0), (master, 2, -1.0)])

    def equivalent_dof(self, element: Any) -> np.ndarray:
        """Global DOF indices of an element (node-major)."""
        d = np.asarray(element.nodes, dtype=int)
        return (d[:, None] * self.ndof + np.arange(self.ndof)[None, :]).ravel()

    # ------------------------------------------------------------------ assembly
    def _scatter(self, key: Any, blocks: list[tuple[np.ndarray, np.ndarray]]) -> sp.csr_matrix:
        """Assemble ``(dof index (ne, m), element matrices (ne, m, m))`` blocks.

        The scatter map is cached per ``key`` and re-used only if the row/column arrays are
        identical to the cached ones (checked every call), so editing the element list can never
        pick up a stale pattern.
        """
        if not blocks:
            raise ValueError("model has no elements")
        rows = np.concatenate([np.repeat(idx, idx.shape[1], axis=1).ravel() for idx, _ in blocks])
        cols = np.concatenate([np.tile(idx, (1, idx.shape[1])).ravel() for idx, _ in blocks])
        hit = self._patterns.get(key)
        if hit is None or not (np.array_equal(hit[0], rows) and np.array_equal(hit[1], cols)):
            hit = self._patterns[key] = (rows, cols, _Pattern(rows, cols, self.n_dof))
        data = np.concatenate([ke.reshape(ke.shape[0], -1).ravel() for _, ke in blocks])
        return hit[2].assemble(data)

    def _assemble(self, func: Callable[[Any], np.ndarray], tag: str = "loop") -> sp.csr_matrix:
        blocks = []
        for e in self.elements:
            ke = np.asarray(func(e), dtype=float)
            idx = self.equivalent_dof(e)
            if ke.shape != (idx.size, idx.size):
                raise ValueError(f"{type(e).__name__}: matrix shape {ke.shape}, expected {idx.size}")
            blocks.append((idx[None, :], ke[None]))
        return self._scatter(tag, blocks)

    def K(self) -> sp.csr_matrix:
        """Global stiffness matrix (CSR)."""
        if not self.batch_assembly:
            return self._assemble(lambda e: e.k(self.X))
        groups: dict[Any, list[Any]] = {}
        single: list[Any] = []
        for e in self.elements:
            key = e.batch_key() if hasattr(e, "batch_key") else None
            (single if key is None else groups.setdefault(key, [])).append(e)
        blocks: list[tuple[np.ndarray, np.ndarray]] = []
        for els in groups.values():
            if len(els) < 4:
                single += els
                continue
            KE = type(els[0]).k_batch(self.X, els)                               # (ne, m, m)
            D_ = np.array([e.nodes for e in els], dtype=int)
            idx = (D_[:, :, None] * self.ndof + np.arange(self.ndof)).reshape(len(els), -1)
            blocks.append((idx, KE))
        for e in single:
            idx = self.equivalent_dof(e)
            ke = np.asarray(e.k(self.X), dtype=float)
            if ke.shape != (idx.size, idx.size):
                raise ValueError(f"{type(e).__name__}: matrix shape {ke.shape}, expected {idx.size}")
            blocks.append((idx[None, :], ke[None]))
        return self._scatter("K", blocks)

    def M(self, lumped: bool = False) -> sp.csr_matrix:
        """Global mass matrix (consistent, or lumped/HRZ)."""
        return self._assemble(lambda e: e.m(self.X, lumped=lumped))

    def KG(self, u: np.ndarray) -> sp.csr_matrix:
        """Geometric stiffness for the pre-load displacement field ``u``."""
        return self._assemble(lambda e: e.kg(self.X, u[self.equivalent_dof(e)]))

    def body_forces(self) -> np.ndarray:
        """Equivalent nodal loads of distributed/body forces of all elements."""
        F = np.zeros(self.n_dof)
        for e in self.elements:
            if hasattr(e, "body_force"):
                F[self.equivalent_dof(e)] += e.body_force(self.X)
        return F

    # ------------------------------------------------------------------ constraints → reduction
    def _partition(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """(free, prescribed, prescribed values) for Dirichlet-only models."""
        if self._mpc:
            raise ValueError("model has multi-point constraints; use reduction() instead of _partition()")
        fixed = np.array(sorted(self._fixed), dtype=int)
        free = np.setdiff1d(np.arange(self.n_dof), fixed)
        value = np.array([self._fixed[i] for i in fixed])
        return free, fixed, value

    def _resolve_mpc(self) -> dict[int, tuple[dict[int, float], float]]:
        """Express every dependent DOF in independent DOFs only (chains substituted, cycles rejected)."""
        out: dict[int, tuple[dict[int, float], float]] = {}

        def expand(s: int, stack: tuple[int, ...]) -> tuple[dict[int, float], float]:
            if s in out:
                return out[s]
            if s in stack:
                raise ValueError("circular multi-point constraints: " +
                                 " -> ".join(self.dof_label(i) for i in (*stack, s)))
            masters, b = self._mpc[s]
            coef: dict[int, float] = {}
            for j, c in masters.items():
                if j in self._fixed:
                    b += c * self._fixed[j]
                elif j in self._mpc:
                    sub, sb = expand(j, (*stack, s))
                    b += c * sb
                    for k, ck in sub.items():
                        coef[k] = coef.get(k, 0.0) + c * ck
                else:
                    coef[j] = coef.get(j, 0.0) + c
            out[s] = ({k: v for k, v in coef.items() if v != 0.0}, b)
            return out[s]

        for s in self._mpc:
            expand(s, ())
        return out

    def reduction(self) -> tuple[sp.csr_matrix, np.ndarray, np.ndarray]:
        """Transformation ``u = T q + g``.

        Returns
        -------
        T : csr_matrix (n_dof, n_independent)
        g : ndarray (n_dof,)
            Prescribed values and MPC offsets.
        independent : ndarray of int
            Global indices of the independent DOFs (columns of ``T``).
        """
        mpc = self._resolve_mpc()
        dependent = set(self._fixed) | set(mpc)
        independent = np.array([i for i in range(self.n_dof) if i not in dependent], dtype=int)
        col = {int(j): k for k, j in enumerate(independent)}
        rows, cols, vals = list(independent), list(range(independent.size)), [1.0] * independent.size
        g = np.zeros(self.n_dof)
        for i, v in self._fixed.items():
            g[i] = v
        for s, (coef, b) in mpc.items():
            g[s] = b
            for j, c in coef.items():
                rows.append(s)
                cols.append(col[j])
                vals.append(c)
        T = sp.csr_matrix((vals, (rows, cols)), shape=(self.n_dof, independent.size))
        return T, g, independent

    def _reduced(self, A: sp.spmatrix) -> tuple[Callable[[sp.spmatrix], sp.spmatrix], np.ndarray]:
        """Return ``(reduce(A), independent DOFs)`` using slicing when there are no MPCs."""
        if not self._mpc:
            free, _, _ = self._partition()
            return (lambda B: sp.csr_matrix(B)[free][:, free]), free
        T, _, ind = self.reduction()
        Tt = T.T.tocsr()
        return (lambda B: (Tt @ sp.csr_matrix(B) @ T).tocsr()), ind

    # ------------------------------------------------------------------ analyses
    def static(self, volume: bool = True, F: np.ndarray | None = None,
               options: solvers.SolverOptions | None = None) -> StaticResult:
        """Linear static analysis ``K u = F``.

        Parameters
        ----------
        volume : bool
            Include element body forces (gravity, distributed loads, centrifugal).
        F : ndarray, optional
            Load vector(s); shape ``(n_dof,)`` or ``(n_dof, n_cases)`` for several load cases
            solved with one factorisation. Default: :attr:`F`.
        options : SolverOptions, optional
            Solver settings (default :attr:`solver_options`).

        Raises
        ------
        aerokit.fem.solvers.SingularMatrixError
            Unsupported DOFs, mechanism or unverifiable solution (subclass of ``ValueError``).
        """
        K = self.K()
        F = (self.F if F is None else np.asarray(F, dtype=float)).copy()
        if F.shape[0] != self.n_dof:
            raise ValueError(f"load vector has {F.shape[0]} rows, model has {self.n_dof} DOFs")
        if volume:
            bf = self.body_forces()
            F = F + (bf[:, None] if F.ndim == 2 else bf)
        opt = options or self.solver_options
        if not self._mpc:
            free, fixed, value = self._partition()
            if free.size == 0:
                raise ValueError("no free DOFs")
            u = np.zeros_like(F)
            u[fixed] = value[:, None] if F.ndim == 2 else value
            Kc = K.tocsc()
            Kff = Kc[free][:, free]
            rhs = F[free] - (Kc[free][:, fixed] @ (u[fixed]))
            x, info, _ = solvers.solve(Kff, rhs, opt, labels=lambda i: self.dof_label(int(free[i])))
            u[free] = x
        else:
            T, g, ind = self.reduction()
            if ind.size == 0:
                raise ValueError("no independent DOFs")
            Kr = (T.T @ K @ T).tocsr()
            G = g[:, None] if F.ndim == 2 else g
            rhs = T.T @ (F - K @ G)
            x, info, _ = solvers.solve(Kr, rhs, opt, labels=lambda i: self.dof_label(int(ind[i])))
            u = T @ x + G
        R = K @ u - F
        energy = 0.5 * np.einsum("i...,i...->...", u, K @ u)
        return StaticResult(u=u, reaction=R, energy=float(energy) if np.ndim(energy) == 0 else energy,
                            residual=info.residual, solver=info)

    @cite("bathe_2014", note="Sec. 10.2 participation factors and effective modal mass")
    def modal(self, n: int = 6, lumped: bool = False) -> ModalResult:
        """Natural frequencies and mass-normalised mode shapes, ``K φ = ω² M φ``.

        Also returns the participation factors ``Γ = φᵀ M r`` and effective masses ``Γ²`` for unit
        rigid-body translations ``r`` along each global axis (``(n, n_axes)`` arrays). They assume
        the first ``dim`` local DOFs are the x, y(, z) translations (true for trusses, frames,
        plane and solid elements; not for the Mindlin plate, whose DOF 0 is ``w``).
        """
        if any(v != 0 for v in self._fixed.values()):
            raise ValueError("modal analysis cannot have enforced displacements")
        K, M = self.K(), self.M(lumped=lumped)
        red, ind = self._reduced(K)
        Kr, Mr = red(K), red(M)
        if ind.size == 0:
            raise ValueError("no free DOFs")
        if not np.all(Mr.diagonal() >= 0) or Mr.diagonal().sum() <= 0:
            raise ValueError("mass matrix is zero or indefinite: give the elements a density (rho)")
        w2, V = solvers.generalized_eigh(Kr, Mr, min(n, ind.size), which="SM")
        w2 = np.where(np.abs(w2) < 1e-9 * max(np.abs(w2).max(), 1.0), 0.0, w2)
        if np.any(w2 < 0):
            raise ValueError("negative eigenvalue: mass or stiffness matrix is wrong")
        modes = self._expand(V, ind)
        omega = np.sqrt(w2)
        n_ax = min(self.ndof, self.X.shape[1])
        r = np.zeros((self.n_dof, n_ax))
        for a in range(n_ax):
            r[a::self.ndof, a] = 1.0
        gamma = modes.T @ (M @ r)
        return ModalResult(omega=omega, f=omega / (2 * np.pi), modes=modes, participation=gamma,
                           effective_mass=gamma ** 2)

    def _expand(self, V: np.ndarray, ind: np.ndarray) -> np.ndarray:
        """Reduced vectors → full DOF vectors (homogeneous constraints)."""
        if not self._mpc:
            full = np.zeros((self.n_dof, V.shape[1]))
            full[ind] = V
            return full
        T, _, _ = self.reduction()
        return np.asarray(T @ V)

    @cite("cook_2002", note="Ch. 18 linear buckling; −K_G φ = μ K φ, λ = 1/μ")
    def buckling(self, n: int = 4, preload: np.ndarray | None = None) -> BucklingResult:
        """Linear buckling load factors ``λ`` with ``(K + λ K_G) φ = 0``.

        ``K_G`` is built from the internal forces of the pre-load solution (default: static
        solution of the current loads), so the critical load is ``λ · F``. Large models are
        solved with ARPACK on ``−K_G φ = μ K φ`` (largest ``μ = 1/λ``).
        """
        if preload is None:
            preload = self.static().u
        K, KG = self.K(), self.KG(preload)
        red, ind = self._reduced(K)
        Kr, Gr = red(K), red(KG)
        k = ind.size if ind.size <= 500 else min(ind.size - 2, max(2 * n, n + 8))
        mu, V = solvers.generalized_eigh(-Gr, Kr, k, which="LA")
        pos = mu > 1e-12 * max(np.abs(mu).max(), 1e-300)
        if not np.any(pos):
            raise ValueError("no positive buckling factor (the load may be tensile)")
        mu, V = mu[pos], V[:, pos]
        order = np.argsort(-mu)[:n]
        return BucklingResult(lambda_=1 / mu[order], modes=self._expand(V[:, order], ind))

    def condition_estimate(self) -> float:
        """1-norm condition estimate of the reduced stiffness matrix (ill-conditioning check)."""
        K = self.K()
        red, _ = self._reduced(K)
        return solvers.condition_estimate(red(K))

    # ------------------------------------------------------------------ post-processing
    def element_results(self, u: np.ndarray) -> list[dict[str, Any]]:
        """``stress(X, ue)`` of every element."""
        return [e.stress(self.X, u[self.equivalent_dof(e)]) for e in self.elements]

    def node_stresses(self, u: np.ndarray) -> np.ndarray:
        """Nodal stresses of 2-D continuum elements, averaged over the elements sharing a node.

        Each element evaluates its stress directly at its nodes (natural coordinates); nodes not
        belonging to any continuum element get NaN. Returns ``(n_node, n_components)``.
        """
        total: np.ndarray | None = None
        count = np.zeros(self.n_node)
        for e in self.elements:
            if not hasattr(e, "NATURAL"):
                continue
            ue = u[self.equivalent_dof(e)]
            for d, (xi, eta) in zip(e.nodes, e.NATURAL, strict=True):
                s = e.stress_at_point(self.X, ue, xi, eta)[0]
                if total is None:
                    total = np.zeros((self.n_node, s.size))
                total[d] += s
                count[d] += 1
        if total is None:
            raise ValueError("model has no 2-D continuum elements")
        count[count == 0] = np.nan
        return total / count[:, None]
