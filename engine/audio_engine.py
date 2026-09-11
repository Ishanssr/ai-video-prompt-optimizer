from .types import AudioPlan, Script, ScriptLanguage, SpeechModel


def compile_audio_directive(audio_plan: AudioPlan, script: Script = None) -> str:
    """Layer: Produces a complete audio directive for Veo prompt."""
    parts = []

    if audio_plan.dialogue_colon:
        parts.append(f"Dialogue: {audio_plan.dialogue_colon.rstrip('.')}")

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
        parts.append(f"CTA emphasis: final line, prominent")

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
    """Estimate if dialogue fits the safe speech budget (canonical SpeechModel)."""
    report = SpeechModel.fit_report(dialogue, target_seconds, lang)
    return {
        "word_count": report["words"],
        "estimated_seconds": report["estimated_seconds"],
        "max_words_at_rate": report["max_words_safe"],
        "fits": report["fits_safe"],
        "words_over": max(0, report["words"] - report["max_words_safe"]),
        "rate": SpeechModel.rate(lang),
    }
