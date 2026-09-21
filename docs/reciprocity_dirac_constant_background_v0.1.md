# Reciprocity Dirac Constant-Background Bridge v0.1

## Purpose

The repository now contains a Wilson-Dirac lattice fermion operator on a fixed
U(1) background.

This extension asks how a Dirac field behaves on the reciprocity geometry
before introducing spatially varying tetrads and spin connection.

Implementation:

`src/reciprocity_dirac_constant_background.py`

Tests:

`tests/test_reciprocity_dirac_constant_background.py`

## 1. Constant reciprocity metric

For spatially uniform (psi),

[
ds^2
=
-e^{-2psi}dt^2
+
e^{2psi}dmathbf x^2.
]

Define

[
N=e^{-psi},
qquad
a=e^psi.
]

Because (N) and (a) are constant in space and time in this bridge, the
tetrad is constant and the spin connection vanishes.

## 2. Dirac Hamiltonian

The coordinate-time Dirac equation gives

[
oxed{
H_psi
=
rac{N}{a}
oldsymbol{alpha}cdotmathbf p
+
Neta_D m.
}
]

Therefore

[
oxed{
H_psi
=
e^{-2psi}
oldsymbol{alpha}cdotmathbf p
+
e^{-psi}
eta_D m.
}
]

## 3. Dispersion relation

The positive-energy branch is

[
oxed{
E_+^2
=
e^{-4psi}|mathbf p|^2
+
e^{-2psi}m^2.
}
]

## 4. Massless causal cone

For

[
m=0,
]

the coordinate group speed is

[
oxed{
v_{m Dirac}
=
e^{-2psi}.
}
]

This matches:

[
v_{m null}
=
e^{-2psi},
]

[
v_{m scalar}
=
e^{-2psi},
]

and the gauge characteristic speed already derived in the reciprocity action.

Thus scalar, gauge, and massless spinor sectors share one coordinate causal
cone in a uniform reciprocity background.

## 5. Rest-energy redshift

For

[
mathbf p=0,
]

[
oxed{
E_{m coordinate}
=
m e^{-psi}.
}
]

A static local observer divides coordinate energy by the lapse:

[
E_{m local}
=
rac{
E_{m coordinate}
}{
e^{-psi}
}.
]

Therefore

[
oxed{
E_{m local}=m.
}
]

So the local rest mass remains unchanged while the energy seen relative to the
asymptotic coordinate time redshifts with the clock lapse.

## 6. Stationary source universality

The general metric source remains

[
T^{00}+sum_iT^{ii}.
]

For a stationary localized spinor composite satisfying the total von Laue
condition,

[
int T^{ij}d^3x=0,
]

the integrated geometry source is

[
oxed{
M_{m active}
=
E_{m total}.
}
]

Thus fermionic matter is compatible with the same stationary universality
mechanism as scalar and gauge composites.

## 7. What remains missing

For spatially varying

[
psi(mathbf x,t),
]

the tetrad derivatives are nonzero.

Then the curved-space Dirac equation requires a spin connection

[
Gamma_mu
=
rac14
omega_{mu ab}gamma^agamma^b.
]

That contribution is not included in this module.

Therefore the present result is exact only for constant (psi).

## Status

The fermion sector now shares the reciprocity redshift and causal-cone
structure in the controlled uniform-background limit.

The next step is the full tetrad/spin-connection derivation.
