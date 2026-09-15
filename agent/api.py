import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .audit import AuditTrail
from .config import AgentConfig, default_config
from .graph import build_graph
from .llm import LLMClient, FakeLLM, get_client


@dataclass
class AgentResult:
    accepted: bool
    rounds: int
    prompt: str
    prompt_structured: str
    blueprint: Any
    validation: Dict[str, Any]
    engine_score: Dict[str, Any]
    critique: Dict[str, Any]
    mutations_rejected: list
    provider: str
    model: str
    audit_dir: str
    repair_log: list = field(default_factory=list)
    was_repaired: bool = False
    elapsed_ms: float = 0.0

    def as_dict(self) -> Dict[str, Any]:
        return {
            "accepted": self.accepted,
            "rounds": self.rounds,
            "prompt": self.prompt,
            "prompt_structured": self.prompt_structured,
            "validation": self.validation,
            "engine_score": self.engine_score,
            "critique": self.critique,
            "mutations_rejected": self.mutations_rejected,
            "provider": self.provider,
            "model": self.model,
            "audit_dir": self.audit_dir,
            "repair_log": self.repair_log,
            "was_repaired": self.was_repaired,
            "elapsed_ms": round(self.elapsed_ms, 1),
        }


def run_agent(
    user_input: Dict[str, Any],
    config: Optional[AgentConfig] = None,
    verbose: bool = False,
) -> AgentResult:
    cfg = (config or default_config()).resolve()
    cfg.provider = "fake" if not cfg.api_key and cfg.provider != "fake" else cfg.provider
    audit = AuditTrail(cfg.audit_path())
    llm: LLMClient = get_client(cfg)
    if verbose:
        _banner(cfg, offline=isinstance(llm, FakeLLM))
    app = build_graph(cfg, llm, audit)
    started = time.time()
    final = app.invoke({
        "user_input": user_input,
        "target_score": cfg.target_score,
        "max_iterations": cfg.max_iterations,
        "provider": cfg.provider,
        "model": cfg.model,
        "audit": audit,
    })
    elapsed = (time.time() - started) * 1000
    result = AgentResult(
        elapsed_ms=elapsed,
        **(final.get("result") or {}),
    )
    if verbose:
        _report(result, audit_dir=cfg.audit_path(), trail=list(audit.timeline()))
    return result


def _banner(cfg, offline: bool):
    mode = "OFFLINE (fake) determinism" if offline else cfg.provider
    print(f"[agent] provider={cfg.provider} model={cfg.model} max_iter={cfg.max_iterations} "
          f"target={cfg.target_score} | {mode}")


def _report(result: AgentResult, audit_dir, trail):
    print(f"\n[agent] accepted={result.accepted} rounds={result.rounds} "
          f"elapsed={result.elapsed_ms:.0f}ms")
    print(f"[agent] critic total={result.critique.get('total')}")
    print(f"[agent] engine score={result.engine_score.get('final')} "
          f"passed={result.validation.get('passed')}")
    if result.mutations_rejected:
        print(f"[agent] rejected mutations: {result.mutations_rejected}")
    print(f"[agent] audit trail: {audit_dir}")
    print("\n" + ("#" * 60))
    print("# FINAL VEO PROMPT  " + ("ACCEPTED" if result.accepted else "BEST-EFFORT (not gate-passed)"))
    print("#" * 60)
    print(result.prompt + "\n")
    print("#" * 60)
    print("# CRITIC QUICK VIEW")
    print("#" * 60)
    for issue in result.critique.get("issues", [])[:5]:
        print(f"- {issue}")