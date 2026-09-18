import json
import tempfile
import unittest
from pathlib import Path

from fairpalette import (
    CreatorRecord,
    CreatorRegistry,
    DiffusersAttributionSession,
    ModuleRegistration,
    RegistryValidationError,
)


class FakePipeline:
    def set_adapters(self, adapter_names, adapter_weights=None):
        return adapter_names, adapter_weights


class CreatorRegistryTests(unittest.TestCase):
    def make_registry(self) -> CreatorRegistry:
        return CreatorRegistry(
            creators=[
                CreatorRecord("artist_A", "Artist A"),
                CreatorRecord("artist_B", "Artist B"),
            ],
            modules=[
                ModuleRegistration("linework", "artist_A", "commercial_allowed"),
                ModuleRegistration(
                    "retired", "artist_B", "noncommercial_only", active=False
                ),
            ],
        )

    def test_round_trip_preserves_registry(self) -> None:
        registry = self.make_registry()

        with tempfile.TemporaryDirectory() as directory:
            path = registry.write(Path(directory) / "registry.json")
            restored = CreatorRegistry.read(path)

        self.assertEqual(restored, registry)

    def test_rejects_duplicate_ids_and_unknown_creator_references(self) -> None:
        with self.assertRaisesRegex(RegistryValidationError, "creator_id.*unique"):
            CreatorRegistry(
                creators=[
                    CreatorRecord("artist_A", "One"),
                    CreatorRecord("artist_A", "Two"),
                ],
                modules=[],
            )

        with self.assertRaisesRegex(RegistryValidationError, "unknown creators"):
            CreatorRegistry(
                creators=[],
                modules=[ModuleRegistration("linework", "missing", "allowed")],
            )

    def test_only_active_modules_are_available_to_diffusers(self) -> None:
        attribution = self.make_registry().active_adapter_attribution()

        self.assertEqual(list(attribution), ["linework"])
        self.assertEqual(attribution["linework"].artist_id, "artist_A")

    def test_registry_drives_diffusers_manifest(self) -> None:
        registry = self.make_registry()
        session = DiffusersAttributionSession(
            FakePipeline(),
            base_model="sdxl",
            adapter_attribution=registry.active_adapter_attribution(),
        )

        session.set_adapters("linework", 0.8)
        manifest = session.create_manifest("gen_registry")

        self.assertEqual(manifest.contributors[0].artist_id, "artist_A")
        self.assertEqual(manifest.contributors[0].license, "commercial_allowed")

    def test_example_matches_schema_shape(self) -> None:
        root = Path(__file__).parents[1]
        example = json.loads((root / "examples" / "creator_registry.json").read_text())
        schema = json.loads(
            (root / "schema" / "creator-registry-v0.1.schema.json").read_text()
        )

        registry = CreatorRegistry.from_dict(example)
        self.assertEqual(registry.registry_version, schema["properties"]["registry_version"]["const"])
        self.assertEqual(set(example), set(schema["required"]))


if __name__ == "__main__":
    unittest.main()
