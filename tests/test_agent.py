"""Offline agent tests for the LangGraph layer (zero provider SDKs required).

Run with the project venv (has langgraph):
    ./.venv/bin/python tests/run_agent_all.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import run_agent, default_config, AgentConfig
from agent.llm import FakeLLM, LLMClient, get_client
from agent.mutations import apply_mutations, IMMUTABLE, TARGET_SCHEMA
from agent.compile import build_brief, compile_brief, dialogue_audit

import tempfile
import json

NEW_LAUNCH_INPUT = {
    "objective": "new_launch",
    "ad_concept": "reveal",
    "brand": "Hyundai",
    "car_model": "Creta",
    "car_colour": "abyss black",
    "duration": 8,
    "language": "hindi",
    "creative_direction": "premium new-launch reveal feel, high energy, short punchy hook",
}


def test_default_config_is_offline():
    cfg = default_config().resolve()
    assert cfg.provider == "fake"
    assert get_client(cfg) is not None


def test_run_agent_converges_in_two_rounds():
    result = run_agent(NEW_LAUNCH_INPUT)
    assert result.accepted is True
    assert result.rounds == 2
    assert result.validation.get("passed") is True
    assert result.critique["total"] >= 85


def test_modifier_hook_lands_in_final_prompt():
    result = run_agent(NEW_LAUNCH_INPUT)
    assert "Nayi Creta, abhi dekhiye." in result.prompt


def test_run_agent_respects_max_iterations():
    cfg = default_config()
    cfg.max_iterations = 1
    cfg.target_score = 200  # unreachable gate -> forces the cap
    result = run_agent(NEW_LAUNCH_INPUT, config=cfg)
    assert result.rounds == 1
    assert result.accepted is False


def test_agent_writes_jsonl_audit_trail():
    cfg = default_config()
    cfg.audit_dir = tempfile.mkdtemp(prefix="veo_agent_test_")
    result = run_agent(NEW_LAUNCH_INPUT, config=cfg)
    trail_path = os.path.join(cfg.audit_path(), "trail.jsonl")
    assert os.path.exists(trail_path)
    rows = [json.loads(line) for line in open(trail_path)]
    nodes = [r["node"] for r in rows]
    assert nodes == ["strategist", "critic", "modifier", "critic", "finalize"]


def test_immutable_targets_are_rejected():
    b = build_brief(NEW_LAUNCH_INPUT)
    _, rejected = apply_mutations(b, [{"target": "brand", "value": "Maruti"}])
    assert rejected == ["brand: immutable anchor, cannot change"]


def test_unknown_targets_are_rejected():
    b = build_brief(NEW_LAUNCH_INPUT)
    _, rejected = apply_mutations(b, [{"target": "car_transmission", "value": "auto"}])
    assert "car_transmission: not a mutable agent target" in rejected[0]


def test_duration_bounds_match_veo():
    spec = TARGET_SCHEMA["duration"]
    assert spec["type"] == "int"
    assert spec["min"] == 4 and spec["max"] == 8
    b = build_brief(NEW_LAUNCH_INPUT)
    _, rejected = apply_mutations(b, [{"target": "duration", "value": 10}])
    assert rejected
    _, rejected = apply_mutations(b, [{"target": "duration", "value": 8}])
    assert not rejected


def test_dialogue_audit_surfaces_dropped_segments():
    b = build_brief(dict(
        NEW_LAUNCH_INPUT,
        custom_hook="Nayi Creta — aapke sapno mein hai.",
        custom_benefit="Nayi design, nayi power.",
        custom_cta="Abhi test drive book kijiye.",
    ))
    out = compile_brief(b)
    audit = dialogue_audit(b, out)
    assert audit["requested"]["hook"] == "Nayi Creta — aapke sapno mein hai."
    assert set(audit.keys()) == {"requested", "applied", "dropped", "altered"}


def test_reveal_prompt_has_no_false_gesture_conflict():
    b = build_brief(NEW_LAUNCH_INPUT)
    out = compile_brief(b)
    assert out["validation"]["passed"] is True
    errors = " ".join(out["validation"]["errors"])
    assert "conflict" not in errors


def test_long_strategist_hook_is_surfaced_as_altered():
    b = build_brief(NEW_LAUNCH_INPUT)
    from agent.mutations import strategist_to_mutations
    from agent import llm
    cfg = default_config().resolve()
    client = llm.get_client(cfg)
    resp = client.complete_json("CREATIVE STRATEGIST system", "brief", schema_hint="")
    b2, rejected = apply_mutations(b, strategist_to_mutations(resp))
    assert not rejected
    out = compile_brief(b2)
    audit = dialogue_audit(b2, out)
    assert audit["requested"]["hook"] == "Nayi Creta — aapke sapno mein hai."
    assert "hook" not in audit["applied"] or audit["applied"]["hook"] != audit["requested"]["hook"]


if __name__ == "__main__":
    failed = 0
    count = 0
    for name, fn in sorted(globals().items()):
        if callable(fn) and name.startswith("test_"):
            count += 1
            try:
                fn()
                print(f"   ok  {name}")
            except Exception:
                failed += 1
                print(f"   FAIL {name}")
                import traceback

                traceback.print_exc()
    print(f"\n{count} tests, {failed} failed")
    sys.exit(1 if failed else 0)