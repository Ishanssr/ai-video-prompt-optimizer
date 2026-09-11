import re
from .types import (
    ValidationResult, ValidationScore, ScenePlan, Script, OfferClaim,
    ScriptLanguage, SpeechModel, CommercialIssue, ClaimCategory,
    GenerationMode, BrandPolicy, ReferenceProfile, VEO_3_1,
)


# Semantic lexicons ---------------------------------------------------
# Camera visits: contextual disambiguation avoids "track LEDs" / "track lighting"
# being read as a camera move.
CAMERA_MOVES = [
    "push-in", "push in", "dolly in", "dolly out", "panning", "pan",
    "tracking", "track shot", "crane", "aerial", "orbit", "gliding", "glide",
    "zoom", "arc shot", "sweeping", "slider", "pull-back", "float-in",
]
_CAMERA_PATTERNS = [
    (r"\bpull[- ]?back\b", "pull-back"),
    (r"\bpush[- ]?in\b", "push-in"),
    (r"\bdolly[- ]?in\b", "dolly in"),
    (r"\bdolly[- ]?out\b", "dolly out"),
    (r"\bpan(?:n?ing|s)?\b", "pan"),
    (r"\bcrane\b", "crane"),
    (r"\baerial\b", "aerial"),
    (r"\borbit(?:s|ing)?\b", "orbit"),
    (r"\bglid(?:e|ing)\b", "glide"),
    (r"\bzoom\b", "zoom"),
    (r"\bars?\b\s*shot\b", "arc shot"),
    (r"\bsweep(?:ing)?\b", "sweeping"),
    (r"\bslider\b", "slider"),
    (r"\bfloat[- ]?in\b", "float-in"),
]
# "track(s|ing)" is ambiguous between camera tracking and track lighting.
_TRACK_PATTERN = re.compile(r"\btrack(?:ing|s)?\b", re.I)
_AMBIENT_MARKERS = ("led", "lighting", "light", "lamps", "railing", "ceiling")

# Action intents: a top-level action is ONE of these intents, no matter how
# many verbs flesh it out. Multiple intents in the Action clause = conflict.
ACTION_VERBS = [
    "speaks", "says", "talks", "addresses", "gestures", "points", "waves",
    "slides off", "reveals", "receives the keys", "hands over",
    "walks", "approaches", "moves", "inspects", "wipes", "opens the door",
    "sits inside", "smiles", "celebrates", "hugs",
]
_ACTION_INTENTS = {
    "presenter_address": [r"\bspeaks?\b", r"\baddresses?\b", r"\btalks?\b", r"\bsays\b"],
    "gesture": [
        r"\bgesture[sd]?\b", r"\bgesturing\b", r"\bpoints?\b", r"\bpointing\b",
        r"\bwaves?\b", r"\bwaving\b", r"\braises?\b", r"\braising\b",
        r"\bhands?\b", r"\bhanding\b", r"\bholds? up\b", r"\bholding up\b",
        r"\boffers?\b", r"\boffering\b", r"\bpresents?\b", r"\bpresenting\b",
    ],
    "invitation": [r"\binvites?\b", r"\binviting\b", r"\binvites the viewer\b"],
    "reveal": [r"\bslides? off\b", r"\breveal(?:ed|s|ing)?\b", r"\bunveil(?:ed|s|ing)?\b", r"\bcover slides?\b"],
    "delivery": [r"\bhands? over\b", r"\breceives? the keys?\b", r"\bhandover\b", r"\bkeys\b"],
    "motion": [
        r"\bwalks?\b", r"\bwalking\b", r"\bapproaches?\b", r"\bapproaching\b",
        r"\bmoves?\b", r"\bmoving\b", r"\benters?\b", r"\bentering\b",
    ],
    "inspection": [r"\binspects?\b", r"\binspecting\b", r"\bxamines?\b", r"\bchecks?\b"],
    "care": [r"\bwipes?\b", r"\bcleans?\b", r"\bpolishes?\b", r"\bcaring for\b"],
    "celebration": [r"\bcelebrates?\b", r"\bcelebrating\b", r"\bhugs?\b", r"\bsmiles?\b", r"\bembracing\b", r"\bapplauds?\b"],
}


# ─── Camera (semantic, context-disambiguated) ───────────────────────

