from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List


# ─── Campaign / Creative Strategy ───────────────────────────────────

class CampaignObjective(Enum):
    ENQUIRY = "enquiry"
    BOOKING = "booking"
    TEST_DRIVE = "test_drive"
    DELIVERY = "delivery"
    OFFER_AWARENESS = "offer_awareness"
    BRAND_AWARENESS = "brand_awareness"
    SERVICE_BOOKING = "service_booking"
    FESTIVE_PROMO = "festive_promo"
    NEW_LAUNCH = "new_launch"


class AdConcept(Enum):
    PRESENTER_LED = "presenter_led"
    VOICEOVER_LED = "voiceover_led"
    TESTIMONIAL = "testimonial"
    REVEAL = "reveal"
    LIFESTYLE = "lifestyle"
    PRODUCT_SHOWCASE = "product_showcase"
    FESTIVE_CELEBRATION = "festive_celebration"
    DELIVERY_MOMENT = "delivery_moment"
    SERVICE_TRUST = "service_trust"


class ContentFormat(Enum):
    INSTAGRAM_REEL = "instagram_reel"
    YOUTUBE_SHORT = "youtube_short"
    FACEBOOK_REEL = "facebook_reel"
    WHATSAPP_STATUS = "whatsapp_status"
    INSTAGRAM_STORY = "instagram_story"


class GenerationMode(Enum):
    """How the video is produced by Veo."""
    SINGLE_SHOT = "single_shot"
    MULTI_SHOT_TIMED = "multi_shot_timed"


class ScriptLanguage(Enum):
    HINDI = "hi-IN"
    HINGLISH = "hi-IN-Latn"
    ENGLISH = "en-IN"
    MARATHI = "mr-IN"
    GUJARATI = "gu-IN"
    TAMIL = "ta-IN"
    TELUGU = "te-IN"
    KANNADA = "kn-IN"
    MALAYALAM = "ml-IN"
    BENGALI = "bn-IN"
    PUNJABI = "pa-IN"


class VoiceStyle(Enum):
    ENERGETIC = "energetic"
    CONFIDENT = "confident"
    WARM = "warm"
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    EMOTIONAL = "emotional"
    TRUSTWORTHY = "trustworthy"


class DeliveryPacing(Enum):
    SLOW = "slow"
    MEDIUM = "medium"
    MEDIUM_FAST = "medium_fast"
    FAST = "fast"


# ─── Speech model (single canonical estimator) ─────────────────────

@dataclass(frozen=True)
class SpeechBudget:
    rate_wps: float
    duration_seconds: int
    safe_fraction: float
    safe_seconds: float
    max_words_full_pace: int
    max_words_safe: int


