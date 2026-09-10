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
| **Action** | ONE beat per clip. 8 seconds holds a glance, a turn, a reveal - not a sequence |
| **Context** | Sensory language: showroom, festive decor, time of day, lighting source |
| **Lighting** | Single strongest realism anchor. Anchor to real sources (showroom LED, golden hour) |
| **Style** | At END of prompt. "Cinematic color grade, shallow depth of field, film grain" |
| **Audio** | The #1 missed lever. Veo generates native sync audio. Dialogue via COLON (no quotes) |
| **Length** | 40-120 words sweet spot. Under 1,024 tokens |
| **Aspect** | 9:16 vertical for Instagram Reels (critical - these are reels!) |
| **Duration** | 8s max per clip (4/6/8 for Veo 3) |
| **Negatives** | Describe what you WANT as exclusion ("uncluttered, empty showroom floor") not "no clutter" |
| **Timestamps** | Only for 2-beat shots: `[00:00-00:04]` / `[00:04-00:08]` |

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

## Architecture

```
dealer-video-prompt-engine/
├── README.md
├── engine/
│   ├── __init__.py
│   ├── templates.py       # All 9 category templates (Veo formula based)
│   ├── generator.py       # Main prompt builder
│   ├── mapping.py         # Category → template mapping + scene blocks
│   └── params.py          # Input parameters (brand, car, offer, etc.)
├── examples/
│   └── sample_prompts.md  # Rendered examples for all 9 categories
└── references/
    └── veo_prompting_guide.md  # Research summary
```

## Prompt Template Recipe (each category)

Every generated prompt renders as:

```
[SHOT TYPE + CAMERA MOVE] of [SUBJECT: car model + color + condition],
[ACTION: single beat], in [CONTEXT: location + lighting + atmosphere].
[STYLE: grade + lens + film look]. [AUDIO: ambience + dialogue + score].
9:16 vertical, 8 seconds. Motion low.
```

Actually NO - research says narrative blending beats rigid sections. So:

```
"Cinematic slow push-in on a glossy BMW 5 Series in deep blue,
parked under festive marigold garlands in a dealership showroom.
Warm golden string lights create soft bokeh. A sales executive
hands over the keys with a genuine smile. Shallow depth of field,
photoreal commercial grade, warm festive tones. Ambient: soft
festival music, gentle crowd murmur. SFX: keys jingling."
```

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

## Implementation Plan

### Step 1: Core Framework
- `params.py`: CarType, Brand, Color, Festival, Offer, Tone, Duration
- `templates.py`: 9 category templates with scene blocks
- `generator.py`: render function that blends parts into natural prose

### Step 2: Example Outputs
- Generate one example per category for a sample car (e.g., "Tata Nexon")
- Write to `examples/sample_prompts.md`

### Step 3: Validation
- Character/token count check (40-120 words target)
- Checklist verification (has camera, action, context, audio?)

### Step 4: Meta-prompt interface
- Optional mode: output a meta instruction to feed Gemini to elaborate the skeletal prompt

## Success Criteria
1. Each category produces a Veo-formula-compliant natural-language prompt
2. Prompts are parameterized (brand, car, festival, offer)
3. Word count within target range
4. Audio always present (the #1 missed lever)
5. 9:16 vertical always emphasized (Instagram Reels)