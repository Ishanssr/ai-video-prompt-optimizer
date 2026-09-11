import re
from copy import deepcopy
from .types import (
    ScenePlan, Script, RepairOp, RepairResult, ScriptLanguage, SpeechModel,
    OfferClaim,
)
from .script_engine import rewrite_script_to_fit
from .validator import (
    count_camera_moves, count_primary_actions, estimate_speech_duration,
    dialogue_word_count, _iter_camera_moves, action_intents,
    check_commercial_claims,
)


_CANONICAL_MOVE = {
    "push-in": "slow push-in",
    "dolly in": "slow dolly-in",
    "dolly out": "slow dolly-out",
    "pan": "slow pan",
    "crane": "slow crane",
    "aerial": "slow aerial",
    "orbit": "slow orbit",
    "glide": "slow macro glide",
    "zoom": "slow zoom",
    "arc shot": "slow arc shot",
    "sweeping": "slow sweeping",
    "slider": "slow slider",
    "pull-back": "slow pull-back",
    "float-in": "slow float-in",
    "tracking": "tracking shot",
    "track": "tracking shot",
}


def _canonical_move(move: str) -> str:
    if not move:
        return "static"
    intents = list(_iter_camera_moves(move))
    if not intents:
        return move if count_camera_moves("static") == 0 else "static"
    if len(intents) == 1:
        return move
    return _CANONICAL_MOVE.get(intents[0], f"slow {intents[0]}")


_CLAIM_REPLACEMENTS = [
    (r"\bbest[- ]?selling\b", "versatile"),
    (r"\bbest[- ]?seller\b", "popular"),
    (r"\bbest[- ]?in[- ]?class\b", "well-equipped"),
    (r"\bworld'?s?\s+best\b", "exceptionally good"),
    (r"\bsafest\b", "high-safety"),
    (r"\bmost\s+popular\b", "popular"),
    (r"\bpractically\s+perfect\b", "nearly ideal"),
    (r"\bperfect\b", "suitable"),
    (r"\bsabse\s+safe\b", "safe"),
    (r"\bsabse\s+popular\b", "popular"),
    (r"\bsabse\s+behtreen\b", "acchi"),
    (r"\bek\s+number\b", ""),
    (r"\b#\s?1\b", ""),
    (r"\bnumber\s?one\b", ""),
    (r"\bno\s?\.?\s?1\b", ""),
]

_UNAPPROVED_MOVE_HINT = "single camera movement"


def _safe_line_text(text: str) -> str:
    t = text
    for pattern, replacement in _CLAIM_REPLACEMENTS:
        t = re.sub(pattern, replacement, t, flags=re.I)
    t = re.sub(r"\s{2,}", " ", t).strip()
    return t


# ─── Diagnosis (plan-level, automatically recompilable) ─────────────

def diagnose_scene(scene: ScenePlan) -> list:
    """Find scene-level faults that must be repaired in the ScenePlan itself."""
    ops = []
    if not scene:
        return ops

    if scene.camera_move and count_camera_moves(scene.camera_move) != 1:
        new_move = _canonical_move(scene.camera_move)
        ops.append(RepairOp(
            target="scene", field="camera_move",
            old_value=scene.camera_move, new_value=new_move,
            reason="camera_move must resolve to exactly one intent",
        ))

    if scene.primary_action:
        intents = action_intents(scene.primary_action)
        if len(intents) > 1:
            new_action = _single_intent_action(scene.primary_action)
            ops.append(RepairOp(
                target="scene", field="primary_action",
                old_value=scene.primary_action, new_value=new_action,
                reason=f"conflates action intents {intents} — keep a single primary action",
            ))

    if scene.subject and scene.secondary_subject and scene.subject == scene.secondary_subject:
        ops.append(RepairOp(
            target="scene", field="subject",
            old_value=scene.subject, new_value="", reason="subject duplicates vehicle identity",
        ))

    if scene.supporting_beats and len(scene.supporting_beats) > 3:
        ops.append(RepairOp(
            target="scene", field="supporting_beats",
            old_value=str(len(scene.supporting_beats)), new_value="3",
            reason="keep 3 or fewer supporting beats within one primary action",
        ))
    return ops


def _single_intent_action(action: str) -> str:
    intents = action_intents(action)
    if not intents:
        return action
    primary = intents[0]
    verbs = {
        "presenter_address": "presenter speaks directly to camera",
        "gesture": "presenter gestures toward the car",
        "delivery": "family receives the car keys",
        "reveal": "satin cover slides off the car",
        "inspection": "technician inspects the car",
        "motion": "presenter walks beside the car",
        "celebration": "family celebrates together",
        "care": "technician cares for the car",
    }
    return verbs.get(primary, action)


