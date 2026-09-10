from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Category(Enum):
    FESTIVE = "festive"
    DEALER_SHOWROOM = "dealer_showroom"
    OFFER_FEATURES = "offer_features"
    CUSTOMER_TESTIMONIALS = "customer_testimonials"
    CAR_DELIVERY = "car_delivery"
    FEATURES_CLOSEUP = "features_closeup"
    FESTIVE_OFFER = "festive_offer"
    NEW_LAUNCH = "new_launch"
    SERVICE = "service"


class Tone(Enum):
    PREMIUM = "premium"
    ENERGETIC = "energetic"
    WARM = "warm"
    EPIC = "epic"
    PROFESSIONAL = "professional"
    AUTHENTIC = "authentic"
    DYNAMIC = "dynamic"


class CameraMove(Enum):
    SLOW_PUSH_IN = "slow push-in"
    DOLLY_IN = "dolly in"
    DOLLY_OUT = "dolly out"
    SLOW_PAN = "slow pan"
    TRACKING = "tracking shot"
    CRANE = "crane shot"
    HANDHELD_FOLLOW = "handheld follow"
    ORBIT = "orbit"
    MACRO_GLIDE = "macro glide"
    STATIC = "static shot"
    LOCKED_OFF = "locked-off shot"
    AERIAL = "aerial drift"
    SLIDER = "slider shot"
    RACK_FOCUS = "rack focus"


class ShotType(Enum):
    EXTREME_WIDE = "extreme wide shot"
    WIDE = "wide shot"
    MEDIUM = "medium shot"
    MEDIUM_CLOSE = "medium close-up"
    CLOSE_UP = "close-up"
    EXTREME_CLOSE = "extreme close-up"
    LOW_ANGLE = "low-angle shot"
    HIGH_ANGLE = "high-angle shot"
    TWO_SHOT = "two-shot"
    POV = "POV shot"


class LightingStyle(Enum):
    WARM_GOLDEN = "warm golden light"
    COOL_BLUE = "cool blue ambient"
    NEON = "neon accent lighting"
    SHOWROOM_LED = "bright showroom track lighting"
    BACKLIT = "backlit with rim light"
    GOLDEN_HOUR = "golden hour sunlight"
    DRAMATIC_SPOT = "dramatic spotlight"
    SOFT_DIFFUSED = "soft diffused light"
    FESTIVE_WARM = "warm festive string light"
    DAYLIGHT = "natural daylight"


class FilmStyle(Enum):
    PHOTOREAL = "photorealistic commercial"
    CINEMATIC = "cinematic"
    LUXURY_AD = "luxury advertisement"
    DOCUMENTARY = "documentary style"
    VINTAGE_FILM = "vintage film stock"
    MODERN_CLEAN = "modern clean digital"
    FILM_GRAIN = "subtle 35mm film grain"
    EPIC = "epic cinematic"


class AudioTrack(Enum):
    FESTIVE_INSTRUMENTAL = "soft festive instrumental"
    AMBIENT_JAZZ = "soft ambient jazz"
    ENERGETIC_BEAT = "upbeat rhythmic music"
    DRAMATIC_SCORE = "dramatic orchestral score"
    PROFESSIONAL_SOFT = "soft professional background"
    CELEBRATORY = "celebratory upbeat music"
    ELECTRONIC_AMBIENT = "soft electronic ambient"
    NONE = ""


@dataclass
class Character:
    description: str
    voice_style: Optional[str] = None
    dialogue: Optional[str] = None

    @property
    def has_dialogue(self) -> bool:
        return self.dialogue is not None


@dataclass
class VeoParams:
    category: Category
    brand: str
    car_model: str
    car_color: str = "white"
    tone: Tone = Tone.PREMIUM

    shot_type: ShotType = ShotType.MEDIUM
    camera_move: CameraMove = CameraMove.SLOW_PUSH_IN
    secondary_camera: Optional[CameraMove] = None

    lighting: LightingStyle = LightingStyle.SHOWROOM_LED
    film_style: FilmStyle = FilmStyle.PHOTOREAL

    audio_track: AudioTrack = AudioTrack.AMBIENT_JAZZ
    ambient_sfx: str = ""
    dialogue_char: Optional[Character] = None

    setting: str = ""
    duration: int = 8
    motion_intensity: str = "low"

    festival: Optional[str] = None
    offer_text: Optional[str] = None

    additional_details: list = field(default_factory=list)
    negatives: list = field(default_factory=list)

    def __post_init__(self):
        if self.car_model and not self.setting:
            self.setting = self._default_setting()

    def _default_setting(self) -> str:
        defaults = {
            Category.FESTIVE: f"festive-decorated {self.brand} dealership showroom",
            Category.DEALER_SHOWROOM: f"premium {self.brand} dealership showroom",
            Category.OFFER_FEATURES: f"branded {self.brand} dealership showroom",
            Category.CUSTOMER_TESTIMONIALS: f"{self.brand} dealership forecourt",
            Category.CAR_DELIVERY: f"{self.brand} dealership delivery bay",
            Category.FEATURES_CLOSEUP: "dark studio with glossy reflections",
            Category.FESTIVE_OFFER: f"festive-decorated {self.brand} dealership",
            Category.NEW_LAUNCH: f"{self.brand} showroom reveal stage",
            Category.SERVICE: f"modern {self.brand} authorized service center",
        }
        return defaults.get(self.category, f"{self.brand} dealership")

    @property
    def aspect_ratio(self) -> str:
        return "9:16 vertical"

    @property
    def format_instruction(self) -> str:
        return f"{self.aspect_ratio}, {self.duration} seconds"
