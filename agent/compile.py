from typing import Any, Dict

from engine import (
    Brief, full_pipeline,
)

REQUIRED = ["objective", "ad_concept", "brand", "car_model"]


def build_brief(user_input: Dict[str, Any]) -> Brief:
    from engine import (
        CampaignObjective, AdConcept, ContentFormat, ScriptLanguage,
        GenerationMode, VoiceStyle, DeliveryPacing,
    )

    def _enum(name, values, fallback):
        raw = user_input.get(name)
        if isinstance(raw, values):
            return raw
        try:
            return values(str(raw or "").lower().replace("-", "_"))
        except (ValueError, TypeError):
            return fallback

    return Brief(
        objective=_enum("objective", CampaignObjective, CampaignObjective.ENQUIRY),
        ad_concept=_enum("ad_concept", AdConcept, AdConcept.PRESENTER_LED),
        brand=str(user_input.get("brand", "")).strip() or "Hyundai",
        car_model=str(user_input.get("car_model", "")).strip() or "Creta",
        car_colour=str(user_input.get("car_colour", "")).strip() or "white",
        format=_enum("format", ContentFormat, ContentFormat.INSTAGRAM_REEL),
        language=_enum("language", ScriptLanguage, ScriptLanguage.HINDI),
        duration=int(float(user_input.get("duration", 8))),
        generation_mode=_enum("generation_mode", GenerationMode, GenerationMode.SINGLE_SHOT),
        voice_style=_enum("voice_style", VoiceStyle, VoiceStyle.CONFIDENT),
        pacing=_enum("pacing", DeliveryPacing, DeliveryPacing.MEDIUM_FAST),
        custom_hook=user_input.get("custom_hook"),
        custom_offer=user_input.get("custom_offer"),
        custom_benefit=user_input.get("custom_benefit"),
        custom_cta=user_input.get("custom_cta"),
        offer=user_input.get("offer"),
        reference=user_input.get("reference"),
    )


def compile_brief(brief: Brief) -> Dict[str, Any]:
    return full_pipeline(brief)


def dialogue_audit(requested_brief, out: Dict[str, Any]) -> Dict[str, Any]:
    script = out.get("script")
    requested = {
        "hook": getattr(requested_brief, "custom_hook", None),
        "benefit": getattr(requested_brief, "custom_benefit", None),
        "cta": getattr(requested_brief, "custom_cta", None),
    }
    applied = {
        seg: getattr(getattr(script, seg, None), "text", "") if script else ""
        for seg in requested
    }
    dropped = [seg for seg, val in requested.items() if val and not applied.get(seg)]
    altered = [
        seg for seg, val in requested.items()
        if val and applied.get(seg) and applied.get(seg) != val and seg not in dropped
    ]
    return {"requested": requested, "applied": applied, "dropped": dropped, "altered": altered}


def artifacts_summary(out: Dict[str, Any], requested_brief: Brief = None) -> Dict[str, Any]:
    bp = out.get("blueprint")
    return {
        "narrative_prompt": out.get("prompt", ""),
        "structured_prompt": out.get("prompt_structured", ""),
        "validation": {
            "passed": out.get("validation", {}).get("passed"),
            "errors": out.get("validation", {}).get("errors", []),
            "warnings": out.get("validation", {}).get("warnings", []),
        },
        "engine_score": out.get("score", {}),
        "dialogue_audit": dialogue_audit(requested_brief, out) if requested_brief else {},
        "repair_log": out.get("repair_log", []),
        "was_repaired": out.get("was_repaired", False),
        "blueprint": {
            "objective": None if bp is None else bp.campaign.objective.value,
            "ad_concept": None if bp is None else bp.campaign.ad_concept.value,
            "dominant_action": None if bp is None else bp.action.dominant,
            "micro_behavior": None if bp is None else bp.action.micro_behavior,
            "background_behavior": None if bp is None else bp.action.background_behavior,
            "shot_type": None if bp is None else bp.shot.shot_type,
            "camera_move": None if bp is None else bp.shot.camera_move,
            "post_overlay": None if bp is None else bp.post.offer_card,
        },
        "timeline": out.get("creative", {}).get("ad_timeline"),
    }


def brief_anchor_text(brief: Brief) -> str:
    return (
        f"objective={brief.objective.value} | concept={brief.ad_concept.value} | "
        f"brand={brief.brand} | model={brief.car_model} ({brief.car_colour}) | "
        f"format={brief.format.value} | lang={brief.language.value} | duration={brief.duration}s"
    )