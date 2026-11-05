"""Hand checks next to the FEA: support reactions per bolt vs the classical bolt-group distribution.

For bolts that share one axis w (all supports of the set-up on bores with the same axis), the applied load of a
case is reduced to the bolt-group centroid c: force F and moment M = Σ (x_i − c) × f_i over the loaded nodes.

* in-plane shear per bolt (u, v plane): elastic rigid-plate method of
  :func:`aerokit.structures.joints.bolt_group` (Bruhn) with the in-plane force and the moment about w;
* axial force per bolt: rigid plate on bolts only (no contact, no prying), F_i = F_w/n + a v_i + b u_i with
  (a, b) from Σ v_i F_i = M_u and −Σ u_i F_i = M_v (moment equilibrium about the in-plane axes) [derived here].

The FEA reaction per bolt is the sum of the nodal reactions on its bore (K u − f at the fixed DOFs). The classical
values assume a rigid plate; differences of tens of per cent are expected where the plate bends (prying, load path)
— this is a plausibility check of magnitudes, directions and load sharing, not a validation of either.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from aerokit.bracket import features, voxfem
from aerokit.references import cite
from aerokit.structures.joints import bolt_group

__all__ = ["bolt_reactions", "classical_bolt_loads", "compare_bolts"]


def bolt_reactions(mesh: voxfem.VoxelMesh, setup: dict[str, Any], E: float, nu: float = 0.3,
                   element: str = "H8IM") -> dict[str, Any]:
    """FEA reaction force vector [N] on every support bore for every load case."""
    ap = features.apply_setup(mesh, setup)
    KE, _ = voxfem.ke_unit(nu, element)
    K = mesh.stiffness(KE, E * np.asarray(mesh.frac) * mesh.h)
    res = voxfem.static(mesh, E, nu, ap.F, ap.fixed, element=element)
    sup = [s["hole"] for s in setup["supports"]]
    holes = {d["id"]: features.Hole.from_json(d) for d in setup["holes"]}
    # every fixed node belongs to the support bolt whose axis is nearest (bore nodes for fixed_bore, the seat
    # annulus for bolt_seat — both lie within a few radii of their own bolt axis)
    fn = np.unique(np.asarray(ap.fixed) // 3)
    dist = np.column_stack([np.linalg.norm(np.delete(mesh.X[fn] - holes[h].center, holes[h].axis, axis=1), axis=1)
                            for h in sup])
    owner = {h: fn[np.argmin(dist, axis=1) == i] for i, h in enumerate(sup)}
    out: dict[str, Any] = {"cases": ap.names, "holes": sup, "reaction_N": {}, "clamp_moment_Nm": {}}
    for k, r in enumerate(res):
        R = (K @ r.U - ap.F[:, k]).reshape(-1, 3)
        out["reaction_N"][ap.names[k]] = {h: R[owner[h]].sum(axis=0).tolist() for h in sup}
        # moment of the support reactions about the bolt centre: a fixed bore is a rigid clamp and carries one,
        # a real bolt (pin + seat) much less — this is what moves load away from the rigid-plate split
        out["clamp_moment_Nm"][ap.names[k]] = {
            h: np.cross(mesh.X[owner[h]] - holes[h].center, R[owner[h]]).sum(axis=0).tolist() for h in sup}
    out["_applied"] = ap
    out["_mesh_X"] = mesh.X
    return out


@cite("bruhn_1973", note="elastic fastener-group method (in-plane part via structures.joints.bolt_group)")
def classical_bolt_loads(setup: dict[str, Any], applied: Any, X: np.ndarray) -> dict[str, Any] | None:
    """Rigid-plate bolt loads (reactions, i.e. opposite to the applied share) [N] per case and support hole;
    ``None`` when the supports are not all bores with one common axis."""
    holes = {d["id"]: features.Hole.from_json(d) for d in setup["holes"]}
    sup = [holes[s["hole"]] for s in setup["supports"]]
    if len({h.axis for h in sup}) != 1 or len(sup) < 2:
        return None
    w = sup[0].axis
    u, v = [a for a in range(3) if a != w]
    P = np.array([h.center for h in sup])
    c = P.mean(axis=0)
    du, dv = P[:, u] - c[u], P[:, v] - c[v]
    n = len(sup)
    A2 = np.array([[np.sum(dv * dv), np.sum(dv * du)], [-np.sum(du * dv), -np.sum(du * du)]])
    out: dict[str, Any] = {"axis": "xyz"[w], "centroid_m": c.tolist(), "cases": {}}
    for k, name in enumerate(applied.names):
        f = applied.F[:, k].reshape(-1, 3)
        nz = np.flatnonzero(np.abs(f).sum(1) > 0)
        Ft = f[nz].sum(axis=0)
        M = np.cross(X[nz] - c, f[nz]).sum(axis=0)
        # bolt_group's moment is counter-clockwise in the (u, v) plane = right-handed about w when (u, v, w) is
        # right-handed: (y, z, x) and (x, y, z) are, (x, z, y) is not → flip the moment for a y-axis group
        sign = -1.0 if w == 1 else 1.0
        bg = bolt_group(np.column_stack([P[:, u], P[:, v]]), float(Ft[u]), float(Ft[v]), sign * float(M[w]))
        try:
            ab = np.linalg.solve(A2, np.array([M[u], M[v]]))
        except np.linalg.LinAlgError:
            ab = np.zeros(2)
        Fax = Ft[w] / n + ab[0] * dv + ab[1] * du
        loads = {}
        for i, h in enumerate(sup):
            vec = np.zeros(3)
            vec[u], vec[v], vec[w] = bg["Fx"][i], bg["Fy"][i], Fax[i]
            loads[h.id] = (-vec).tolist()                 # reaction = − share of the applied load
        out["cases"][name] = loads
    return out


def compare_bolts(fea: dict[str, Any], classical: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Rows: case, hole, FEA shear / axial [N], classical shear / axial [N], FEA clamp moment magnitude [N m]."""
    if classical is None:
        return []
    w = "xyz".index(classical["axis"])
    rows = []
    for case in fea["cases"]:
        for h in fea["holes"]:
            a = np.asarray(fea["reaction_N"][case][h])
            b = np.asarray(classical["cases"][case][h])
            mc = fea.get("clamp_moment_Nm", {}).get(case, {}).get(h)
            rows.append({"case": case, "hole": h, "fea_shear_N": float(np.linalg.norm(np.delete(a, w))),
                         "fea_axial_N": float(a[w]), "classical_shear_N": float(np.linalg.norm(np.delete(b, w))),
                         "classical_axial_N": float(b[w]),
                         "fea_clamp_moment_Nm": float(np.linalg.norm(mc)) if mc is not None else float("nan")})
    return rows
