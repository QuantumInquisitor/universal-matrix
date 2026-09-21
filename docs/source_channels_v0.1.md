# Unified Source Channels v0.1

## Purpose

This extension applies all three additional source mechanisms requested after the polarization-source construction:

1. boundary electric flux through the six external gates;
2. explicit conserved free electric charge;
3. compact-U(1) topological magnetic charge.

These are kept separate from the existing polarization-induced electric source so physically different mechanisms are not conflated.

Implementation:

`src/source_channels.py`

Tests:

`tests/test_source_channels.py`

## 1. Polarization-induced electric source

The existing bound-source channel remains

[
ho_{m pol}=-
abla_{m lat}cdot P.
]

On a periodic lattice,

[
sum_xho_{m pol}=0.
]

This channel therefore produces paired induced sources but no net electric charge.

## 2. Free electric charge

A distinct free-charge density is introduced:

[
ho_{m free}(x).
]

It evolves under its own current according to

[
oxed{
dotho_{m free}
+

abla_{m lat}cdot J_{m free}
=
0.
}
]

On a closed periodic domain with no boundary exchange,

[
oxed{
Q_{m free}
=
sum_xho_{m free}(x)
=
	ext{constant}.
}
]

The total electric source used by Gauss law is

[
oxed{
ho_{m electric}
=
ho_{m pol}
+
ho_{m free}.
}
]

## 3. Boundary flux through the six external gates

The canonical external boundary is

[
B_6=
{+X,-X,+Y,-Y,+Z,-Z}.
]

Each gate is now permitted to carry a signed electric-charge inflow rate:

[
Phi_{+X},
Phi_{-X},
Phi_{+Y},
Phi_{-Y},
Phi_{+Z},
Phi_{-Z}.
]

Positive sign means charge enters the internal lattice.

The total inflow rate is

[
oxed{
dot Q_{m boundary}
=
sum_{gin B_6}Phi_g.
}
]

For one finite time step,

[
oxed{
Delta Q
=
Delta t
sum_gPhi_g.
}
]

Thus the internal electric sector can now acquire nonzero net charge without creating charge locally. Charge enters or leaves through the explicit six-gate boundary channel.

The implementation distributes each face contribution uniformly over the corresponding boundary face. This spatial distribution is a current adapter convention; the integrated balance law is exact.

## 4. Compact-U(1) topological magnetic source

Compact link phases permit plaquette angles to differ from their principal values by integer multiples of (2pi):

[
F^{m raw}_{ij}
=
ar F_{ij}
+
2pi n_{ij},
qquad
n_{ij}inmathbb Z.
]

The integer (n_{ij}) is a compact winding number.

For each elementary cube, the oriented difference of the winding integers on opposite faces defines an integer-valued monopole-like charge:

[
oxed{
m(x)inmathbb Z.
}
]

This is a compact-U(1) **magnetic/topological** source. It is not added to ordinary electric charge density.

The distinction is essential:

[
ho_{m electric}

eq
m_{m magnetic}.
]

The topological sector is therefore treated as a dual/magnetic defect channel.

## 5. Unified source architecture

The engine now contains four source mechanisms:

[
oxed{
ho_{m pol}
}
]

bound/polarization electric source,

[
oxed{
ho_{m free}
}
]

independent conserved electric source,

[
oxed{
Phi_{B_6}
}
]

boundary electric exchange,

and

[
oxed{
m_{m topo}
}
]

integer compact magnetic charge.

The electric Gauss source is

[
oxed{
ho_E
=
ho_{m pol}
+
ho_{m free}.
}
]

Its integrated balance is

[
oxed{
rac{d}{dt}
sum_x ho_E
=
sum_{gin B_6}Phi_g
}
]

because the polarization channel has zero net charge and internal free-current divergence telescopes away.

The magnetic/topological charge remains a separate field sector.

## 6. Relation to polarity reversal

The polarity map still gives

[
Pightarrow-P
]

under

[
sigmaightarrow-sigma,
]

so

[
ho_{m pol}ightarrow-ho_{m pol}.
]

Free charge does not have to reverse under a polarity flip. It is a separate degree of freedom.

Likewise, topological magnetic charge is determined by compact gauge winding, not directly by the local polarity sign.

This separation prevents the engine from assuming that all notions of positive/negative source are the same physical object.

## 7. Tests

The regression suite now verifies:

1. free charge conserves its integrated value under internal current flow;
2. boundary flux changes total internal electric charge by exactly the integrated six-face inflow;
3. total electric source sums polarization and free-charge channels correctly;
4. compact plaquettes detect integer (2pi) winding;
5. compact topological magnetic charge is integer valued.

## 8. Remaining work

The next useful steps are:

- couple (ho_{m electric}) directly into the 3D Gauss solver in a single engine object;
- evolve free charge, polarization current, boundary injection, and gauge fields in one synchronized timestep;
- add a dual magnetic Gauss diagnostic for the topological sector;
- test how topological defects alter the source-interaction energy;
- determine whether boundary injection can be derived from the nested micro-to-macro layer dynamics rather than prescribed externally.

## Status

All three requested mechanisms are now represented:

[
oxed{
	ext{boundary flux}
+
	ext{free electric charge}
+
	ext{topological magnetic charge}
}
]

while the previous polarization-induced source remains active as a fourth channel.

They are combined where mathematically appropriate and kept separate where their conservation laws and physical meanings differ.
