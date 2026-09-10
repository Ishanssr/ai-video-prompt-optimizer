import re
from .validator import (
    count_camera_moves, count_primary_actions, estimate_speech_duration,
    dialogue_word_count, CAMERA_MOVES, ACTION_VERBS,
)


def repair_camera_moves(prompt: str) -> str:
    """If more than one camera move, keep the first, restate others as intent."""
    moves = [m for m in CAMERA_MOVES if re.search(rf"\b{m}\b", prompt.lower())]
    if len(set(moves)) <= 1:
        return prompt

    first = moves[0]
    kept = f"Slow, deliberate {first} only"
    for extra in moves[1:]:
        prompt = re.sub(rf",?\s*(?:\bslow\b\s*)?{re.escape(extra)}\s*(?:drift|shot)?\b", "", prompt, flags=re.I)

    repair_note = f" Single camera movement: {kept}."
    if "Single camera movement" not in prompt:
        prompt = prompt + repair_note
    return prompt


def repair_actions(prompt: str) -> str:
    """Reduce to a single primary action if multiple detected."""
    verbs = [v for v in ACTION_VERBS if re.search(rf"\b{v}\b", prompt.lower())]
    if len(set(verbs)) <= 1:
        return prompt

    primary = verbs[0]
    return prompt + f" One primary action: {primary}."


def repair_dialogue_length(
    dialogue: str,
    target_seconds: int = 8,
    lang_rate: float = 3.0,
) -> str:
    """Trim dialogue to fit target duration."""
    max_words = int(target_seconds * lang_rate)
    words = dialogue.split()
    if len(words) <= max_words:
        return dialogue
    return " ".join(words[:max_words])


def repair_prompt(prompt: str, diagnostics: dict) -> str:
    """Apply all applicable repairs."""
    if diagnostics.get("camera_move_count", 0) > 1:
        prompt = repair_camera_moves(prompt)

    if diagnostics.get("action_count", 0) > 1:
        prompt = repair_actions(prompt)

    if diagnostics.get("dialogue_too_long", False):
        dialogue = diagnostics.get("dialogue", "")
        concept = diagnostics.get("target_seconds", 8)
        prompt = prompt.replace(dialogue, repair_dialogue_length(dialogue, concept))

    return prompt


def auto_repair(
    prompt: str,
    script_text: str = "",
    target_seconds: int = 8,
    lang_rate: float = 3.0,
) -> dict:
    """End-to-end repair pass. Returns repaired prompt + change log."""
    changes = []

    camera_count = count_camera_moves(prompt)
    if camera_count > 1:
        prompt = repair_camera_moves(prompt)
        changes.append(f"camera moves reduced ({camera_count} → 1)")

    action_count = count_primary_actions(prompt)
    if action_count > 1:
        prompt = repair_actions(prompt)
        changes.append(f"actions reduced ({action_count} → 1)")

    if script_text:
        words = dialogue_word_count(script_text)
        dur = estimate_speech_duration(script_text)
        if dur > target_seconds:
            new_dialogue = repair_dialogue_length(script_text, target_seconds, lang_rate)
            prompt = prompt.replace(script_text, new_dialogue)
            changes.append(f"dialogue trimmed ({words} → {len(new_dialogue.split())} words)")

    return {
        "repaired_prompt": prompt,
        "changes": changes,
        "was_repaired": len(changes) > 0,
    }