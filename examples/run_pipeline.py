"""
Full pipeline demo: brief → creative strategy → script → scene → offer → prompt → validate → repair.

Run:  python3 examples/run_pipeline.py
"""

import sys
sys.path.insert(0, ".")

from engine import (
    CampaignObjective, AdConcept, ContentFormat, ScriptLanguage, VoiceStyle,
    OfferType, create_verified_offer, create_unverified_offer,
    create_reference_profile, get_brand_policy,
    creative_director, generate_script, plan_scene,
    compile_optimized_prompt,
)


def demo_enquiry_reel():
    print("═══════════════════════════════════════════════════")
    print(" DEMO 1: Hyundai enquiry reel (salesperson-led)")
    print("═══════════════════════════════════════════════════\n")

    brief = creative_director(
        objective=CampaignObjective.ENQUIRY,
        ad_concept=AdConcept.PRESENTER_LED,
        format=ContentFormat.INSTAGRAM_REEL,
        language=ScriptLanguage.HINDI,
    )
    print(f"[Creative Director] Concept: {brief['ad_concept']}")
    print(f"  Presenter: {brief['presenter']['description']}")
    print(f"  Action: {brief['visual_action']}\n")

    script = generate_script(
        objective=CampaignObjective.ENQUIRY,
        ad_concept=AdConcept.PRESENTER_LED,
        language=ScriptLanguage.HINDI,
        voice_style=VoiceStyle.CONFIDENT,
    )
    print("[Script Engine]")
    for line in script.all_lines:
        if line.text:
            print(f"  [{line.segment:8s}] {line.duration_seconds:.1f}s  {line.text}")
    print(f"  total {script.total_words} words ≈ {script.estimated_duration:.1f}s (8s target)\n")

    offer = create_unverified_offer(OfferType.FINANCE_RATE)
    print(f"[Offer Engine] (no verified data) → {offer.to_safe_text(ScriptLanguage.HINGLISH)}\n")

    scene = plan_scene(
        CampaignObjective.ENQUIRY, AdConcept.PRESENTER_LED,
        car_model="Creta", car_colour="abyss black", brand="Hyundai",
        script=script,
    )
    print(f"[Scene Plan] {scene.composition.shot_type} · {scene.composition.camera_move}")
    print(f"  subject={scene.subject!r} · car={scene.secondary_subject!r}")
    print(f"  location={scene.location!r} · lighting={scene.lighting!r}\n")

    result = compile_optimized_prompt(
        scene,
        script=script,
        offer=offer,
        brand_policy=get_brand_policy("Hyundai"),
        duration=8,
    )

    print("────── FINAL VEO PROMPT ──────\n")
    print(result["prompt"])
    print("\n──────────────────────────────")
    print(f"Validation passed: {result['validation']['passed']}")
    print(f"Errors:   {result['validation']['errors']}")
    print(f"Warnings: {result['validation']['warnings']}")
    print(f"Repairs:  {result['repair_log']}")


def demo_verified_offer():
    print("\n═══════════════════════════════════════════════════")
    print(" DEMO 2: Verified offer — numbers appear safely")
    print("═══════════════════════════════════════════════════\n")

    offer = create_verified_offer(
        offer_type=OfferType.EXCHANGE_BONUS,
        numeric_value=25000,
        unit="₹",
        validity="31 Dec 2026",
        model="Creta",
        source="Hyundai dealer memo #142",
    )
    print(f"Verified offer → {offer.to_safe_text(ScriptLanguage.HINDI)}")
    print(f"Voiceover      → {offer.to_safe_text(ScriptLanguage.ENGLISH)}")

    offer2 = create_unverified_offer(OfferType.FINANCE_RATE)
    print(f"Unverified      → {offer2.to_safe_text(ScriptLanguage.HINDI)}  (safe, no numbers)")
    print(f"  disclaimer: {offer2.disclaimer or '(standard terms apply)'}")


def demo_references():
    print("\n═══════════════════════════════════════════════════")
    print(" DEMO 3: Reference profiles (Veo 3.1 Ingredients)")
    print("═══════════════════════════════════════════════════\n")

    ref = create_reference_profile(
        vehicle_model="Creta",
        vehicle_colour="abyss black",
        person_hair="black",
        person_skin_tone="warm",
        person_clothing="dark blue dealership uniform",
        showroom_type="modern Hyundai showroom",
    )
    print(reference_to_ingredients_block(ref) if "reference_to_ingredients_block" in dir() else "run demo 1 first")
    from engine import reference_to_ingredients_block
    print(reference_to_ingredients_block(ref))


if __name__ == "__main__":
    demo_enquiry_reel()
    demo_verified_offer()
    demo_references()