class SpeechModel:
    """
    Canonical speech-time model. ONE source of truth for words-per-second
    and the safe speech budget inside an ad of a given duration.

    Safe budget = duration * SAFE_FRACTION. For an 8s ad that is ~6.5-7.0s
    of speech, leaving room for music, ambient, pauses and pacing.
    """
    SAFE_FRACTION = 0.85

    RATES_WPS = {
        ScriptLanguage.HINDI: 3.2,
        ScriptLanguage.HINGLISH: 3.0,
        ScriptLanguage.ENGLISH: 2.8,
        ScriptLanguage.MARATHI: 3.0,
        ScriptLanguage.GUJARATI: 3.0,
        ScriptLanguage.TAMIL: 2.8,
        ScriptLanguage.TELUGU: 2.8,
        ScriptLanguage.KANNADA: 2.8,
        ScriptLanguage.MALAYALAM: 2.8,
        ScriptLanguage.BENGALI: 3.0,
        ScriptLanguage.PUNJABI: 3.0,
    }

    @classmethod
    def rate(cls, lang: "ScriptLanguage" = ScriptLanguage.HINDI) -> float:
        return cls.RATES_WPS.get(lang, 3.0)

    @classmethod
    def estimate(cls, text: str, lang: "ScriptLanguage" = ScriptLanguage.HINDI) -> float:
        """Estimated speech seconds for arbitrary text."""
        words = len(text.split()) if text else 0
        if not words:
            return 0.0
        return round(words / cls.rate(lang), 1)

    @classmethod
    def budget(cls, duration: int, lang: "ScriptLanguage" = ScriptLanguage.HINDI) -> SpeechBudget:
        rate = cls.rate(lang)
        safe_seconds = round(duration * cls.SAFE_FRACTION, 1)
        return SpeechBudget(
            rate_wps=rate,
            duration_seconds=duration,
            safe_fraction=cls.SAFE_FRACTION,
            safe_seconds=safe_seconds,
            max_words_full_pace=int(duration * rate),
            max_words_safe=int(safe_seconds * rate),
        )

    @classmethod
    def fit_report(cls, text: str, duration: int, lang: "ScriptLanguage" = ScriptLanguage.HINDI) -> dict:
        b = cls.budget(duration, lang)
        est = cls.estimate(text, lang)
        return {
            "words": len(text.split()) if text else 0,
            "estimated_seconds": est,
            "safe_seconds": b.safe_seconds,
            "duration": duration,
            "rate": b.rate_wps,
            "max_words_safe": b.max_words_safe,
            "fits_safe": est <= b.safe_seconds,
            "fits_at_all": est <= duration,
            "words_over_safe": max(0, est - b.safe_seconds),
        }


# ─── Script / Dialogue ──────────────────────────────────────────────

@dataclass
class ScriptLine:
    segment: str
    text: str
    condensed: str = ""
    duration_seconds: float = 0.0

    @property
    def word_count(self) -> int:
        return len(self.text.split()) if self.text else 0

    @property
    def condensed_word_count(self) -> int:
        return len(self.condensed.split()) if self.condensed else 0

    def estimate_speech_duration(self, lang: ScriptLanguage = ScriptLanguage.HINDI) -> float:
        """Estimated speech duration using the canonical SpeechModel."""
        return SpeechModel.estimate(self.text, lang)

    def pick(self, budget_words: int, lang: ScriptLanguage = ScriptLanguage.HINDI) -> str:
        """Pick full text (or condensed rewrite) that fits a word budget.
        Never cuts mid-sentence: falls back to the condensed variant, else empty."""
        if not self.text:
            return ""
        if self.word_count <= budget_words:
            return self.text
        if self.condensed and self.condensed_word_count <= budget_words:
            return self.condensed
        return ""


def _segment_priority(objective: "CampaignObjective") -> List[str]:
    """Objective-aware priority for deciding what to keep when over budget."""
    offer_leading = {
        CampaignObjective.ENQUIRY,
        CampaignObjective.TEST_DRIVE,
        CampaignObjective.OFFER_AWARENESS,
        CampaignObjective.BOOKING,
        CampaignObjective.FESTIVE_PROMO,
    }
    product_leading = {
        CampaignObjective.NEW_LAUNCH,
        CampaignObjective.BRAND_AWARENESS,
    }
    if objective in offer_leading:
        return ["offer", "cta", "product", "benefit", "hook"]
    if objective in product_leading:
        return ["product", "offer", "cta", "benefit", "hook"]
    # emotion/trust-led
    return ["cta", "benefit", "product", "offer", "hook"]


