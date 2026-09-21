import math

from src.product_group_anomaly_ledger import (
    ProductWeylMultiplet,
    mixed_gravitational_u1_coefficient,
    product_group_anomaly_ledger,
    standard_model_one_generation_reference,
    su2_fundamental_doublet_count,
    su2_global_anomaly_parity,
    su2_squared_u1_coefficient,
    su3_cubic_coefficient,
    su3_squared_u1_coefficient,
    u1_cubic_coefficient,
)


def test_one_standard_model_generation_cancels_supported_anomalies():
    multiplets = standard_model_one_generation_reference()
    ledger = product_group_anomaly_ledger(
        multiplets,
        tolerance=1e-12,
    )

    assert abs(ledger["su3_cubic"]) < 1e-12
    assert abs(ledger["su3_squared_u1"]) < 1e-12
    assert abs(ledger["su2_squared_u1"]) < 1e-12
    assert abs(ledger["u1_cubic"]) < 1e-12
    assert abs(
        ledger["mixed_gravitational_u1"]
    ) < 1e-12
    assert ledger[
        "local_perturbative_anomalies_cancel"
    ]
    assert ledger["su2_global_anomaly_cancels"]
    assert ledger["all_supported_conditions_cancel"]


def test_standard_model_doublet_count_is_even():
    multiplets = standard_model_one_generation_reference()
    assert su2_fundamental_doublet_count(
        multiplets
    ) == 4
    assert su2_global_anomaly_parity(
        multiplets
    ) == 0


def test_right_neutrino_does_not_change_supported_anomaly_coefficients():
    base = product_group_anomaly_ledger(
        standard_model_one_generation_reference(
            include_right_neutrino=False
        )
    )
    extended = product_group_anomaly_ledger(
        standard_model_one_generation_reference(
            include_right_neutrino=True
        )
    )

    for key in (
        "su3_cubic",
        "su3_squared_u1",
        "su2_squared_u1",
        "u1_cubic",
        "mixed_gravitational_u1",
        "su2_global_parity",
    ):
        assert extended[key] == base[key]


def test_single_neutral_su2_doublet_has_global_but_not_local_anomaly():
    multiplets = [
        ProductWeylMultiplet(
            name="single_doublet",
            color_rep="singlet",
            weak_rep="doublet",
            u1_charge=0.0,
            handedness=1,
        )
    ]
    ledger = product_group_anomaly_ledger(
        multiplets
    )

    assert ledger[
        "local_perturbative_anomalies_cancel"
    ]
    assert ledger["su2_global_parity"] == 1
    assert not ledger["su2_global_anomaly_cancels"]
    assert not ledger[
        "all_supported_conditions_cancel"
    ]


def test_vectorlike_weak_doublet_pair_cancels_all_supported_conditions():
    multiplets = [
        ProductWeylMultiplet(
            name="L",
            color_rep="singlet",
            weak_rep="doublet",
            u1_charge=0.4,
            handedness=1,
        ),
        ProductWeylMultiplet(
            name="R",
            color_rep="singlet",
            weak_rep="doublet",
            u1_charge=0.4,
            handedness=-1,
        ),
    ]
    ledger = product_group_anomaly_ledger(
        multiplets
    )
    assert ledger[
        "all_supported_conditions_cancel"
    ]
    assert ledger[
        "su2_fundamental_doublet_count"
    ] == 2


def test_removing_e_right_breaks_abelian_and_mixed_gravitational_cancellation():
    multiplets = [
        m
        for m in standard_model_one_generation_reference()
        if m.name != "e_R"
    ]

    assert abs(
        u1_cubic_coefficient(multiplets)
    ) > 1e-6
    assert abs(
        mixed_gravitational_u1_coefficient(
            multiplets
        )
    ) > 1e-6


def test_standard_model_mixed_coefficients_cancel_independently():
    multiplets = standard_model_one_generation_reference()

    assert math.isclose(
        su3_squared_u1_coefficient(
            multiplets
        ),
        0.0,
        rel_tol=0,
        abs_tol=1e-12,
    )
    assert math.isclose(
        su2_squared_u1_coefficient(
            multiplets
        ),
        0.0,
        rel_tol=0,
        abs_tol=1e-12,
    )


def test_color_cubic_index_distinguishes_fundamental_and_antifundamental():
    multiplets = [
        ProductWeylMultiplet(
            name="3",
            color_rep="fundamental",
            weak_rep="singlet",
            u1_charge=0.0,
            handedness=1,
        ),
        ProductWeylMultiplet(
            name="3bar",
            color_rep="antifundamental",
            weak_rep="singlet",
            u1_charge=0.0,
            handedness=1,
        ),
    ]
    assert su3_cubic_coefficient(
        multiplets
    ) == 0.0
