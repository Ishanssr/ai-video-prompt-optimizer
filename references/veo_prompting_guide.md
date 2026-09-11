# Veo 3.1 Prompting Reference

Research summary for the Dealer Video Prompt Engine.

---

## The Veo Formula

Google's official 5-part formula:

```
[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]
```

With Veo 3.1, **audio** becomes a 6th mandatory layer.

Sources:
- Google DeepMind Prompt Guide: https://deepmind.google/models/veo/prompt-guide/
- Google Cloud Ultimate Prompting Guide: https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1
- Google Cloud Video Prompt Guide: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/video-gen-prompt-guide

---

## Optimal Prompt Structure

> **Engine convention note:** the `Dialogue: ...`, `SFX: ...`, `Ambient: ...`,
> `Music: ...` **colon format** used below is the *convention this engine emits*
> as the cleanest way to express Veo's native audio guidance. It is NOT a
> Google-mandated syntax requirement — it is our ISO-like formatting contract.
> Veo 3.1 accepts natural prose; the colon labels make the segments
> unambiguous, version-controlled, and validation-friendly. The generated
> prompt is kept inside a **40-180-word budget** (under 40 = the model
> auto-expands uncontrollably; over 180 = instructions get dropped).

### Cinematography (Camera)
- **ONE camera move** per clip. Two = "swooping mess"
- Use standard terms: `dolly in`, `tracking shot`, `slow pan`, `crane shot`, `macro glide`
- One move resolves: give it an ending ("settling into place")
- Slow moves > fast moves. Fast = spatial warping
- Arcs: keep under 30 degrees per clip

### Subject
- Be specific: "glossy pearl-white Tata Nexon with chrome grille" > "a car"
- Include color, condition, key distinguishing features
- Texture words for materials: "gleaming", "matte black", "polished chrome"

### Action
- **ONE primary action** per clip, with up to 3 supporting beats (single-shot default)
- Chained actions ("then", "after that") cause morphs
- Physical description over emotion
- Micro-actions for people: "genuine smile", "nodding in approval"
- Dialogue: engine emits `Dialogue: <text>` (colon label), not quotes

### Context / Setting
- Sensory language: specific lighting, time of day, location
- Anchor lighting to real sources: "warm string lights", "golden hour", "showroom track LEDs"
- Foreground/background depth cues for dolly shots

### Style
- Place at END of prompt
- Terms: `photorealistic commercial`, `cinematic`, `subtle 35mm film grain`
- Color grade references: `warm golden palette`, `teal and orange`, `cool blue shadows`
- Depth of field: always specify (`shallow depth of field`)

### Audio (Veo 3/3.1 native)
- The **#1 missed lever** in Veo prompting
- Every prompt should include audio: dialogue, SFX, ambient, or all three
- Dialogue: emitted as `Dialogue: <snip>` by the engine (colon convention)
- Short lines sync best: under 12 words for 8 seconds
- Label SFX: `SFX: keys jingling, confetti pop`
- Label ambient: `Ambient: soft showroom hum, crowd murmur`

---

## Clips, Durations & Modes

- Veo 3.1 generates clips of **4, 6 or 8 seconds** — the engine validates
  `duration` against this capability table, not just "8s".
- **Single-shot (default):** the whole ad is ONE continuous clip; ONE camera
  move, ONE primary action, up to 3 supporting beats.
- **Multi-shot timed:** for longer ads, Veo 3.1's *time-based prompting*
  stitches timestamped segments (`[00:00.0] ...`) into one video. The engine
  offers a `MULTI_SHOT_TIMED` scaffold whose segment boundaries come from the
  *actual fitted script timing* (see `Script.spoken_lines`).
- **Reference images:** Veo 3.1's Ingredients-to-Video accepts up to 5
  reference images and is limited to **8-second** clips; the engine carries
  immutable vehicle identity (model/colour/trim) + a scale graph so those
  attributes survive generation while camera-mutable properties (position,
  orientation) are free to change.

## Key Rules

| Rule | Why |
|------|-----|
| One camera move | Two moves fight, producing random drift |
| One primary action | Chained verbs cause morphs in short clips |
| 40-180 words | Under 15 words = auto-expanded uncontrollably; over 180 = instructions dropped |
| Always include audio | Veo generates synced native audio; silence = generic hum |
| Physical > emotional | "genuine smile" > "happy" (model can't visualize emotion) |
| 9:16 vertical for Reels | Instagram Reels format = portrait orientation |
| No readable text | Models render garbled pseudo-lettering; composite later |
| Generated vs composited | Engine splits "generated in Veo" (cinematography/material) from "composited after" (logo, offer badge, CTA) |
| Negatives as descriptions | "empty, uncluttered floor" not "no clutter" |
| Seed consistency | Same seed = same output; reuse across related shots |
| Clips are 4/6/8s | Use multi-shot timed mode for longer sequences |

---

## The Meta-Prompt Advantage

Google's own UX engineers use **meta-prompting**: feed a skeleton prompt to Gemini and ask it to elaborate. The prompt engine uses this pattern:
1. Structured skeleton generated from templates
2. Optional: feed skeleton to Gemini for multi-page elaboration
3. Iterate on one variable at a time

---

## Aspect Ratios

| Ratio | Use Case |
|-------|----------|
| 9:16 | Instagram Reels, TikTok, YouTube Shorts |
| 16:9 | YouTube, TV, desktop viewing |
| 1:1 | Instagram feed, Facebook feed |

---

## Reference Links

- Veo 3 Prompt Guide (DeepMind): https://deepmind.google/models/veo/prompt-guide/
- Veo 3.1 Ultimate Prompting Guide (Google Cloud): https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1
- Video Generation Prompt Guide (Google): https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/video-gen-prompt-guide
- Best Practices for Veo (Google): https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/best-practice
- Veo 3 Prompt Structure Guide: https://prompt-architects.com/blog/21-veo3-prompt-structure
- DreamPixel Forge Guide: https://www.dreampixelforge.com/blog/veo-3-prompts
