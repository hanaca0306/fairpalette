import json
import unittest
from pathlib import Path

from fairpalette import AttributionManifest, Contributor


class SchemaTests(unittest.TestCase):
    def test_schema_is_valid_json_and_matches_sdk_shape(self) -> None:
        root = Path(__file__).parents[1]
        schema = json.loads(
            (root / "schema" / "attribution-manifest-v0.1.schema.json").read_text()
        )
        payload = AttributionManifest(
            "gen_001",
            "sdxl",
            [Contributor("artist_A", "lora_A", 1.0)],
            timestamp="2026-05-26T12:00:00Z",
        ).to_dict()

        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(set(schema["required"]), set(payload))
        self.assertEqual(
            set(schema["properties"]["contributors"]["items"]["required"]),
            set(payload["contributors"][0]),
        )
