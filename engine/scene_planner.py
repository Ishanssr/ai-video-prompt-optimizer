from .types import (
    ScenePlan, ShotComposition, AudioPlan, AdTimeline,
    CampaignObjective, AdConcept, ContentFormat,
    ScriptLanguage, Script,
)


def plan_scene(
    objective: CampaignObjective,
    ad_concept: AdConcept,
    car_model: str,
    car_colour: str,
    brand: str,
    script: Script = None,
    duration: int = 8,
    format: ContentFormat = ContentFormat.INSTAGRAM_REEL,
) -> ScenePlan:
    """Layer 3: Creates a full scene plan from creative strategy."""

    composition = _plan_composition(ad_concept)
    audio = _plan_audio(ad_concept, script)
    timeline = _plan_timeline(objective, ad_concept, duration)

    subject = _select_subject(ad_concept, brand, car_model)
    action = _select_action(ad_concept, objective)
    location = _select_location(ad_concept, brand)
    lighting = _select_lighting(ad_concept)

    script_text = ""
    cta = ""
    if script:
        script_text = script.compress(duration)
        cta = script.cta.text

    return ScenePlan(
        duration=duration,
        aspect_ratio="9:16",
        shot_count=1,
        camera_move=composition.camera_move,
        subject=subject,
        secondary_subject=f"{car_colour} {car_model}" if car_model else "",
        primary_action=action,
        location=location,
        lighting=lighting,
        script_language=script.language.value if script else "hi-IN",
        script=script_text,
        cta=cta,
        composition=composition,
        audio=audio,
        ad_timeline=timeline,
    )


def _plan_composition(ad_concept: AdConcept) -> ShotComposition:
    configs = {
        AdConcept.PRESENTER_LED: ShotComposition(
            shot_type="medium presenter shot",
            camera_move="slow push-in",
            headroom="standard",
            hand_visibility="natural_gesture",
            offer_card_visibility="central_safe_zone",
            vehicle_visibility="rear_three_quarter_background",
            safe_zone="9:16_center",
            cta_safe_zone="lower_third",
            depth="shallow",
        ),
        AdConcept.VOICEOVER_LED: ShotComposition(
            shot_type="medium product shot",
            camera_move="slow pan",
            headroom="standard",
            vehicle_visibility="center_frame",
            safe_zone="9:16_center",
            depth="shallow",
        ),
        AdConcept.TESTIMONIAL: ShotComposition(
            shot_type="medium close-up",
            camera_move="static",
            headroom="standard",
            vehicle_visibility="background",
            safe_zone="9:16_center",
            depth="shallow",
        ),
        AdConcept.REVEAL: ShotComposition(
            shot_type="wide shot",
            camera_move="crane",
            vehicle_visibility="center_stage",
            safe_zone="9:16_center",
            depth="deep_for_reveal",
        ),
        AdConcept.DELIVERY_MOMENT: ShotComposition(
            shot_type="medium shot",
            camera_move="tracking",
            headroom="standard",
            vehicle_visibility="background",
            hand_visibility="keys_handover",
            safe_zone="9:16_center",
            depth="shallow",
        ),
        AdConcept.SERVICE_TRUST: ShotComposition(
            shot_type="medium tracking",
            camera_move="tracking",
            vehicle_visibility="on_lift",
            hand_visibility="tool_handling",
            safe_zone="9:16_center",
            depth="medium",
        ),
        AdConcept.PRODUCT_SHOWCASE: ShotComposition(
            shot_type="extreme close-up",
            camera_move="macro glide",
            vehicle_visibility="detail_focus",
            safe_zone="9:16_center",
            depth="very_shallow",
        ),
        AdConcept.FESTIVE_CELEBRATION: ShotComposition(
            shot_type="wide shot",
            camera_move="slow pan",
            vehicle_visibility="festive_decor",
            safe_zone="9:16_center",
            depth="shallow",
        ),
        AdConcept.LIFESTYLE: ShotComposition(
            shot_type="medium wide",
            camera_move="tracking",
            vehicle_visibility="environmental",
            safe_zone="9:16_center",
            depth="medium",
        ),
    }
    return configs.get(ad_concept, configs[AdConcept.PRESENTER_LED])


def _plan_audio(ad_concept: AdConcept, script: Script = None) -> AudioPlan:
    has_dialogue = script and script.compress(8).strip()
    return AudioPlan(
        voice_priority="dominant" if has_dialogue else "none",
        music_level="-12dB relative" if has_dialogue else "primary",
        ambient_level="subtle",
        key_sfx=_select_sfx(ad_concept),
        cta_emphasis="final_sentence",
        music_style=_select_music(ad_concept),
        ambient_sounds=_select_ambient(ad_concept),
        dialogue_colon=script.compress(8) if has_dialogue else "",
    )


def _plan_timeline(
    objective: CampaignObjective,
    ad_concept: AdConcept,
    duration: int,
) -> dict:
    if ad_concept == AdConcept.TESTIMONIAL:
        return {
            "0.0-1.0": "Customer begins story",
            "1.0-5.5": "Customer experience + car shown",
            "5.5-7.0": "Genuine emotion moment",
            "7.0-8.0": "CTA / brand tag",
        }
    elif ad_concept == AdConcept.DELIVERY_MOMENT:
        return {
            "0.0-2.0": "Family approaches car",
            "2.0-5.0": "Keys handover, joy moment",
            "5.0-7.0": "Reaction shots",
            "7.0-8.0": "Brand tag",
        }
    elif ad_concept == AdConcept.REVEAL:
        return {
            "0.0-1.5": "Dark room, anticipation",
            "1.5-4.0": "Cover slides off, spotlights converge",
            "4.0-6.5": "Car details revealed",
            "6.5-8.0": "CTA",
        }
    else:
        return {
            "0.0-1.5": "Hook / attention",
            "1.5-4.5": "Offer message",
            "4.5-6.5": "Car + benefit",
            "6.5-8.0": "CTA",
        }