@dataclass
class Script:
    hook: ScriptLine
    offer: ScriptLine
    product: ScriptLine
    benefit: ScriptLine
    cta: ScriptLine
    language: ScriptLanguage = ScriptLanguage.HINDI
    voice_style: VoiceStyle = VoiceStyle.CONFIDENT
    pacing: DeliveryPacing = DeliveryPacing.MEDIUM_FAST
    cta_emphasis: str = "high"
    objective: Optional["CampaignObjective"] = None
    ad_concept: Optional["AdConcept"] = None

    @property
    def total_words(self) -> int:
        return sum(s.word_count for s in self.all_lines)

    @property
    def estimated_duration(self) -> float:
        return round(sum(s.estimate_speech_duration(self.language) for s in self.all_lines), 1)

    @property
    def all_lines(self) -> List[ScriptLine]:
        return [self.hook, self.offer, self.product, self.benefit, self.cta]

    def segment_order(self) -> List[str]:
        return ["hook", "offer", "product", "benefit", "cta"]

    def priority(self) -> List[str]:
        obj = self.objective or CampaignObjective.ENQUIRY
        return _segment_priority(obj)

    def with_segment(self, segment: str, text: str, condensed: str = "") -> "Script":
        line = ScriptLine(segment=segment, text=text, condensed=condensed)
        setattr(self, segment, line)
        return self

    def rewrite_to_fit(self, duration: int = 8) -> "Script":
        """Returns a NEW Script rewritten to fit the safe speech budget.

        Never truncates a sentence: whole lines whose full form does not fit
        fall back to their condensed rewrite. The CTA is always preserved.
        """
        from .script_engine import rewrite_script_to_fit
        return rewrite_script_to_fit(self, target_seconds=duration)

    def dialogue_text(self, duration: int = 8, rewritten: bool = True) -> str:
        target = self.rewrite_to_fit(duration) if rewritten else self
        kept = [s.text.strip().rstrip(".") for s in target.all_lines if s.text]
        return (". ".join(kept) + ".") if kept else ""

    def compress(self, target_seconds: int = 8) -> str:
        """DEPRECATED: use dialogue_text(rewritten=True). Kept for back-compat."""
        return self.dialogue_text(target_seconds)

    def spoken_lines(self, duration: int = 8) -> List[ScriptLine]:
        """The exact lines that survive the rewrite, in narrative order, with timings."""
        rewritten = self.rewrite_to_fit(duration)
        out = []
        t = 0.0
        for line in rewritten.all_lines:
            if not line.text:
                continue
            dur = line.estimate_speech_duration(rewritten.language)
            out.append(_timed_line(line, t, dur))
            t += dur
        return out


def _timed_line(line: ScriptLine, start: float, duration: float) -> dict:
    return {
        "segment": line.segment,
        "text": line.text,
        "start_seconds": round(start, 1),
        "end_seconds": round(start + duration, 1),
        "duration_seconds": round(duration, 1),
    }


# ─── Brief (single intake for the full pipeline) ────────────────────

@dataclass
class Brief:
    """The one business brief that drives every downstream layer."""
    objective: CampaignObjective
    ad_concept: AdConcept
    brand: str
    car_model: str
    car_colour: str = "white"
    format: ContentFormat = ContentFormat.INSTAGRAM_REEL
    language: ScriptLanguage = ScriptLanguage.HINDI
    duration: int = 8
    generation_mode: GenerationMode = GenerationMode.SINGLE_SHOT
    voice_style: VoiceStyle = VoiceStyle.CONFIDENT
    pacing: DeliveryPacing = DeliveryPacing.MEDIUM_FAST
    custom_hook: Optional[str] = None
    custom_offer: Optional[str] = None
    custom_benefit: Optional[str] = None
    custom_cta: Optional[str] = None
    offer: Optional["OfferClaim"] = None
    reference: Optional["ReferenceProfile"] = None
    debug: bool = False


# ─── Offer Intelligence ─────────────────────────────────────────────

class OfferType(Enum):
    CASHBACK = "cashback"
    FINANCE_RATE = "finance_rate"
    EXCHANGE_BONUS = "exchange_bonus"
    FREE_ACCESSORY = "free_accessory"
    INSURANCE = "insurance"
    CORPORATE_DISCOUNT = "corporate_discount"
    FESTIVE_DISCOUNT = "festive_discount"
    LOW_EMI = "low_emi"
    ZERO_DOWNPAYMENT = "zero_downpayment"
    GENERIC = "generic"


