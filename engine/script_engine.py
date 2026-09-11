from .types import (
    Script, ScriptLine, ScriptLanguage, VoiceStyle, DeliveryPacing,
    CampaignObjective, AdConcept, SpeechModel,
)


# Every template line carries a full form and a complete condensed rewrite.
# Condensed lines are WHOLE sentences (rewrites), so fitting a duration never
# means cutting dialogue mid-sentence.
HINDI_SCRIPTS = {
    CampaignObjective.ENQUIRY: {
        AdConcept.PRESENTER_LED: {
            "hook": {
                "full": "Aapke liye ek khaas offer laaye hain.",
                "condensed": "Khaas offer aaya hai.",
            },
            "offer": {
                "full": "Ismein special finance options available hain.",
                "condensed": "Special finance options hain.",
            },
            "product": {
                "full": "Ye hai hamari versatile family SUV.",
                "condensed": "Ye SUV versatile hai.",
            },
            "benefit": {
                "full": "Comfort aur safety dono milegi.",
                "condensed": "Comfort aur safety dono.",
            },
            "cta": {
                "full": "Aaj hi showroom visit kijiye.",
                "condensed": "Aaj hi visit kijiye.",
            },
        },
    },
    CampaignObjective.OFFER_AWARENESS: {
        AdConcept.PRESENTER_LED: {
            "hook": {
                "full": "Dekhiye kya khaas offer chal raha hai.",
                "condensed": "Kya khaas offer hai?",
            },
            "offer": {
                "full": "Is model mein exchange bonus mil raha hai.",
                "condensed": "Exchange bonus mil raha hai.",
            },
            "product": {
                "full": "Ye hai hamari latest SUV.",
                "condensed": "Ye hai latest SUV.",
            },
            "benefit": {
                "full": "Quality features, smart price.",
                "condensed": "Quality features millte hain.",
            },
            "cta": {
                "full": "Sirf limited time ke liye. Visit kijiye.",
                "condensed": "Limited time. Visit kijiye.",
            },
        },
    },
    CampaignObjective.BOOKING: {
        AdConcept.PRESENTER_LED: {
            "hook": {
                "full": "Soch rahe hain nayi gaadi lena?",
                "condensed": "Nayi gaadi lena?",
            },
            "offer": {
                "full": "Ab booking pe special discount mil raha hai.",
                "condensed": "Booking pe discount hai.",
            },
            "product": {
                "full": "Ye SUV har travel need ke liye suitable hai.",
                "condensed": "Ye SUV reliable hai.",
            },
            "benefit": {
                "full": "Space, style aur performance.",
                "condensed": "Space aur performance.",
            },
            "cta": {
                "full": "Abhi book kijiye, offer miss mat kijiye.",
                "condensed": "Abhi book kijiye.",
            },
        },
    },
    CampaignObjective.DELIVERY: {
        AdConcept.DELIVERY_MOMENT: {
            "hook": {
                "full": "Is pal mein kuchh khaas hai.",
                "condensed": "Kuchh khaas ho raha hai.",
            },
            "offer": {
                "full": "",
                "condensed": "",
            },
            "product": {
                "full": "Nayi car, nayi shuruaat.",
                "condensed": "Nayi car, nayi shuruaat.",
            },
            "benefit": {
                "full": "Ghar ki khushi, bas ab mil gayi.",
                "condensed": "Har member ki khushi.",
            },
            "cta": {
                "full": "Is din ko yaad rakhne ke liye visit kijiye.",
                "condensed": "Yaad rakhne layak din.",
            },
        },
    },
    CampaignObjective.FESTIVE_PROMO: {
        AdConcept.FESTIVE_CELEBRATION: {
            "hook": {
                "full": "Festive season mein khaas offers hain.",
                "condensed": "Festive offers hain.",
            },
            "offer": {
                "full": "Is tyohaar pe special finance options.",
                "condensed": "Special finance options.",
            },
            "product": {
                "full": "Ye SUV festive season ke liye suitable hai.",
                "condensed": "Ye SUV suitable hai.",
            },
            "benefit": {
                "full": "Festive ka pura fayda uthaiye.",
                "condensed": "Festive ka fayda uthaiye.",
            },
            "cta": {
                "full": "Aaj hi aaiye, offer enjoy kijiye.",
                "condensed": "Aaj hi aaiye.",
            },
        },
    },
    CampaignObjective.NEW_LAUNCH: {
        AdConcept.REVEAL: {
            "hook": {
                "full": "Pesh hai hamari ekdum nayi SUV.",
                "condensed": "Pesh hai nayi SUV.",
            },
            "offer": {
                "full": "Launch offers abhi shuru.",
                "condensed": "Launch offers shuru.",
            },
            "product": {
                "full": "Naya design, naye features.",
                "condensed": "Naya design.",
            },
            "benefit": {
                "full": "Future ready, today.",
                "condensed": "Future ready.",
            },
            "cta": {
                "full": "Exclusive preview ke liye visit kijiye.",
                "condensed": "Preview ke liye visit kijiye.",
            },
        },
    },
    CampaignObjective.SERVICE_BOOKING: {
        AdConcept.SERVICE_TRUST: {
            "hook": {
                "full": "Aapki car deserve karti hai poori care.",
                "condensed": "Aapki car deserves care.",
            },
            "offer": {
                "full": "Free multi-point check-up available hai.",
                "condensed": "Free check-up available hai.",
            },
            "product": {
                "full": "Authorized service center mein trained technicians.",
                "condensed": "Trained technicians hain.",
            },
            "benefit": {
                "full": "Genuine parts, complete care.",
                "condensed": "Genuine parts milenge.",
            },
            "cta": {
                "full": "Service book kijiye, call kijiye.",
                "condensed": "Abhi book kijiye.",
            },
        },
    },
    CampaignObjective.TEST_DRIVE: {
        AdConcept.PRESENTER_LED: {
            "hook": {
                "full": "Test drive lijiye, khud feel kijiye.",
                "condensed": "Test drive lijiye.",
            },
            "offer": {
                "full": "Test drive pe special offer milega.",
                "condensed": "Test drive offer hai.",
            },
            "product": {
                "full": "Ye SUV drive mein confidently perform karti hai.",
                "condensed": "Ye SUV confident hai.",
            },
            "benefit": {
                "full": "Comfort, handling aur safety.",
                "condensed": "Comfort aur handling.",
            },
            "cta": {
                "full": "Aaj hi test drive book kijiye.",
                "condensed": "Aaj hi book kijiye.",
            },
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

FALLBACK_OBJECTIVE = CampaignObjective.ENQUIRY
FALLBACK_CONCEPT = AdConcept.PRESENTER_LED


def _templates_for(objective: CampaignObjective, ad_concept: AdConcept) -> dict:
    templates = HINDI_SCRIPTS.get(objective, {}).get(ad_concept)
    if templates is None:
        templates = HINDI_SCRIPTS.get(FALLBACK_OBJECTIVE, {}).get(FALLBACK_CONCEPT, {})
    return templates


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
    """Layer 2: Generates a structured script with full + condensed rewrites.

    Every line has a whole-sentence rewrite, so fitting the ad duration never
    truncates dialogue mid-sentence.
    """
    templates = _templates_for(objective, ad_concept)

    def _line(segment: str, custom: str = None) -> ScriptLine:
        t = templates.get(segment, {"full": "", "condensed": ""})
        full = custom if custom is not None else t.get("full", "")
        condensed = t.get("condensed", "")
        line = ScriptLine(segment=segment, text=full, condensed=condensed)
        line.duration_seconds = line.estimate_speech_duration(language)
        return line

    script = Script(
        hook=_line("hook", custom_hook),
        offer=_line("offer", custom_offer),
        product=_line("product"),
        benefit=_line("benefit", custom_benefit),
        cta=_line("cta", custom_cta),
        language=language,
        voice_style=voice_style,
        pacing=pacing,
        objective=objective,
        ad_concept=ad_concept,
    )
    return script


def rewrite_script_to_fit(
    script: Script,
    target_seconds: int = 8,
    margin: float = None,
) -> Script:
    """Rewrite a script to fit the safe speech budget for an ad duration.

    Whole sentences only:
      * The CTA is always preserved (highest allocation priority).
      * Remaining segments are allocated in objective-aware priority order.
      * If a full line cannot fit, its complete condensed rewrite is used.
      * Nothing is ever cut mid-sentence.

    Returns a NEW Script; segments that could not fit are emptied.
    """
    from dataclasses import replace

    lang = script.language
    fraction = margin if margin is not None else SpeechModel.SAFE_FRACTION
    buffer = SpeechModel.budget(target_seconds, lang)
    max_words = int(buffer.safe_seconds * buffer.rate_wps)

    priority = list(dict.fromkeys(["cta"] + script.priority()))
    remaining = max_words

    chosen = {seg: "" for seg in ["hook", "offer", "product", "benefit", "cta"]}
    budget_by_segment = {seg: 0 for seg in chosen}

    # First pass: allocate guaranteed segments (cta) then priority order.
    for seg in priority:
        if seg not in chosen:
            continue
        line: ScriptLine = getattr(script, seg)
        if not line.text:
            chosen[seg] = ""
            continue
        picked = line.pick(remaining, lang)
        if picked:
            chosen[seg] = picked
            budget_by_segment[seg] = len(picked.split())
            remaining -= len(picked.split())

    rewritten = replace(script)
    for seg, text in chosen.items():
        line = getattr(rewritten, seg)
        line.text = text
        line.duration_seconds = SpeechModel.estimate(text, lang) if text else 0.0
    return rewritten


def script_to_colon_format(script: Script, target_seconds: int = 8) -> str:
    """Convert script to Veo colon-format dialogue for native audio.

    Uses the rewritten (fitted) dialogue, never a raw truncation.
    """
    dialogue = script.dialogue_text(target_seconds, rewritten=True)
    if not dialogue.strip():
        return ""
    return _sentences_to_colon(dialogue)


def _sentences_to_colon(dialogue: str) -> str:
    parts = [p.strip().rstrip(".") for p in dialogue.split(". ") if p.strip()]
    return ". ".join(parts)


def estimate_speech_duration_seconds(
    text: str,
    lang: ScriptLanguage = ScriptLanguage.HINDI,
) -> float:
    """Canonical speech duration estimate (single SpeechModel)."""
    return SpeechModel.estimate(text, lang)


def speech_rates() -> dict:
    """Expose the single canonical words-per-second table."""
    return {k.value: v for k, v in SpeechModel.RATES_WPS.items()}