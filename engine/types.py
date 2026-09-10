from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


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


# ─── Script / Dialogue ──────────────────────────────────────────────

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


@dataclass
class ScriptLine:
    segment: str
    text: str
    duration_seconds: float = 0.0

    def estimate_speech_duration(self, words: Optional[list] = None) -> float:
        """Estimate speech duration. Indian speech ~3.2 words/sec for Hindi, ~2.8 for English."""
        w = words or self.text.split()
        word_count = len(w)
        wps = 3.0
        return round(word_count / wps, 1)


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

    @property
    def total_words(self) -> int:
        return sum(len(s.text.split()) for s in self.all_lines)

    @property
    def estimated_duration(self) -> float:
        return sum(s.estimate_speech_duration() for s in self.all_lines)

    @property
    def all_lines(self) -> list:
        return [self.hook, self.offer, self.product, self.benefit, self.cta]

    def compress(self, target_seconds: int = 8) -> str:
        """Compress script into spoken lines that fit target duration."""
        max_words = int(target_seconds * 2.8)
        lines = []
        total = 0
        for s in self.all_lines:
            words = s.text.strip().rstrip(".").split()
            remaining = max_words - total
            if remaining <= 0:
                break
            trimmed = words[:remaining]
            total += len(trimmed)
            if trimmed:
                lines.append(" ".join(trimmed))
        return ". ".join(lines)


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
    position: str = "rear_three_quarter"
    orientation: str = "angled_front"


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
        t = 0
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