@dataclass
class OfferClaim:
    offer_type: OfferType
    value: Optional[str] = None
    numeric_value: Optional[float] = None
    unit: Optional[str] = None
    validity: Optional[str] = None
    model: Optional[str] = None
    geography: Optional[str] = None
    finance_conditions: Optional[str] = None
    source: Optional[str] = None
    verified: bool = False
    disclaimer: str = ""

    def to_safe_text(self, language: ScriptLanguage = ScriptLanguage.HINDI) -> str:
        if not self.verified:
            return self._generic_fallback(language)
        parts = []
        if self.numeric_value and self.unit:
            parts.append(f"{self.unit}{self.numeric_value:,.0f}")
        elif self.value:
            parts.append(self.value)
        if self.validity:
            parts.append(f"valid till {self.validity}")
        return " + ".join(parts) if parts else self._generic_fallback(language)

    def _generic_fallback(self, lang: ScriptLanguage) -> str:
        fallbacks = {
            ScriptLanguage.HINDI: "Special finance offers available hain",
            ScriptLanguage.HINGLISH: "Special finance offers available hain",
            ScriptLanguage.ENGLISH: "Special finance offers available now",
        }
        return fallbacks.get(lang, "Special finance offers available now")


# ─── Commercial claims (offer + product + performance + comparative) ─

class ClaimCategory(Enum):
    OFFER = "offer"
    PRODUCT = "product"
    PERFORMANCE = "performance"
    SAFETY = "safety"
    COMPARATIVE = "comparative"
    SUPERLATIVE = "superlative"
    URGENCY = "urgency"
    FINANCE = "finance"
    TCO = "total_cost_of_ownership"
    WARRANTY = "warranty"


@dataclass
class CommercialIssue:
    category: ClaimCategory
    severity: str  # "error" | "warning"
    message: str
    recommendation: str = ""
    evidence: str = ""

    @property
    def is_error(self) -> bool:
        return self.severity == "error"


# ─── Reference Intelligence ─────────────────────────────────────────

@dataclass
class ReferencePerson:
    face_identity: str = ""
    approximate_height: str = "average"
    body_proportions: str = "average"
    hair: str = ""
    skin_tone: str = ""
    clothing: str = ""
    accessories: str = ""
    pose: str = "standing"
    camera_relationship: str = "looking_at_camera"


@dataclass
class ReferenceVehicle:
    model: str = ""
    body_type: str = "SUV"
    colour: str = ""
    generation: str = "current"
    geometry: str = ""
    wheel_design: str = ""
    trim: str = ""
    badging: str = ""
    position: str = "rear_three_quarter"
    orientation: str = "angled_front"

    @property
    def identity_terms(self) -> dict:
        """Immutable identity — must survive in the generated video."""
        return {
            "model": self.model,
            "body_type": self.body_type,
            "colour": self.colour,
            "generation": self.generation,
            "geometry": self.geometry,
            "trim": self.trim,
            "badging": self.badging,
        }

    @property
    def identity_present(self) -> bool:
        return any(self.identity_terms.values())


IMMUTABLE_VEHICLE_ATTRS = ("model", "body_type", "generation", "geometry", "colour", "trim", "badging")
MUTABLE_VEHICLE_ATTRS = ("position", "orientation")


@dataclass
class ScaleGraph:
    """Physical relationship that must be preserved between subjects."""
    presenter_to_vehicle_m: float = 1.5
    camera_to_subject_m: float = 2.2
    lens_focal_mm: int = 35
    constraint: str = (
        "preserve exact human-to-vehicle proportions"
    )


@dataclass
class ReferenceEnvironment:
    location_type: str = "showroom"
    architecture: str = "modern_dealership"
    floor: str = "polished_tile"
    lighting: str = "showroom_led"
    background: str = "clean_showroom"
    props: str = ""