def _select_subject(ad_concept: AdConcept, brand: str, car_model: str) -> str:
    subjects = {
        AdConcept.PRESENTER_LED: f"salesperson in branded {brand} uniform",
        AdConcept.VOICEOVER_LED: f"{car_model}" if car_model else "car",
        AdConcept.TESTIMONIAL: "satisfied car owner",
        AdConcept.REVEAL: f"{car_model}" if car_model else "new car model",
        AdConcept.DELIVERY_MOMENT: "family receiving car keys",
        AdConcept.SERVICE_TRUST: "certified service technician",
        AdConcept.PRODUCT_SHOWCASE: f"{car_model} detail" if car_model else "car detail",
        AdConcept.FESTIVE_CELEBRATION: f"{car_model} with festive decor" if car_model else "festive car",
    }
    return subjects.get(ad_concept, "presenter")


def _select_action(ad_concept: AdConcept, objective: CampaignObjective) -> str:
    actions = {
        AdConcept.PRESENTER_LED: "presenter speaks directly to camera while standing beside the car",
        AdConcept.VOICEOVER_LED: "car shown in cinematic motion",
        AdConcept.TESTIMONIAL: "customer turns to camera with genuine smile",
        AdConcept.REVEAL: "satin cover slides off in slow motion, spotlights converge",
        AdConcept.DELIVERY_MOMENT: "family receives the keys in an emotional celebratory moment",
        AdConcept.SERVICE_TRUST: "technician inspects the engine with precision",
        AdConcept.PRODUCT_SHOWCASE: "camera glides slowly along body lines, light catching contours",
        AdConcept.FESTIVE_CELEBRATION: "festive garlands placed on car, warm smiles",
    }
    return actions.get(ad_concept, "presenter speaks to camera")


def _select_location(ad_concept: AdConcept, brand: str) -> str:
    locations = {
        AdConcept.PRESENTER_LED: f"premium {brand} dealership showroom",
        AdConcept.VOICEOVER_LED: f"{brand} dealership forecourt or studio",
        AdConcept.TESTIMONIAL: f"{brand} dealership forecourt",
        AdConcept.REVEAL: f"{brand} showroom reveal stage",
        AdConcept.DELIVERY_MOMENT: f"{brand} dealership delivery bay",
        AdConcept.SERVICE_TRUST: f"modern {brand} authorized service center",
        AdConcept.PRODUCT_SHOWCASE: "dark studio with dramatic lighting",
        AdConcept.FESTIVE_CELEBRATION: f"festive-decorated {brand} dealership",
    }
    return locations.get(ad_concept, f"{brand} dealership")


def _select_lighting(ad_concept: AdConcept) -> str:
    lightings = {
        AdConcept.PRESENTER_LED: "bright showroom track LEDs, warm and even",
        AdConcept.VOICEOVER_LED: "golden hour natural light",
        AdConcept.TESTIMONIAL: "natural golden hour, outdoor",
        AdConcept.REVEAL: "dramatic spotlights, dark surroundings",
        AdConcept.DELIVERY_MOMENT: "bright showroom lighting, celebratory",
        AdConcept.SERVICE_TRUST: "clean overhead workshop LEDs",
        AdConcept.PRODUCT_SHOWCASE: "single key dramatic light, dark background",
        AdConcept.FESTIVE_CELEBRATION: "warm festive string lights, soft bokeh",
    }
    return lightings.get(ad_concept, "showroom lighting")


def _select_sfx(ad_concept: AdConcept) -> str:
    sfx = {
        AdConcept.PRESENTER_LED: "subtle whoosh on camera move",
        AdConcept.REVEAL: "dramatic whoosh, drum roll",
        AdConcept.DELIVERY_MOMENT: "confetti pop, applause, child laugh",
        AdConcept.SERVICE_TRUST: "pneumatic tools, metal precision sounds",
        AdConcept.FESTIVE_CELEBRATION: "festive bells, crowd murmur",
        AdConcept.PRODUCT_SHOWCASE: "soft whoosh, metallic resonance",
    }
    return sfx.get(ad_concept, "")


def _select_music(ad_concept: AdConcept) -> str:
    music = {
        AdConcept.PRESENTER_LED: "upbeat professional",
        AdConcept.VOICEOVER_LED: "cinematic ambient",
        AdConcept.TESTIMONIAL: "soft emotional underscore",
        AdConcept.REVEAL: "dramatic orchestral score",
        AdConcept.DELIVERY_MOMENT: "celebratory upbeat",
        AdConcept.SERVICE_TRUST: "soft professional background",
        AdConcept.PRODUCT_SHOWCASE: "electronic ambient",
        AdConcept.FESTIVE_CELEBRATION: "festive upbeat instrumental",
    }
    return music.get(ad_concept, "professional background")


def _select_ambient(ad_concept: AdConcept) -> list:
    ambients = {
        AdConcept.PRESENTER_LED: ["soft showroom hum"],
        AdConcept.TESTIMONIAL: ["light wind", "distant traffic"],
        AdConcept.DELIVERY_MOMENT: ["celebration ambient"],
        AdConcept.SERVICE_TRUST: ["workshop ambient"],
        AdConcept.FESTIVE_CELEBRATION: ["crowd murmur", "festive ambience"],
    }
    return ambients.get(ad_concept, ["ambient background"])
