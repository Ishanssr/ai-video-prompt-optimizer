# Dealer Video Prompt Engine - Development Plan (v2 - Research-Based)

## Research Findings (Veo 3.1 / Gemini Veo)

### The Official Veo Formula
Google's 5-part formula for optimal control:
```
[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]
```
Source: Google Cloud Blog - "Ultimate prompting guide for Veo 3.1"

### Critical Prompt Elements (verified across 15+ sources)

| Element | Best Practice |
|---------|---------------|
| **Cinematography** | ONE camera move per clip (slow push-in, dolly, tracking). Two moves fight each other |
| **Subject** | Specific, detailed (car model, color, condition). Never "a car" |
| **Action** | ONE dominant action + ONE continuous micro-behavior + inert background per clip (never `"speaks while walking and inspecting"`). Veo 3.1 multi-shot timed mode stitches timestamped segments instead |
| **Context** | Sensory language: showroom, festive decor, time of day, lighting source |
| **Lighting** | Single strongest realism anchor. Anchor to real sources (showroom LED, golden hour) |
| **Style** | At END of prompt. "Cinematic color grade, shallow depth of field, film grain" |
| **Audio** | The #1 missed lever. Veo generates native sync audio. Engine emits `Dialogue:`/`SFX:`/`Ambient:` colon labels — an engine convention, not a Google syntax requirement |
| **Length** | 40-160 words. Under 15 loses control; over 160 the model drops instructions |
| **Aspect** | 9:16 vertical for Instagram Reels (critical - these are reels!) |
| **Duration** | Veo 3.1 clips are 4, 6 or 8 seconds. Single-shot default; multi-shot timed for longer |
| **Negatives** | Describe what you WANT as exclusion ("uncluttered, empty showroom floor") not "no clutter" |
| **Timestamps** | Only in `MULTI_SHOT_TIMED` mode, derived from actually-fitted script timing |

### Key Rules
1. **One camera move** per clip - over-directing creates "swooping mess"
2. **One action** per clip - chained verbs cause morphs
3. **Commentary** - physical description over emotion ("man smiles genuinely, tears in eyes" not "man is happy")
4. **No readable text/logos** in prompt - models render garbled text. Composite later
5. **Motion intensity**: `low` for people closeups, `medium` for hero car shots
6. **First frame = brand** (photoreal commercial aesthetic)

### The "Meta-Prompt" Advantage
Google's own developers use **meta-prompting**: ask an LLM to write elaborate prompts from a template skeleton. The prompt engine should output BOTH:
- A structured template (human-maintainable)
- Instructions that could feed a meta-prompt for elaboration

## Architecture (implemented)

```
dealer-video-prompt-engine/
├── README.md
├── engine/
│   ├── __init__.py                 # Public API (full_pipeline, Brief, enums, ...)
│   ├── types.py                    # Brief, CampaignObjective, AdConcept, ContentFormat,
│   │                               # GenerationMode, ScriptLanguage, SpeechModel + natural
│   │                               # speech budget, OfferClaim/OfferType, ReferenceProfile,
│   │                               # ScenePlan, ShotComposition, Immutable/Mutable vehicle
│   │                               # attrs, BrandPolicy, ValidationScore, RepairPlan,
│   │                               # CreativeBlueprint (Campaign/Presenter/Vehicle/Shot/
│   │                               # Action/Script/Audio/Post specs) ...
│   ├── prompt_compiler.py          # full_pipeline() orchestration + build_blueprint() +
│   │                               # Blueprint → narrative (canonical) + structured compilers
│   │                               # + structural repair loop (validate → fix plan → recompile)
│   ├── creative_director.py        # Strategy per objective+concept+format+language
│   ├── script_engine.py            # Script with SpeechModel-budgeted lines + rewrite engine
│   ├── scene_planner.py            # ScenePlan: single source of action/camera/motion
│   ├── camera_engine.py            # Shot composition: safe zones, framing, position
│   ├── offer_engine.py             # Verified vs unverified offer claims (no invented numbers)
│   ├── reference_engine.py         # ReferenceProfile, immutable/mutable split, scale graph
│   ├── brand_engine.py             # BrandPolicy + model/variant feature applicability
│   ├── audio_engine.py             # Dialogue/SFX/Ambient/Music directive compiler
│   ├── validator.py                # Semantic validation + scored result (0-100, A-F)
│   └── repair.py                   # STRUCTURAL repair (fix the data, then recompile)
├── examples/
│   ├── run_pipeline.py              # End-to-end demo (4 demos)
│   ├── run_agent.py                 # Agent-engine offline demo (fake LLM, audit trail)
│   └── sample_prompts.md            # Rendered examples
├── agent/                           # LangGraph agent layer (requires venv + langgraph)
│   ├── config.py                    # AgentConfig + VEO_AGENT_* env routing
│   ├── llm.py                       # LLMClient + OpenAI/Anthropic/Gemini adapters + FakeLLM
│   ├── graph.py                     # Strategist → Critic ⇄ Modifier → Finalize (AgentState)
│   ├── compile.py                   # build_brief / compile_brief + dialogue_audit
│   ├── mutations.py                 # bounded mutation targets + immutable anchors
│   ├── rubric.py                    # 10-dim critique + gated pass (MUST_PASS ∩ ≥ target)
│   ├── audit.py                     # JSONL trail + final.json per run
│   └── api.py                       # run_agent() public entry (returns AgentResult)
├── references/
│   └── veo_prompting_guide.md      # Research summary (corrected)
├── tests/                          # run_all.py (engine) + run_agent_all.py (agent)
└── requirements.txt                # langgraph (agent layer only)
```

## Prompt Template Recipe (implemented)

