"""SU(3) x SU(2) x U(1) Weyl-representation anomaly ledger.

This module is representation bookkeeping. It does not claim that the Universal
Matrix derives the Standard Model representation content.

For a physical Weyl multiplet with handedness chi in {-1,+1}, color
representation R3, weak representation R2, and U(1) charge Y, the supported
four-dimensional perturbative coefficients are

    SU(3)^3:
        sum chi * A_3(R3) * dim(R2)

    SU(3)^2 U(1):
        sum chi * Y * T_3(R3) * dim(R2)

    SU(2)^2 U(1):
        sum chi * Y * T_2(R2) * dim(R3)

    U(1)^3:
        sum chi * Y^3 * dim(R3) * dim(R2)

    grav^2 U(1):
        sum chi * Y * dim(R3) * dim(R2).

Normalization:
    T(fundamental SU(N)) = 1/2
    A_3(3) = +1
    A_3(3bar) = -1.

For the representations supported here, SU(2) has no local cubic gauge anomaly
because the doublet is pseudoreal. The separate Witten global SU(2) condition
requires an even number of fundamental doublets, counting spectator color
multiplicity modulo two.

The ledger distinguishes:
- local perturbative anomaly cancellation;
- the mod-2 SU(2) global condition;
- a supplied representation spectrum;
- any claim that such a spectrum is derived from the finite Matrix kernel.

Only the first two are evaluated here.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from collections.abc import Sequence


COLOR_REPS = {
    "singlet": {
        "dimension": 1,
        "dynkin_index": 0.0,
        "cubic_index": 0.0,
    },
    "fundamental": {
        "dimension": 3,
        "dynkin_index": 0.5,
        "cubic_index": 1.0,
    },
    "antifundamental": {
        "dimension": 3,
        "dynkin_index": 0.5,
        "cubic_index": -1.0,
    },
}

WEAK_REPS = {
    "singlet": {
        "dimension": 1,
        "dynkin_index": 0.0,
        "is_fundamental_doublet": False,
    },
    "doublet": {
        "dimension": 2,
        "dynkin_index": 0.5,
        "is_fundamental_doublet": True,
    },
}


@dataclass(frozen=True)
class ProductWeylMultiplet:
    name: str
    color_rep: str
    weak_rep: str
    u1_charge: float
    handedness: int
    multiplicity: int = 1

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name must be non-empty")
        if self.color_rep not in COLOR_REPS:
            raise ValueError(
                f"unsupported color_rep: {self.color_rep}"
            )
        if self.weak_rep not in WEAK_REPS:
            raise ValueError(
                f"unsupported weak_rep: {self.weak_rep}"
            )
        if not math.isfinite(self.u1_charge):
            raise ValueError("u1_charge must be finite")
        if self.handedness not in (-1, 1):
            raise ValueError(
                "handedness must be -1 or +1"
            )
        if self.multiplicity < 1:
            raise ValueError(
                "multiplicity must be positive"
            )

    @property
    def color_dimension(self) -> int:
        return int(
            COLOR_REPS[self.color_rep]["dimension"]
        )

    @property
    def weak_dimension(self) -> int:
        return int(
            WEAK_REPS[self.weak_rep]["dimension"]
        )

    @property
    def color_dynkin_index(self) -> float:
        return float(
            COLOR_REPS[self.color_rep]["dynkin_index"]
        )

    @property
    def color_cubic_index(self) -> float:
        return float(
            COLOR_REPS[self.color_rep]["cubic_index"]
        )

    @property
    def weak_dynkin_index(self) -> float:
        return float(
            WEAK_REPS[self.weak_rep]["dynkin_index"]
        )

    @property
    def is_weak_doublet(self) -> bool:
        return bool(
            WEAK_REPS[self.weak_rep][
                "is_fundamental_doublet"
            ]
        )


def su3_cubic_coefficient(
    multiplets: Sequence[ProductWeylMultiplet],
) -> float:
    return float(
        sum(
            m.multiplicity
            * m.handedness
            * m.color_cubic_index
            * m.weak_dimension
            for m in multiplets
        )
    )


def su3_squared_u1_coefficient(
    multiplets: Sequence[ProductWeylMultiplet],
) -> float:
    return float(
        sum(
            m.multiplicity
            * m.handedness
            * m.u1_charge
            * m.color_dynkin_index
            * m.weak_dimension
            for m in multiplets
        )
    )


def su2_squared_u1_coefficient(
    multiplets: Sequence[ProductWeylMultiplet],
) -> float:
    return float(
        sum(
            m.multiplicity
            * m.handedness
            * m.u1_charge
            * m.weak_dynkin_index
            * m.color_dimension
            for m in multiplets
        )
    )


def u1_cubic_coefficient(
    multiplets: Sequence[ProductWeylMultiplet],
) -> float:
    return float(
        sum(
            m.multiplicity
            * m.handedness
            * m.u1_charge**3
            * m.color_dimension
            * m.weak_dimension
            for m in multiplets
        )
    )


def mixed_gravitational_u1_coefficient(
    multiplets: Sequence[ProductWeylMultiplet],
) -> float:
    return float(
        sum(
            m.multiplicity
            * m.handedness
            * m.u1_charge
            * m.color_dimension
            * m.weak_dimension
            for m in multiplets
        )
    )


def su2_fundamental_doublet_count(
    multiplets: Sequence[ProductWeylMultiplet],
) -> int:
    """Count SU(2) doublets including spectator color multiplicity.

    Handedness does not change this mod-2 count because the SU(2)
    fundamental is pseudoreal.
    """
    return int(
        sum(
            m.multiplicity
            * m.color_dimension
            for m in multiplets
            if m.is_weak_doublet
        )
    )


def su2_global_anomaly_parity(
    multiplets: Sequence[ProductWeylMultiplet],
) -> int:
    return (
        su2_fundamental_doublet_count(
            multiplets
        )
        % 2
    )


def product_group_anomaly_ledger(
    multiplets: Sequence[ProductWeylMultiplet],
    tolerance: float = 1e-12,
) -> dict[str, float | bool | int]:
    if tolerance < 0:
        raise ValueError(
            "tolerance must be non-negative"
        )

    su3_3 = su3_cubic_coefficient(
        multiplets
    )
    su3_2_u1 = su3_squared_u1_coefficient(
        multiplets
    )
    su2_2_u1 = su2_squared_u1_coefficient(
        multiplets
    )
    u1_3 = u1_cubic_coefficient(
        multiplets
    )
    grav_u1 = (
        mixed_gravitational_u1_coefficient(
            multiplets
        )
    )
    doublets = su2_fundamental_doublet_count(
        multiplets
    )
    parity = doublets % 2

    local_cancel = all(
        abs(value) <= tolerance
        for value in (
            su3_3,
            su3_2_u1,
            su2_2_u1,
            u1_3,
            grav_u1,
        )
    )
    global_su2_cancel = parity == 0

    return {
        "multiplet_count": len(multiplets),
        "su3_cubic": su3_3,
        "su3_squared_u1": su3_2_u1,
        "su2_squared_u1": su2_2_u1,
        "u1_cubic": u1_3,
        "mixed_gravitational_u1": grav_u1,
        "su2_fundamental_doublet_count": doublets,
        "su2_global_parity": parity,
        "local_perturbative_anomalies_cancel": (
            local_cancel
        ),
        "su2_global_anomaly_cancels": (
            global_su2_cancel
        ),
        "all_supported_conditions_cancel": (
            local_cancel
            and global_su2_cancel
        ),
    }


def standard_model_one_generation_reference(
    include_right_neutrino: bool = False,
) -> list[ProductWeylMultiplet]:
    """Return a correspondence reference, not a Matrix-derived spectrum.

    Hypercharge convention:
        Q = T3 + Y.

    Physical handedness is kept explicit instead of converting every field to
    a left-handed conjugate.
    """
    out = [
        ProductWeylMultiplet(
            name="Q_L",
            color_rep="fundamental",
            weak_rep="doublet",
            u1_charge=1.0 / 6.0,
            handedness=1,
        ),
        ProductWeylMultiplet(
            name="u_R",
            color_rep="fundamental",
            weak_rep="singlet",
            u1_charge=2.0 / 3.0,
            handedness=-1,
        ),
        ProductWeylMultiplet(
            name="d_R",
            color_rep="fundamental",
            weak_rep="singlet",
            u1_charge=-1.0 / 3.0,
            handedness=-1,
        ),
        ProductWeylMultiplet(
            name="L_L",
            color_rep="singlet",
            weak_rep="doublet",
            u1_charge=-1.0 / 2.0,
            handedness=1,
        ),
        ProductWeylMultiplet(
            name="e_R",
            color_rep="singlet",
            weak_rep="singlet",
            u1_charge=-1.0,
            handedness=-1,
        ),
    ]

    if include_right_neutrino:
        out.append(
            ProductWeylMultiplet(
                name="nu_R",
                color_rep="singlet",
                weak_rep="singlet",
                u1_charge=0.0,
                handedness=-1,
            )
        )

    return out
