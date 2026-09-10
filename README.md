# Dealer Video Prompt Engine — AI Automotive Dealer Creative Engine

Generates optimized Veo prompts for dealer promotional videos.

## Quick Start

```python
from engine import full_pipeline, CampaignObjective, AdConcept

result = full_pipeline(
    objective=CampaignObjective.ENQUIRY,
    ad_concept=AdConcept.PRESENTER_LED,
    car_model="Creta",
    car_colour="abyss black",
    brand="Hyundai",
)

print(result["prompt"])          # Ready-to-paste Veo prompt
print(result["validation"])      # Validation report
print(result["repair_log"])      # What the engine auto-repaired
```

## Architecture

```
Brief (Hyundai wants more enquiries)
  ↓
Creative Director      campaign objective → ad concept → presenter → hook → timeline
  ↓
Scene Planner          shot composition → camera → action → location → lighting → ad timeline
  ↓
Script Engine          hook → offer → product → benefit → CTA (+ speech duration estimate)
  ↓
Offer Engine            verified claims only — no hallucinated numbers
  ↓
Reference Engine       person / vehicle / environment profiles → Veo Ingredients block
  ↓
Prompt Compiler        [Cinematography] [Subject] [Action] [Context] [Style] [Audio]
  ↓
Validator              12 checks (camera count, action count, dialogue fit, text risk, offer claims…)
  ↓
Repair Loop            auto-trims/rewrites to pass
  ↓
Final Veo Prompt       9:16 · 8s · native audio
```

## Modules

| Module | Responsibility |
|--------|---------------|
| `creative_director.py` | Business objective → creative strategy (concept, presenter, hook, ad timeline) |
| `scene_planner.py` | Builds `ScenePlan`: shot type, camera, action, location, lighting, timeline |
| `script_engine.py` | Generates structured scripts (hook/offer/product/benefit/CTA), estimates speech duration, compresses to fit 8s |
| `offer_engine.py` | Offer claims. **Unverified offers render only generic wording — never invented numbers** |
| `reference_engine.py` | Reference profiles for Veo 3.1 Ingredients-to-Video (person/vehicle/environment locks) |
| `camera_engine.py` | Shot-specific composition: headroom, hand visibility, safe zones, vehicle position |
| `audio_engine.py` | Voice/music/ambience/SFX/mixing priority; dialogue fit estimation |
| `brand_engine.py` | Per-OEM policy: approved models, terminology, no invented claims, logo handling |
| `prompt_compiler.py` | Compiles all plans into the final Veo prompt (5+1 formula) |
| `validator.py` | 12 automated checks — camera move count, action count, verb density, dialogue word count, estimated speech duration, subject count, reference integrity, frame safety, offer claim validation, text-generation risk |
| `repair.py` | Auto-fixes: collapses multiple camera moves, trims dialogue to fit, reduces actions |

## Example: Hyundai Enquiry Reel

**Creative Director input:**
```
objective=ENQUIRY
concept=PRESENTER_LED
→ "Salesperson-led finance-offer Reel. Salesperson beside Creta. One slow push-in.
   Salesperson speaks directly to camera. CTA: showroom visit."
```

**Generated script** (with speech duration estimates):
```
hook     (2.3s) Aapke liye ek khaas offer laaye hain.
offer    (2.0s) Ismein special finance options available hain.
product  (1.7s) Ye hamari best-selling SUV hai.
benefit  (1.7s) Comfort aur safety dono milegi.
cta      (1.7s) Aaj hi showroom visit kijiye.
→ 28 words ≈ 9.4s → auto-compressed to fit 8s
```

**Final prompt (simplified):**
```
Cinematography: medium presenter shot with a slow push-in
Subject: salesperson in branded Hyundai uniform
Secondary subject: abyss black Creta
Action: presenter speaks directly to camera while standing beside the car
Context: premium Hyundai dealership showroom. bright showroom track LEDs, warm and even.
Style: photorealistic commercial, shallow depth of field, professional energetic delivery
Audio: Dialogue: Aapke liye ek khaas offer laaye hain. Ismein special finance
  options available hain. Ye hamari best-selling SUV hai. Comfort aur safety dono.
  Music: upbeat professional (soft, behind dialogue). Ambient: soft showroom hum.
  SFX: subtle whoosh on camera move. CTA emphasis: final spoken line, clear and prominent
Brand: Brand: Hyundai (official dealership setting). Approved terminology: SmartSense
  safety, BlueLink connectivity, e-CALL (SOS), Panoramic Sunroof. No invented claims,
  no altered vehicle geometry. Do not generate readable logos or model-name text
Compositing: Offer card: central_safe_zone — composite post-generation. CTA: lower_third
  — overlay post-generation. Vehicle: rear_three_quarter_background
Format: 9:16 vertical, 8 seconds
```

## Offer Truth Layer

**Never hallucinate offer numbers.**

```python
# ⛔ Wrong:
offer = create_unverified_offer(OfferType.FINANCE_RATE)
offer.to_safe_text()  # → "Special finance offers available hain"

# ✅ When real data exists:
offer = create_verified_offer(
    offer_type=OfferType.EXCHANGE_BONUS,
    numeric_value=25000,
    unit="₹",
    validity="31 Dec 2026",
    model="Creta",
    source="dealer memo #142",
)
offer.to_safe_text()  # → "₹25,000 exchange bonus" + validity
```

The validator runs `check_offer_claims()` — if an unverified offer appears alongside specific numbers in the script, it flags hallucination risk.

## Speech Duration Fit

Veo's native dialogue is real — the engine calculates whether a script fits:

```python
from engine import estimate_dialogue_fit, ScriptLanguage
d = estimate_dialogue_fit("28-word script...", 8, ScriptLanguage.HINDI)
# {'word_count': 28, 'estimated_seconds': 8.8, 'fits': False, 'words_over': 3}
```

Scripts that overflow are auto-compressed by `repair.py` before compilation.

## Reference Intelligence (Veo 3.1 Ingredients)

```python
ref = create_reference_profile(
    vehicle_model="Creta", vehicle_colour="abyss black",
    person_hair="black", person_skin_tone="warm",
    person_clothing="dark blue dealership uniform",
)
reference_to_ingredients_block(ref)
# "Reference images provided for: Vehicle reference: abyss black Creta…; Person reference: …; Environment reference: …"
```

## Brands Supported

Hyundai, Maruti Suzuki, Mahindra, Kia, Tata (each with approved models + terminology). Unknown brands fall back to a strict generic policy.

## Workflow Modes (planned API)

- **A** Text → Video
- **B** Reference → Video (Veo 3.1 Ingredients)
- **C** First Frame → Video
- **D** First + Last Frame → Video
- **E** Multi-shot continuity (scene extension)

## Requirements

Python 3.9+, no external dependencies.