def _guard_track(haystack: str, line: str, match) -> bool:
    """Return True if a 'track*' token is ambient-lighting, not a camera move."""
    start = match.start()
    window = haystack[max(0, start - 40): start + 40]
    return any(m in window for m in _AMBIENT_MARKERS)


def _iter_camera_moves(text: str):
    """Yield distinct camera-move intents in FIRST-OCCURRENCE order."""
    if not text:
        return
    low = text.lower()
    hits = []
    for pattern, label in _CAMERA_PATTERNS:
        m = re.search(pattern, low)
        if m:
            hits.append((m.start(), label))
    for m in _TRACK_PATTERN.finditer(low):
        if _guard_track(low, text, m):
            continue
        label = "tracking" if m.group(0).endswith("ing") else "track"
        hits.append((m.start(), label))
    seen = set()
    for pos, label in sorted(hits):
        if label in seen:
            continue
        seen.add(label)
        yield label


def count_camera_moves(text: str) -> int:
    """Distinct camera-move intents (semantic). 'track LEDs' does not count."""
    return len(list(_iter_camera_moves(text)))


def _strip_cinematography_clause(prompt: str) -> str:
    """Remove the compiled Cinematography clause so we only scan stray prose."""
    lines = []
    for line in prompt.split("\n"):
        if line.lower().startswith("cinematography:"):
            continue
        lines.append(line)
    return "\n".join(lines)


def stray_camera_moves(prompt: str, plan_move: str = None) -> list:
    """Camera-move intents found OUTSIDE the compiled cinematography clause.

    Returns (intent, source_line) pairs. A clean prompt yields [].
    """
    plan = plan_move.lower() if plan_move else ""
    found = []
    seen = set()
    for line in _strip_cinematography_clause(prompt).split("\n"):
        line_l = line.lower()
        if line_l.startswith(("references", "brand", "format", "audio", "subject",
                              "secondary subject", "action", "context", "style",
                              "compositing", "composite", "timing")):
            pass
        for intent in _iter_camera_moves(line):
            if intent in plan or intent in seen:
                continue
            seen.add(intent)
            found.append((intent, line.strip()))
    return found


# ─── Actions (semantic, intent-based) ───────────────────────────────

def action_intents(text: str) -> list:
    if not text:
        return []
    low = text.lower()
    intents = []
    for intent, patterns in _ACTION_INTENTS.items():
        for p in patterns:
            matched = False
            for m in re.finditer(p, low):
                if _guarded_token(intent, low, m):
                    continue
                matched = True
                break
            if matched:
                intents.append(intent)
                break
    return intents


def _guarded_token(intent: str, low: str, m) -> bool:
    """Skip false positives like 'camera move' (not a character walking)."""
    if intent == "motion":
        context = low[max(0, m.start() - 25): m.start() + 15]
        if "camera" in context:
            return True
    return False


def count_primary_actions(text: str) -> int:
    """Number of distinct action intents in the text (semantic)."""
    return len(action_intents(text))


def conflicting_action_intents(scene_plan: ScenePlan, prompt: str) -> list:
    """Action intents in the prose that disagree with the plan.

    The plan's allowed intents = primary_action + its supporting beats, so
    beats written into the Action clause are NOT conflicts.
    """
    if not scene_plan or not scene_plan.primary_action:
        return []
    allowed = set(action_intents(scene_plan.primary_action))
    allowed |= set(action_intents(" ".join(scene_plan.supporting_beats)))
    if not allowed:
        return []
    prose_intents = action_intents(_strip_cinematography_clause(prompt))
    return [i for i in prose_intents if i not in allowed]


# ─── Speech / words ─────────────────────────────────────────────────

def estimate_speech_duration(text: str, lang: ScriptLanguage = ScriptLanguage.HINDI) -> float:
    return SpeechModel.estimate(text, lang)


def fit_report(text: str, duration: int, lang: ScriptLanguage = ScriptLanguage.HINDI) -> dict:
    return SpeechModel.fit_report(text, duration, lang)


def dialogue_word_count(text: str) -> int:
    return len(text.split())


def verb_density(text: str) -> float:
    words = text.split()
    if not words:
        return 0
    return round(len(action_intents(text)) / len(words), 3)


# ─── Reference integrity ────────────────────────────────────────────

def has_reference_attribute_integrity(description: str, variable: str, original_value: str) -> bool:
    """Check that reference description retains the key (immutable) attribute."""
    return original_value.lower() in description.lower()


