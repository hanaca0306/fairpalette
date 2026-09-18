import unittest

from fairpalette import (
    AdapterAttribution,
    DiffusersAttributionSession,
    ManifestValidationError,
)


class FakePipeline:
    def __init__(self) -> None:
        self.calls: list[tuple[list[str], list[float]]] = []

    def set_adapters(
        self, adapter_names: list[str], adapter_weights: list[float] | None = None
    ) -> str:
        self.calls.append((adapter_names, adapter_weights or []))
        return "configured"


class FailingPipeline(FakePipeline):
    def set_adapters(
        self, adapter_names: list[str], adapter_weights: list[float] | None = None
    ) -> str:
        raise RuntimeError("pipeline rejected adapters")


class DiffusersAttributionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registrations = {
            "linework": AdapterAttribution("artist_A", "commercial_allowed"),
            "color": AdapterAttribution("artist_B", metadata={"source": "registry"}),
        }

    def test_tracks_successful_set_adapters_call(self) -> None:
        pipeline = FakePipeline()
        session = DiffusersAttributionSession(
            pipeline,
            base_model="stabilityai/sdxl",
            adapter_attribution=self.registrations,
        )

        result = session.set_adapters(["linework", "color"], [0.7, 0.3])
        manifest = session.create_manifest("gen_001", metadata={"prompt_hash": "abc"})

        self.assertEqual(result, "configured")
        self.assertEqual(pipeline.calls, [(["linework", "color"], [0.7, 0.3])])
        self.assertEqual(
            [item.applied_weight for item in manifest.contributors], [0.7, 0.3]
        )
        self.assertEqual(manifest.metadata, {"prompt_hash": "abc"})

    def test_single_adapter_defaults_to_full_weight(self) -> None:
        session = DiffusersAttributionSession(
            FakePipeline(),
            base_model="sdxl",
            adapter_attribution=self.registrations,
        )

        session.set_adapters("linework")

        self.assertEqual(session.active_contributors[0].applied_weight, 1.0)

    def test_rejects_unregistered_adapter_before_calling_pipeline(self) -> None:
        pipeline = FakePipeline()
        session = DiffusersAttributionSession(
            pipeline,
            base_model="sdxl",
            adapter_attribution=self.registrations,
        )

        with self.assertRaisesRegex(ManifestValidationError, "missing attribution"):
            session.set_adapters("unknown")

        self.assertEqual(pipeline.calls, [])

    def test_failed_pipeline_call_does_not_replace_active_contributors(self) -> None:
        session = DiffusersAttributionSession(
            FailingPipeline(),
            base_model="sdxl",
            adapter_attribution=self.registrations,
        )

        with self.assertRaisesRegex(RuntimeError, "rejected"):
            session.set_adapters("linework")

        self.assertEqual(session.active_contributors, ())
        with self.assertRaisesRegex(ManifestValidationError, "must succeed"):
            session.create_manifest("gen_001")


if __name__ == "__main__":
    unittest.main()
