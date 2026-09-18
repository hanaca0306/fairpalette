import hashlib
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from fairpalette import (
    AttributionManifest,
    Contributor,
    ManifestValidationError,
    MetadataBundle,
    RoyaltyAllocation,
    describe_asset,
    export_metadata_bundle,
)


class MetadataExportTests(unittest.TestCase):
    def make_manifest(self) -> AttributionManifest:
        return AttributionManifest(
            "gen_export",
            "sdxl",
            [Contributor("artist_A", "linework", 1.0)],
            timestamp="2026-05-26T12:00:00Z",
        )

    def test_describe_asset_hashes_content_without_exporting_full_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            asset = Path(directory) / "output.png"
            asset.write_bytes(b"generated image bytes")
            descriptor = describe_asset(asset)

        self.assertEqual(descriptor.filename, "output.png")
        self.assertEqual(descriptor.media_type, "image/png")
        self.assertEqual(descriptor.size_bytes, 21)
        self.assertEqual(
            descriptor.sha256, hashlib.sha256(b"generated image bytes").hexdigest()
        )

    def test_export_writes_manifest_asset_royalties_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            asset = root / "output.bin"
            asset.write_bytes(b"asset")
            output = export_metadata_bundle(
                self.make_manifest(),
                root / "output.fairpalette.json",
                asset_path=asset,
                royalties=[RoyaltyAllocation("artist_A", "linework", Decimal("1.25"))],
                metadata={"currency": "USD"},
            )
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(payload["format_version"], "0.1")
        self.assertEqual(payload["manifest"]["generation_id"], "gen_export")
        self.assertEqual(payload["asset"]["filename"], "output.bin")
        self.assertEqual(payload["royalties"][0]["amount"], "1.25")
        self.assertEqual(payload["metadata"], {"currency": "USD"})

    def test_manifest_only_export_uses_null_asset(self) -> None:
        bundle = MetadataBundle(self.make_manifest())

        self.assertIsNone(bundle.to_dict()["asset"])
        self.assertEqual(bundle.to_dict()["royalties"], [])

    def test_rejects_royalty_for_module_absent_from_manifest(self) -> None:
        with self.assertRaisesRegex(ManifestValidationError, "absent from manifest"):
            MetadataBundle(
                self.make_manifest(),
                royalties=[RoyaltyAllocation("artist_B", "unknown", Decimal("1.00"))],
            )

    def test_rejects_royalty_artist_that_does_not_match_manifest(self) -> None:
        with self.assertRaisesRegex(ManifestValidationError, "artists do not match"):
            MetadataBundle(
                self.make_manifest(),
                royalties=[
                    RoyaltyAllocation("artist_B", "linework", Decimal("1.00"))
                ],
            )

    def test_rejects_missing_asset(self) -> None:
        with self.assertRaisesRegex(ManifestValidationError, "does not exist"):
            describe_asset("missing-output.png")


if __name__ == "__main__":
    unittest.main()
