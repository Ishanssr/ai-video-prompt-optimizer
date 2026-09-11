from .types import (
    Brief, ScenePlan, ReferenceProfile, Script, OfferClaim, BrandPolicy,
    ContentFormat, GenerationMode, ScriptLanguage,
)
from .scene_planner import plan_scene
from .camera_engine import get_safe_zone_prompt
from .audio_engine import compile_audio_directive
from .reference_engine import reference_to_ingredients_block, create_reference_profile
from .brand_engine import build_brand_constraint_section, get_brand_policy
from .validator import validate_prompt, score_validation
from .repair import repair_plan
from .script_engine import generate_script
from .creative_director import creative_director
from .offer_engine import offer_to_script_text, offer_to_voiceover


# ─── Overlay plan: generated vs composited ─────────────────────────

def overlay_plan(
    scene: ScenePlan,
    offer: OfferClaim = None,
    brand_policy: BrandPolicy = None,
) -> dict:
    """Explicitly split what Veo generates vs what must be composited later.

    Veo renders garbled pseudo-text, so anything needing readable text/logo
    is produced POST-GENERATION. This makes that contract explicit.
    """
    comp = scene.composition
    generated = [
        "cinematography (single camera move)",
        "subject + secondary subject scene",
        "primary action + supporting beats",
        "context / lighting",
        "audio: dialogue, music, ambient, SFX",
    ]
    composited = []
    if comp and comp.offer_card_visibility:
        composited.append("offer card / price badge")
    if comp and comp.cta_safe_zone:
        composited.append("CTA text overlay")
    if brand_policy:
        if brand_policy.logo_handling == "do_not_generate_text":
            composited.append("brand logo")
        if brand_policy.contact_info:
            composited.append("contact number / handle")
        if brand_policy.disclaimer:
            composited.append("legal disclaimer line")
    return {
        "generated_in_veo": generated,
        "composited_after": composited,
        "note": "Readable text, logos and offer badges are ALWAYS post-composited.",
    }


# ─── Subject / identity resolution ──────────────────────────────────

def resolve_subjects(scene: ScenePlan, reference: ReferenceProfile = None) -> tuple:
    """Return (subject, secondary_subject) with vehicle identity and dedup applied."""
    subject = (scene.subject or "").strip()
    secondary = (scene.secondary_subject or "").strip()

    if reference and reference.vehicle and reference.vehicle.model:
        rv = reference.vehicle
        identity = f"{rv.colour} {rv.model}".strip()
        if rv.position:
            identity += f" in {rv.position}"
        if rv.orientation:
            identity += f", {rv.orientation}"
        if identity:
            secondary = identity

    if secondary:
        model = reference.vehicle.model if (reference and reference.vehicle) else (scene.secondary_subject or "")
        if scene.subject and scene.subject == scene.secondary_subject:
            secondary = ""
        elif model and model.lower() in subject.lower():
            # The vehicle is already the on-screen subject; do not repeat it.
            secondary = ""
    return subject, secondary


# ─── Compilers ──────────────────────────────────────────────────────

