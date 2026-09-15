from typing import Any, Dict, Optional, TypedDict

from langgraph.graph import StateGraph, END, START

from .audit import AuditTrail
from .compile import artifacts_summary, brief_anchor_text, build_brief, compile_brief
from .llm import LLMClient
from .mutations import apply_mutations, strategist_to_mutations
from .rubric import Critique, critic_prompt_schema


class AgentState(TypedDict, total=False):
    user_input: Dict[str, Any]
    brief: Any
    target_score: int
    max_iterations: int
    provider: str
    model: str
    iteration: int
    current_out: Dict[str, Any]
    best: Dict[str, Any]
    critique: Optional[Critique]
    accepted: bool
    engine_ok: bool
    mutation_report: list
    result: Dict[str, Any]
    audit: AuditTrail


STRATEGIST_SYS = (
    "You are the CREATIVE STRATEGIST of an automotive-dealer AI video agent engine. "
    "The deterministic engine produces a canonical CreativeBlueprint and a Veo 3.1 "
    "probability critical plan for a single 8s vertical ad. You must improve only the "
    "creative surface the engine accepts: hook, offer framing, benefit, CTA, voice "
    "style, pacing, duration, and (rarely) ad concept. Never invent offers, numbers, "
    "or facts. The engine's brand/offer/validation guards are final."
)

CRITIC_SYS = (
    "You are the EXECUTIVE CREATIVE DIRECTOR CRITIC of a Veo 3.1 video prompt engine. "
    "Review the compiled artifacts like a ruthless art director who knows Veo motion: "
    "one dominant action only, continuous micro-behavior, usable 9:16 frame, no "
    "readable text/logos in-frame (post-composite), speech within budget, brand-safe "
    "claims. Score each dim, list concrete reparable issues only. "
    "If dialogue_audit shows a requested line was dropped or altered (replaced "
    "during fit), a proposed creative line did NOT survive the speech budget: "
    "fail dialogue_fit and demand a strictly shorter replacement (<=8 words) "
    "for each affected segment."
)

MODIFIER_SYS = (
    "You are the REFINEMENT AGENT. Given the critic's issues and the current brief "
    "state, propose bounded typed mutations. Targets: custom_hook, custom_offer, "
    "custom_benefit, custom_cta, voice_style, pacing, duration, ad_concept. "
    "Never touch objective/brand/model/offer/reference. Never invent offer numbers. "
    "If the critic reported a dropped or altered segment, propose a shorter "
    "replacement (<=8 words) for the same target. Return JSON: "
    "{\"mutations\": [{\"target\": ..., \"value\": ...}], "
    "\"notes\": \"...\"}. Empty mutations means the plan is already strong."
)


def _pass_count(state: AgentState) -> int:
    return int(state.get("iteration") or 0)


def _update_best(state: AgentState, critique: Critique, out: Dict[str, Any], engine_ok: bool):
    current_best: Optional[Dict[str, Any]] = state.get("best")
    candidate = {"out": out, "critique": critique, "engine_ok": engine_ok}
    if current_best is None:
        return candidate
    cur_ok = current_best.get("engine_ok", False)
    new_ok = engine_ok
    if cur_ok != new_ok:
        return candidate if new_ok else current_best
    return candidate if critique.total >= current_best["critique"].total else current_best


