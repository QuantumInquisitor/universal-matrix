"""Commercial product-family entitlement model.

This module provides an implementation-neutral entitlement layer for proprietary
deployments. It does not implement billing, payment processing, contract terms,
or DRM.

Entitlements are explicit, typed, and separated from the public AGPL license.
A commercial deployment may map executed license agreements to these product
families or to finer-grained features as needed.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ProductFamily(StrEnum):
    CORE = "core"
    SPATIAL = "spatial"
    ROBOTICS = "robotics"
    MANUFACTURING = "manufacturing"
    RESEARCH = "research"
    EDGE = "edge"
    ENTERPRISE = "enterprise"


FAMILY_FEATURES: dict[ProductFamily, frozenset[str]] = {
    ProductFamily.CORE: frozenset(
        {
            "canonical.kernel",
            "canonical.projection",
            "canonical.routing",
            "sdk.core",
        }
    ),
    ProductFamily.SPATIAL: frozenset(
        {
            "spatial.xr",
            "spatial.teleoperation",
            "spatial.command_validation",
            "spatial.digital_twin_view",
        }
    ),
    ProductFamily.ROBOTICS: frozenset(
        {
            "robotics.trajectory",
            "robotics.command_validation",
            "robotics.ros2_adapter",
            "robotics.can_adapter",
            "robotics.hil",
            "robotics.swarm_research",
        }
    ),
    ProductFamily.MANUFACTURING: frozenset(
        {
            "manufacturing.gcode",
            "manufacturing.toolpath",
            "manufacturing.cnc_adapter",
            "manufacturing.visualization",
            "manufacturing.optimization",
        }
    ),
    ProductFamily.RESEARCH: frozenset(
        {
            "research.gauge",
            "research.reciprocity",
            "research.dirac",
            "research.chiral",
            "research.anomaly",
            "research.numerical",
        }
    ),
    ProductFamily.EDGE: frozenset(
        {
            "edge.hal",
            "edge.device_adapters",
            "edge.orchestration",
            "edge.telemetry",
            "edge.audit",
        }
    ),
    ProductFamily.ENTERPRISE: frozenset(
        {
            "enterprise.private_api",
            "enterprise.tenancy",
            "enterprise.entitlements",
            "enterprise.metering",
            "enterprise.deployment",
            "enterprise.audit",
        }
    ),
}


@dataclass(frozen=True)
class CommercialEntitlement:
    tenant_id: str
    families: frozenset[ProductFamily]
    extra_features: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if not self.tenant_id.strip():
            raise ValueError("tenant_id must be non-empty")

    @property
    def effective_features(self) -> frozenset[str]:
        features: set[str] = set(self.extra_features)
        for family in self.families:
            features.update(FAMILY_FEATURES[family])
        return frozenset(features)

    def allows_family(self, family: ProductFamily) -> bool:
        return family in self.families

    def allows_feature(self, feature: str) -> bool:
        return feature in self.effective_features

    def snapshot(self) -> dict[str, object]:
        return {
            "tenant_id": self.tenant_id,
            "families": sorted(family.value for family in self.families),
            "extra_features": sorted(self.extra_features),
            "effective_features": sorted(self.effective_features),
        }


def enterprise_bundle(
    tenant_id: str,
    *,
    include_research: bool = True,
    include_hardware_surfaces: bool = True,
) -> CommercialEntitlement:
    """Create a conventional full-platform commercial entitlement.

    This helper is only a software convenience. Actual legal rights come from
    the executed commercial agreement, not from this object.
    """
    families = {
        ProductFamily.CORE,
        ProductFamily.SPATIAL,
        ProductFamily.ENTERPRISE,
    }
    if include_hardware_surfaces:
        families.update(
            {
                ProductFamily.ROBOTICS,
                ProductFamily.MANUFACTURING,
                ProductFamily.EDGE,
            }
        )
    if include_research:
        families.add(ProductFamily.RESEARCH)

    return CommercialEntitlement(
        tenant_id=tenant_id,
        families=frozenset(families),
    )
