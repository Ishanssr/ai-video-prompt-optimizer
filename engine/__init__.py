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
    CampaignObjective, AdConcept, ContentFormat,
    Script, ScriptLine, ScriptLanguage, VoiceStyle, DeliveryPacing,
    OfferClaim, OfferType,
    ReferenceProfile, ReferencePerson, ReferenceVehicle, ReferenceEnvironment,
    ScenePlan, ShotComposition, AudioPlan, AdTimeline,
    BrandPolicy, ValidationResult,
)
from .creative_director import creative_director
from .script_engine import (
    generate_script, script_to_colon_format, estimate_speech_duration_seconds,
)
from .offer_engine import (
    create_verified_offer, create_unverified_offer,
    offer_to_script_text, offer_to_voiceover, safety_check,
)
from .reference_engine import (
    create_reference_profile, reference_to_ingredients_block,
)
from .scene_planner import plan_scene
from .audio_engine import (
    compile_audio_directive, audio_to_veo_format,
    validate_audio_plan, estimate_dialogue_fit,
)
from .brand_engine import (
    get_brand_policy, validate_brand_safety, build_brand_constraint_section,
)
from .camera_engine import (
    compose_shot, camera_to_veo_prompt, get_safe_zone_prompt,
)
from .prompt_compiler import (
    compile_prompt, compile_optimized_prompt, full_pipeline,
)
from .validator import (
    validate_prompt, count_camera_moves, count_primary_actions,
    estimate_speech_duration, check_offer_claims, check_text_generation_risk,
)
from .repair import auto_repair

__all__ = [
    # Legacy / VeoParams API
    "VeoParams", "Category", "Tone", "CameraMove", "ShotType",
    "LightingStyle", "FilmStyle", "AudioTrack", "Character",
    "generate", "generate_brief", "generate_json", "generate_elaborated",
    "festive", "showroom", "offer_features", "testimonial",
    "delivery", "features_closeup", "festive_offer",
    "new_launch", "service",
    # Industry-grade API
    "CampaignObjective", "AdConcept", "ContentFormat",
    "Script", "ScriptLine", "ScriptLanguage", "VoiceStyle", "DeliveryPacing",
    "OfferClaim", "OfferType",
    "ReferenceProfile", "ReferencePerson", "ReferenceVehicle", "ReferenceEnvironment",
    "ScenePlan", "ShotComposition", "AudioPlan", "AdTimeline",
    "BrandPolicy", "ValidationResult",
    "creative_director",
    "generate_script", "script_to_colon_format", "estimate_speech_duration_seconds",
    "create_verified_offer", "create_unverified_offer",
    "offer_to_script_text", "offer_to_voiceover", "safety_check",
    "create_reference_profile", "reference_to_ingredients_block",
    "plan_scene",
    "compile_audio_directive", "audio_to_veo_format",
    "validate_audio_plan", "estimate_dialogue_fit",
    "get_brand_policy", "validate_brand_safety", "build_brand_constraint_section",
    "compose_shot", "camera_to_veo_prompt", "get_safe_zone_prompt",
    "compile_prompt", "compile_optimized_prompt", "full_pipeline",
    "validate_prompt", "count_camera_moves", "count_primary_actions",
    "estimate_speech_duration", "check_offer_claims", "check_text_generation_risk",
    "auto_repair",
]