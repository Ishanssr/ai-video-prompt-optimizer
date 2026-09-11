from .types import ShotComposition, AdConcept


SHOT_KNOWLEDGE = {
    "medium presenter shot": {
        "subject_headroom": "top 1/3, face upper-center",
        "hand_visibility": "waist up, hands visible for gestures",
        "offer_card_position": "lower-center safe zone, no face overlap",
        "vehicle_position": "rear three-quarter behind presenter",
        "safe_zone": "9:16 center 60%, text-safe lower 30%",
        "composition_notes": (
            "presenter foreground left or right, vehicle visible in background. "
            "face unobstructed, eye contact with camera. "
            "offer card composited in lower third after generation."
        ),
    },
    "medium product shot": {
        "subject_headroom": "top 1/4",
        "vehicle_position": "center frame, 3/4 front angle",
        "safe_zone": "9:16 full frame",
        "composition_notes": (
            "car fills frame, clean background. "
            "hero lighting on body lines. "
            "text overlay composited post-generation."
        ),
    },
    "medium close-up": {
        "subject_headroom": "top 1/4",
        "vehicle_position": "soft background, left third",
        "safe_zone": "9:16 center",
        "composition_notes": (
            "subject in sharp focus, car slightly soft background. "
            "natural expression, stable tripod-like framing."
        ),
    },
    "wide shot": {
        "subject_headroom": "top 1/3",
        "vehicle_position": "center or slight right",
        "safe_zone": "9:16 center",
        "composition_notes": (
            "full vehicle in frame, context visible. "
            "for reveals: dark surroundings, spotlights on car."
        ),
    },
    "medium shot": {
        "subject_headroom": "waist up",
        "vehicle_position": "background right or left",
        "safe_zone": "9:16 center",
        "composition_notes": (
            "subjects waist-up, car visible in background. "
            "natural candid framing for delivery moments."
        ),
    },
    "medium tracking": {
        "subject_headroom": "waist up, motion frame",
        "vehicle_position": "center background, on lift",
        "safe_zone": "9:16 center",
        "composition_notes": (
            "follow subject as they move through service bay. "
            "car on lift in background, tools in midground."
        ),
    },
    "extreme close-up": {
        "vehicle_position": "fills entire frame",
        "safe_zone": "9:16 center",
        "composition_notes": (
            "macro detail: light playing on surface. "
            "very shallow depth of field, dark background."
        ),
    },
    "wide shot, crane": {
        "vehicle_position": "center stage",
        "safe_zone": "9:16 center",
        "composition_notes": (
            "crane starts low, rises to reveal car. "
            "dramatic lighting, dark room."
        ),
    },
}


def compose_shot(shot_type: str, composition: ShotComposition) -> dict:
    """Get composition guidance for a specific shot type."""
    return SHOT_KNOWLEDGE.get(shot_type, SHOT_KNOWLEDGE.get("medium shot", {}))


def camera_to_veo_prompt(composition: ShotComposition) -> str:
    """Convert shot composition into Veo cinematography clause."""
    shot = composition.shot_type

    move = composition.camera_move
    if move and move != "static":
        move_clause = f", {move}"
    else:
        move_clause = ""

    knowledge = compose_shot(shot, composition)
    notes = knowledge.get("composition_notes", "")

    return f"{shot}{move_clause} — {notes}" if notes else f"{shot}{move_clause}"


def get_safe_zone_prompt(composition: ShotComposition) -> str:
    """Returns safe zone text for post-compositing guidance."""
    parts = []
    if composition.offer_card_visibility:
        parts.append(f"Offer card: {composition.offer_card_visibility} (composite later)")
    if composition.cta_safe_zone:
        parts.append(f"CTA: {composition.cta_safe_zone} (overlay later)")
    return ". ".join(parts) if parts else ""


def suggest_camera_for_ad_type(ad_concept: AdConcept) -> dict:
    """Suggests optimal camera parameters for each ad type."""
    suggestions = {
        AdConcept.PRESENTER_LED: {
            "shot_type": "medium presenter shot",
            "camera_move": "slow push-in",
            "depth": "shallow",
            "reasoning": "Push-in creates engagement while maintaining presenter visibility",
        },
        AdConcept.TESTIMONIAL: {
            "shot_type": "medium close-up",
            "camera_move": "static",
            "depth": "shallow",
            "reasoning": "Static shot keeps focus on genuine emotion, avoids distraction",
        },
        AdConcept.REVEAL: {
            "shot_type": "wide shot",
            "camera_move": "crane",
            "depth": "deep_for_reveal",
            "reasoning": "Crane shot creates dramatic reveal moment",
        },
        AdConcept.PRODUCT_SHOWCASE: {
            "shot_type": "extreme close-up",
            "camera_move": "macro glide",
            "depth": "very_shallow",
            "reasoning": "Macro glide highlights premium surface details",
        },
    }
    return suggestions.get(ad_concept, suggestions[AdConcept.PRESENTER_LED])
