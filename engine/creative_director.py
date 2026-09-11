from .types import (
    CampaignObjective, AdConcept, ContentFormat,
    ScriptLanguage,
)


# ONE source of truth for the on-screen action. Every layer (creative
# director, scene planner, compiler, validator) reads from this table, so
# the "3 actions vs 1 action" divergence can no longer happen.
# Each concept has exactly ONE primary action + up to 3 supporting beats
# (beats are written as gerund phrases so they grammatically chain on
# "while …").
VISUAL_ACTIONS = {
    (CampaignObjective.ENQUIRY, AdConcept.PRESENTER_LED): {
        "primary": "presenter speaks directly to camera",
        "beats": ["gesturing toward the car", "raising an offer card"],
    },
    (CampaignObjective.OFFER_AWARENESS, AdConcept.PRESENTER_LED): {
        "primary": "presenter speaks directly to camera",
        "beats": ["holding up an offer card", "pointing to car features"],
    },
    (CampaignObjective.BOOKING, AdConcept.PRESENTER_LED): {
        "primary": "presenter speaks directly to camera",
        "beats": ["inviting for a test drive", "walking toward the car"],
    },
    (CampaignObjective.TEST_DRIVE, AdConcept.PRESENTER_LED): {
        "primary": "presenter speaks directly to camera",
        "beats": ["pointing to the car", "offering the keys"],
    },
    (CampaignObjective.DELIVERY, AdConcept.DELIVERY_MOMENT): {
        "primary": "family receives the car keys",
        "beats": ["embracing in celebration", "opening the car door"],
    },
    (CampaignObjective.FESTIVE_PROMO, AdConcept.FESTIVE_CELEBRATION): {
        "primary": "family celebrates beside the festive car",
        "beats": ["placing a garland on the car", "raising hands in joy"],
    },
    (CampaignObjective.NEW_LAUNCH, AdConcept.REVEAL): {
        "primary": "satin cover slides off the car",
        "beats": ["converging spotlights", "presenter revealing the car"],
    },
    (CampaignObjective.SERVICE_BOOKING, AdConcept.SERVICE_TRUST): {
        "primary": "technician inspects the car",
        "beats": ["demonstrating care", "pointing to the service bay"],
    },
}

_ACTION_FALLBACK = {
    "primary": "presenter speaks directly to camera",
    "beats": ["gestures toward the car"],
}


def resolve_visual_action(objective: CampaignObjective, ad_concept: AdConcept) -> dict:
    """Single canonical action for any objective+concept combination."""
    return VISUAL_ACTIONS.get((objective, ad_concept), _ACTION_FALLBACK)


def creative_director(
    objective: CampaignObjective,
    ad_concept: AdConcept,
    format: ContentFormat = ContentFormat.INSTAGRAM_REEL,
    language: ScriptLanguage = ScriptLanguage.HINDI,
) -> dict:
    """
    Layer 1: Translates business brief into creative strategy.
    Returns a creative brief that drives all downstream engines.
    """
    timeline = _build_timeline(objective, ad_concept)
    presenter = _select_presenter(ad_concept)
    visual_action = resolve_visual_action(objective, ad_concept)
    hook_strategy = _select_hook(objective, ad_concept, language)

    return {
        "objective": objective.value,
        "ad_concept": ad_concept.value,
        "format": format.value,
        "language": language.value,
        "timeline": timeline,
        "presenter": presenter,
        "visual_action": visual_action,
        "hook_strategy": hook_strategy,
        "ad_structure": {
            "0.0-1.5": "Hook / presenter attention",
            "1.5-4.5": "Offer message",
            "4.5-6.5": "Car + benefit",
            "6.5-8.0": "CTA",
        },
    }


def _build_timeline(objective: CampaignObjective, ad_concept: AdConcept) -> dict:
    if ad_concept == AdConcept.TESTIMONIAL:
        return {
            "hook_seconds": 1.0,
            "offer_seconds": 0,
            "product_seconds": 5.5,
            "cta_seconds": 1.5,
            "total_seconds": 8.0,
            "note": "Testimonial leads with story, not offer",
        }
    elif ad_concept == AdConcept.DELIVERY_MOMENT:
        return {
            "hook_seconds": 0,
            "offer_seconds": 0,
            "product_seconds": 6.5,
            "cta_seconds": 1.5,
            "total_seconds": 8.0,
            "note": "Emotional moment, no hard sell",
        }
    else:
        return {
            "hook_seconds": 1.5,
            "offer_seconds": 3.0,
            "product_seconds": 2.0,
            "cta_seconds": 1.5,
            "total_seconds": 8.0,
            "note": "Standard ad structure",
        }


def _select_presenter(ad_concept: AdConcept) -> dict:
    presenters = {
        AdConcept.PRESENTER_LED: {
            "type": "salesperson",
            "description": "Salesperson in branded uniform, beside the car",
            "position": "foreground_midground",
            "vehicle_position": "rear_three_quarter_background",
            "camera_relationship": "direct_to_camera",
            "hand_visibility": "natural_gesture",
            "shot": "medium presenter shot",
        },
        AdConcept.VOICEOVER_LED: {
            "type": "voiceover",
            "description": "Car in hero position, no presenter visible",
            "position": "not_visible",
            "vehicle_position": "center_frame",
            "camera_relationship": "narration",
            "hand_visibility": "not_applicable",
            "shot": "medium product shot",
        },
        AdConcept.TESTIMONIAL: {
            "type": "customer",
            "description": "Satisfied customer with their car",
            "position": "midground",
            "vehicle_position": "background",
            "camera_relationship": "direct_to_camera",
            "hand_visibility": "natural",
            "shot": "medium close-up",
        },
        AdConcept.REVEAL: {
            "type": "none",
            "description": "Car as hero, dramatic reveal",
            "position": "not_visible",
            "vehicle_position": "center_stage",
            "camera_relationship": "product_focus",
            "hand_visibility": "not_applicable",
            "shot": "wide shot",
        },
        AdConcept.DELIVERY_MOMENT: {
            "type": "family",
            "description": "Family receiving car keys",
            "position": "midground",
            "vehicle_position": "background",
            "camera_relationship": "candid_moment",
            "hand_visibility": "keys_handover",
            "shot": "medium shot",
        },
        AdConcept.SERVICE_TRUST: {
            "type": "technician",
            "description": "Certified technician in service center",
            "position": "midground",
            "vehicle_position": "on_lift",
            "camera_relationship": "working",
            "hand_visibility": "tool_handling",
            "shot": "medium tracking",
        },
    }
    return presenters.get(ad_concept, presenters[AdConcept.PRESENTER_LED])


def _select_hook(objective: CampaignObjective, ad_concept: AdConcept, lang: ScriptLanguage) -> dict:
    hooks = {
        CampaignObjective.OFFER_AWARENESS: {
            "type": "offer_lead",
            "template": " offer-oriented attention grabber",
        },
        CampaignObjective.ENQUIRY: {
            "type": "question_lead",
            "template": "engaging question to camera",
        },
        CampaignObjective.NEW_LAUNCH: {
            "type": "dramatic_reveal",
            "template": "anticipation build before reveal",
        },
        CampaignObjective.DELIVERY: {
            "type": "emotional_moment",
            "template": "genuine joy reaction",
        },
    }
    return hooks.get(objective, {
        "type": "attention",
        "template": "direct address to camera",
    })