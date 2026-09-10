from .params import VeoParams
from .templates import SceneBlock


def generate(params: VeoParams) -> str:
    scene = SceneBlock(params)
    sections = _compose(scene, params)
    return _render(sections)


def generate_brief(params: VeoParams) -> str:
    """Generate a short 1-2 sentence prompt for quick testing."""
    scene = SceneBlock(params)
    return (
        f"{scene.shot()} of {scene.subject()}, "
        f"{scene.action()}, {scene.context()}. "
        f"{scene.style()}. {scene.audio()}"
    )


def generate_elaborated(params: VeoParams) -> str:
    """
    Generate a detailed prompt following the exact Veo best-practice formula.
    Optimized for maximum Gemini Veo output quality.
    """
    scene = SceneBlock(params)
    return _render(_compose(scene, params))


def generate_json(params: VeoParams) -> dict:
    """Return prompt components as structured JSON for API consumption."""
    scene = SceneBlock(params)
    return {
        "cinematography": scene.shot(),
        "subject": scene.subject(),
        "action": scene.action(),
        "context": scene.context(),
        "style": scene.style(),
        "audio": scene.audio(),
        "format": scene.format_line(),
        "motion": scene.motion_line(),
        "negatives": scene.negatives_line(),
    }


def _compose(scene: SceneBlock, params: VeoParams) -> dict:
    return {
        "hero": (
            f"{scene.shot()} of {scene.subject()}, "
            f"{scene.action()}."
        ),
        "context": f"{scene.context()}.",
        "style": f"{scene.style()}.",
        "audio": f"{scene.audio()}.",
        "format": f"{scene.format_line()}. {scene.motion_line()}.",
    }


def _render(sections: dict) -> str:
    lines = [sections["hero"]]
    lines.append("")
    lines.append(sections["context"])
    lines.append("")
    lines.append(sections["style"])
    lines.append("")
    lines.append(sections["audio"])
    lines.append("")
    lines.append(sections["format"])
    return "\n".join(lines)


# ─── Convenience builders per category ──────────────────────────────

def festive(car_model: str, brand: str = "Maruti Suzuki",
            car_color: str = "white", festival: str = "Diwali",
            offer_text: str = None, tone: str = "warm") -> str:
    from .params import Category, Tone
    from .templates import CameraMove, ShotType, LightingStyle, FilmStyle, AudioTrack, Character

    params = VeoParams(
        category=Category.FESTIVE,
        brand=brand,
        car_model=car_model,
        car_color=car_color,
        tone=Tone(tone),
        shot_type=ShotType.MEDIUM,
        camera_move=CameraMove.SLOW_PUSH_IN,
        lighting=LightingStyle.FESTIVE_WARM,
        film_style=FilmStyle.PHOTOREAL,
        audio_track=AudioTrack.FESTIVE_INSTRUMENTAL,
        ambient_sfx="soft temple bells in the distance, crowd murmur",
        festival=festival,
        setting=(
            f"festive-decorated {brand} dealership showroom at dusk, "
            "marigold and jasmine garlands on every surface, "
            "rangoli patterns on the floor"
        ),
        additional_details=[
            "warm string lights create soft bokeh",
            "diyas flicker on the floor",
        ],
    )
    return generate(params)


def showroom(car_model: str, brand: str = "Maruti Suzuki",
             car_color: str = "silver", tone: str = "premium") -> str:
    from .params import Category, Tone
    from .templates import CameraMove, ShotType, LightingStyle, FilmStyle, AudioTrack

    params = VeoParams(
        category=Category.DEALER_SHOWROOM,
        brand=brand,
        car_model=car_model,
        car_color=car_color,
        tone=Tone(tone),
        shot_type=ShotType.WIDE,
        camera_move=CameraMove.DOLLY_IN,
        lighting=LightingStyle.SHOWROOM_LED,
        film_style=FilmStyle.PHOTOREAL,
        audio_track=AudioTrack.AMBIENT_JAZZ,
        ambient_sfx="soft footsteps, quiet conversation",
    )
    return generate(params)


def offer_features(car_model: str, brand: str = "Maruti Suzuki",
                   car_color: str = "red", offer: str = None,
                   tone: str = "energetic") -> str:
    from .params import Category, Tone
    from .templates import CameraMove, ShotType, LightingStyle, FilmStyle, AudioTrack

    params = VeoParams(
        category=Category.OFFER_FEATURES,
        brand=brand,
        car_model=car_model,
        car_color=car_color,
        tone=Tone(tone),
        shot_type=ShotType.CLOSE_UP,
        camera_move=CameraMove.SLOW_PAN,
        lighting=LightingStyle.SHOWROOM_LED,
        film_style=FilmStyle.LUXURY_AD,
        audio_track=AudioTrack.ENERGETIC_BEAT,
        ambient_sfx="electronic whoosh on transitions",
        offer_text=offer,
    )
    return generate(params)


