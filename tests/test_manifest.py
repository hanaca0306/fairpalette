import json
import unittest
from decimal import Decimal

from fairpalette import (
    AttributionManifest,
    Contributor,
    ManifestValidationError,
    calculate_royalties,
)


class ManifestTests(unittest.TestCase):
    def test_manifest_serializes_with_version_and_metadata(self) -> None:
        manifest = AttributionManifest(
            generation_id="gen_001",
            base_model="sdxl",
            contributors=[Contributor("artist_A", "lora_A", 0.7)],
            timestamp="2026-05-26T12:00:00Z",
        )

        payload = json.loads(manifest.to_json())
        self.assertEqual(payload["spec_version"], "0.1")
        self.assertEqual(payload["contributors"][0]["module_id"], "lora_A")
        self.assertEqual(payload["metadata"], {})

    def test_contributor_rejects_invalid_weight(self) -> None:
        for weight in (0, -0.1, True, "0.5"):
            with self.subTest(weight=weight), self.assertRaises(ManifestValidationError):
                Contributor("artist_A", "lora_A", weight)  # type: ignore[arg-type]

    def test_manifest_rejects_duplicate_modules(self) -> None:
        contributors = [
            Contributor("artist_A", "shared", 0.7),
            Contributor("artist_B", "shared", 0.3),
        ]
        with self.assertRaisesRegex(ManifestValidationError, "unique"):
            AttributionManifest("gen_001", "sdxl", contributors)

    def test_royalties_apply_fees_and_preserve_pool_total(self) -> None:
        contributors = [
            Contributor("artist_A", "lora_A", 0.7),
            Contributor("artist_B", "lora_B", 0.3),
        ]
        allocations = calculate_royalties(
            Decimal("10.00"),
            contributors,
            platform_fee_rate=Decimal("0.10"),
            infrastructure_cost_rate=Decimal("0.05"),
        )

        self.assertEqual(
            [item.amount for item in allocations],
            [Decimal("5.95"), Decimal("2.55")],
        )
        self.assertEqual(sum(item.amount for item in allocations), Decimal("8.50"))

    def test_royalties_reject_fee_rates_above_one(self) -> None:
        with self.assertRaises(ManifestValidationError):
            calculate_royalties(
                Decimal("10"),
                [Contributor("artist_A", "lora_A", 1)],
                platform_fee_rate=Decimal("0.8"),
                infrastructure_cost_rate=Decimal("0.3"),
            )