def build_graph(config, llm: LLMClient, audit: AuditTrail):
    def strategist(state: AgentState) -> Dict[str, Any]:
        b = build_brief(state["user_input"])
        anchor = brief_anchor_text(b)
        themes = "\n".join(
            f"- {k}: {v}" for k, v in (state.get("user_input") or {}).items()
            if k not in {"objective", "ad_concept", "brand", "car_model"}
        ) or "- (no extra creative direction)"
        resp = llm.complete_json(
            STRATEGIST_SYS,
            f"Brief:\n{anchor}\nCreative direction:\n{themes}\n"
            "Propose the initial creative surface (short, claim-safe, campaign voice).",
            schema_hint=(
                'Return STRICT JSON: {"custom_hook": str, "custom_benefit": str, '
                '"custom_cta": str, "offer_framing": str, "voice_style": str, '
                '"pacing": str, "duration": int, "ad_concept": str, "rationale": str}'
            ),
        )
        mutations = strategist_to_mutations(resp)
        b2, rejected = apply_mutations(b, mutations)
        out = compile_brief(b2)
        audit.log(
            "strategist", provider=config.provider, model=config.model,
            input_preview={"brief": anchor, "themes": themes},
            output={"mutations": mutations, "rejected": rejected},
            iteration=1,
        )
        return {"brief": b2, "current_out": out, "iteration": 1,
                "mutations_rejected": rejected}

    def critic(state: AgentState) -> Dict[str, Any]:
        out = state["current_out"]
        engine_ok = bool(out.get("validation", {}).get("passed") or False)
        summary = artifacts_summary(out, requested_brief=state.get("brief"))
        resp = llm.complete_json(
            CRITIC_SYS + "\n" + critic_prompt_schema(),
            "Compiled artifacts:\n" + _dump(summary),
        )
        critique = Critique.from_llm(resp)
        best = _update_best(state, critique, out, engine_ok)
        audit.log(
            "critic", provider=config.provider, model=config.model,
            input_preview={"engine_ok": engine_ok, "dims": critique.dims},
            output={"total": critique.total, "passed": critique.passed,
                    "issues": critique.issues},
            score=critique.total, iteration=_pass_count(state),
        )
        return {"critique": critique, "best": best, "engine_ok": engine_ok,
                "accepted": engine_ok and critique.gated_passed(state["target_score"])[0]}

    def modifier(state: AgentState) -> Dict[str, Any]:
        b = state["brief"]
        critique = state["critique"]
        issues = (critique.issues if critique else [])[:6]
        anchor = brief_anchor_text(b)
        resp = llm.complete_json(
            MODIFIER_SYS,
            f"Current brief: {anchor}\n"
            f"Critic total: {critique.total if critique else '?'}\n"
            f"Critic issues:\n" + ("\n".join(f"- {i}" for i in issues) or "- none") +
            "\nPropose the next bounded mutation round.",
            schema_hint=(
                'Return STRICT JSON: {"mutations": [{"target": str, "value": any}], '
                '"notes": str}'
            ),
        )
        mutations = list((resp.get("mutations") or []))
        b2, rejected = apply_mutations(b, mutations)
        out = compile_brief(b2)
        audit.log(
            "modifier", provider=config.provider, model=config.model,
            input_preview={"issues": issues[:3]},
            output={"mutations": mutations, "rejected": rejected},
            iteration=_pass_count(state) + 1,
        )
        return {"brief": b2, "current_out": out, "iteration": _pass_count(state) + 1,
                "mutations_rejected": rejected}

    def finalize(state: AgentState) -> Dict[str, Any]:
        best = state.get("best") or {}
        out = best.get("out") or state.get("current_out") or {}
        critique = best.get("critique") or state.get("critique")
        accepted = bool(best.get("engine_ok", state.get("engine_ok", False)))
        if accepted and critique:
            accepted = critique.gated_passed(state["target_score"])[0]
        result = {
            "accepted": accepted,
            "rounds": _pass_count(state),
            "prompt": out.get("prompt", ""),
            "prompt_structured": out.get("prompt_structured", ""),
            "blueprint": out.get("blueprint"),
            "validation": out.get("validation", {}),
            "engine_score": out.get("score", {}),
            "repair_log": out.get("repair_log", []),
            "was_repaired": out.get("was_repaired", False),
            "critique": critique.as_dict() if critique else {},
            "mutations_rejected": state.get("mutations_rejected", []),
            "provider": config.provider,
            "model": config.model,
            "audit_dir": str(audit.run_dir),
        }
        audit.write_final(result)
        audit.log("finalize", provider=config.provider, model=config.model,
                  output={"accepted": accepted, "rounds": _pass_count(state)},
                  score=critique.total if critique else None)
        return {"result": result}

    g = StateGraph(AgentState)
    g.add_node("strategist", strategist)
    g.add_node("critic", critic)
    g.add_node("modifier", modifier)
    g.add_node("finalize", finalize)
    g.add_edge(START, "strategist")
    g.add_edge("strategist", "critic")

    def router(state: AgentState) -> str:
        accepted = bool(state.get("accepted"))
        iteration = _pass_count(state)
        if accepted or iteration >= state["max_iterations"]:
            return "finalize"
        return "modifier"

    g.add_conditional_edges("critic", router, {"finalize": "finalize", "modifier": "modifier"})
    g.add_edge("modifier", "critic")
    g.add_edge("finalize", END)
    return g.compile()


def _dump(obj, limit: int = 1400) -> str:
    import json

    text = json.dumps(obj, default=str, ensure_ascii=False, indent=1)
    return text[:limit] + ("\n...[truncated]" if len(text) > limit else "")