The engine folds every plan into a single `CreativeBlueprint` object
(`build_blueprint()` in `prompt_compiler.py`), then compiles BOTH formats
from it. The **narrative form is the canonical payload** (`full_pipeline()`
returns it as `prompt`); the labeled form below is `prompt_structured` and is
what the validator/repair loop reason over:

```
Cinematography: <one camera move>            (no chained moves)
Subject: <presenter/vehicle identity>
Secondary subject: <vehicle w/ identity + position>   (deduped if same as subject)
Action: <ONE dominant action>, <micro-behavior>   (never "while walking and inspecting")
Background: <inert background behavior>
Context: <location>. <lighting>.             (incl. environment reference overrides)
Style: photorealistic commercial, ...
Audio: Dialogue: ... Music: ... Ambient: ... SFX: ...
References: <ingredients-to-video images>    (immutable identity + scale graph)
Brand: <approved terminology + constraints>
Composite after generation: <overlays>       (never generated in Veo)
Format: 9:16 vertical, 8 seconds (Veo 3.1)
```

The action contract is strict: **ONE dominant action + ONE continuous
micro-behavior + an inert background behavior**. This kills the Veo failure
mode of chained/competing intents (`"speaks while gesturing while inspecting"`).
`ActionSpec` in the Blueprint pins `dominant` / `micro_behavior` /
`background_behavior`; the compilers pass them through verbatim, so the
Blueprint and the rendered prompt cannot drift.

Because the prose is regenerated from the same plans every compile, a validator
re-checks the *plans* — not regex-patched final text. Repair mutates the
`ScenePlan`/`Script`, the Blueprint is rebuilt, then recompiled. The length
(40-180 word) contract is enforced on the canonical narrative payload, not the
verbose inspection form.

## Category Templates (based on reference reels)

### 1. Festive
- **Camera**: slow pan or push-in across decorated showroom
- **Subject**: car dressed with garlands/rangoli
- **Context**: warm festive lighting, diyas, marigold
- **Mood**: celebratory, warm, family
- **Audio**: festive instrumental, temple bells, crowd joy

### 2. Dealer Showroom
- **Camera**: wide establishing → dolly through lineup
- **Subject**: multiple cars in showroom floor
- **Context**: spotless floor, track lighting, glass facade
- **Mood**: premium, professional, trustworthy
- **Audio**: subtle ambient showroom, soft jazz/music

### 3. Offer + Features + Showroom
- **Camera**: closeups intercut with wide showroom
- **Subject**: feature closeups (grille, dash, seats)
- **Context**: showroom + offer banners (no readable text)
- **Mood**: urgency, value, exciting
- **Audio**: energetic music, offer announce voice

### 4. Customer Testimonials
- **Camera**: medium closeup, stable, eye-level
- **Subject**: satisfied customer, genuine expression
- **Context**: with their new car, dealership forecourt
- **Mood**: authentic, happy, trust
- **Audio**: customer voice (colon format), ambient

### 5. Car Delivery
- **Camera**: tracking/follow handover moment
- **Subject**: family + car + keys ceremony
- **Context**: delivery bay, ribbon, flowers, confetti
- **Mood**: triumphant, emotional, celebration
- **Audio**: celebratory music, congratulations, applause

### 6. Features/Closeup
- **Camera**: macro extreme closeups, slow glide
- **Subject**: headlamps, alloys, dashboard, touchscreen (no readable UI)
- **Context**: dark studio / glossy reflections
- **Mood**: premium, sleek, high-tech
- **Audio**: soft whoosh, electronic accents, ambient hum

### 7. Festive + Offer
- **Camera**: reveal move, high-energy cuts
- **Subject**: car with festive decor + offer framing
- **Context**: festive showroom, price/offer (unreadable text plate)
- **Mood**: urgency + celebration
- **Audio**: festive music + offer voice announce (colon)

### 8. New Launch
- **Camera**: dramatic slow reveal, curtain drop, spotlight sweep
- **Subject**: new car model premier
- **Context**: stage, spotlights, dark room, crowd silhouettes
- **Mood**: epic, exclusive, exciting
- **Audio**: dramatic score, applause, whoosh

### 9. Service
- **Camera**: tracking around service bay, closeup on precision work
- **Subject**: technicians, car on lift
- **Context**: modern service center, clean, organized
- **Mood**: professional, reliable, caring
- **Audio**: workshop ambient, wrench SFX, soft professionalism music

## Historical Implementation Plan (pre-rewrite notes)

The original plan below predates the current engine; the implemented design and
architecture live in the "Architecture (implemented)" section above.

### Step 1: Core Framework
- `params.py`: CarType, Brand, Color, Festival, Offer, Tone, Duration
- `templates.py`: 9 category templates with scene blocks
- `generator.py`: render function that blends parts into natural prose

### Step 2: Example Outputs
- Generate one example per category for a sample car (e.g., "Tata Nexon")
- Write to `examples/sample_prompts.md`

### Step 3: Validation *(superseded)*
- Word-count check — **now a 40-180 word contract enforced by `validator.py`**
  (under 40 loses control; over 180 risks dropped instructions)
- Checklist verification (camera/action/context/audio) — superseded by the
  semantic plan-level validator + structural repair loop

### Step 4: Meta-prompt interface
- Optional mode: output a meta instruction to feed Gemini to elaborate the skeletal prompt

## Success Criteria
1. Each category produces a Veo-formula-compliant natural-language prompt
2. Prompts are parameterized (brand, car, festival, offer)
3. Word count within target range (40-180 enforced)
4. Audio always present (the #1 missed lever)
5. 9:16 vertical always emphasized (Instagram Reels)