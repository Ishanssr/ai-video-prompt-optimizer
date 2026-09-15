import json
import time
from pathlib import Path
from typing import Any, Dict


class AuditTrail:
    """JSONL step-by-step trail of every agent decision for production review."""

    def __init__(self, run_dir: Path):
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self._path = self.run_dir / "trail.jsonl"
        self._path.touch(exist_ok=True)

    def log(
        self,
        node: str,
        *,
        provider: str = "",
        model: str = "",
        input_preview: Dict[str, Any] = None,
        output: Dict[str, Any] = None,
        score: float = None,
        status: str = "ok",
        iteration: int = 0,
    ):
        entry = {
            "ts": round(time.time(), 3),
            "node": node,
            "provider": provider,
            "model": model,
            "iteration": iteration,
            "status": status,
            "score": score,
            "input": _preview(input_preview),
            "output": _preview(output),
        }
        with open(self._path, "a") as fh:
            fh.write(json.dumps(entry) + "\n")
        return entry

    def write_final(self, result: Dict[str, Any]):
        with open(self.run_dir / "final.json", "w") as fh:
            json.dump(result, fh, indent=2, default=str)

    def timeline(self) -> list:
        events = []
        with open(self._path) as fh:
            for line in fh:
                if line.strip():
                    events.append(json.loads(line))
        return events


def _preview(value, limit: int = 60):
    if value is None:
        return None
    try:
        text = json.dumps(value, default=str, ensure_ascii=False)
    except TypeError:
        text = str(value)
    if len(text) > limit * 4:
        text = text[: limit * 4] + f"...[truncated {len(text) - limit*4} chars]"
    return text