from .params import (
    VeoParams, Category, Tone, CameraMove, ShotType,
    LightingStyle, FilmStyle, AudioTrack, Character
)


class SceneBlock:
    def __init__(self, params: VeoParams):
        self.p = params

    def shot(self) -> str:
        parts = [self.p.shot_type.value]
        if self.p.camera_move not in (CameraMove.STATIC, CameraMove.LOCKED_OFF):
            move = self.p.camera_move.value
            move_label = move.replace(" shot", "")
            parts.append(f", {move_label}")
        return "".join(parts)

    def subject(self) -> str:
        parts = [f"glossy {self.p.car_color} {self.p.car_model}"]
        extras = self._category_subject_extras()
        if extras:
            parts.append(extras)
        return " ".join(parts)

    def _category_subject_extras(self) -> str:
        return {
            Category.FESTIVE: self._festive_subject(),
            Category.DEALER_SHOWROOM: self._showroom_subject(),
            Category.OFFER_FEATURES: self._offer_subject(),
            Category.CUSTOMER_TESTIMONIALS: self._testimonial_subject(),
            Category.CAR_DELIVERY: self._delivery_subject(),
            Category.FEATURES_CLOSEUP: self._feature_subject(),
            Category.FESTIVE_OFFER: self._festive_offer_subject(),
            Category.NEW_LAUNCH: self._launch_subject(),
            Category.SERVICE: self._service_subject(),
        }.get(self.p.category, "")

    def _festive_subject(self) -> str:
        festival = self.p.festival or "festive"
        return (
            f"adorned with garlands of marigold and jasmine, "
            f"a hand-laid rangoli at its front"
        )

    def _showroom_subject(self) -> str:
        return (
            f"gleaming under polished showroom floor reflections, "
            f"part of a pristine lineup"
        )

    def _offer_subject(self) -> str:
        return (
            f"with close-up feature highlights: sculpted grille, "
            f"LED headlamp signature, premium alloy wheel"
        )

    def _testimonial_subject(self) -> str:
        return (
            f"beside its proud new owner, "
            f"fresh off the delivery"
        )

    def _delivery_subject(self) -> str:
        return (
            f"with a silk ribbon across the hood, "
            f"keys in hand"
        )

    def _feature_subject(self) -> str:
        return (
            "in extreme macro detail: the chrome grille "
            "catching light, glossy paint reflections "
            "sweeping across sculpted body lines"
        )

    def _festive_offer_subject(self) -> str:
        return (
            f"dressed with marigold garlands, "
            f"festive decorations on the showroom"
        )

    def _launch_subject(self) -> str:
        return (
            f"shrouded under a satin cover as it is "
            f"dramatically unveiled"
        )

    def _service_subject(self) -> str:
        return (
            f"on a hydraulic lift in a spotless, well-lit service bay, "
            f"technician attending with precision"
        )

    def action(self) -> str:
        return {
            Category.FESTIVE: self._festive_action(),
            Category.DEALER_SHOWROOM: self._showroom_action(),
            Category.OFFER_FEATURES: self._offer_action(),
            Category.CUSTOMER_TESTIMONIALS: self._testimonial_action(),
            Category.CAR_DELIVERY: self._delivery_action(),
            Category.FEATURES_CLOSEUP: self._feature_action(),
            Category.FESTIVE_OFFER: self._festive_offer_action(),
            Category.NEW_LAUNCH: self._launch_action(),
            Category.SERVICE: self._service_action(),
        }.get(self.p.category, self._generic_action())

    def _festive_action(self) -> str:
        return (
            "a sales executive gently places a marigold garland "
            "on the rearview mirror and smiles at the camera"
        )

    def _showroom_action(self) -> str:
        return (
            "camera glides between models, a sales professional "
            "gestures welcomingly toward the featured car"
        )

    def _offer_action(self) -> str:
        return (
            "camera sweeps over sculpted body lines, "
            "lingers on the alloy wheel and LED headlamp"
        )

    def _testimonial_action(self) -> str:
        return (
            "the customer turns to camera with a genuine, "
            "unrehearsed smile, nodding in approval"
        )

    def _delivery_action(self) -> str:
        return (
            "a family receives the keys, the child jumps with "
            "excitement, parents beam with pride"
        )

    def _feature_action(self) -> str:
        return (
            "camera glides slowly along the grille, "
            "light catching every contour"
        )

    def _festive_offer_action(self) -> str:
        return (
            "camera pulls back to reveal the car draped in "
            "festive decor as an executive gestures the offer"
        )

    def _launch_action(self) -> str:
        return (
            "the satin cover slides off in slow motion, "
            "revealing the car as spotlights converge"
        )

    def _service_action(self) -> str:
        return (
            "a technician in branded uniform inspects the engine, "
            "wipes a surface with a microfiber cloth"
        )

    def _generic_action(self) -> str:
        return "a single, clean motion"

    def context(self) -> str:
        lighting = self.p.lighting.value
        setting = self.p.setting
        extras = self._category_context_extras()
        parts = [setting]
        if extras:
            parts.append(f"{lighting}, {extras}")
        else:
            parts.append(f"{lighting}")
        return ". ".join(parts)

    def _category_context_extras(self) -> str:
        extras = {
            Category.FESTIVE: "warm string lights create soft bokeh, diyas flicker gently",
            Category.DEALER_SHOWROOM: "spotless white floor reflecting overhead track LEDs",
            Category.OFFER_FEATURES: "clean showroom backdrop, large display stand nearby",
            Category.CUSTOMER_TESTIMONIALS: "afternoon daylight, open forecourt",
            Category.CAR_DELIVERY: "delivery bay with confetti and balloon arch",
            Category.FEATURES_CLOSEUP: "dark matte background, single key light creating drama",
            Category.FESTIVE_OFFER: "string lights and seasonal decor, warm ambient glow",
            Category.NEW_LAUNCH: "dark showroom, focused spotlights on stage",
            Category.SERVICE: "organized modern service bay, crisp overhead LEDs",
        }
        return extras.get(self.p.category, "")

    def style(self) -> str:
        parts = [self.p.film_style.value]
        parts.append("shallow depth of field")
        tone_map = {
            Tone.PREMIUM: "elevated commercial polish",
            Tone.ENERGETIC: "high-energy vibrant grade",
            Tone.WARM: "warm golden color palette",
            Tone.EPIC: "epic cinematic grade",
            Tone.PROFESSIONAL: "clean professional grade",
            Tone.AUTHENTIC: "natural, documentary feel",
            Tone.DYNAMIC: "bold high-contrast grade",
        }
        tone_label = tone_map.get(self.p.tone, "")
        if tone_label:
            parts.append(tone_label)
        return ", ".join(parts)

    def audio(self) -> str:
        segments = []
        if self.p.audio_track and self.p.audio_track != AudioTrack.NONE:
            segments.append(f"Ambient music: {self.p.audio_track.value}")
        if self.p.ambient_sfx:
            segments.append(f"SFX: {self.p.ambient_sfx}")
        if self.p.dialogue_char and self.p.dialogue_char.has_dialogue:
            ch = self.p.dialogue_char
            voice = ""
            if ch.voice_style:
                article = "an" if ch.voice_style.lstrip().lower().startswith(("a", "e", "i", "o", "u")) else "a"
                voice = f"in {article} {ch.voice_style} voice"
            line = ch.dialogue.strip().rstrip(".")
            segments.append(f"Character says {voice}: {line}")
        return ". ".join(segments) if segments else "Ambient: soft showroom hum"

    def format_line(self) -> str:
        return self.p.format_instruction

    def negatives_line(self) -> str:
        negs = list(self.p.negatives)
        negs.append("blurry faces")
        negs.append("unreadable text")
        return ", ".join(negs)

    def motion_line(self) -> str:
        return f"Motion: {self.p.motion_intensity}"