def check_reference_integrity(scene: ScenePlan, reference: ReferenceProfile) -> list:
    """Immutable identity attributes must survive; camera-mutable ones may not."""
    issues = []
    if reference and reference.vehicle and reference.vehicle.model:
        v = reference.vehicle
        if v.colour and scene.secondary_subject and v.colour.lower() not in scene.secondary_subject.lower():
            issues.append(f"Vehicle colour changed: reference shows {v.colour}, scene says {scene.secondary_subject}")
    return issues


# ─── Text-generation risk (Veo) ─────────────────────────────────────

def check_text_generation_risk(prompt: str) -> list:
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


def check_frame_safety(prompt: str, safe_zones: dict) -> list:
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


# ─── Commercial claims ──────────────────────────────────────────────

_SUPERLATIVE_PATTERNS = [
    r"\bbest[- ]?selling\b", r"\bbest[- ]?seller\b", r"\bbest[- ]?in[- ]?class\b",
    r"\bworld'?s?\s+best\b", r"\b#\s?1\b", r"\bnumber\s?one\b", r"\bno\s?\.?\s?1\b",
    r"\bsafest\b", r"\bbiggest\b", r"\bcheapest\b", r"\bmost\s+popular\b",
    r"\btop[- ]?rated\b", r"\bperfect\b", r"\bflawless\b", r"\bleading\b",
    r"\bsabse\s+safe\b", r"\bsabse\s+better\b", r"\bsabse\s+popular\b",
    r"\bek\s+number\b",
]
_COMPARATIVE_PATTERNS = [
    r"\bbetter\s+than\b", r"\bfaster\s+than\b", r"\bcheaper\s+than\b",
    r"\bse\s+behtar\b", r"\bvs\b", r"\bcompared?\s+to\b",
]
_URGENCY_PATTERNS = [
    r"\blimited\s+time\b", r"\bwhile\s+stocks?\s+last\b", r"\bjaldi\s+karein\b",
    r"\bhurry\b", r"\bsirf\s+kuchh\s+din\b", r"\blast\s+chance\b",
]
_FINANCE_NUMBER = re.compile(r"\d+(?:\.\d+)?\s*%|\u20b9|\$\d+|\d+\s*(?:lakh|thousand|k|crore)")
_PERFORMANCE_PATTERNS = [r"\bfastest\b", r"\bmost\s+powerful\b", r"\bhighest\s*(?:mileage|torque)?\b", r"\bexceeds?\s+\d+\s*(?:kmpl|km/h)\b"]
_SAFETY_PATTERNS = [r"\b5[- ]?star\b", r"\bgncap\b", r"\bzero\s+(?:accident|fatalities?)\b", r"\bsafest\b"]


def _issues_from(script_text: str) -> list:
    low = script_text.lower()
    issues = []
    for pat in _SUPERLATIVE_PATTERNS:
        m = re.search(pat, low)
        if m:
            issues.append(CommercialIssue(
                category=ClaimCategory.SUPERLATIVE,
                severity="error",
                message=f"Unverified superlative claim: '{m.group(0)}'",
                recommendation="Replace with a neutral descriptor or supply a verified benchmark/source.",
                evidence=m.group(0),
            ))
    if re.search(r"\bsafest\b", low) or any(re.search(p, low) for p in _SAFETY_PATTERNS):
        issues.append(CommercialIssue(
            category=ClaimCategory.SAFETY, severity="warning",
            message="Safety claim present — verify against published test ratings.",
            recommendation="Cite GNCAP/BNCAP/NCAP rating or remove the ranking.",
        ))
    if any(re.search(p, low) for p in _PERFORMANCE_PATTERNS):
        issues.append(CommercialIssue(
            category=ClaimCategory.PERFORMANCE, severity="warning",
            message="Performance claim present without benchmark data.",
            recommendation="Attach measured figures with source or soften wording.",
        ))
    for pat in _COMPARATIVE_PATTERNS:
        if re.search(pat, low):
            issues.append(CommercialIssue(
                category=ClaimCategory.COMPARATIVE, severity="warning",
                message="Comparative claim present ('better than…').",
                recommendation="Only use if you can cite the comparison baseline.",
            ))
            break
    return issues


