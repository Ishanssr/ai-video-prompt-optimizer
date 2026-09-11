"""
Full pipeline demo: ONE Brief → creative strategy → script (rewritten to fit)
→ scene → reference → brand → audio → compile → validate → STRUCTURAL repair
→ recompile → final validate → scored result.

Run:  python3 examples/run_pipeline.py
"""

import sys
sys.path.insert(0, ".")

from engine import (
    Brief, CampaignObjective, AdConcept, ContentFormat, ScriptLanguage, VoiceStyle,
    DeliveryPacing, GenerationMode,
    OfferType, create_verified_offer,
    full_pipeline, resolve_visual_action,
)


def demo_enquiry_reel():
    print("═══════════════════════════════════════════════════")
    print(" DEMO 1: Hyundai enquiry reel (salesperson-led)")
    print("═══════════════════════════════════════════════════\n")

    brief = Brief(
        objective=CampaignObjective.ENQUIRY,
        ad_concept=AdConcept.PRESENTER_LED,
        brand="Hyundai",
        car_model="Creta",
        car_colour="abyss black",
        format=ContentFormat.INSTAGRAM_REEL,
        language=ScriptLanguage.HINDI,
        voice_style=VoiceStyle.CONFIDENT,
        pacing=DeliveryPacing.MEDIUM_FAST,
        duration=8,
        offer=create_verified_offer(
            OfferType.EXCHANGE_BONUS,
            unit="₹", numeric_value=30000,
            validity="31 Dec 2026",
            model="Creta",
            source="Hyundai dealer memo #142",
        ),
    )

    out = full_pipeline(brief)

    print(f"[Brief] {brief.objective.value} · {brief.ad_concept.value} · {brief.car_model} · {brief.duration}s")
    print(f"[Creative] action: {resolve_visual_action(brief.objective, brief.ad_concept)['primary']}")
    print(f"[Script]  {out['script'].dialogue_text(brief.duration)}\n")

    print("────── FINAL VEO PROMPT (narrative canonical) ──────\n")
    print(out["prompt"])
    print("\n────── STRUCTURED PROMPT (inspection) ──────\n")
    print(out["prompt_structured"])
    print("\n────── CREATIVE BLUEPRINT ──────\n")
    bp = out["blueprint"]
    print(f"Campaign: {bp.campaign.objective.value} · {bp.campaign.ad_concept.value} · pattern={bp.campaign.creative_pattern}")
    print(f"Action:   dominant={bp.action.dominant}")
    print(f"          micro={bp.action.micro_behavior} · background={bp.action.background_behavior}")
    print(f"Post:     offer_card={bp.post.offer_card} · CTA={bp.post.cta_overlay}")
    print("\n──────────────────────────────")
    print(f"Validation passed: {out['validation']['passed']}")
    print(f"Errors:   {out['validation']['errors']}")
    print(f"Warnings: {out['validation']['warnings']}")
    print(f"Score:    {out['score']['final']} ({out['score']['final_grade']})")
    print(f"Repairs:  {out['repair_log']}")
    print(f"Composited after generation: {', '.join(out['overlay_plan']['composited_after'])}")


def demo_script_rewriting():
    print("\n═══════════════════════════════════════════════════")
    print(" DEMO 2: Rewriting (not truncation) + claim guard")
    print("═══════════════════════════════════════════════════\n")

    brief = Brief(
        objective=CampaignObjective.ENQUIRY,
        ad_concept=AdConcept.PRESENTER_LED,
        brand="Hyundai", car_model="Creta",
        duration=8,
        custom_hook="Duniya ki sabse best-selling SUV aapko is showroom mein milegi.",
        custom_cta="Visit kijiye, ek number deal.",
    )
    out = full_pipeline(brief)

    print(f"Repairs:  {out['repair_log']}")
    print(f"Final:    {out['script'].dialogue_text(8)!r}")
    print(f"Speech:   {out['script'].estimated_duration}s target 8s (safe budget ~6.8s)")
    print(f"Score:    {out['score']['final']} ({out['score']['final_grade']})")


def demo_verified_offer():
    print("\n═══════════════════════════════════════════════════")
    print(" DEMO 3: Verified offer — numbers appear safely")
    print("═══════════════════════════════════════════════════\n")
    offer = create_verified_offer(
        offer_type=OfferType.EXCHANGE_BONUS,
        numeric_value=25000,
        unit="₹",
        validity="31 Dec 2026",
        model="Creta",
        source="Hyundai dealer memo #142",
    )
    from engine import offer_to_script_text
    print(f"Verified offer → {offer_to_script_text(offer, ScriptLanguage.HINDI)}")
    print(f"Voiceover      → {offer_to_script_text(offer, ScriptLanguage.ENGLISH)}")


def demo_multishot():
    print("\n═══════════════════════════════════════════════════")
    print(" DEMO 4: Multi-shot timed mode scaffold")
    print("═══════════════════════════════════════════════════\n")
    brief = Brief(
        objective=CampaignObjective.BOOKING,
        ad_concept=AdConcept.PRESENTER_LED,
        brand="Maruti Suzuki", car_model="Baleno", car_colour="Nexa blue",
        generation_mode=GenerationMode.MULTI_SHOT_TIMED,
    )
    out = full_pipeline(brief)
    print(out["prompt_timed"] or "(no timed scaffold for single-shot mode)")


if __name__ == "__main__":
    demo_enquiry_reel()
    demo_script_rewriting()
    demo_verified_offer()
    demo_multishot()