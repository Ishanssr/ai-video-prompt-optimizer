from dataclasses import dataclass, field
from typing import Dict, List


MUST_PASS_AT = 80

RUBRIC_DIMS = [
    ("brand_safety", "No invented claims, approved terminology, logo is NOT generated in-frame"),
    ("offer_integrity", "Numbers appear ONLY from a verified offer; otherwise generic wording"),
    ("single_dominant_action", "Exactly ONE dominant action + continuous micro-behavior; no competing intents"),
    ("hook_strength", "First 1.5s hooks attention for the target audience"),
    ("offer_framing", "Offer is clear, truthful, and prominent"),
    ("cta_actionability", "CTA is specific, simple, and actionable"),
    ("dialogue_fit", "Dialogue fits the speech budget with a safe margin"),
    ("text_out_of_frame", "No readable text/logos directive; overlays deferred to post-production"),
    ("shot_grammar_specificity", "Camera move, framing, lighting, and depth are concrete and unambiguous"),
    ("clarity_and_detail", "Everything an 8s single shot needs is specified; nothing contradictory"),
]

MUST_PASS_DIMS = {
    "brand_safety",
    "offer_integrity",
    "single_dominant_action",
    "text_out_of_frame",
}


@dataclass
class Critique:
    total: float = 0.0
    passed: bool = False
    dims: Dict[str, float] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    notes: str = ""

    @classmethod
    def from_llm(cls, data: dict) -> "Critique":
        dims = {}
        issues = []
        raw_dims = data.get("dims") or {}
        for name, _ in RUBRIC_DIMS:
            val = raw_dims.get(name)
            dims[name] = max(0.0, min(100.0, float(val))) if val is not None else 0.0
        for item in data.get("issues") or []:
            if isinstance(item, str):
                issues.append(item)
        total = float(data.get("total", 0))
        if not total:
            total = sum(dims.values()) / max(1, len(dims))
        else:
            total = max(0.0, min(100.0, total))
        return cls(
            total=total,
            dims=dims,
            issues=issues,
            notes=data.get("notes", ""),
            passed=bool(data.get("passed")),
        )

    def gated_passed(self, target_score: int) -> tuple:
        gate_violations = []
        for name in MUST_PASS_DIMS:
            score = self.dims.get(name, 0.0)
            if score < MUST_PASS_AT:
                gate_violations.append(f"{name}={score:.0f} (<{MUST_PASS_AT})")
        if gate_violations:
            passed = False
        else:
            passed = bool(self.passed) and self.total >= target_score
        return passed, gate_violations

    def as_dict(self) -> Dict[str, object]:
        return {
            "total": round(self.total, 1),
            "passed": self.passed,
            "dims": {k: round(v, 1) for k, v in self.dims.items()},
            "issues": self.issues,
            "notes": self.notes,
        }


def critic_prompt_schema() -> str:
    dims_bl = ", ".join(f"{name}" for name, _ in RUBRIC_DIMS)
    return (
        "Return STRICT JSON only:\n"
        '{"total": <0-100>, "passed": <bool>, '
        '"dims": {' + ", ".join(f'"{n}": <0-100>' for n, _ in RUBRIC_DIMS) + "}, "
        '"issues": ["one actionable issue per problem found"], '
        '"notes": "<one-line summary>"}\n'
        "Scores per dim (" + dims_bl + "). Be a demanding art director AND a "
        "Veo-motion expert: every issue must be concrete and reparable."
    )