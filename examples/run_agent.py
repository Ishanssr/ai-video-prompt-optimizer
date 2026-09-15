#!/usr/bin/env python3
"""Offline demo of the agent engine (FakeLLM, no API key)."""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent.api import run_agent
from agent.config import AgentConfig
from agent.llm import FakeLLM


def main():
    brief = {
        "objective": "new_launch",
        "ad_concept": "reveal",
        "brand": "Hyundai",
        "car_model": "Creta",
        "car_colour": "abyss black",
        "duration": 8,
        "language": "hindi",
        "creative_direction": "premium new-launch reveal feel, high energy, short punchy hook",
    }

    print("=" * 60)
    print("VEO AGENT ENGINE — OFFLINE DEMO")
    print("=" * 60)
    result = run_agent(brief, verbose=True)

    if result.accepted:
        print("\n✅ Agent gate passed — prompt ready for Veo 3.1")
    else:
        print("\n⚠️  Not gate-passed; best effort returned (offline critic limits quality)")
    print(f"Audit: {result.audit_dir}/trail.jsonl")


if __name__ == "__main__":
    main()
