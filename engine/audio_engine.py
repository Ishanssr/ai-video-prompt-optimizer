from .types import AudioPlan, Script, ScriptLanguage


def compile_audio_directive(audio_plan: AudioPlan, script: Script = None) -> str:
    """Layer: Produces a complete audio directive for Veo prompt."""
    parts = []

    if audio_plan.dialogue_colon:
        parts.append(f"Dialogue: {audio_plan.dialogue_colon}")

    if audio_plan.music_style:
        music_desc = audio_plan.music_style
        if audio_plan.voice_priority == "dominant":
            music_desc += " (soft, behind dialogue)"
        parts.append(f"Music: {music_desc}")

    if audio_plan.ambient_sounds:
        parts.append(f"Ambient: {', '.join(audio_plan.ambient_sounds)}")

    if audio_plan.key_sfx:
        sfx = audio_plan.key_sfx
        if audio_plan.key_sfx_timing:
            sfx += f" at {audio_plan.key_sfx_timing}"
        parts.append(f"SFX: {sfx}")

    if audio_plan.cta_emphasis == "final_sentence" and script and script.cta.text:
        parts.append(f"CTA emphasis: final spoken line, clear and prominent")

    return ". ".join(parts) if parts else "Ambient: subtle background"


def audio_to_veo_format(audio_plan: AudioPlan, script: Script = None) -> str:
    """Convert audio plan to Veo-native colon format."""
    segments = []

    if audio_plan.dialogue_colon:
        segments.append(audio_plan.dialogue_colon)

    if audio_plan.ambient_sounds:
        segments.append(f"Ambient: {', '.join(audio_plan.ambient_sounds)}")

    if audio_plan.key_sfx:
        segments.append(f"SFX: {audio_plan.key_sfx}")

    if audio_plan.music_style:
        segments.append(f"Background music: {audio_plan.music_style}")

    return ". ".join(segments) if segments else "Ambient: subtle background"


def validate_audio_plan(audio_plan: AudioPlan) -> list:
    """Check audio plan for Veo best practices."""
    warnings = []
    if audio_plan.voice_priority == "none" and not audio_plan.music_style:
        warnings.append("No voice and no music — clip may feel empty")
    if audio_plan.music_style and audio_plan.voice_priority == "none":
        warnings.append("Music primary with no dialogue — ensure music carries the ad")
    if audio_plan.dialogue_colon:
        words = audio_plan.dialogue_colon.split()
        if len(words) > 25:
            warnings.append(f"Dialogue is {len(words)} words — may exceed 8s speech window")
    return warnings


def estimate_dialogue_fit(dialogue: str, target_seconds: int = 8, lang: ScriptLanguage = ScriptLanguage.HINDI) -> dict:
    """Estimate if dialogue fits within target duration."""
    words = dialogue.split()
    word_count = len(words)
    wps_rates = {
        ScriptLanguage.HINDI: 3.2,
        ScriptLanguage.HINGLISH: 3.0,
        ScriptLanguage.ENGLISH: 2.8,
    }
    rate = wps_rates.get(lang, 3.0)
    estimated = round(word_count / rate, 1)
    max_words = int(target_seconds * rate)
    fits = estimated <= target_seconds

    return {
        "word_count": word_count,
        "estimated_seconds": estimated,
        "max_words_at_rate": max_words,
        "fits": fits,
        "words_over": max(0, word_count - max_words),
        "rate": rate,
    }