def compile_prompt(
    scene: ScenePlan,
    script: Script = None,
    reference: ReferenceProfile = None,
    offer: OfferClaim = None,
    brand_policy: BrandPolicy = None,
    language: str = "hi-IN",
    duration: int = 8,
    mode: GenerationMode = GenerationMode.SINGLE_SHOT,
    verbose: bool = False,
) -> str:
    """Layer 5: Compile all plans into a single Veo prompt.

    Structurally produced from the ScenePlan; readable text/logo explicitly
    deferred to post-compositing.
    """
    comp = scene.composition
    sections = []

    move = comp.camera_move
    move_clause = f" with a {move}" if move and move != "static" else ""
    sections.append(f"Cinematography: {comp.shot_type}{move_clause}")

    subject, secondary = resolve_subjects(scene, reference)
    sections.append(f"Subject: {subject}")
    if secondary:
        sections.append(f"Secondary subject: {secondary}")

    action_line = scene.primary_action
    if scene.supporting_beats:
        action_line += " while " + ", ".join(scene.supporting_beats)
    sections.append(f"Action: {action_line}")

    if reference and reference.environment:
        env = reference.environment
        if env.location_type in ("showroom", "modern_dealership", "dealership"):
            context = f"{scene.location}. {scene.lighting}."
        else:
            context = f"{env.location_type}. {env.lighting} lighting, {env.floor} floor."
    else:
        context = f"{scene.location}. {scene.lighting}."
    sections.append(f"Context: {context}")

    sections.append(f"Style: {_derive_style(scene)}")

    sections.append(f"Audio: {compile_audio_directive(scene.audio, script)}")

    if reference:
        ref_block = reference_to_ingredients_block(reference)
        if ref_block:
            sections.append(f"References: {ref_block}")

    if brand_policy:
        sections.append(f"Brand: {build_brand_constraint_section(brand_policy)}")

    safe = get_safe_zone_prompt(comp)
    overlay = overlay_plan(scene, offer, brand_policy)
    composite_notes = []
    if safe:
        composite_notes.append(safe)
    for item in overlay.get("composited_after", []):
        implied = item in ("offer card / price badge", "CTA text overlay") and safe
        if not implied:
            composite_notes.append(item)
    if composite_notes:
        sections.append(
            "Composite after generation (do not render in Veo): "
            + ", ".join(composite_notes)
        )

    format_line = f"Format: 9:16 vertical, {duration} seconds (Veo 3.1)"
    if mode == GenerationMode.MULTI_SHOT_TIMED:
        format_line += " — multi-shot, time-based prompting"
    sections.append(format_line)

    if verbose and scene.ad_timeline:
        sections.append("Timing: " + "; ".join(sorted(scene.ad_timeline.keys())) if "speech_paced" not in scene.ad_timeline
                        else "Timing: speech-paced from fitted dialogue")

    prompt = "\n".join(sections)
    return prompt


def compile_narrative(
    scene: ScenePlan,
    script: Script = None,
    reference: ReferenceProfile = None,
    offer: OfferClaim = None,
    brand_policy: BrandPolicy = None,
    language: str = "hi-IN",
    duration: int = 8,
    mode: GenerationMode = GenerationMode.SINGLE_SHOT,
) -> str:
    """Natural cinematic paragraph form of the same prompt (Veo prose style)."""
    subject, secondary = resolve_subjects(scene, reference)
    comp = scene.composition
    move_clause = f" with a {comp.camera_move}" if comp.camera_move and comp.camera_move != "static" else ""

    sentences = []
    if secondary:
        sentences.append(
            f"Single continuous {comp.shot_type}{move_clause} in 9:16 vertical "
            f"featuring {subject} beside the {secondary}."
        )
    else:
        sentences.append(
            f"Single continuous {comp.shot_type}{move_clause} in 9:16 vertical "
            f"featuring {subject}."
        )

    action_line = scene.primary_action
    if scene.supporting_beats:
        action_line += " while " + ", ".join(scene.supporting_beats)
    sentences.append(action_line.capitalize() + ". Natural, believable movements throughout.")

    sentences.append(
        f"Set in {scene.location}, {scene.lighting}."
    )

    if script:
        dialogue = script.dialogue_text(duration, rewritten=True)
        if dialogue:
            sentences.append(
                f"The voice speaks in {language}: '{dialogue}' with clear, confident "
                f"delivery, prominent in the mix."
            )

    sentences.append(
        f"Audio includes {scene.audio.music_style or 'a clean professional bed'} "
        f"behind the voice, with {', '.join(scene.audio.ambient_sounds) or 'subtle ambience'}"
        + (f" and {scene.audio.key_sfx}" if scene.audio.key_sfx else "")
        + "."
    )

    sentences.append(
        f"The final {duration}-second shot holds a clean frame free of readable text "
        f"and logos; offer badge and CTA are added in post-production."
    )

    return " ".join(sentences)


def compile_timed_prompt(
    scene: ScenePlan,
    script: Script = None,
    **compile_kwargs,
) -> str:
    """Multi-shot timed scaffold using the ACTUAL speech-paced timeline."""
    lines = [
        f"# Veo 3.1 time-based multi-shot scaffold ({scene.duration}s, 9:16)",
        f"Subject: {scene.subject}",
        f"Primary action: {scene.primary_action}",
    ]
    if scene.ad_timeline and "speech_paced" in scene.ad_timeline:
        for key, val in scene.ad_timeline["speech_paced"].items():
            t1, t2 = key.split("-", 1)
            lines.append(f"[{float(t1):06.1f}-{float(t2):06.1f}] {val}")
    lines.append(f"[{float(scene.duration):06.1f}] end with CTA safe-frame, no readable text")
    return "\n".join(lines)