@dataclass
class ReferenceProfile:
    person: Optional[ReferencePerson] = None
    vehicle: Optional[ReferenceVehicle] = None
    environment: Optional[ReferenceEnvironment] = None
    scale: Optional[ScaleGraph] = None
    reference_image_count: int = 0

    def describe_for_prompt(self) -> str:
        parts = []
        if self.vehicle and self.vehicle.model:
            v = self.vehicle
            parts.append(
                f"{v.colour} {v.model} in {v.position} position, "
                f"{v.orientation} orientation"
            )
        if self.person and self.person.face_identity:
            p = self.person
            parts.append(
                f"person: {p.hair} hair, {p.skin_tone} skin, "
                f"wearing {p.clothing}"
            )
        if self.environment:
            e = self.environment
            parts.append(
                f"setting: {e.location_type}, {e.lighting} lighting, "
                f"{e.floor} floor"
            )
        if self.scale:
            parts.append(f"scale: {self.scale.constraint}")
        return "; ".join(parts)


# ─── Scene Planning ─────────────────────────────────────────────────

@dataclass
class ShotComposition:
    shot_type: str = "medium"
    camera_move: str = "slow push-in"
    headroom: str = "standard"
    hand_visibility: str = "natural"
    offer_card_visibility: Optional[str] = None
    vehicle_visibility: str = "background"
    safe_zone: str = "9:16_center"
    cta_safe_zone: str = "lower_third"
    depth: str = "shallow"


@dataclass
class AudioPlan:
    voice_priority: str = "dominant"
    music_level: str = "-12dB relative"
    ambient_level: str = "subtle"
    key_sfx: str = ""
    key_sfx_timing: Optional[str] = None
    cta_emphasis: str = "final_sentence"
    music_style: str = ""
    ambient_sounds: list = field(default_factory=list)
    dialogue_colon: str = ""


@dataclass
class ScenePlan:
    duration: int = 8
    aspect_ratio: str = "9:16"
    shot_count: int = 1
    camera_move: str = "slow push-in"
    subject: str = ""
    secondary_subject: str = ""
    primary_action: str = ""
    dominant_action: str = ""
    micro_behavior: str = ""
    background_behavior: str = ""
    supporting_beats: list = field(default_factory=list)
    location: str = ""
    lighting: str = ""
    script_language: str = "hi-IN"
    script: str = ""
    cta: str = ""
    composition: Optional[ShotComposition] = None
    audio: Optional[AudioPlan] = None
    ad_timeline: Optional[dict] = None


# ─── Ad Psychology Timeline ─────────────────────────────────────────

@dataclass
class AdTimeline:
    hook_seconds: float = 1.5
    offer_seconds: float = 3.0
    product_seconds: float = 2.0
    cta_seconds: float = 1.5
    total_seconds: float = 8.0

    def timecoded_segments(self) -> dict:
        t = 0.0
        segments = {}
        for name, dur in [
            ("hook", self.hook_seconds),
            ("offer", self.offer_seconds),
            ("product", self.product_seconds),
            ("cta", self.cta_seconds),
        ]:
            start = t
            t += dur
            segments[name] = (round(start, 1), round(t, 1))
        return segments


# ─── Creative Blueprint (v2 — the strict internal contract) ──────────
# Every layer converges into ONE CreativeBlueprint; the Veo prompt is then a
# pure compiler output from it. Nothing downstream rewrites the prose around
# it — repair mutates the inputs, the compiler re-renders.

@dataclass
class CampaignSpec:
    objective: CampaignObjective
    ad_concept: AdConcept
    format: ContentFormat = ContentFormat.INSTAGRAM_REEL
    language: ScriptLanguage = ScriptLanguage.HINDI
    duration: int = 8
    audience: str = ""
    proof: str = ""
    creative_pattern: str = "offer_first"
    hook_strategy: str = ""
    ad_structure: dict = field(default_factory=dict)


