import json
import re
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional


class LLMError(RuntimeError):
    pass


class MalformedOutput(LLMError):
    pass


class LLMClient(ABC):
    @abstractmethod
    def complete_json(
        self,
        system: str,
        user: str,
        schema_hint: str = "",
        temperature: float = 0.4,
    ) -> Dict[str, Any]:
        return self._parse(self._complete(system + "\n\n" + schema_hint, user, temperature))

    @abstractmethod
    def _complete(self, system: str, user: str, temperature: float) -> str:
        raise NotImplementedError

    @staticmethod
    def _parse(text: str) -> Dict[str, Any]:
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if not match:
                raise MalformedOutput(f"no JSON object found in model output: {text[:300]}")
            data = json.loads(match.group(0))
        if not isinstance(data, dict):
            raise MalformedOutput(f"model output is not a JSON object: {text[:300]}")
        return data


class OpenAIAdapter(LLMClient):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def _complete(self, system: str, user: str, temperature: float) -> str:
        import openai

        client = openai.OpenAI(api_key=self.api_key)
        resp = client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content or ""


class AnthropicAdapter(LLMClient):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def _complete(self, system: str, user: str, temperature: float) -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)
        resp = client.messages.create(
            model=self.model,
            max_tokens=2048,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(block.text for block in resp.content if getattr(block, "type", "") == "text")


class GeminiAdapter(LLMClient):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def _complete(self, system: str, user: str, temperature: float) -> str:
        import google.generativeai as genai

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model, system_instruction=system)
        resp = model.generate_content(
            user,
            generation_config={"temperature": temperature, "response_mime_type": "application/json"},
        )
        return resp.text or ""


class FakeLLM(LLMClient):
    def __init__(self, scripted: Optional[Callable[[str, str, "FakeLLM"], Dict[str, Any]]] = None):
        self.scripted = scripted or _demo_fake_responder
        self.calls: List[dict] = []

    def reset(self):
        self.calls = []

    def _complete(self, system, user, temperature=0.4):
        raise NotImplementedError("FakeLLM stages directly from scripted responder")

    def complete_json(self, system, user, schema_hint="", temperature=0.4):
        result = self.scripted(system, user, self)
        self.calls.append({"system": system, "user": user, "output": result})
        return result


def _demo_fake_responder(system: str, user: str, llm: FakeLLM) -> Dict[str, Any]:
    lowered = system.lower()
    if "creative strategist" in lowered:
        return {
            "voice_style": "confident",
            "pacing": "medium_fast",
            "duration": 8,
            "custom_hook": "Nayi Creta — aapke sapno mein hai.",
            "custom_benefit": "Nayi design, nayi power.",
            "custom_cta": "Abhi test drive book kijiye.",
            "offer_framing": "Use the verified offer wording exactly as written by the engine.",
            "ad_concept": "reveal",
            "rationale": "offline fake strategist",
        }
    if "refinement agent" in lowered:
        if "hook_strength" in user or "hook" in user:
            return {
                "mutations": [{"target": "custom_hook", "value": "Nayi Creta, abhi dekhiye."}],
                "notes": "offline fake modifier: tightens the hook",
            }
        return {"mutations": [], "notes": "no changes suggested"}
    if "executive creative director critic" in lowered:
        critic_round = sum(1 for c in llm.calls if "critic" in c["system"].lower())
        if critic_round <= 1:
            return {
                "total": 78,
                "passed": False,
                "dims": {
                    "brand_safety": 95, "offer_integrity": 95,
                    "single_dominant_action": 100, "hook_strength": 55,
                    "offer_framing": 92, "cta_actionability": 90,
                    "dialogue_fit": 95, "text_out_of_frame": 100,
                    "shot_grammar_specificity": 85, "clarity_and_detail": 82,
                },
                "issues": ["hook_strength: the hook is a flat statement, not an "
                           "attention-grabbing opener — tighten it"],
                "notes": "offline fake critic round one: demands a stronger hook",
            }
        return {
            "total": 92,
            "passed": True,
            "dims": {
                "brand_safety": 95, "offer_integrity": 95,
                "single_dominant_action": 100, "hook_strength": 88,
                "offer_framing": 92, "cta_actionability": 90,
                "dialogue_fit": 95, "text_out_of_frame": 100,
                "shot_grammar_specificity": 85, "clarity_and_detail": 88,
            },
            "issues": [],
            "notes": "offline fake critic: gates pass, refinement accepted",
        }
    if "modifier" in lowered or "refinement agent" in lowered or "refinement" in lowered:
        if "hook_strength" in user or "hook" in user:
            return {
                "mutations": [{"target": "custom_hook", "value": "Nayi Creta, abhi dekhiye."}],
                "notes": "offline fake modifier: tightens the hook",
            }
        return {"mutations": [], "notes": "no changes suggested"}
    return {}


def get_client(cfg) -> LLMClient:
    cls = {
        "openai": OpenAIAdapter,
        "anthropic": AnthropicAdapter,
        "gemini": GeminiAdapter,
    }.get(cfg.provider)
    if cfg.provider == "fake" or cls is None:
        return FakeLLM()
    return cls(api_key=cfg.api_key, model=cfg.model)