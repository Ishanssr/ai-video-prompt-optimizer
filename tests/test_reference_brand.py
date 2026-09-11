"""Reference integrity (immutable identity) + brand feature applicability."""

from engine import (
    create_reference_profile, vehicle_identity, assert_vehicle_identity_untouched,
    IMMUTABLE_VEHICLE_ATTRS, MUTABLE_VEHICLE_ATTRS, ScaleGraph,
    validate_model_feature, get_brand_policy, get_model_spec,
)


def test_immutable_vs_mutable_attributes():
    assert "model" in IMMUTABLE_VEHICLE_ATTRS
    assert "colour" in IMMUTABLE_VEHICLE_ATTRS
    assert "position" in MUTABLE_VEHICLE_ATTRS
    assert "orientation" in MUTABLE_VEHICLE_ATTRS
    assert "position" not in IMMUTABLE_VEHICLE_ATTRS


def test_identity_terms_extracted():
    ref = create_reference_profile(vehicle_model="Creta", vehicle_colour="abyss black")
    identity = vehicle_identity(ref)
    assert identity["model"] == "Creta"
    assert identity["colour"] == "abyss black"


def test_identity_colour_mismatch_detected():
    ref = create_reference_profile(vehicle_model="Creta", vehicle_colour="abyss black")
    issues = assert_vehicle_identity_untouched(ref, scene_colour="White", scene_model="Creta")
    assert any("colour" in i for i in issues)


def test_scale_graph_present():
    ref = create_reference_profile(vehicle_model="Creta")
    assert isinstance(ref.scale, ScaleGraph)
    assert ref.scale.presenter_to_vehicle_m > 0


def test_model_feature_applicability_variant_scoped():
    appl = validate_model_feature("Hyundai", "Creta", "panoramic sunroof")
    assert appl["verifiable"] is True
    assert "SX(O)" in appl["applicable_variants"]
    assert "E" not in appl["applicable_variants"]


def test_model_feature_unavailable():
    appl = validate_model_feature("Hyundai", "Creta", "ADAS Level 2")
    assert appl["verifiable"] is True
    assert appl["applicable"] is False


def test_unknown_model_unverified():
    appl = validate_model_feature("Hyundai", "Fictional X9", "sunroof")
    assert appl["verifiable"] is False


def test_tata_nexon_safety_available():
    appl = validate_model_feature("Tata", "Nexon", "5-star GNCAP safety")
    assert appl["verifiable"] is True
    assert any("all variants" in v for v in appl["applicable_variants"]) or len(appl["applicable_variants"]) > 0


def test_tata_harrier_adas_available():
    appl = validate_model_feature("Tata", "Harrier", "ADAS")
    assert appl["verifiable"] is True
    assert appl["applicable"] is True


def test_brand_policy_approved_models():
    policy = get_brand_policy("Hyundai")
    assert "Creta" in policy.approved_model_names