from .types import (
    Script, ScriptLine, ScriptLanguage, VoiceStyle, DeliveryPacing,
    CampaignObjective, AdConcept,
)


HINDI_SCRIPTS = {
    CampaignObjective.ENQUIRY: {
        AdConcept.PRESENTER_LED: {
            "hook": "Aapke liye ek khaas offer laaye hain.",
            "offer": "Ismein special finance options available hain.",
            "product": "Ye hamari best-selling SUV hai.",
            "benefit": "Comfort aur safety dono milegi.",
            "cta": "Aaj hi showroom visit kijiye.",
        },
    },
    CampaignObjective.OFFER_AWARENESS: {
        AdConcept.PRESENTER_LED: {
            "hook": "Dekhiye kya khaas offer chal raha hai.",
            "offer": "Is model mein exchange bonus mil raha hai.",
            "product": "Ye hai hamari latest SUV.",
            "benefit": "Best features, best price.",
            "cta": "Sirf limited time ke liye. Visit kijiye.",
        },
    },
    CampaignObjective.BOOKING: {
        AdConcept.PRESENTER_LED: {
            "hook": "Soch rahe hain nayi gaadi lena?",
            "offer": "Ab booking pe special discount mil raha hai.",
            "product": "Ye SUV har need ke liye perfect hai.",
            "benefit": "Space, style aur performance.",
            "cta": "Abhi book kijiye, offer miss mat kijiye.",
        },
    },
    CampaignObjective.DELIVERY: {
        AdConcept.DELIVERY_MOMENT: {
            "hook": "",
            "offer": "",
            "product": "",
            "benefit": "",
            "cta": "",
        },
    },
    CampaignObjective.FESTIVE_PROMO: {
        AdConcept.FESTIVE_CELEBRATION: {
            "hook": "Festive season mein khaas offers hain.",
            "offer": "Is tyohaar pe special finance options.",
            "product": "Ye hamari sabse popular SUV.",
            "benefit": "Festive ka pura fayda uthaiye.",
            "cta": "Aaj hi aaiye, offer enjoy kijiye.",
        },
    },
    CampaignObjective.NEW_LAUNCH: {
        AdConcept.REVEAL: {
            "hook": "Pesh hai hamari ekdum nayi SUV.",
            "offer": "Launch offer abhi shuru.",
            "product": "Naya design, naye features.",
            "benefit": "Future ready, today.",
            "cta": "Exclusive preview ke liye visit kijiye.",
        },
    },
    CampaignObjective.SERVICE_BOOKING: {
        AdConcept.SERVICE_TRUST: {
            "hook": "Aapki car ko milti hai best care.",
            "offer": "Free multi-point check-up available hai.",
            "product": "Authorized service center mein trained technicians.",
            "benefit": "Genuine parts, complete care.",
            "cta": "Service book kijiye, call kijiye.",
        },
    },
}

HINDI_TECHNICAL_TERMS = {
    "SUV": "SUV",
    "engine": "engine",
    "features": "features",
    "finance": "finance",
    "EMI": "EMI",
    "exchange": "exchange",
    "insurance": "insurance",
    "service": "service",
    "booking": "booking",
    "test drive": "test drive",
    "showroom": "showroom",
    "accessories": "accessories",
    "turbo": "turbo",
    "automatic": "automatic",
    "manual": "manual",
    "sunroof": "sunroof",
    "cruise control": "cruise control",
}


def generate_script(
    objective: CampaignObjective,
    ad_concept: AdConcept,
    language: ScriptLanguage = ScriptLanguage.HINDI,
    voice_style: VoiceStyle = VoiceStyle.CONFIDENT,
    pacing: DeliveryPacing = DeliveryPacing.MEDIUM_FAST,
    custom_hook: str = None,
    custom_offer: str = None,
    custom_benefit: str = None,
    custom_cta: str = None,
) -> Script:
    """Layer 2: Generates a structured script with timing estimates."""
    templates = HINDI_SCRIPTS.get(objective, {}).get(ad_concept, {})
    if not templates:
        templates = HINDI_SCRIPTS[CampaignObjective.ENQUIRY][AdConcept.PRESENTER_LED]

    lines = {
        "hook": custom_hook or templates.get("hook", ""),
        "offer": custom_offer or templates.get("offer", ""),
        "product": templates.get("product", ""),
        "benefit": custom_benefit or templates.get("benefit", ""),
        "cta": custom_cta or templates.get("cta", ""),
    }

    script_lines = {}
    for segment, text in lines.items():
        sl = ScriptLine(segment=segment, text=text)
        sl.duration_seconds = sl.estimate_speech_duration()
        script_lines[segment] = sl

    return Script(
        hook=script_lines["hook"],
        offer=script_lines["offer"],
        product=script_lines["product"],
        benefit=script_lines["benefit"],
        cta=script_lines["cta"],
        language=language,
        voice_style=voice_style,
        pacing=pacing,
    )


def script_to_colon_format(script: Script, target_seconds: int = 8) -> str:
    """Convert script to Veo colon-format dialogue for native audio."""
    compressed = script.compress(target_seconds)
    if not compressed.strip():
        return ""
    parts = compressed.split(". ")
    colon_parts = []
    for part in parts:
        part = part.strip().rstrip(".")
        if part:
            colon_parts.append(part)
    return ". ".join(colon_parts)


def estimate_speech_duration_seconds(text: str, lang: ScriptLanguage = ScriptLanguage.HINDI) -> float:
    words = text.split()
    wps = {
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
    rate = wps.get(lang, 3.0)
    return round(len(words) / rate, 1)
