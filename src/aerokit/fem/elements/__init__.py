"""Element library of :mod:`aerokit.fem`.

``line``      :class:`~aerokit.fem.elements.line.Bar`, :class:`~aerokit.fem.elements.line.Frame2D`,
              :class:`~aerokit.fem.elements.line.Frame3D`
``plane``     T3, Q4, QM6 (incompatible modes), Q8 — plane stress, plane strain, axisymmetric
``solid``     T4, T10, H8
``plate``     MITC4 Mindlin-Reissner plate
``discrete``  springs and point masses

Every element implements the protocol described in :mod:`aerokit.fem.model` (``nodes``, ``ndof``,
``k(X)``, ``m(X, lumped)``, ``kg(X, ue)``, ``stress(X, ue)`` and optionally ``body_force(X)``).
"""
