"""Full pipeline: honest orchestration from a single Brief."""

from engine import (
    Brief, CampaignObjective, AdConcept, ContentFormat, ScriptLanguage,
    GenerationMode, OfferType, create_verified_offer, full_pipeline,
    resolve_visual_action, create_reference_profile,
)


def _brief(**overrides):
    data = dict(
        objective=CampaignObjective.ENQUIRY,
        ad_concept=AdConcept.PRESENTER_LED,
        brand="Hyundai",
        car_model="Creta",
        car_colour="White",
        format=ContentFormat.INSTAGRAM_REEL,
        language=ScriptLanguage.HINDI,
        duration=8,
    )
    data.update(overrides)
    return Brief(**data)


def test_orchestrates_every_layer():
    out = full_pipeline(_brief())
    for key in ("creative", "script", "scene", "prompt", "prompt_narrative",
                "overlay_plan", "validation", "score", "repair_log", "timeline"):
        assert key in out, f"missing {key}"


def test_scene_uses_creative_action_source():
    b = _brief()
    out = full_pipeline(b)
    expected = resolve_visual_action(b.objective, b.ad_concept)["primary"]
    assert out["scene"].primary_action == expected


def test_clean_brief_validates_clean():
    b = _brief(offer=create_verified_offer(
        OfferType.EXCHANGE_BONUS, unit="₹", numeric_value=25000,
        validity="31 Dec 2026", model="Creta", source="dealer memo",
    ))
    out = full_pipeline(b)
    assert out["validation"]["passed"], out["validation"]["errors"]
    assert out["score"]["final"] >= 70


def test_prompt_has_all_sections():
    out = full_pipeline(_brief())
    lines = out["prompt"].split("\n")
    prefixes = ["Cinematography:", "Subject:", "Action:", "Context:", "Style:",
                "Audio:", "Format:"]
    for p in prefixes:
        assert any(l.startswith(p) for l in lines), p


def test_overlay_split_present():
    out = full_pipeline(_brief())
    assert out["overlay_plan"]["generated_in_veo"]
    assert "CTA text overlay" in out["overlay_plan"]["composited_after"]


def test_narrative_paragraph_compiles():
    out = full_pipeline(_brief())
    assert len(out["prompt_narrative"].split()) > 30


def test_timeline_derived_from_speech():
    out = full_pipeline(_brief())
    assert "speech_paced" in out["timeline"], out["timeline"]


def test_unverified_numbers_are_flagged():
    out = full_pipeline(_brief(custom_offer="₹60,000 cashback mil raha hai."))
    finance_error = any("₹" in e or "cashback" in e or "specific numbers" in e for e in out["validation"]["errors"])
    assert finance_error or any("cashback" in r for r in out["repair_log"])


def test_superlative_repaired():
    out = full_pipeline(_brief(custom_hook="Ye hamari best-selling SUV hai.", duration=10))
    dialogue = out["script"].dialogue_text(10).lower()
    assert "best-selling" not in dialogue


def test_reference_identity_flows_to_prompt():
    ref = create_reference_profile(vehicle_model="Creta", vehicle_colour="Deep Forest")
    out = full_pipeline(_brief(reference=ref))
    assert "Deep Forest" in out["prompt"]


def test_multishot_timed_mode():
    out = full_pipeline(_brief(objective=CampaignObjective.BOOKING,
                               ad_concept=AdConcept.PRESENTER_LED,
                               brand="Maruti Suzuki", car_model="Baleno",
                               car_colour="Nexa blue",
                               generation_mode=GenerationMode.MULTI_SHOT_TIMED))
    assert out["prompt_timed"]
    assert "[" in out["prompt_timed"]


def test_legacy_positional_style_still_works():
    out = full_pipeline(
        CampaignObjective.ENQUIRY, AdConcept.PRESENTER_LED,
        "Creta", "White", "Hyundai",
        duration=8,
    )
    assert out["prompt"]


def test_reference_colour_mismatch_caught_by_validator():
    ref = create_reference_profile(vehicle_model="Creta", vehicle_colour="Deep Forest")
    out = full_pipeline(_brief(car_colour="White", reference=ref))
    integrity = any("colour" in e.lower() for e in out["validation"]["errors"])
    # colour mismatch should at minimum be surfaced as an error or a warning:
    assert integrity or any("colour" in w.lower() for w in out["validation"]["warnings"])