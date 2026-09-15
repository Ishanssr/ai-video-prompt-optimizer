import os
import shutil
import uuid
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AgentConfig:
    provider: str = "fake"
    model: str = ""
    api_key: str = ""
    max_iterations: int = 3
    target_score: int = 85
    audit_dir: str = "agent_runs"
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    def resolve(self) -> "AgentConfig":
        self.provider = os.environ.get("VEO_AGENT_PROVIDER", self.provider).lower()
        self.api_key = os.environ.get("VEO_AGENT_API_KEY", "").strip()
        self.max_iterations = int(os.environ.get("VEO_AGENT_MAX_ITERATIONS", self.max_iterations))
        self.target_score = int(os.environ.get("VEO_AGENT_TARGET_SCORE", self.target_score))
        self.audit_dir = os.environ.get("VEO_AGENT_AUDIT_DIR", self.audit_dir)
        return self

    def model_for(self, provider: str) -> str:
        env_model = os.environ.get("VEO_AGENT_MODEL", "").strip()
        if env_model:
            return env_model
        default_models = {
            "openai": "gpt-4o",
            "anthropic": "claude-sonnet-4-20250514",
            "gemini": "gemini-2.0-flash",
            "fake": "fake/offline",
        }
        return default_models.get(provider, "gpt-4o")

    def api_key_env_for(self, provider: str) -> str:
        standard = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": "GEMINI_API_KEY",
        }
        return standard.get(provider, "VEO_AGENT_API_KEY")

    def audit_path(self) -> Path:
        return Path(self.audit_dir) / self.run_id

    def is_offline(self) -> bool:
        return self.provider == "fake" or not self.api_key


def default_config() -> AgentConfig:
    cfg = AgentConfig().resolve()
    if cfg.provider != "fake" and not cfg.api_key:
        fallback = os.environ.get(cfg.api_key_env_for(cfg.provider), "").strip()
        cfg.api_key = fallback
    if cfg.provider != "fake" and not cfg.api_key:
        cfg.provider = "fake"
    if not cfg.model:
        cfg.model = cfg.model_for(cfg.provider)
    return cfg


def ensure_online(cfg: AgentConfig) -> AgentConfig:
    if cfg.provider == "fake":
        raise RuntimeError(
            "Agent is running with the OFFLINE fake provider (no API key found). "
            "Set VEO_AGENT_API_KEY or THE provider's standard key to get real LLM critiques."
        )
    return cfg