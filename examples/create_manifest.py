from decimal import Decimal

from fairpalette import AttributionManifest, Contributor, calculate_royalties


contributors = [
    Contributor("artist_A", "lora_A", 0.7, "commercial_allowed"),
    Contributor("artist_B", "lora_B", 0.3, "commercial_allowed"),
]
manifest = AttributionManifest(
    generation_id="gen_20260526_001",
    base_model="stabilityai/stable-diffusion-xl-base-1.0",
    contributors=contributors,
)

print(manifest.to_json())
print(calculate_royalties(Decimal("10.00"), contributors))
