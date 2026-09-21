# Physical Benchmark Note 001: Clock-Shift No-Go Result

## Question

Can the v0.4 canonical kernel, without adding a fitted physical law, produce a nonzero differential clock-frequency shift between two otherwise unspecified core states?

## Result

No.

This is a structural result, not a failed numerical fit.

The bare core is the homogeneous cyclic space

```
C = Z_108.
```

Its canonical operators are translations E=T9, T=T21, P=T54, the reflection F(n)=107-n, and the canonical-representative register projection pi(n)=7n mod64.

A physical differential clock observable would require a dimensionless scalar

```
R(a,b) = (f_b - f_a)/f_a
```

whose value changes with the physical configurations represented by a and b.

### Translation-homogeneity theorem

Let s:C->R be a scalar observable that is invariant under every core translation:

```
s(n+d)=s(n) for every n,d in Z_108.
```

Then s is constant.

Proof: for arbitrary a,b choose d=b-a. Translation invariance gives s(b)=s(a+d)=s(a). Since a and b were arbitrary, s is constant on C.

Therefore any scalar clock rate derived only from translation-invariant properties of the bare cyclic core has

```
Delta f / f = 0
```

between all core states.

### Canonical operators do not supply physical height

The operators E, T, and P distinguish algebraic relations, not SI spatial separation. Their orders are fixed globally:

```
ord(E)=12
ord(T)=36
ord(P)=2.
```

Those orders do not vary from state to state.

The register projection does have canonical-coordinate carry discontinuities:

- E gives register increments 63 or 11 modulo 64;
- T21 gives increments 19 or 31 modulo 64;
- P gives increments 58 or 6 modulo 64.

These differences are consequences of choosing canonical representatives before projection. They do not define meters, elevation, mass, energy, or clock frequency. Treating a carry as a gravitational redshift would add an unsupported physical identification.

The reflection F similarly supplies an involutive symmetry but no dimensional clock observable.

## Consequence

A nonzero physical clock shift requires additional structure that breaks the translation homogeneity of the bare core.

At minimum a physical extension must introduce, independently of the target clock data:

1. a source or boundary configuration;
2. a rule mapping that configuration into a state-dependent scalar or transition rate;
3. an operational definition of physical separation;
4. a conversion to a dimensionless frequency ratio.

The new structure must not be a renamed Newtonian potential, metric component, gravitational acceleration, or fitted redshift formula if the objective is an independent non-gravitational theory.

## What can be tested next

The six external boundary gates are the first canonical objects capable of breaking full core translation symmetry. A defensible next model should therefore ask whether specified boundary states induce a nonuniform internal transition-rate field through a rule fixed before comparison with clock experiments.

If no such rule follows from additional independently motivated postulates, v0.4 remains a finite mathematical architecture rather than a predictive physical theory.

## Status

**No-go result:** the bare v0.4 kernel cannot independently predict a nonzero differential clock shift.

**Reason:** homogeneous finite-state topology supplies relations and dimensionless counts but no state-dependent physical clock-rate observable.

**Required next step:** formulate and justify a boundary-to-core dynamical law, then derive its observable consequences without calibration to the target measurement.


## Addendum: Nested Polarity Dynamics Extension

The no-go result above applies only to the bare homogeneous v0.4 core. It does not apply once a time-dependent, nested polarity dynamics is added as extra structure.

The exploratory extension in `src/nested_polarity_dynamics.py` introduces layer states

```
X_l = (n_l, sigma_l, phi_l, A_l)
```

with polarity `sigma_l in {-1,+1}`, phase `phi_l`, amplitude `A_l`, and canonical core position `n_l`.

The polarity-flip operator is

```
Q(n,sigma) = (n+54,-sigma)
```

and satisfies `Q^2=I`.

Routing is polarity-sensitive:

```
sigma=+1 -> T_21
sigma=-1 -> T_-21.
```

Adjacent micro-to-macro layers exchange amplitude through an explicitly labeled modeling ansatz. The current implementation uses a bounded conservative nearest-neighbor flux dependent on amplitude, relative polarity, and phase difference. This creates state-dependent layer behavior and therefore breaks the translation-homogeneity assumption behind the bare-core clock-shift no-go theorem.

This does not yet constitute a physical redshift prediction. The extension currently produces dimensionless transition rates only. A physical clock comparison still requires an independently justified map from those rates to measured frequency ratios.

The important change is structural: a nonzero differential rate is now mathematically possible without inserting a gravitational potential into the core.