def _derive_style(scene: ScenePlan) -> str:
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


# ─── Validation + repair loop ──────────────────────────────────────

def compile_optimized_prompt(
    scene: ScenePlan,
    script: Script = None,
    reference: ReferenceProfile = None,
    offer: OfferClaim = None,
    brand_policy: BrandPolicy = None,
    duration: int = 8,
    language: str = "hi-IN",
    mode: GenerationMode = GenerationMode.SINGLE_SHOT,
) -> dict:
    """compile → validate → STRUCTURAL repair (plan, not prose) → recompile → re-validate."""
    lang = ScriptLanguage(language) if isinstance(language, str) else language

    def _recompile(s: ScenePlan, sc: Script):
        return compile_prompt(s, sc, reference, offer, brand_policy, language=language, duration=duration, mode=mode)

    prompt = _recompile(scene, script)

    initial = validate_prompt(
        prompt, script=script, offer=offer, lang=lang, target_duration=duration,
        scene=scene, reference=reference, brand_policy=brand_policy,
        generation_mode=mode,
    )

    repair = repair_plan(
        scene, script, offer, duration=duration, lang=lang,
        recompile=_recompile,
    )

    final_prompt = repair.prompt or prompt
    final_result = validate_prompt(
        final_prompt, script=repair.script, offer=offer, lang=lang,
        target_duration=duration, scene=repair.scene,
        reference=reference, brand_policy=brand_policy, generation_mode=mode,
    )

    initial_score = score_validation(initial)
    final_score = score_validation(final_result)

    return {
        "prompt": final_prompt,
        "scene": repair.scene or scene,
        "script": repair.script or script,
        "validation": {
            "passed": len(final_result.errors) == 0,
            "errors": final_result.errors,
            "warnings": final_result.warnings,
            "initial_errors": initial.errors,
            "smoke": bool(repair.was_repaired),
        },
        "score": {
            "initial": initial_score.score,
            "initial_grade": initial_score.grade,
            "final": final_score.score,
            "final_grade": final_score.grade,
        },
        "repair_log": repair.changes,
        "was_repaired": repair.was_repaired,
        "final_validation_score": final_score.score,
    }


# ─── Full pipeline (honest orchestration) ───────────────────────────

def _brief_from_kwargs(kwargs: dict) -> Brief:
    from .types import CampaignObjective, AdConcept
    objective = kwargs.get("objective")
    ad_concept = kwargs.get("ad_concept")
    if isinstance(objective, str):
        objective = CampaignObjective(objective)
    if isinstance(ad_concept, str):
        ad_concept = AdConcept(ad_concept)
    fmt = kwargs.get("format") or ContentFormat.INSTAGRAM_REEL
    if isinstance(fmt, str):
        fmt = ContentFormat(fmt)
    lang = kwargs.get("language") or ScriptLanguage.HINDI
    if isinstance(lang, str):
        lang = ScriptLanguage(lang)
    offer = kwargs.get("offer")
    if isinstance(offer, str):
        offer = _unverified_offer_from_text(offer)
    return Brief(
        objective=objective,
        ad_concept=ad_concept,
        brand=kwargs.get("brand", ""),
        car_model=kwargs.get("car_model", ""),
        car_colour=kwargs.get("car_colour") or "white",
        format=fmt,
        language=lang,
        duration=kwargs.get("duration", 8),
        custom_hook=kwargs.get("custom_hook"),
        custom_offer=kwargs.get("custom_offer"),
        custom_benefit=kwargs.get("custom_benefit"),
        custom_cta=kwargs.get("custom_cta"),
        offer=offer,
        reference=kwargs.get("reference"),
    )


def _unverified_offer_from_text(text: str) -> "OfferClaim":
    from .offer_engine import create_unverified_offer
    return create_unverified_offer(description=text)