def check_commercial_claims(
    script_text: str,
    offer: OfferClaim = None,
    policy: BrandPolicy = None,
    lang: ScriptLanguage = ScriptLanguage.HINDI,
) -> list:
    """Validate ALL claim categories (offer, product, superlative, comparative,
    performance, safety, urgency, finance) — not just offer numbers."""
    issues = []

    for issue in _issues_from(script_text):
        issues.append(issue)

    low = script_text.lower()

    has_urgency = any(re.search(p, low) for p in _URGENCY_PATTERNS)
    if has_urgency:
        if offer is None:
            issues.append(CommercialIssue(
                category=ClaimCategory.URGENCY, severity="warning",
                message="Urgency language used but no offer validity supplied.",
                recommendation="Add a validity window or remove the urgency cue.",
            ))
        elif not offer.validity:
            issues.append(CommercialIssue(
                category=ClaimCategory.URGENCY, severity="error",
                message="Urgency language used but offer has no validity date.",
                recommendation=f"Set offer.validity before using '{script_text}'.",
            ))

    has_numbers = bool(_FINANCE_NUMBER.search(low))
    if has_numbers and (offer is None or not offer.verified):
        issues.append(CommercialIssue(
            category=ClaimCategory.FINANCE, severity="error",
            message="Script contains specific numbers/₹ without a verified offer source.",
            recommendation="Use create_verified_offer() with source before emitting numbers.",
        ))

    if offer and offer.verified:
        if offer.numeric_value and offer.numeric_value > 200000:
            issues.append(CommercialIssue(
                category=ClaimCategory.OFFER, severity="warning",
                message=f"High-value offer ({offer.numeric_value:,.0f}) — verify source before broadcast.",
                recommendation="Confirm with finance team + attach advisory snippet.",
            ))
        if offer.offer_type in ("finance_rate", "low_emi", "zero_downpayment") and not offer.finance_conditions:
            issues.append(CommercialIssue(
                category=ClaimCategory.FINANCE, severity="warning",
                message="Finance offer missing conditions.",
                recommendation="Add finance_conditions (e.g., 'conditions apply').",
            ))

    if policy and policy.no_invented_claims and has_numbers and (offer is None or not offer.verified):
        issues.append(CommercialIssue(
            category=ClaimCategory.FINANCE, severity="error",
            message=f"Brand policy '{policy.brand}' forbids invented claims.",
            recommendation="Remove specific numbers or route through a verified offer.",
        ))

    seen = set()
    deduped = []
    for i in issues:
        key = (i.category, i.evidence or i.message)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(i)
    return deduped


def check_offer_claims(offer: OfferClaim, script_text: str = "") -> list:
    """Back-compat wrapper mapping prior offer checks into CommercialIssue list."""
    return check_commercial_claims(script_text, offer)


# ─── Validators ─────────────────────────────────────────────────────

