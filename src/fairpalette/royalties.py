"""Transparent royalty allocation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from typing import Sequence

from .manifest import Contributor, ManifestValidationError


@dataclass(frozen=True, slots=True)
class RoyaltyAllocation:
    artist_id: str
    module_id: str
    amount: Decimal


def calculate_royalties(
    total_payment: Decimal,
    contributors: Sequence[Contributor],
    *,
    platform_fee_rate: Decimal = Decimal("0"),
    infrastructure_cost_rate: Decimal = Decimal("0"),
    currency_precision: Decimal = Decimal("0.01"),
) -> list[RoyaltyAllocation]:
    """Allocate the creator pool by normalized declared adapter weights.

    Rounding remainder is assigned to the last contributor so allocations always
    add up exactly to the creator pool at the requested currency precision.
    """

    if total_payment < 0:
        raise ManifestValidationError("total_payment cannot be negative")
    if not contributors:
        raise ManifestValidationError("contributors must not be empty")
    if platform_fee_rate < 0 or infrastructure_cost_rate < 0:
        raise ManifestValidationError("fee rates cannot be negative")
    if platform_fee_rate + infrastructure_cost_rate > 1:
        raise ManifestValidationError("combined fee rates cannot exceed 1")

    pool = (total_payment * (1 - platform_fee_rate - infrastructure_cost_rate)).quantize(
        currency_precision
    )
    total_weight = sum(Decimal(str(item.applied_weight)) for item in contributors)
    allocated = Decimal("0")
    result: list[RoyaltyAllocation] = []

    for index, contributor in enumerate(contributors):
        if index == len(contributors) - 1:
            amount = pool - allocated
        else:
            amount = (
                pool * Decimal(str(contributor.applied_weight)) / total_weight
            ).quantize(currency_precision, rounding=ROUND_DOWN)
            allocated += amount
        result.append(RoyaltyAllocation(contributor.artist_id, contributor.module_id, amount))

    return result