@dataclass
class PresenterSpec:
    type: str = "salesperson"
    description: str = ""
    position: str = "midground"
    camera_relationship: str = "direct_to_camera"
    hand_visibility: str = "natural"
    voice: str = ""
    reference_person: Optional["ReferencePerson"] = None


@dataclass
class VehicleSpec:
    model: str = ""
    colour: str = ""
    body_type: str = "SUV"
    generation: str = "current"
    trim: str = ""
    position: str = "rear_three_quarter"
    orientation: str = "angled_front"
    relation_to_presenter: str = "1.5m beside the presenter"
    reference_vehicle: Optional["ReferenceVehicle"] = None


@dataclass
class ShotSpec:
    shot_type: str = "medium presenter shot"
    camera_move: str = "slow push-in"
    headroom: str = "standard"
    hand_visibility: str = "natural"
    depth: str = "shallow"
    offer_card_visibility: Optional[str] = None
    vehicle_visibility: str = "background"
    safe_zone: str = "9:16_center"
    cta_safe_zone: str = "lower_third"
    aspect_ratio: str = "9:16"
    duration: int = 8


@dataclass
class ActionSpec:
    """ONE dominant action + optional CONTINUOUS micro-behavior + background.

    Not "one primary + up to 3 beats": an 8s single shot holds ONE dominant
    visible action. The micro-behavior is a continuous, non-competitive trait
    (e.g. speaking naturally); the background behavior is inert context.
    """
    dominant: str = ""
    micro_behavior: str = ""
    background_behavior: str = ""

    @property
    def primary(self) -> str:
        return self.dominant


@dataclass
class ScriptSpec:
    hook: str = ""
    offer: str = ""
    product: str = ""
    benefit: str = ""
    cta: str = ""
    dialogue: str = ""
    language: ScriptLanguage = ScriptLanguage.HINDI
    voice_style: VoiceStyle = VoiceStyle.CONFIDENT
    pacing: DeliveryPacing = DeliveryPacing.MEDIUM_FAST


@dataclass
class BlueprintAudio:
    voice_priority: str = "dominant"
    music_style: str = ""
    ambient: list = field(default_factory=list)
    sfx: str = ""
    cta_emphasis: str = "final_sentence"
    dialogue: str = ""


@dataclass
class PostPlan:
    offer_card: Optional[str] = None
    cta_overlay: Optional[str] = None
    logo: bool = True
    contact_info: bool = False
    disclaimer: bool = False


@dataclass
class CreativeBlueprint:
    """The strict internal object the whole engine compiles from."""
    campaign: CampaignSpec
    presenter: PresenterSpec
    vehicle: VehicleSpec
    shot: ShotSpec
    action: ActionSpec
    script: ScriptSpec
    audio: BlueprintAudio
    post: PostPlan
    generation_mode: GenerationMode = GenerationMode.SINGLE_SHOT
    reference: Optional["ReferenceProfile"] = None
    brand_policy: Optional["BrandPolicy"] = None
    ad_timeline: Optional[dict] = None


# ─── Brand Safety ───────────────────────────────────────────────────

@dataclass
class BrandPolicy:
    brand: str = ""
    approved_model_names: list = field(default_factory=list)
    approved_offer_wording: list = field(default_factory=list)
    approved_terminology: list = field(default_factory=list)
    logo_handling: str = "do_not_generate_text"
    dealership_environment: str = "official_showroom"
    no_invented_claims: bool = True
    no_altered_geometry: bool = True
    contact_info: str = ""
    disclaimer: str = ""
    tagline: str = ""


@dataclass
class VariantSpec:
    name: str
    features: list = field(default_factory=list)
    transmission: str = ""


