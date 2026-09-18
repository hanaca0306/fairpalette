import unittest

from fairpalette import (
    AttributionSessionError,
    AttributionSessionManager,
    Contributor,
    SessionState,
)


class AttributionSessionManagerTests(unittest.TestCase):
    def make_contributor(self, module_id: str = "linework") -> Contributor:
        return Contributor("artist_A", module_id, 0.8, "commercial_allowed")

    def test_session_lifecycle_finalizes_stable_manifest(self) -> None:
        manager = AttributionSessionManager(default_base_model="sdxl")
        session = manager.start_session(
            "gen_001",
            timestamp="2026-05-26T12:00:00Z",
            metadata={"prompt_hash": "abc"},
        )
        session.add_contributor(self.make_contributor())

        manifest = manager.finalize_session("gen_001")

        self.assertIs(manifest, session.finalize())
        self.assertEqual(session.state, SessionState.FINALIZED)
        self.assertEqual(manifest.base_model, "sdxl")
        self.assertEqual(manifest.metadata, {"prompt_hash": "abc"})

    def test_accepts_initial_contributors_and_base_model_override(self) -> None:
        manager = AttributionSessionManager(default_base_model="default-model")
        session = manager.start_session(
            "gen_override",
            base_model="custom-model",
            contributors=[self.make_contributor()],
        )

        self.assertEqual(session.base_model, "custom-model")
        self.assertEqual(session.contributors, (self.make_contributor(),))
        self.assertEqual(manager.open_sessions, (session,))

    def test_rejects_duplicate_generation_id_even_after_abort(self) -> None:
        manager = AttributionSessionManager(default_base_model="sdxl")
        manager.start_session("gen_001")
        manager.abort_session("gen_001", "pipeline failed")

        with self.assertRaisesRegex(AttributionSessionError, "already managed"):
            manager.start_session("gen_001")

    def test_rejects_duplicate_module_within_session(self) -> None:
        session = AttributionSessionManager(
            default_base_model="sdxl"
        ).start_session("gen_001", contributors=[self.make_contributor()])

        with self.assertRaisesRegex(AttributionSessionError, "already recorded"):
            session.add_contributor(self.make_contributor())

    def test_finalized_session_rejects_changes(self) -> None:
        session = AttributionSessionManager(
            default_base_model="sdxl"
        ).start_session("gen_001", contributors=[self.make_contributor()])
        session.finalize()

        with self.assertRaisesRegex(AttributionSessionError, "finalized"):
            session.add_contributor(self.make_contributor("color"))
        with self.assertRaisesRegex(AttributionSessionError, "finalized"):
            session.abort()

    def test_aborted_session_cannot_finalize(self) -> None:
        manager = AttributionSessionManager(default_base_model="sdxl")
        session = manager.start_session("gen_001")
        manager.abort_session("gen_001", "cancelled")

        self.assertEqual(session.state, SessionState.ABORTED)
        self.assertEqual(session.abort_reason, "cancelled")
        self.assertEqual(manager.open_sessions, ())
        with self.assertRaisesRegex(AttributionSessionError, "aborted"):
            session.finalize()

    def test_requires_contributor_base_model_and_known_session(self) -> None:
        manager = AttributionSessionManager()
        with self.assertRaisesRegex(AttributionSessionError, "base_model is required"):
            manager.start_session("gen_001")

        configured = AttributionSessionManager(default_base_model="sdxl")
        session = configured.start_session("gen_002")
        with self.assertRaisesRegex(AttributionSessionError, "at least one contributor"):
            session.finalize()
        with self.assertRaisesRegex(AttributionSessionError, "unknown generation_id"):
            configured.get_session("missing")

    def test_rejects_invalid_timestamp_and_empty_model_override(self) -> None:
        manager = AttributionSessionManager(default_base_model="sdxl")
        with self.assertRaisesRegex(AttributionSessionError, "timezone"):
            manager.start_session("gen_time", timestamp="2026-05-26T12:00:00")
        with self.assertRaisesRegex(AttributionSessionError, "base_model"):
            manager.start_session("gen_model", base_model="")


if __name__ == "__main__":
    unittest.main()