def diagnose_script(script: Script, duration: int, offer: OfferClaim = None) -> list:
    """Find script-level faults: over-budget dialogue + unsupported claims."""
    ops = []
    if not script:
        return ops
    lang = script.language

    if script.total_words:
        raw = script.dialogue_text(duration, rewritten=False)
        report = SpeechModel.fit_report(raw, duration, lang)
        if report["words"] and not report["fits_at_all"]:
            ops.append(RepairOp(
                target="script", field="dialogue",
                old_value=f"{report['words']} words / ~{report['estimated_seconds']}s",
                new_value=f"rewritten to fit {duration}s",
                reason="dialogue exceeds ad duration — rewrite, never truncate",
            ))

    for line in script.all_lines:
        if not line.text:
            continue
        issues = [i for i in check_commercial_claims(line.text, offer, None, lang) if i.is_error]
        if not issues:
            continue
        safe = _safe_line_text(line.text)
        if safe != line.text:
            ops.append(RepairOp(
                target="script", field=f"line:{line.segment}",
                old_value=line.text, new_value=safe,
                reason=f"unverified claim blocked ({issues[0].category.value})",
            ))
    return ops


# ─── Repair application (structural, then recompile) ────────────────

def apply_repairs(
    scene: ScenePlan,
    script: Script,
    ops: list,
    duration: int = 8,
) -> tuple:
    """Apply plan-level repairs. Returns (scene, script) with faults fixed.
    The compiled prompt is NEVER patched — it must be recompiled from here."""
    scene2 = deepcopy(scene) if scene else None
    script2 = deepcopy(script) if script else None

    for op in ops:
        if op.target == "scene" and scene2:
            if op.field == "camera_move":
                scene2.camera_move = op.new_value
            elif op.field == "primary_action":
                scene2.primary_action = op.new_value
            elif op.field == "subject":
                scene2.subject = op.new_value
            elif op.field == "secondary_subject":
                scene2.secondary_subject = op.new_value
            elif op.field == "supporting_beats":
                scene2.supporting_beats = scene2.supporting_beats[:3]
        elif op.target == "script" and script2:
            if op.field == "dialogue":
                script2 = rewrite_script_to_fit(script2, target_seconds=duration)
            elif op.field.startswith("line:"):
                seg = op.field.split(":", 1)[1]
                setattr(script2, seg, deepcopy(getattr(script2, seg)))
                getattr(script2, seg).text = op.new_value

    return scene2, script2


def repair_plan(
    scene: ScenePlan,
    script: Script = None,
    offer: OfferClaim = None,
    duration: int = 8,
    lang: ScriptLanguage = None,
    recompile=None,
) -> RepairResult:
    """End-to-end structural repair: diagnose plan → apply → recompile.

    `recompile` is a callable(scene, script) -> str used by the compiler to
    produce the final prompt from the repaired plan (never regex surgery).
    """
    lang = lang or (script.language if script else ScriptLanguage.HINDI)
    ops = diagnose_scene(scene) + diagnose_script(script, duration, offer)

    if not ops:
        prompt = recompile(scene, script) if recompile else ""
        return RepairResult(prompt=prompt, scene=scene, script=script, score=100.0)

    scene2, script2 = apply_repairs(scene, script, ops, duration)
    prompt = recompile(scene2, script2) if recompile else ""

    # residual faults that survive repair lower the score
    residue = diagnose_scene(scene2) + diagnose_script(script2, duration, offer)
    residual_score = max(0.0, 100.0 - len(residue) * 20 - len(scene2.supporting_beats) * 5)

    return RepairResult(prompt=prompt, scene=scene2, script=script2, ops=ops, score=round(residual_score, 1))


# ─── Back-compat string repairs (legacy; not used by the new pipeline) ─

def repair_camera_moves(prompt: str) -> str:
    """DEPRECATED: the pipeline now repairs the ScenePlan and recompiles."""
    intents = list(_iter_camera_moves(prompt))
    if len(intents) <= 1:
        return prompt
    return prompt + f" Single camera movement: {_CANONICAL_MOVE.get(intents[0], intents[0])}."


def repair_actions(prompt: str) -> str:
    """DEPRECATED: action repair now happens at the ScenePlan layer."""
    intents = action_intents(prompt)
    if len(intents) <= 1:
        return prompt
    return prompt + f" One primary action: {intents[0]}."


def repair_dialogue_length(
    dialogue: str,
    target_seconds: int = 8,
    lang_rate: float = 3.0,
) -> str:
    """DEPRECATED: use Script.rewrite_to_fit() for sentence-safe rewrites."""
    max_words = int(target_seconds * lang_rate)
    words = dialogue.split()
    if len(words) <= max_words:
        return dialogue
    return " ".join(words[:max_words])


def repair_prompt(prompt: str, diagnostics: dict) -> str:
    """DEPRECATED: legacy prose-patcher. Prefer repair_plan()."""
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
    """DEPRECATED: legacy entry point. Returns change log for compatibility."""
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
        dur = estimate_speech_duration(script_text)
        if dur > target_seconds:
            new_dialogue = repair_dialogue_length(script_text, target_seconds, lang_rate)
            prompt = prompt.replace(script_text, new_dialogue)
            changes.append(
                f"dialogue trimmed ({dialogue_word_count(script_text)} → "
                f"{len(new_dialogue.split())} words)"
            )

    return {
        "repaired_prompt": prompt,
        "changes": changes,
        "was_repaired": len(changes) > 0,
    }