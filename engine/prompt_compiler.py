from .types import (
    ScenePlan, ReferenceProfile, Script, OfferClaim,
    BrandPolicy,
)
from .scene_planner import plan_scene
from .camera_engine import get_safe_zone_prompt
from .audio_engine import compile_audio_directive
from .reference_engine import reference_to_ingredients_block
from .brand_engine import build_brand_constraint_section
from .validator import validate_prompt
from .repair import auto_repair


def compile_prompt(
    scene: ScenePlan,
    script: Script = None,
    reference: ReferenceProfile = None,
    offer: OfferClaim = None,
    brand_policy: BrandPolicy = None,
    language: str = "hi-IN",
    duration: int = 8,
    verbose: bool = False,
) -> str:
    """Layer 5: Compile all plans into a single Veo prompt."""
    sections = []
    comp = scene.composition

    # Cinematography
    move = comp.camera_move
    move_clause = f" with a {move}" if move and move != "static" else ""
    cinematography = f"{comp.shot_type}{move_clause}"
    sections.append(f"Cinematography: {cinematography}")

    # Subject
    subject = scene.subject
    if reference and reference.vehicle and reference.vehicle.model:
        rv = reference.vehicle
        subject = (
            f"{rv.colour} {rv.model} in {rv.position}, {rv.orientation}"
        ) if rv.colour else f"{rv.model}"
    sections.append(f"Subject: {subject}")

    # Secondary subject (car)
    if scene.secondary_subject and scene.subject != scene.secondary_subject:
        sections.append(f"Secondary subject: {scene.secondary_subject}")

    # Action
    action = scene.primary_action
    sections.append(f"Action: {action}")

    # Context
    context = f"{scene.location}. {scene.lighting}."
    if reference and reference.environment:
        env = reference.environment
        context = f"{env.location_type}, {env.lighting} lighting, {env.floor} floor."
    sections.append(f"Context: {context}")

    # Style & ambiance
    style = _derive_style(scene)
    sections.append(f"Style: {style}")

    # Audio
    audio = compile_audio_directive(scene.audio, script)
    if offer and offer.verified:
        pass  # offer already in script text handled by script_engine
    sections.append(f"Audio: {audio}")

    # Reference block (Veo 3.1 Ingredients-to-Video)
    if reference:
        ref_block = reference_to_ingredients_block(reference)
        if ref_block:
            sections.append(f"References: {ref_block}")

    # Brand constraints
    if brand_policy:
        brand_line = build_brand_constraint_section(brand_policy)
        sections.append(f"Brand: {brand_line}")

    # Safe-zone / composite notes
    safe = get_safe_zone_prompt(comp)
    if safe:
        sections.append(f"Compositing: {safe}")

    # Format
    sections.append(f"Format: 9:16 vertical, {duration} seconds")

    prompt = "\n".join(sections)

    result = validate_prompt(
        prompt,
        script=script,
        target_duration=duration,
    )

    if verbose:
        prompt += "\n\n# Validation:\n"
        for e in result.errors:
            prompt += f"- ERROR: {e}\n"
        for w in result.warnings:
            prompt += f"- WARN: {w}\n"

    return prompt


def compile_optimized_prompt(
    scene: ScenePlan,
    script: Script = None,
    reference: ReferenceProfile = None,
    offer: OfferClaim = None,
    brand_policy: BrandPolicy = None,
    duration: int = 8,
) -> dict:
    """
    Full pipeline: compile → validate → auto-repair → final prompt.
    Returns prompt, validation result, and repair log.
    """
    prompt = compile_prompt(
        scene, script, reference, offer, brand_policy,
        duration=duration,
    )

    script_text = ""
    if script:
        script_text = script.compress(duration)

    result = validate_prompt(
        prompt,
        script=script,
        offer=offer,
        target_duration=duration,
    )

    repair = auto_repair(
        prompt,
        script_text=script_text,
        target_seconds=duration,
    )

    final_prompt = repair["repaired_prompt"]

    if len(result.warnings) <= 2:
        final_result = validate_prompt(
            final_prompt,
            script=script,
            offer=offer,
            target_duration=duration,
        )
        final_errors = final_result.errors
    else:
        final_errors = result.errors

    return {
        "prompt": final_prompt,
        "validation": {
            "passed": len(final_errors) == 0,
            "errors": final_errors,
            "warnings": result.warnings,
        },
        "repair_log": repair["changes"],
        "was_repaired": repair["was_repaired"],
    }


def _derive_style(scene: ScenePlan) -> str:
    comp = scene.composition
    depth = "shallow depth of field"
    tone = _tone_for_ad(scene)
    return f"photorealistic commercial, {depth}, {tone}"


def _tone_for_ad(scene: ScenePlan) -> str:
    subject = scene.subject.lower() if scene.subject else ""
    if "salesperson" in subject or "presenter" in subject:
        return "professional energetic delivery"
    if "customer" in subject:
        return "authentic warm tone"
    if "family" in subject:
        return "emotional celebratory tone"
    if "technician" in subject:
        return "trustworthy professional tone"
    if "reveal" in scene.primary_action:
        return "epic dramatic grade"
    return "elevated commercial polish"


# ─── High-level API ─────────────────────────────────────────────────

def full_pipeline(
    objective,
    ad_concept,
    car_model,
    car_colour,
    brand,
    duration: int = 8,
    format=None,
    language=None,
    script=None,
    offer=None,
    reference=None,
    brand_policy=None,
    custom_hook=None,
    custom_offer=None,
    custom_benefit=None,
    custom_cta=None,
) -> dict:
    """
    End-to-end: brief → concept → scene → script → audio → prompt.
    """
    scene = plan_scene(
        objective, ad_concept, car_model, car_colour,
        brand, script=script, duration=duration, format=format,
    )

    return compile_optimized_prompt(
        scene,
        script=script,
        reference=reference,
        offer=offer,
        brand_policy=brand_policy,
        duration=duration,
    )