def full_pipeline(
    brief: Brief = None,
    ad_concept=None,
    car_model=None,
    car_colour=None,
    brand=None,
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
    **kwargs,
) -> dict:
    """
    End-to-end: ONE Brief → creative strategy → script (rewritten to fit) → scene
    → reference → brand policy → audio → compile → VALIDATE → STRUCTURAL REPAIR
    → recompile → final validate → scored result.

    Accepts a Brief, or legacy keyword/positional fields (objective via kwargs).
    """
    if not isinstance(brief, Brief):
        if brief is None and (kwargs or any([ad_concept, car_model, brand])):
            brief = _brief_from_kwargs({**kwargs, "ad_concept": ad_concept, "car_model": car_model,
                                        "car_colour": car_colour, "brand": brand, "duration": duration,
                                        "format": format, "language": language, "offer": offer,
                                        "reference": reference,
                                        "custom_hook": custom_hook, "custom_offer": custom_offer,
                                        "custom_benefit": custom_benefit, "custom_cta": custom_cta})
        else:
            brief = _brief_from_kwargs({
                "objective": brief, "ad_concept": ad_concept, "car_model": car_model,
                "car_colour": car_colour, "brand": brand, "duration": duration,
                "format": format, "language": language, "offer": offer, "reference": reference,
                "custom_hook": custom_hook, "custom_offer": custom_offer,
                "custom_benefit": custom_benefit, "custom_cta": custom_cta, **kwargs,
            })

    return _run_full_pipeline(brief, brand_policy=brand_policy, legacy_script=script)


def _run_full_pipeline(brief: Brief, brand_policy: BrandPolicy = None, legacy_script: Script = None) -> dict:
    lang = brief.language

    # Layer 1 — creative strategy
    creative = creative_director(brief.objective, brief.ad_concept, brief.format, lang)

    # Layer 2 — script with offer injection
    offer = brief.offer
    offer_line = ""
    if offer:
        offer_line = offer_to_script_text(offer, lang)
    script = legacy_script or generate_script(
        brief.objective, brief.ad_concept,
        lang, brief.voice_style, brief.pacing,
        custom_hook=brief.custom_hook,
        custom_offer=offer_line or brief.custom_offer,
        custom_benefit=brief.custom_benefit,
        custom_cta=brief.custom_cta,
    )
    if offer:
        script.offer.text = offer_line or script.offer.text
        short = offer_to_voiceover(offer, lang)
        if short:
            script.offer.condensed = short
        script.offer.duration_seconds = script.offer.estimate_speech_duration(lang)

    # Layer 3 — scene plan (single action source)
    scene = plan_scene(
        brief.objective, brief.ad_concept, brief.car_model, brief.car_colour,
        brief.brand, script=script, duration=brief.duration, format=brief.format,
        creative=creative, generation_mode=brief.generation_mode,
    )

    # Layer 4 — reference + brand
    reference = brief.reference or create_reference_profile(
        vehicle_model=brief.car_model, vehicle_colour=brief.car_colour,
    )
    policy = brand_policy or get_brand_policy(brief.brand)

    # Layers 5-7 — compile, validate, structural repair, recompile, re-validate
    optimized = compile_optimized_prompt(
        scene, script, reference, offer, policy,
        duration=brief.duration, language=brief.language.value,
        mode=brief.generation_mode,
    )

    repaired_scene = optimized["scene"]
    repaired_script = optimized["script"]

    return {
        "brief": brief,
        "creative": creative,
        "script": repaired_script,
        "raw_script": script,
        "scene": repaired_scene,
        "prompt": optimized["prompt"],
        "prompt_narrative": compile_narrative(
            repaired_scene, repaired_script, reference, offer, policy,
            language=brief.language.value, duration=brief.duration,
            mode=brief.generation_mode,
        ),
        "prompt_timed": compile_timed_prompt(repaired_scene, repaired_script) if brief.generation_mode == GenerationMode.MULTI_SHOT_TIMED else "",
        "overlay_plan": overlay_plan(repaired_scene, offer, policy),
        "validation": optimized["validation"],
        "score": optimized["score"],
        "repair_log": optimized["repair_log"],
        "was_repaired": optimized["was_repaired"],
        "timeline": repaired_scene.ad_timeline,
        "references": reference,
        "brand_policy": policy,
    }