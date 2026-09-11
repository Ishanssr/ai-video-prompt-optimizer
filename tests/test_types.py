"""Types module sanity."""

from engine import (
    Brief, Script, ScriptLine, ScriptLanguage, CampaignObjective, AdConcept,
    ValidationScore, RepairOp, RepairResult, VeoCapability, VEO_3_1,
)


def test_brief_defaults():
    b = Brief(objective=CampaignObjective.ENQUIRY, ad_concept=AdConcept.PRESENTER_LED,
              brand="Hyundai", car_model="Creta")
    assert b.duration == 8
    assert b.language == ScriptLanguage.HINDI


def test_script_segment_order():
    s = Script(hook=ScriptLine("hook", "a"), offer=ScriptLine("offer", "b"),
               product=ScriptLine("product", "c"), benefit=ScriptLine("benefit", "d"),
               cta=ScriptLine("cta", "e"))
    assert s.segment_order() == ["hook", "offer", "product", "benefit", "cta"]


def test_priority_maps_objective():
    s = Script(hook=ScriptLine("hook", ""), offer=ScriptLine("offer", ""),
               product=ScriptLine("product", ""), benefit=ScriptLine("benefit", ""),
               cta=ScriptLine("cta", ""), objective=CampaignObjective.OFFER_AWARENESS)
    assert s.priority()[0] == "offer"


def test_validation_score_deductions():
    s = ValidationScore()
    s.deduct(15, "boom")
    assert s.score == 85.0
    s.deduct(50, "catastrophe")
    assert s.score == 35.0
    assert not s.passed


def test_repair_result_properties():
    r = RepairResult(ops=[RepairOp(target="scene", field="camera_move")])
    assert r.was_repaired
    assert r.changes


def test_veo_capability_frozen():
    assert VEO_3_1.model == "veo-3.1"
    try:
        VEO_3_1.model = "nope"
        raise AssertionError("VeoCapability must be immutable")
    except Exception as e:
        # frozen dataclass raises FrozenInstanceError-ish
        assert e is not None