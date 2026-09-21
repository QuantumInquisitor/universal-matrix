from src.commercial_entitlements import (
    CommercialEntitlement,
    ProductFamily,
    enterprise_bundle,
)


def test_family_entitlement_exposes_expected_features():
    entitlement = CommercialEntitlement(
        tenant_id="tenant-1",
        families=frozenset(
            {
                ProductFamily.SPATIAL,
                ProductFamily.ROBOTICS,
            }
        ),
    )

    assert entitlement.allows_family(ProductFamily.SPATIAL)
    assert entitlement.allows_feature("spatial.teleoperation")
    assert entitlement.allows_feature("robotics.trajectory")
    assert not entitlement.allows_feature("manufacturing.gcode")


def test_extra_feature_can_be_granted_without_family():
    entitlement = CommercialEntitlement(
        tenant_id="tenant-2",
        families=frozenset({ProductFamily.CORE}),
        extra_features=frozenset({"custom.customer_feature"}),
    )

    assert entitlement.allows_feature("custom.customer_feature")
    assert entitlement.allows_feature("canonical.kernel")


def test_enterprise_bundle_can_include_full_platform():
    entitlement = enterprise_bundle("tenant-3")

    for family in ProductFamily:
        assert entitlement.allows_family(family)


def test_enterprise_bundle_can_exclude_research_and_hardware():
    entitlement = enterprise_bundle(
        "tenant-4",
        include_research=False,
        include_hardware_surfaces=False,
    )

    assert entitlement.allows_family(ProductFamily.CORE)
    assert entitlement.allows_family(ProductFamily.SPATIAL)
    assert entitlement.allows_family(ProductFamily.ENTERPRISE)
    assert not entitlement.allows_family(ProductFamily.RESEARCH)
    assert not entitlement.allows_family(ProductFamily.ROBOTICS)
    assert not entitlement.allows_family(ProductFamily.MANUFACTURING)
    assert not entitlement.allows_family(ProductFamily.EDGE)


def test_snapshot_is_stable_and_serializable():
    entitlement = CommercialEntitlement(
        tenant_id="tenant-5",
        families=frozenset({ProductFamily.MANUFACTURING}),
    )
    snapshot = entitlement.snapshot()

    assert snapshot["tenant_id"] == "tenant-5"
    assert snapshot["families"] == ["manufacturing"]
    assert "manufacturing.gcode" in snapshot["effective_features"]
