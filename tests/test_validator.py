"""Semantic validation: context-disambiguated camera/action + scored output."""

from engine import (
    count_camera_moves, count_primary_actions, validate_prompt, score_validation,
    validate_scene_plan, stray_camera_moves, ScriptLanguage,
    ScenePlan, ShotComposition,
    CampaignObjective, AdConcept, generate_script,
)

from engine.validator import action_intents


def test_track_led_is_not_a_camera_move():
    assert count_camera_moves("Bright showroom track LEDs, warm and even.") == 0


def test_track_lighting_phrase_not_a_move():
    assert count_camera_moves("overhead track lighting glows softly.") == 0


def test_real_camera_moves_detected():
    assert count_camera_moves("camera tracking the subject") == 1
    assert count_camera_moves("slow push-in") == 1
    assert count_camera_moves("camera panning left, then orbits far") >= 2


def test_stray_camera_outside_cinematography_clause():
    prompt = (
        "Cinematography: medium shot with a slow push-in\n"
        "Context: camera orbit after the subject enters the showroom"
    )
    stray = stray_camera_moves(prompt, plan_move="slow push-in")
    assert any(s[0] == "orbit" for s in stray), stray


def test_action_intents_semantic():
    assert action_intents("presenter speaks directly to camera") == ["presenter_address"]
    assert "camera move" not in action_intents("SFX: subtle whoosh on camera move")


def test_count_primary_actions_single_intent():
    assert count_primary_actions("presenter speaks directly to camera") == 1


def test_count_primary_actions_unified_primary_plus_beat():
    # primary + one supporting beat = 2 distinct intents by design
    unified = "presenter speaks directly to camera while gesturing toward the car"
    assert count_primary_actions(unified) == 2


def test_validate_prompt_short_warns():
    r = validate_prompt("A man.", target_duration=8)
    assert any("short" in w.lower() for w in r.warnings)


def test_validate_prompt_fails_on_stray_camera():
    scene = ScenePlan(
        duration=8, camera_move="slow push-in", subject="salesperson",
        primary_action="presenter speaks directly to camera",
        composition=ShotComposition(camera_move="slow push-in"),
    )
    prompt = "Cinematography: medium shot with a slow push-in\nContext: camera pans away"
    r = validate_prompt(prompt, scene=scene, target_duration=8)
    assert not r.passed
    assert any("Stray camera" in e for e in r.errors)


def test_score_and_grade():
    r = validate_prompt("short", target_duration=8)
    score = score_validation(r)
    assert 0.0 <= score.score <= 100.0
    assert score.grade in ("A", "B", "C", "D", "F")


def test_validate_scene_plan_empty_subject():
    scene = ScenePlan()
    r = validate_scene_plan(scene)
    assert any("subject" in e.lower() for e in r.errors)


def test_validate_scene_plan_camera_single():
    scene = ScenePlan(camera_move="slow push-in", subject="presenter",
                      primary_action="presenter speaks directly to camera")
    r = validate_scene_plan(scene, duration=8)
    assert not any("camera" in e for e in r.errors)


def test_validates_passed_default_language():
    scene = ScenePlan(camera_move="static", subject="presenter",
                      primary_action="presenter speaks directly to camera",
                      duration=8)
    r = validate_scene_plan(scene, duration=8)
    assert r.passed or len(r.errors) <= 1