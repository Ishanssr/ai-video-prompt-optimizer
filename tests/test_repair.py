"""Structural repair: fix the PLAN, then recompile — never regex the prose."""

from engine import (
    ScenePlan, ShotComposition, CampaignObjective, AdConcept, ScriptLanguage,
    diagnose_scene, diagnose_script, apply_repairs, repair_plan,
    generate_script, SpeechModel,
    RepairOp,
)


def _scene(camera_move="slow push-in", subject="salesperson", secondary="", action="presenter speaks directly to camera"):
    return ScenePlan(
        duration=8, camera_move=camera_move, subject=subject,
        secondary_subject=secondary, primary_action=action,
        composition=ShotComposition(camera_move=camera_move, shot_type="medium shot"),
    )


def test_camera_conflation_repaired():
    s = _scene(camera_move="slow push-in and then camera orbit")
    ops = diagnose_scene(s)
    assert any(o.field == "camera_move" for o in ops)
    fixed, _ = apply_repairs(s, None, ops, 8)
    assert fixed.camera_move == "slow push-in"
    assert s.camera_move == "slow push-in and then camera orbit"  # original untouched


def test_subject_dedup_repaired():
    s = _scene(subject="White Creta", secondary="White Creta")
    ops = diagnose_scene(s)
    assert any(o.field == "subject" for o in ops)
    fixed, _ = apply_repairs(s, None, ops, 8)
    assert fixed.subject == ""


def test_action_conflation_repaired():
    s = _scene(action="presenter speaks directly to camera while walking and inspecting")
    ops = diagnose_scene(s)
    assert any(o.field == "primary_action" for o in ops)
    fixed, _ = apply_repairs(s, None, ops, 8)
    assert fixed.primary_action  # set to a single canonical intent


def test_superlative_script_line_repaired():
    script = generate_script(CampaignObjective.ENQUIRY, AdConcept.PRESENTER_LED, ScriptLanguage.HINDI,
                             custom_hook="Ye hamari best-selling SUV hai.")
    ops = diagnose_script(script, 8)
    assert any(o.field == "line:hook" for o in ops)
    _, fixed = apply_repairs(None, script, ops, 8)
    assert "best-selling" not in fixed.hook.text.lower()


def test_dialogue_overbudget_repaired():
    script = generate_script(CampaignObjective.ENQUIRY, AdConcept.PRESENTER_LED, ScriptLanguage.HINDI)
    long = script.rewrite_to_fit(30)  # 30s -> keeps everything
    long.hook = long.hook.__class__(segment="hook", text=long.hook.text * 3, condensed=long.hook.condensed)
    s = _scene()
    ops = diagnose_script(long, 8)
    assert any(o.field == "dialogue" for o in ops)
    _, fixed = apply_repairs(s, long, ops, 8)
    report = SpeechModel.fit_report(fixed.dialogue_text(8), 8, ScriptLanguage.HINDI)
    assert report["fits_at_all"]


def test_repair_plan_recompiles_via_callback():
    script = generate_script(CampaignObjective.ENQUIRY, AdConcept.PRESENTER_LED, ScriptLanguage.HINDI,
                             custom_hook="Ye hamari best-selling SUV hai.")
    s = _scene(camera_move="slow push-in and then camera orbit")

    called = {"n": 0}

    def recompile(scene, sc):
        called["n"] += 1
        return f"compiled::{scene.camera_move}::{sc.hook.text}"

    result = repair_plan(s, script, None, duration=8, recompile=recompile)
    assert called["n"] >= 1
    assert result.prompt.startswith("compiled::slow push-in")
    assert "best-selling" not in result.prompt
    assert any(isinstance(op, RepairOp) for op in result.ops)
    assert result.was_repaired


def test_clean_plan_requires_no_repair():
    # a genuinely short script (well under the safe budget) attracts no repairs
    s = _scene()
    script = generate_script(
        CampaignObjective.ENQUIRY, AdConcept.PRESENTER_LED, ScriptLanguage.HINDI,
        custom_hook="Hola.", custom_offer="Special offer.", custom_benefit="Totally safe.",
        custom_cta="Visit kijiye.",
    )
    result = repair_plan(s, script, None, duration=8)
    assert not result.was_repaired, result.changes
    assert result.ops == []