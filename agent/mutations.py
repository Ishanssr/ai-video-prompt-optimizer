from typing import Any, Dict, List, Tuple

from engine import (
    Brief, AdConcept, VoiceStyle, DeliveryPacing, ScriptLanguage,
    ContentFormat, GenerationMode,
)

IMMUTABLE = {"objective", "brand", "car_model", "car_colour", "format", "language", "offer", "reference"}

TARGET_SCHEMA = {
    "custom_hook": {"type": "str", "max_len": 90, "hint": "short attention-grabbing hook line"},
    "custom_offer": {"type": "str", "max_len": 110, "hint": "offer framing; numbers only if they came from the verified offer"},
    "custom_benefit": {"type": "str", "max_len": 90, "hint": "product benefit line"},
    "custom_cta": {"type": "str", "max_len": 70, "hint": "specific actionable CTA"},
    "voice_style": {"type": "enum", "enum": VoiceStyle},
    "pacing": {"type": "enum", "enum": DeliveryPacing},
    "duration": {"type": "int", "min": 4, "max": 8, "hint": "Veo 3.1 only supports 4, 6, or 8 seconds"},
    "ad_concept": {"type": "enum", "enum": AdConcept, "hint": "unless the objective demands a different concept"},
}

ALLOWED_OVERRIDES = set(TARGET_SCHEMA.keys()) | set()


def apply_mutations(brief: Brief, mutations: List[Dict[str, Any]]) -> Tuple[Brief, List[str]]:
    current = brief
    rejected = []
    for m in mutations or []:
        target = str(m.get("target", "")).strip()
        value = m.get("value")
        if target in IMMUTABLE:
            rejected.append(f"{target}: immutable anchor, cannot change")
            continue
        spec = TARGET_SCHEMA.get(target)
        if spec is None:
            rejected.append(f"{target}: not a mutable agent target")
            continue
        if spec["type"] == "str":
            value = _safe_text(value, spec, target, rejected)
            if value is None:
                continue
            current = _with_text(current, target, value)
            continue
        if spec["type"] == "enum":
            try:
                enum_value = spec["enum"](str(value or "").lower().replace("-", "_"))
            except (ValueError, TypeError):
                rejected.append(f"{target}: {value!r} is not a valid {spec['enum'].__name__}")
                continue
            current = _with_enum(current, target, enum_value)
            continue
        if spec["type"] == "int":
            try:
                num = int(float(value))
            except (TypeError, ValueError):
                rejected.append(f"{target}: {value!r} is not an integer")
                continue
            if not (spec["min"] <= num <= spec["max"]):
                rejected.append(f"{target}: {num} outside [{spec['min']}, {spec['max']}]")
                continue
            current = _with_int(current, target, num)
            continue
    return current, rejected


def _with_text(brief: Brief, target: str, value: str) -> Brief:
    primitives = dict(_brief_primitives(brief))
    primitives[target] = value
    return Brief(**primitives)


def _with_enum(brief: Brief, target: str, value: Any) -> Brief:
    primitives = dict(_brief_primitives(brief))
    primitives[target] = value
    return Brief(**primitives)


def _with_int(brief: Brief, target: str, value: int) -> Brief:
    primitives = dict(_brief_primitives(brief))
    primitives[target] = value
    return Brief(**primitives)


def _brief_primitives(brief: Brief) -> Dict[str, Any]:
    return {
        "objective": brief.objective,
        "ad_concept": brief.ad_concept,
        "brand": brief.brand,
        "car_model": brief.car_model,
        "car_colour": brief.car_colour,
        "format": brief.format or ContentFormat.INSTAGRAM_REEL,
        "language": brief.language or ScriptLanguage.HINDI,
        "duration": brief.duration,
        "generation_mode": brief.generation_mode or GenerationMode.SINGLE_SHOT,
        "voice_style": brief.voice_style or VoiceStyle.CONFIDENT,
        "pacing": brief.pacing or DeliveryPacing.MEDIUM_FAST,
        "custom_hook": getattr(brief, "custom_hook", None),
        "custom_offer": getattr(brief, "custom_offer", None),
        "custom_benefit": getattr(brief, "custom_benefit", None),
        "custom_cta": getattr(brief, "custom_cta", None),
        "offer": getattr(brief, "offer", None),
        "reference": getattr(brief, "reference", None),
    }


def _safe_text(value, spec, target, rejected):
    if not isinstance(value, str) or not value.strip():
        rejected.append(f"{target}: empty value")
        return None
    text = value.strip()
    if len(text) > spec["max_len"]:
        rejected.append(f"{target}: {len(text)} chars exceeds {spec['max_len']} max")
        return None
    return text


def strategist_to_mutations(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    mutations = []
    for target in ("custom_hook", "custom_benefit", "custom_cta", "ad_concept", "voice_style", "pacing", "duration"):
        if target == "ad_concept" and str(data.get(target, "")).strip() in ("", "same"):
            continue
        value = data.get(target)
        if value is None or str(value).strip() in ("", "-", "keep", "none"):
            continue
        mutations.append({"target": target, "value": value})
    offer_framing = data.get("offer_framing", "")
    if isinstance(offer_framing, str) and offer_framing.strip():
        lowered = offer_framing.lower()
        if "use the verified offer" in lowered or "engine" in lowered:
            pass
        elif len(offer_framing.strip()) > 10:
            mutations.append({"target": "custom_offer", "value": offer_framing.strip()})
    return mutations