def testimonial(car_model: str, brand: str = "Maruti Suzuki",
                car_color: str = "blue",
                customer_dialogue: str = "This is the best decision of my life.",
                customer_voice: str = "warm, genuine",
                tone: str = "authentic") -> str:
    from .params import Category, Tone
    from .templates import CameraMove, ShotType, LightingStyle, FilmStyle, AudioTrack, Character

    params = VeoParams(
        category=Category.CUSTOMER_TESTIMONIALS,
        brand=brand,
        car_model=car_model,
        car_color=car_color,
        tone=Tone(tone),
        shot_type=ShotType.MEDIUM_CLOSE,
        camera_move=CameraMove.STATIC,
        lighting=LightingStyle.GOLDEN_HOUR,
        film_style=FilmStyle.DOCUMENTARY,
        audio_track=AudioTrack.NONE,
        ambient_sfx="light wind, distant traffic",
        dialogue_char=Character(
            description="a satisfied car owner",
            voice_style=customer_voice,
            dialogue=customer_dialogue,
        ),
    )
    return generate(params)


def delivery(car_model: str, brand: str = "Maruti Suzuki",
             car_color: str = "white",
             customer_dialogue: str = None,
             tone: str = "warm") -> str:
    from .params import Category, Tone
    from .templates import CameraMove, ShotType, LightingStyle, FilmStyle, AudioTrack, Character

    dialogue_char = None
    if customer_dialogue:
        dialogue_char = Character(
            description="the proud car owner",
            voice_style="emotional, proud",
            dialogue=customer_dialogue,
        )

    params = VeoParams(
        category=Category.CAR_DELIVERY,
        brand=brand,
        car_model=car_model,
        car_color=car_color,
        tone=Tone(tone),
        shot_type=ShotType.MEDIUM,
        camera_move=CameraMove.TRACKING,
        lighting=LightingStyle.SHOWROOM_LED,
        film_style=FilmStyle.CINEMATIC,
        audio_track=AudioTrack.CELEBRATORY,
        ambient_sfx="confetti pop, applause, child's excited laugh",
        dialogue_char=dialogue_char,
    )
    return generate(params)


def features_closeup(car_model: str, brand: str = "Maruti Suzuki",
                     car_color: str = "black",
                     features: str = None,
                     tone: str = "premium") -> str:
    from .params import Category, Tone
    from .templates import CameraMove, ShotType, LightingStyle, FilmStyle, AudioTrack

    params = VeoParams(
        category=Category.FEATURES_CLOSEUP,
        brand=brand,
        car_model=car_model,
        car_color=car_color,
        tone=Tone(tone),
        shot_type=ShotType.EXTREME_CLOSE,
        camera_move=CameraMove.MACRO_GLIDE,
        lighting=LightingStyle.DRAMATIC_SPOT,
        film_style=FilmStyle.LUXURY_AD,
        audio_track=AudioTrack.ELECTRONIC_AMBIENT,
        ambient_sfx="soft whoosh, subtle metallic resonance",
        motion_intensity="low",
    )
    return generate(params)


def festive_offer(car_model: str, brand: str = "Maruti Suzuki",
                  car_color: str = "red", festival: str = "Diwali",
                  offer: str = None, tone: str = "energetic") -> str:
    from .params import Category, Tone
    from .templates import CameraMove, ShotType, LightingStyle, FilmStyle, AudioTrack

    params = VeoParams(
        category=Category.FESTIVE_OFFER,
        brand=brand,
        car_model=car_model,
        car_color=car_color,
        tone=Tone(tone),
        shot_type=ShotType.WIDE,
        camera_move=CameraMove.SLOW_PAN,
        lighting=LightingStyle.FESTIVE_WARM,
        film_style=FilmStyle.CINEMATIC,
        audio_track=AudioTrack.ENERGETIC_BEAT,
        ambient_sfx="festive clapping, firecrackers in distance",
        festival=festival,
        offer_text=offer,
    )
    return generate(params)


def new_launch(car_model: str, brand: str = "Maruti Suzuki",
               car_color: str = "silver", tone: str = "epic") -> str:
    from .params import Category, Tone
    from .templates import CameraMove, ShotType, LightingStyle, FilmStyle, AudioTrack

    params = VeoParams(
        category=Category.NEW_LAUNCH,
        brand=brand,
        car_model=car_model,
        car_color=car_color,
        tone=Tone(tone),
        shot_type=ShotType.WIDE,
        camera_move=CameraMove.CRANE,
        lighting=LightingStyle.DRAMATIC_SPOT,
        film_style=FilmStyle.EPIC,
        audio_track=AudioTrack.DRAMATIC_SCORE,
        ambient_sfx="drum roll, dramatic whoosh, crowd gasp",
    )
    return generate(params)


def service(car_model: str, brand: str = "Maruti Suzuki",
            car_color: str = "white",
            technician_dialogue: str = None,
            tone: str = "professional") -> str:
    from .params import Category, Tone
    from .templates import CameraMove, ShotType, LightingStyle, FilmStyle, AudioTrack, Character

    dialogue_char = None
    if technician_dialogue:
        dialogue_char = Character(
            description="a certified service technician",
            voice_style="professional, confident",
            dialogue=technician_dialogue,
        )

    params = VeoParams(
        category=Category.SERVICE,
        brand=brand,
        car_model=car_model,
        car_color=car_color,
        tone=Tone(tone),
        shot_type=ShotType.MEDIUM,
        camera_move=CameraMove.TRACKING,
        lighting=LightingStyle.SHOWROOM_LED,
        film_style=FilmStyle.DOCUMENTARY,
        audio_track=AudioTrack.PROFESSIONAL_SOFT,
        ambient_sfx="pneumatic tools, metal-on-metal precision sounds",
        dialogue_char=dialogue_char,
    )
    return generate(params)
