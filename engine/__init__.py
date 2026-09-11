from .params import (
    VeoParams, Category, Tone, CameraMove, ShotType,
    LightingStyle, FilmStyle, AudioTrack, Character,
)
from .generator import (
    generate, generate_brief, generate_json, generate_elaborated,
    festive, showroom, offer_features, testimonial,
    delivery, features_closeup, festive_offer,
    new_launch, service,
)

# ─── Industry-grade architecture ────────────────────────────────────
from .types import (
    CampaignObjective, AdConcept, ContentFormat, GenerationMode,
    Script, ScriptLine, ScriptLanguage, VoiceStyle, DeliveryPacing,
    OfferClaim, OfferType, ClaimCategory, CommercialIssue,
    ReferenceProfile, ReferencePerson, ReferenceVehicle, ReferenceEnvironment,
    ScaleGraph, ModelSpec, VariantSpec,
    ScenePlan, ShotComposition, AudioPlan, AdTimeline,
    BrandPolicy, ValidationResult, ValidationScore,
    SpeechModel, SpeechBudget, Brief, RepairOp, RepairResult,
    VeoCapability, VEO_3_1,
    CreativeBlueprint, CampaignSpec, PresenterSpec, VehicleSpec,
    ShotSpec, ActionSpec, ScriptSpec, BlueprintAudio, PostPlan,
)
from .creative_director import (
    creative_director, resolve_visual_action, VISUAL_ACTIONS,
)
from .script_engine import (
    generate_script, script_to_colon_format, estimate_speech_duration_seconds,
    rewrite_script_to_fit, speech_rates,
)
from .offer_engine import (
    create_verified_offer, create_unverified_offer,
    offer_to_script_text, offer_to_voiceover, safety_check,
)
from .reference_engine import (
    create_reference_profile, reference_to_ingredients_block,
    reference_to_prompt_text, vehicle_identity,
    assert_vehicle_identity_untouched,
    IMMUTABLE_VEHICLE_ATTRS, MUTABLE_VEHICLE_ATTRS,
)
from .scene_planner import plan_scene
from .audio_engine import (
    compile_audio_directive, audio_to_veo_format,
    validate_audio_plan, estimate_dialogue_fit,
)
from .brand_engine import (
    get_brand_policy, validate_brand_safety, build_brand_constraint_section,
    get_model_spec, validate_model_feature, MODEL_FEATURES,
)
from .camera_engine import (
    compose_shot, camera_to_veo_prompt, get_safe_zone_prompt,
)
from .prompt_compiler import (
    compile_prompt, compile_optimized_prompt, full_pipeline,
    compile_narrative, compile_timed_prompt, overlay_plan,
    build_blueprint,
)
from .validator import (
    validate_prompt, count_camera_moves, count_primary_actions,
    estimate_speech_duration, check_offer_claims, check_text_generation_risk,
    check_commercial_claims, score_validation, validate_scene_plan,
    stray_camera_moves, conflicting_action_intents,
)
from .repair import (
    auto_repair, repair_plan, diagnose_scene, diagnose_script, apply_repairs,
)

__all__ = [
    # Legacy / VeoParams API
    "VeoParams", "Category", "Tone", "CameraMove", "ShotType",
    "LightingStyle", "FilmStyle", "AudioTrack", "Character",
    "generate", "generate_brief", "generate_json", "generate_elaborated",
    "festive", "showroom", "offer_features", "testimonial",
    "delivery", "features_closeup", "festive_offer",
    "new_launch", "service",
    # Industry-grade API
    "CampaignObjective", "AdConcept", "ContentFormat", "GenerationMode",
    "Script", "ScriptLine", "ScriptLanguage", "VoiceStyle", "DeliveryPacing",
    "OfferClaim", "OfferType", "ClaimCategory", "CommercialIssue",
    "ReferenceProfile", "ReferencePerson", "ReferenceVehicle", "ReferenceEnvironment",
    "ScaleGraph", "ModelSpec", "VariantSpec",
    "ScenePlan", "ShotComposition", "AudioPlan", "AdTimeline",
    "BrandPolicy", "ValidationResult", "ValidationScore",
    "SpeechModel", "SpeechBudget", "Brief", "RepairOp", "RepairResult",
    "VeoCapability", "VEO_3_1",
    "CreativeBlueprint", "CampaignSpec", "PresenterSpec", "VehicleSpec",
    "ShotSpec", "ActionSpec", "ScriptSpec", "BlueprintAudio", "PostPlan",
    "creative_director", "resolve_visual_action", "VISUAL_ACTIONS",
    "generate_script", "script_to_colon_format", "estimate_speech_duration_seconds",
    "rewrite_script_to_fit", "speech_rates",
    "create_verified_offer", "create_unverified_offer",
    "offer_to_script_text", "offer_to_voiceover", "safety_check",
    "create_reference_profile", "reference_to_ingredients_block",
    "reference_to_prompt_text", "vehicle_identity",
    "assert_vehicle_identity_untouched",
    "IMMUTABLE_VEHICLE_ATTRS", "MUTABLE_VEHICLE_ATTRS",
    "plan_scene",
    "compile_audio_directive", "audio_to_veo_format",
    "validate_audio_plan", "estimate_dialogue_fit",
    "get_brand_policy", "validate_brand_safety", "build_brand_constraint_section",
    "get_model_spec", "validate_model_feature", "MODEL_FEATURES",
    "compose_shot", "camera_to_veo_prompt", "get_safe_zone_prompt",
    "compile_prompt", "compile_optimized_prompt", "full_pipeline",
    "compile_narrative", "compile_timed_prompt", "overlay_plan",
    "build_blueprint",
    "validate_prompt", "count_camera_moves", "count_primary_actions",
    "estimate_speech_duration", "check_offer_claims", "check_text_generation_risk",
    "check_commercial_claims", "score_validation", "validate_scene_plan",
    "stray_camera_moves", "conflicting_action_intents",
    "auto_repair", "repair_plan", "diagnose_scene", "diagnose_script",
    "apply_repairs",
]