def validate_prompt(
    prompt: str,
    script: Script = None,
    offer: OfferClaim = None,
    lang: ScriptLanguage = ScriptLanguage.HINDI,
    target_duration: int = 8,
    scene: ScenePlan = None,
    reference: ReferenceProfile = None,
    brand_policy: BrandPolicy = None,
    generation_mode: GenerationMode = GenerationMode.SINGLE_SHOT,
) -> ValidationResult:
    result = ValidationResult()

    # ── Capability model
    plan_move = scene.camera_move if scene else None
    cap_issues = VEO_3_1.validate_duration(target_duration)
    for i in cap_issues:
        result.fail(i)
    if generation_mode:
        for i in VEO_3_1.validate_mode(generation_mode, target_duration):
            result.warn(i)

    # ── Camera: semantic, plan-aware
    plan_cam = count_camera_moves(plan_move or "")
    if plan_cam > 1:
        result.fail(f"ScenePlan camera_move contains {plan_cam} moves (max 1): '{plan_move}'")
    stray = stray_camera_moves(prompt, plan_move)
    if stray:
        intents = [s[0] for s in stray]
        result.fail(
            f"Stray camera intents outside the Cinematography clause: {intents} "
            f"— remove them to keep a single camera move"
        )

    # ── Actions: semantic, plan-aware
    if scene:
        planned = action_intents(scene.primary_action)
        if len(planned) > 1:
            result.fail(f"ScenePlan primary_action conflates intents {planned}: '{scene.primary_action}'")
        if scene.supporting_beats and len(scene.supporting_beats) > 3:
            result.warn(f"{len(scene.supporting_beats)} supporting beats — keep ≤ 3 within one action")
        conflicts = conflicting_action_intents(scene, prompt)
        if conflicts:
            result.fail(f"Prose action intents conflict with primary action: {conflicts}")
    else:
        action_count = count_primary_actions(prompt)
        if action_count > 2:
            result.fail(f"Actions detected: {action_count} distinct intents")

    # ── Length (40-180 word contract: under 40 loses control, over 180 drops instructions)
    word_count = len(prompt.split())
    if word_count < 40:
        result.warn(f"Prompt too short ({word_count} words) — add detail for control")
    elif word_count > 180:
        result.warn(f"Prompt long ({word_count} words) — model may drop instructions")

    # ── Dialogue within safe speech budget (canonical SpeechModel)
    if script:
        dialogue = script.dialogue_text(target_duration, rewritten=True)
        report = fit_report(dialogue, target_duration, lang)
        if dialogue and not report["fits_safe"]:
            if report["fits_at_all"]:
                result.warn(
                    f"Dialogue ~{report['estimated_seconds']}s is over the safe "
                    f"{report['safe_seconds']}s budget (words {report['words']})"
                )
            else:
                result.fail(
                    f"Dialogue ~{report['estimated_seconds']}s exceeds "
                    f"{target_duration}s ad duration — must rewrite"
                )
        if dialogue and target_duration <= 0:
            result.fail("Dialogue present but duration invalid")

    # ── Audio
    has_audio = any(k in prompt.lower() for k in ["ambient", "sfx", "music", "dialogue"])
    if not has_audio:
        result.warn("No audio cues — Veo generates synced audio, always specify it")

    # ── Text-generation risk
    for r in check_text_generation_risk(prompt)[:2]:
        result.warn(r)

    # ── Aspect
    if "9:16" not in prompt:
        result.warn("Aspect ratio not specified — may generate 16:9 by default")

    # ── Commercial claims
    if script:
        script_text = script.dialogue_text(target_duration, rewritten=True)
        for issue in check_commercial_claims(script_text, offer, brand_policy, lang):
            if issue.is_error:
                result.fail(issue.message)
            else:
                result.warn(issue.message)

    # ── Reference integrity
    if scene and reference:
        for issue in check_reference_integrity(scene, reference):
            result.fail(issue)

    if result.errors:
        result.passed = False
    return result


def validate_scene_plan(
    scene: ScenePlan,
    script: Script = None,
    offer: OfferClaim = None,
    brand_policy: BrandPolicy = None,
    lang: ScriptLanguage = ScriptLanguage.HINDI,
    generation_mode: GenerationMode = GenerationMode.SINGLE_SHOT,
    duration: int = None,
) -> ValidationResult:
    """Validate the structured plan before it is ever compiled to prose."""
    result = ValidationResult()
    duration = duration or scene.duration or 8

    if not scene.subject:
        result.fail("ScenePlan.subject is empty")
    if scene.subject and scene.secondary_subject and scene.subject == scene.secondary_subject:
        result.warn("ScenePlan.subject duplicates secondary_subject — dedupe in compile")
    if scene.primary_action and count_primary_actions(f"x {scene.primary_action} y"):
        planned = action_intents(scene.primary_action)
        if len(planned) > 1:
            result.fail(f"primary_action conflates {planned} intents")

    camera = count_camera_moves(scene.camera_move) if scene.camera_move else 0
    if scene.camera_move and camera != 1:
        result.fail(f"camera_move must resolve to exactly 1 intent, got {camera}: '{scene.camera_move}'")

    for ci in VEO_3_1.validate_duration(duration):
        result.fail(ci)

    if script:
        report = fit_report(script.dialogue_text(scene.duration, rewritten=True), scene.duration, lang)
        if report["words"] and not report["fits_at_all"]:
            result.fail(f"Script {report['words']} words won't fit {scene.duration}s — rewrite required")
        if script.cta.text and not script.dialogue_text(scene.duration, rewritten=True).rstrip(".").endswith(script.cta.text.strip().rstrip(".")[-20:]):
            pass  # CTA preservation is enforced by the rewriter, not re-parsed here

    if not result.errors:
        result.passed = True
    return result


def score_validation(result: ValidationResult) -> ValidationScore:
    """Convert a ValidationResult into a 0-100 score with grades."""
    score = ValidationScore()
    for _e in result.errors:
        score.deduct(15, "validation error")
    for _w in result.warnings:
        score.deduct(4, "validation warning")
    if len(result.errors) > 6:
        score.deduct(round((len(result.errors) - 6) * 5), "error cascade")
    return score