import re
from .types import ValidationResult, ScenePlan, Script, OfferClaim, ScriptLanguage


CAMERA_MOVES = [
    "push-in", "push in", "dolly in", "dolly out", "panning", "tracks",
    "tracking", "crane", "aerial", "orbit", "gliding", "glide",
    "follow-shot", "zoom", "arc shot", "sweeping", "slider",
]

ACTION_VERBS = [
    "speaks", "turns to", "hands over", "receives the keys",
    "slides off", "reveals", "inspects", "wipes",
    "jumps with excitement", "points to",
]


def count_camera_moves(text: str) -> int:
    text_l = text.lower()
    return sum(1 for m in CAMERA_MOVES if re.search(rf"\b{m}\b", text_l))


def count_primary_actions(text: str) -> int:
    text_l = text.lower()
    return sum(1 for v in ACTION_VERBS if re.search(rf"\b{v}\b", text_l))


def count_subjects(text: str) -> int:
    text_l = text.lower()
    subject_hints = ["salesperson", "sales executive", "customer", "family", "technician", "voiceover", "presenter"]
    return sum(1 for s in subject_hints if s in text_l)


def verb_density(text: str) -> float:
    words = text.split()
    if not words:
        return 0
    verbs = count_primary_actions(text)
    return round(verbs / len(words), 3)


def dialogue_word_count(text: str) -> int:
    return len(text.split())


def estimate_speech_duration(
    text: str,
    lang: ScriptLanguage = ScriptLanguage.HINDI,
) -> float:
    words = len(re.findall(r"[\w']+", text))
    wps_rates = {
        ScriptLanguage.HINDI: 3.2,
        ScriptLanguage.HINGLISH: 3.0,
        ScriptLanguage.ENGLISH: 2.8,
        ScriptLanguage.MARATHI: 3.0,
        ScriptLanguage.GUJARATI: 3.0,
        ScriptLanguage.TAMIL: 2.8,
        ScriptLanguage.TELUGU: 2.8,
    }
    rate = wps_rates.get(lang, 3.0)
    return round(words / rate, 1)


def has_reference_attribute_integrity(description: str, variable: str, original_value: str) -> bool:
    """Check that reference description retains key attribute."""
    return original_value.lower() in description.lower()


def check_frame_safety(prompt: str, safe_zones: dict) -> list:
    """Check that prompt doesn't ask for text in unsafe frame areas."""
    warnings = []
    lines = prompt.split("\n")
    for line in lines:
        lower = line.lower()
        if any(neg in lower for neg in ["do not", "don't", "avoid", "no readable", "composite", "post-generation"]):
            continue
        if "readable text" in lower or re.search(r"\blogo\b", lower):
            warnings.append("Prompt references readable text/logo — models render garbled shapes")
        if "screen" in lower and "out of focus" not in lower:
            warnings.append("Screen/UI requested without defocus instruction")
    return warnings


def check_offer_claims(offer: OfferClaim, script_text: str = "") -> list:
    """Validate offer claims against script text for risk."""
    issues = []
    script_l = script_text.lower()
    if not offer.verified:
        if re.search(r"\d+(?:\.\d+)?%|\u20b9|\$\d+|\d+\s*(?:lakh|thousand|k)", script_l):
            issues.append("Unverified offer but script contains specific numbers — hallucination risk")
    else:
        if offer.numeric_value and offer.numeric_value > 200000:
            issues.append("High-value claim (>2L) — verify source before broadcast")
        if not offer.validity and "limited" in script_l:
            issues.append("Urgency language but no validity date — misleading")
    return issues


def check_text_generation_risk(prompt: str) -> list:
    """Check for text generation risks in Veo output."""
    risks = []
    lines = prompt.split("\n")
    for line in lines:
        lower = line.lower()
        if any(neg in lower for neg in ["do not", "don't", "avoid", "no readable", "composite", "post-generation"]):
            continue
        if re.search(r"\btext:|caption:", lower):
            risks.append("Text/caption generation requested — Veo renders garbled pseudo-text")
        if re.search(r"\blogo\b", lower):
            risks.append("Logo generation requested — composite brand assets post-generation")
        for w in ["readable", "title card", "banner text", "brand name written"]:
            if w in lower:
                risks.append(f"Text-rendering risk: '{w}' — avoid readable text in Veo prompts")
    return list(dict.fromkeys(risks))


def validate_prompt(
    prompt: str,
    script: Script = None,
    offer: OfferClaim = None,
    lang: ScriptLanguage = ScriptLanguage.HINDI,
    target_duration: int = 8,
) -> ValidationResult:
    result = ValidationResult()

    camera_count = count_camera_moves(prompt)
    if camera_count > 1:
        result.fail(f"Camera moves detected: {camera_count} (max 1)")

    action_count = count_primary_actions(prompt)
    if action_count > 1:
        result.fail(f"Major actions detected: {action_count} (max 1)")

    word_count = len(prompt.split())
    if word_count < 40:
        result.warn(f"Prompt too short ({word_count} words) — add detail for control")
    if word_count > 160:
        result.warn(f"Prompt long ({word_count} words) — model may drop instructions")

    if script:
        dialogue = script.compress(target_duration)
        d_count = dialogue_word_count(dialogue)
        if d_count > int(target_duration * 3.2):
            result.warn(
                f"Dialogue {d_count} words — estimated speech ~{d_count / 3.2:.1f}s "
                f"exceeds {target_duration}s target"
            )
        if dialogue and target_duration <= 0:
            result.fail("Dialogue present but duration invalid")

    has_audio = any(k in prompt.lower() for k in ["ambient", "sfx", "music", "dialogue"])
    if not has_audio:
        result.warn("No audio cues — Veo generates synced audio, always specify it")

    text_risks = check_text_generation_risk(prompt)
    for r in text_risks[:2]:
        result.warn(r)

    if "9:16" not in prompt:
        result.warn("Aspect ratio not specified — may generate 16:9 by default")

    if result.errors:
        result.passed = False

    return result