from .types import ReferenceProfile, ReferencePerson, ReferenceVehicle, ReferenceEnvironment


def create_reference_profile(
    vehicle_model: str = "",
    vehicle_colour: str = "",
    vehicle_trim: str = "",
    person_hair: str = "",
    person_skin_tone: str = "",
    person_clothing: str = "",
    showroom_type: str = "modern_dealership",
) -> ReferenceProfile:
    person = None
    if any([person_hair, person_skin_tone, person_clothing]):
        person = ReferencePerson(
            hair=person_hair,
            skin_tone=person_skin_tone,
            clothing=person_clothing,
        )

    vehicle = None
    if vehicle_model:
        vehicle = ReferenceVehicle(
            model=vehicle_model,
            colour=vehicle_colour,
            trim=vehicle_trim,
        )

    environment = ReferenceEnvironment(
        location_type=showroom_type,
    ) if showroom_type else None

    return ReferenceProfile(
        person=person,
        vehicle=vehicle,
        environment=environment,
    )


def reference_to_prompt_text(profile: ReferenceProfile) -> str:
    """Convert reference profile to a description for the Veo prompt."""
    return profile.describe_for_prompt()


def reference_to_ingredients_block(profile: ReferenceProfile) -> str:
    """Generate instructions for Veo 3.1 Ingredients-to-Video feature."""
    parts = []
    if profile.vehicle:
        parts.append(
            f"Vehicle reference: {profile.vehicle.colour} {profile.vehicle.model}, "
            f"{profile.vehicle.position}, {profile.vehicle.orientation}"
        )
    if profile.person:
        parts.append(
            f"Person reference: {profile.person.hair} hair, "
            f"{profile.person.skin_tone} skin, {profile.person.clothing}"
        )
    if profile.environment:
        parts.append(
            f"Environment reference: {profile.environment.location_type}, "
            f"{profile.environment.lighting} lighting"
        )
    if not parts:
        return ""
    return "Reference images provided for: " + "; ".join(parts) + "."