@dataclass
class ModelSpec:
    model: str
    body_type: str = "SUV"
    variants: List[VariantSpec] = field(default_factory=list)
    shared_features: list = field(default_factory=list)
    unavailable_features: list = field(default_factory=list)

    def has_feature(self, feature: str) -> bool:
        f = feature.lower()
        if f in [x.lower() for x in self.unavailable_features]:
            return False
        if f in [x.lower() for x in self.shared_features]:
            return True
        return any(f in [y.lower() for y in v.features] for v in self.variants)

    def feature_applicability(self, feature: str) -> dict:
        f = feature.lower()
        applicable_variants = [] if self.has_feature(feature) else ["none"]
        if f not in [x.lower() for x in self.unavailable_features]:
            applicable_variants = sorted(
                set(
                    [v.name for v in self.variants if f in [y.lower() for y in v.features]]
                )
            )
            if not applicable_variants and f in [x.lower() for x in self.shared_features]:
                applicable_variants = ["all variants"]
        return {
            "feature": feature,
            "model": self.model,
            "applicable": self.has_feature(feature),
            "applicable_variants": applicable_variants,
        }


# ─── Validation ─────────────────────────────────────────────────────

@dataclass
class ValidationResult:
    passed: bool = True
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def fail(self, msg: str):
        self.passed = False
        self.errors.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)

    def __bool__(self):
        return self.passed


@dataclass
class ValidationScore:
    score: float = 100.0
    grade: str = "A"
    deductions: list = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.score >= 70.0

    def deduct(self, points: float, reason: str):
        self.score = round(max(0.0, self.score - points), 1)
        self.deductions.append(f"-{points:g} {reason}")
        self.grade = self._grade()

    @staticmethod
    def _grade_from(s: float) -> str:
        if s >= 90:
            return "A"
        if s >= 80:
            return "B"
        if s >= 70:
            return "C"
        if s >= 60:
            return "D"
        return "F"

    def _grade(self) -> str:
        return self._grade_from(self.score)


# ─── Repair (structural, applied to the Plan not the prose) ─────────

@dataclass
class RepairOp:
    target: str      # "scene" | "script" | "prompt" | "claim"
    field: str = ""
    old_value: str = ""
    new_value: str = ""
    reason: str = ""

    def describe(self) -> str:
        if self.field and self.old_value:
            return f"{self.field}: [{self.old_value}] -> [{self.new_value}] ({self.reason})"
        return f"{self.target}: {self.reason}"


@dataclass
class RepairResult:
    prompt: str = ""
    scene: Optional[ScenePlan] = None
    script: Optional[Script] = None
    ops: List[RepairOp] = field(default_factory=list)
    score: float = 100.0

    @property
    def was_repaired(self) -> bool:
        return bool(self.ops)

    @property
    def changes(self) -> List[str]:
        return [op.describe() for op in self.ops]


# ─── Veo capability model ───────────────────────────────────────────

@dataclass(frozen=True)
class VeoCapability:
    model: str = "veo-3.1"
    durations_seconds: tuple = (4, 6, 8)
    aspect_ratios: tuple = ("9:16", "16:9", "1:1", "4:3", "3:4", "4:5")
    max_reference_images: int = 5
    reference_i2v_max_seconds: int = 8
    audio_enabled: bool = True

    def validate_duration(self, duration: int) -> list:
        issues = []
        if duration not in self.durations_seconds:
            issues.append(
                f"Duration {duration}s not supported by {self.model} "
                f"(supported: {self.durations_seconds})"
            )
        return issues

    def validate_aspect(self, aspect: str) -> list:
        issues = []
        if aspect not in self.aspect_ratios:
            issues.append(f"Aspect {aspect} not supported (supported: {self.aspect_ratios})")
        return issues

    def validate_mode(self, mode: "GenerationMode", duration: int) -> list:
        issues = []
        if mode == GenerationMode.MULTI_SHOT_TIMED and duration != 8:
            issues.append("Multi-shot timed mode models Veo 3.1 time-based prompting for 8s clips")
        return issues


VEO_3_1 = VeoCapability()